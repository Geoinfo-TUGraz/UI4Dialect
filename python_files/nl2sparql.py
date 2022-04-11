import stanza
from stanza.utils.conll import CoNLL
from thefuzz import process
import nltk
from nltk.corpus import stopwords
from werkzeug.exceptions import InternalServerError
from python_files.init_functions import query_endpoint
import textwrap


class NLProcessor:
    """
    A class for processing the natural language question.

    Args:
        input_question(str): Input question of the user

    Attributes:
        input_question(str): Input question of the user
        processed_question(list): Question after processing
    """

    def __init__(self, input_question):
        self.input_question = input_question
        self.processed_question = []

    def process_question(self):
        """Processing the question using NLP tools"""
        # Create Stanza pipeline (lang=german)
        nlp = stanza.Pipeline(lang='de', dir='C:/Users/gi_admin/stanza_resources', processors='tokenize,mwt,pos,lemma')
        doc = nlp(self.input_question)

        # Store the processed question in a list in the CoNLL format
        self.processed_question_raw = CoNLL.doc2conll(doc)[0]

        #Split and store in list
        for i in range(len(self.processed_question_raw)):
            self.processed_question.append(self.processed_question_raw[i].split("\t"))
            # Workaround --> CoreNLP does not lemmatize "Lemmata" correctly
            if self.processed_question[i][2] == "Lemmata":
                self.processed_question[i][2] = "Lemma"

        # Remove stop words
        nltk.data.path.append("C:\\Users\\gi_admin\\AppData\\Roaming\\nltk_data")
        stop_words = set(stopwords.words("german"))

        # Add words that aren't in the NLTK stopwords list
        add_stopword = ['?', 'zugeordnet']
        stop_words = stop_words.union(add_stopword)
        list_remove = []
        for listitem in self.processed_question:
            if listitem[1].casefold() in stop_words:
                list_remove.append(listitem)

        # Delete stopwords from question
        self.processed_question = [e for e in self.processed_question if e not in list_remove]

    def get_result(self):
        """Return the processed question"""
        return self.processed_question


class ClassIdentifier:
    """
    A class for identifying and matching classes in the processed question.

    Args:
        input_question(str): The processed input question (Output of the NLProcessor)

    Attributes:
        input_question(str): The processed input question (Output of the NLProcessor)
        classes(list): Stores the classes from the database
    """

    def __init__(self, input_question):
        self.input_question = input_question
        self.classes = []

    def get_classes_from_db(self):
        """Queries all classes from the database"""
        querystring = '''
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        Select DISTINCT ?class WHERE {
        ?s rdf:type ?class.
        }'''

        results = query_endpoint(querystring)

        # Store classes from db in list
        for result in results["results"]["bindings"]:
            self.classes.append(result["class"]["value"])

        # Remove URI from classes
        self.classes = [w.replace('http://40.91.234.77/ontology/dboe#', '') for w in self.classes]

        # Remove bedeutung class, because this is a predicate
        self.classes.remove("bedeutung")

    def map_class_to_question(self):
        """Maps the classes from the database to the question

        Returns:
            list: Processed question annotated with classes
        """

        count = 0
        # Loop through rows (words) in input question
        for list_item in self.input_question:
            word = list_item[2]  # Lemmatized word

            # Extract best matching class
            best_match = process.extractOne(word, self.classes)
            print("class", word)
            print("bestmatch", best_match)

            # Check if the match is rated higher than the limit
            if best_match[1] > 90:
                # Append the class to the question
                self.input_question[count].append(best_match[0])
                self.input_question[count].append("class")

            count = count+1

        return self.input_question


class RelationIdentifier:
    """
    A class for identifying and matching relations in the processed question.

    Args:
        input_question(str): The processed input question annotated with classes (Output of the ClassIdentifier)

    Attributes:
        input_question(str): The processed input question annotated with classes (Output of the ClassIdentifier)
        predicates(list): Stores the predicates (relations) from the database
    """

    def __init__(self, input_question):
        self.input_question = input_question
        self.predicates = []

    def get_predicates_from_db(self):
        """Queries all predicates from the database"""
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        Select DISTINCT ?p WHERE {
        ?s ?p ?o 
          FILTER(CONTAINS(str(?p), str(dboe:hat)))
        }'''
        results = query_endpoint(querystring)

        # Store predicates from db in list
        for result in results["results"]["bindings"]:
            self.predicates.append(result["p"]["value"])

        # Remove URI from predicates
        self.predicates = [w.replace('http://40.91.234.77/ontology/dboe#', '') for w in self.predicates]

    def map_relation_to_question(self):
        """Maps the relations (predicates) from the db to the question

        Returns:
            list: Processed question annotated with relations
        """
        count = 0
        # Loop through rows
        for list_item in self.input_question:
            if len(list_item) == 10:
                word = list_item[2]  # Lemmatized word

                # Extract best matching predicate
                best_match = process.extractOne(word, self.predicates)
                print("word", word)
                print("bestmatch", best_match)

                # Check if the match is rated higher than the limit
                if best_match[1] > 85:
                    # Append the relation (predicate) to the question
                    self.input_question[count].append(best_match[0])
                    self.input_question[count].append("relation")

                count = count+1

        return self.input_question


class SpatialRelationIdentifier:
    """
    A class for identifying and matching spatial relations in the processed question.

    Args:
        input_question(str): The processed input question annotated with classes and relations (Output of the RelationIdentifier)

    Attributes:
        input_question(str): The processed input question annotated with classes and relations (Output of the RelationIdentifier)
        dict_spatial_relations(dict): Stores the spatial relations
    """

    def __init__(self, input_question):
        self.input_question = input_question
        self.dict_spatial_relations = {'sfIntersects': 'überschneiden',
                                          'sfWithin': 'innerhalb',
                                          'sfTouches': 'berühren'}
        # near': ['nahe', 'in der Nähe', 'neben']

    def map_spatial_relations_to_question(self):
        """Maps the spatial relations to the question

        Returns:
            list: Processed question annotated with spatial relations
        """
        count = 0
        # Loop through rows
        for list_item in self.input_question:
            if len(list_item) == 10:
                word = list_item[2]  # Lemmatized word

                # Extract best matching georelation
                best_match = process.extractOne(word, self.dict_spatial_relations)
                print("word", word)
                print("bestmatch", best_match)

                # Check if the match is rated higher than the limit
                if best_match[1] > 85:
                    # Append the spatial relation to the question
                    self.input_question[count].append(best_match[2])
                    self.input_question[count].append("georelation")

            count = count+1

        return self.input_question


class InstanceIdentifier:
    """
    A class for identifying and matching instances in the processed question.

    Args:
        input_question(str): The processed input question annotated with classes, relations and spatial relations (Output of the SpatialRelationIdentifier)

    Attributes:
        input_question(str): The processed input question annotated with classes, relations and spatial relations (Output of the SpatialRelationIdentifier)
        instance(str): Stores the instance found in the question
        instances_and_ids_from_db(dict): Stores the instances and their respective ids from the database
        class_of_instance(str): Stores the class of the instance found in the question
        index_of_class_of_instance(int): Position of the class of the instance in the question
        instance_rows(list): Stores the rows of the instance or instance parts
    """

    def __init__(self, input_question):
        self.input_question = input_question
        self.instance = ""
        self.instances_and_ids_from_db = {}
        self.class_of_instance = ""
        self.index_of_class_of_instance = 0
        self.instance_rows = []

    def preprocess_instance(self):
        """Preprocess the question and instance to make it mappable later

        Raises:
            InternalServerError: Gets raised if the question could not be resolved
        """
        # Get class of instance and its index
        for index, item in enumerate(self.input_question):
            if item[-1] == 'class':
                self.class_of_instance = item[-2]
                self.index_of_class_of_instance = index

        # Store the rows of the instance or instance parts
        self.instance_rows = self.input_question[self.index_of_class_of_instance+1:]

        # If the instance is in parts (e.g. Hall in Tirol), put the instance parts together and store it in the list
        if len(self.instance_rows) > 1:
            for item in self.instance_rows:
                self.instance = self.instance + item[1] + " "

            # Remove the instance parts from the question
            [self.input_question.remove(item) for item in self.instance_rows]

            # Add the concatenated instance parts as a new row
            self.input_question.append(['99', self.instance, "", "", "", "", "", "", "", ""])

        # Get the associated predicate of the class
        if self.class_of_instance in ['ort', 'gemeinde', 'region']:
            self.add_predicate = 'dboe:hatNameLang'
        elif self.class_of_instance == 'beleg':
            self.add_predicate = 'dboe:hatBelegbezeichnung'
        elif self.class_of_instance == 'lemma':
            self.add_predicate = 'dboe:hatDBOlemma'
        else:
            raise InternalServerError("Question could not be resolved (Instance)")

    def get_instances_from_db(self):
        """Queries all instances of a class from the database"""
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        Select DISTINCT ?s ?o WHERE {
        ?s rdf:type dboe:'''+self.class_of_instance+'''.
        ?s ''' + self.add_predicate + ''' ?o.
        }'''
        results = query_endpoint(querystring)

        # Store the instances and id's in list
        for result in results["results"]["bindings"]:
            self.instances_and_ids_from_db[result["s"]["value"]] = result["o"]["value"]

    def map_instance_to_question(self):
        """Maps the instance to the question

        Returns:
            list: Processed question annotated with instance
        """
        # Get instance from question
        instance_from_input = self.input_question[-1][1]

        # Extract best matching instance
        best_match = process.extractOne(instance_from_input, self.instances_and_ids_from_db)
        print("word", instance_from_input)
        print("bestmatch", best_match)

        # Check if the match is rated higher than the limit
        if best_match[1] > 90:
            self.input_question[-1].append(best_match[0])  # Store the instance name
            self.input_question[-1].append("instance")
        else:
            raise InternalServerError("Instance was not found in database")

        return self.input_question


class QueryConstructor:
    """
    A class for constructing the SPARQL query based on the previously processed question.

    Args:
        input_question(str): The processed input question annotated with classes, relations, spatial relations and instance (Output of the InstanceIdentifier)

    Attributes:
        input_question(str): The processed input question annotated with classes, relations, spatial relations and instance (Output of the InstanceIdentifier)
        question_attributes(list): Stores the annotations of the question (class, relation, georelation, instance)
        question_values(dict): Stores the values from the database which were annotated to the question (ort, gemeinde, region, lemma, beleg, instance, ...)
        query(str): Stores the querystring
    """

    def __init__(self, processed_question):
        self.processed_question = processed_question
        self.question_attributes = []
        self.question_values = []
        self.query = ""

    def define_querytype_and_value(self):
        """Stores the question attributes and values in lists"""
        for list_item in self.processed_question:
            if len(list_item) == 12:
                # class, relation, instance or georelation
                self.question_attributes.append(list_item[11])
                # beleg, lemma, ort, region, gemeinde, instance...
                self.question_values.append(list_item[10])

    
    def __construct_CCI_query(self):
        """Constructs the SPARQL query for the CCI case
        Example for CCI: Welche Belege gibt es in der Gemeinde Tamsweg?

        Returns:
            str: Querystring
        """
        # If the class of the instance is lemma
        if self.question_values[1] == 'lemma':
            instance = self.question_values[2]  # Lemma

            querystring = textwrap.dedent('''\
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            Select ?belegId ?belegbezeichnung WHERE 
            {
                ?lemmaId dboe:hatDBOlemma "''' + instance + '''"^^xsd:string.
                ?belegId dboe:hatHauptlemma ?lemmaId.
                ?belegId dboe:hatBelegbezeichnung ?belegbezeichnung.
            }''')
        else:
            # Class of instance is Ort, Gemeinde, Region
            class_of_instance = self.question_values[1].capitalize()
            class_of_result = self.question_values[0]  # Beleg, Lemma
            instance = self.question_values[2]  # Locationname
            variables_for_query, added_term = self.__add_term_for_CCI_query(class_of_result, class_of_instance)

            querystring = textwrap.dedent('''\
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>

            Select ''' + variables_for_query + ''' WHERE 
            {   
                BIND("'''+instance+'''"^^xsd:string AS ?locationName)

                ''' + added_term+'''
                ?locationId dboe:hatNameLang ?locationName.
                
                OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                OPTIONAL{
                    SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                    ?geodaten geo:asWKT ?geom.}
                }
            }''')
        return querystring

    def __construct_CI_query(self):
        """Constructs the SPARQL query for the CI case
        Example: Wo gibt es den Beleg xy?

        Returns:
            str: Querystring
        """

        instance = self.question_values[1]  # DBOLemma, Record description (Belegbezeichnung)
        class_of_instance = self.question_values[0]  # Lemma, Beleg

        if class_of_instance == 'lemma':
            querystring = textwrap.dedent('''\
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            Select ?locationId ?locationName ?geom WHERE 
            {
                {
                    ?lemmaId dboe:hatDBOlemma "''' + instance + '''"^^xsd:string.
                    ?belegId dboe:hatHauptlemma ?lemmaId.
                    ?belegzettelId dboe:istBelegzettelVon ?belegId.
                    ?belegzettelId dboe:hatLokationOrt ?locationId.
                    ?locationId dboe:hatNameLang ?locationName.
                
                    OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                    BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                    OPTIONAL{
                        SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                        ?geodaten geo:asWKT ?geom.}
                    }
                }
                UNION
                {   
                    ?lemmaId dboe:hatDBOlemma "''' + instance + '''"^^xsd:string.
                    ?belegId dboe:hatHauptlemma ?lemmaId.
                    ?belegzettelId dboe:istBelegzettelVon ?belegId. 
                    ?belegzettelId dboe:hatLokationGemeinde ?locationId.
                    ?locationId dboe:hatNameLang ?locationName.
                    OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                    BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                    OPTIONAL{
                        SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                        ?geodaten geo:asWKT ?geom.}
                    }
                }
                UNION
                {
                    ?lemmaId dboe:hatDBOlemma "''' + instance + '''"^^xsd:string.
                    ?belegId dboe:hatHauptlemma ?lemmaId.
                    ?belegzettelId dboe:istBelegzettelVon ?belegId.
                    ?belegzettelId dboe:hatLokationRegion ?locationId.
                    ?locationId dboe:hatNameLang ?locationName.
                    OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                    BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                    OPTIONAL{
                        SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                        ?geodaten geo:asWKT ?geom.}
                    }
                }
            }
            ORDER BY ?locationId
            ''')
        else:
            querystring = textwrap.dedent('''\
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            
            Select ?locationId ?locationName ?geom WHERE 
            {
                {
                    ?belegId dboe:hatBelegbezeichnung "''' + instance + '''"^^xsd:string.
                    ?belegzettelId dboe:istBelegzettelVon ?belegId.
                    ?belegzettelId dboe:hatLokationOrt ?locationId.
                    ?locationId dboe:hatNameLang ?locationName.
                    OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                    BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                    OPTIONAL{
                        SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                        ?geodaten geo:asWKT ?geom.}
                    }
                }
                UNION
                {   
                    ?belegId dboe:hatBelegbezeichnung "''' + instance + '''"^^xsd:string.
                    ?belegzettelId dboe:istBelegzettelVon ?belegId.
                    ?belegzettelId dboe:hatLokationGemeinde ?locationId.
                    ?locationId dboe:hatNameLang ?locationName.
                    OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                    BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                    OPTIONAL{
                        SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                        ?geodaten geo:asWKT ?geom.}
                    }
                }
                UNION
                {
                    ?belegId dboe:hatBelegbezeichnung "''' + instance + '''"^^xsd:string.
                    ?belegzettelId dboe:istBelegzettelVon ?belegId.
                    ?belegzettelId dboe:hatLokationRegion ?locationId.
                    ?locationId dboe:hatNameLang ?locationName.
                    OPTIONAL{?locationId geo:hasGeometry ?locationGeodaten.}
                    BIND(IF(BOUND(?locationGeodaten), ?locationGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                    OPTIONAL{
                        SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                        ?geodaten geo:asWKT ?geom.}
                    }
                }
            }
            ORDER BY ?locationId
            ''')
        return querystring

    def __construct_RCI_query(self):
        """Constructs the SPARQL query for the RCI case
        Example: Welches Hauptlemma hat der Beleg xy?

        Returns:
            str: Querystring
        """
        predicate_of_relation = self.question_values[0]
        class_of_instance = self.question_values[1]
        instance = self.question_values[2]  # record_description
        variables_for_query, added_term = self.__add_term_for_RCI_query(instance, predicate_of_relation)

        querystring = textwrap.dedent('''\
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ''' + variables_for_query + ''' WHERE 
        {
            ''' + added_term+'''
        }''')
        return querystring

    def __construct_CgeoRCI_query(self):
        """Constructs the SPARQL query for the CgeoRCI case
        Example: Welche Gemeinden schneiden die Region xy?

        Returns:
            str: Querystring
        """
        class_of_result = self.question_values[0]
        georelation = self.question_values[1]
        class_of_instance = self.question_values[2]
        instance = self.question_values[3]

        # 2 Queries, because of a bug 
        # Strabon crashes, when there is a url from the outer query given into a service query, where 2 geometries are queried
        # 1st query: get the geodata URI from the instance
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        Select ?instanceGeodaten WHERE 
        {
            ?locationId dboe:hatNameLang "''' + instance + '''"^^xsd:string.
            ?locationId rdf:type dboe:''' + class_of_instance + '''.
            ?locationId geo:hasGeometry ?instanceGeodaten.
        }
        '''

        results = query_endpoint(querystring)

        if results["results"]["bindings"]:
            for result in results["results"]["bindings"]:
                instance_geodaten = result["instanceGeodaten"]["value"]

            # 2nd query: Get location_id, location_name and geometry of the result
            querystring = textwrap.dedent('''\
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>
            PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
            
            Select DISTINCT ?locationId ?locationName ?geom WHERE
            {
                ?locationId geo:hasGeometry ?locationGeodaten.
                ?locationId rdf:type dboe:''' + class_of_result + '''.
                ?locationId dboe:hatNameLang ?locationName.

                SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                    ?locationGeodaten geo:asWKT ?geom.
                    <''' + instance_geodaten + '''> geo:asWKT ?instanceGeometry.
                    FILTER(geof:''' + georelation + '''(?geom ,?instanceGeometry))
                }
            }
            ''')

            return querystring
        else:
            raise InternalServerError("No geodata was found for this instance")


    def __add_term_for_CCI_query(self, class_of_result, class_of_instance):
        """Adds a part to the CCI SPARQL query depending on the arguments

        Args:
            class_of_result (str): Defines the class of the query result
            class_of_instance (str): Defines the class of the instance

        Returns:
            list: Includes the query variables and the added SPARQL term
        """

        added_term = '''?belegzettelId dboe:hatLokation''' + class_of_instance + ''' ?locationId.'''

        if (class_of_result == 'beleg') or (class_of_result == 'lemma'):
            added_term = added_term + '''
                ?belegId dboe:hatBelegzettel ?belegzettelId.
                ?belegId dboe:hatBelegbezeichnung ?belegbezeichnung.'''
            variables_for_query = "?belegId ?belegbezeichnung ?locationName ?geom"

        if class_of_result == 'lemma':
            added_term = added_term + '''
                ?belegId dboe:hatHauptlemma ?lemmaId.
                ?lemmaId dboe:hatDBOlemma ?lemmaDBO.'''
            variables_for_query = "?lemmaId ?lemmaDBO ?locationName ?geom"

        return [variables_for_query, added_term]

    def __add_term_for_RCI_query(self, record_description, predicate_of_relation):
        """Adds a part to the RCI SPARQL query depending on the arguments

        Args:
            record_description (str): Record description
            predicate_of_relation (str): Defines the predicate of the relation for the query

        Returns:
            list: Includes the query variables and the added SPARQL term
        """
        added_term = ""
        variables_for_query = ""

        if predicate_of_relation == 'hatBedeutung':
            added_term = '''?belegId dboe:hatBelegbezeichnung "''' + record_description + '''"^^xsd:string.
                ?belegId dboe:hatBedeutung ?bedeutungId.
                ?bedeutungId dboe:hatBeschreibung ?bedeutung.'''
            variables_for_query = "?bedeutungId ?bedeutung"

        if predicate_of_relation == 'hatHauptlemma':
            added_term = added_term + '''?belegId dboe:hatBelegbezeichnung "''' + record_description + '''"^^xsd:string.
            ?belegId dboe:hatHauptlemma ?hauptlemmaId.
            ?hauptlemmaId dboe:hatDBOlemma ?hauptlemmaDBO.'''
            variables_for_query = "?hauptlemmaId ?hauptlemmaDBO"

        if predicate_of_relation == 'hatNebenlemma':
            added_term = added_term + '''?belegId dboe:hatBelegbezeichnung "''' + record_description + '''"^^xsd:string.
            ?belegId dboe:hatNebenlemma ?nebenlemmaId.
            ?nebenlemmaId dboe:hatDBOlemma ?nebenlemmaDBO.'''
            variables_for_query = "?nebenlemmaId ?nebenlemmaDBO"

        return [variables_for_query, added_term]

    def build_query(self):
        """Constructs the query depending on the question_attributes

        Raises:
            InternalServerError: Get raised when the question could not be resolved
        """
        if self.question_attributes == ['class', 'class', 'instance']:
            final_query = self.__construct_CCI_query()

        elif self.question_attributes == ['class', 'instance']:
            final_query = self.__construct_CI_query()

        elif self.question_attributes == ['relation', 'class', 'instance']:
            final_query = self.__construct_RCI_query()

        elif self.question_attributes == ['class', 'georelation', 'class', 'instance']:
            final_query = self.__construct_CgeoRCI_query()
        else:
            raise InternalServerError("Question could not be analyzed correctly")

        self.query = final_query

    def get_query(self):
        """Return the querystring"""
        return self.query


class NL2SPARQL:
    """
    A class for converting the natural language question into a SPARQL query.

    Attributes:
        query(str): Stores the querystring
    """

    def __init__(self):
        self.query = ""

    def create_query_from_question(self, question):
        """Translates the question into SPARQL

        Args:
            question (str): Input question of the user
        """
        # NLP (Natural Language Processor)
        nlp = NLProcessor(question)
        nlp.process_question()
        output_nlp = nlp.get_result()

        # Class Identifier
        cid = ClassIdentifier(output_nlp)
        cid.get_classes_from_db()
        output_cid = cid.map_class_to_question()

        # Relation Identifier
        rid = RelationIdentifier(output_cid)
        rid.get_predicates_from_db()
        output_rid = rid.map_relation_to_question()

        # Spatial Relation Identifier
        grid = SpatialRelationIdentifier(output_rid)
        output_grid = grid.map_spatial_relations_to_question()

        # Instance Identifier
        iid = InstanceIdentifier(output_grid)
        iid.preprocess_instance()
        iid.get_instances_from_db()
        question_fullyAnnotated = iid.map_instance_to_question()

        # Generate Query
        qconst = QueryConstructor(question_fullyAnnotated)
        qconst.define_querytype_and_value()
        qconst.build_query()
        self.query = qconst.get_query()

    def get_query(self):
        """Returns the querystring"""
        return self.query
