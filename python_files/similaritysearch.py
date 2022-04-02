from python_files.init_functions import query_endpoint
from shapely_geojson import dumps, Feature, FeatureCollection
import shapely.wkt
from Levenshtein import distance


class SimilaritySearch:
    """
    A class for searching similar dialect words using the Levenshtein distance.

    Args:
        input_value(str): The starting word
        levenshtein_value(int): The levenshtein distance
        levenshtein_select(str): Level of the location ('1' == Place, '2' == Municipality, '3' == Region)

    Attributes:
        input_value(str): The starting word
        levenshtein_value(int): The levenshtein distance
        levenshtein_select(str): Level of the location ('1' == Place, '2' == Municipality, '3' == Region)
        results(dict): Dict for storing the query data
    """

    def __init__(self, input_value, levenshtein_value, levenshtein_select):
        self.input_value = input_value
        self.levenshtein_value = levenshtein_value
        self.levenshtein_select = levenshtein_select
        self.results = {}

    def get_data_from_db(self):
        """Queries the database to get the data used for the similarity search"""
        # Add term to SPARQL query according to the levenshtein_select
        add_term = ""
        if self.levenshtein_select == '1':  # Places
            add_term = '''?belegzettelId dboe:hatLokationOrt ?locationId.
            ?locationId dboe:hatNameLang ?locationName.   
            ?locationId geo:hasGeometry ?geodaten.
            SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
            ?geodaten geo:asWKT ?geom.
            }'''
        elif self.levenshtein_select == '2':  # Municipalities
            add_term = '''?belegzettelId dboe:hatLokationGemeinde ?locationId.
            ?locationId dboe:hatNameLang ?locationName.   
            ?locationId geo:hasGeometry ?geodaten.
            SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
            ?geodaten geo:asWKT ?geom.
            }'''
        else:  # Regions
            add_term = '''?belegzettelId dboe:hatLokationRegion ?locationId.
            ?locationId dboe:hatNameLang ?locationName.   
            ?locationId geo:hasGeometry ?geodaten.
            SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
            ?geodaten geo:asWKT ?geom.
            }'''

        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>

        SELECT ?locationId ?locationName ?belegId ?bezeichnung ?geom WHERE {
        ?belegId dboe:hatBelegbezeichnung ?bezeichnung.
        ?belegId dboe:hatBelegzettel ?belegzettelId.
        
        ''' + add_term + ''' 
        } order by ?locationName
        '''

        self.results = query_endpoint(querystring)

    def search_records(self):
        """Search similar dialect records/words based on the Levenshtein distance

        Returns:
            str: GeoJSON dictionary
        """
        isAlreadyFeature = False
        features = []

        # Loop through query results
        for result in self.results["results"]["bindings"]:
            location_id = result["locationId"]["value"]
            location_name = result["locationName"]["value"]
            record_id = result["belegId"]["value"]
            record_description = result["bezeichnung"]["value"]
            geom = shapely.wkt.loads(result["geom"]["value"])

            # Calculate levenshtein distance
            edit_dist = distance(record_description, self.input_value)

            # If calculated distance is max the levenshtein value
            if edit_dist <= self.levenshtein_value:
                for feature in features:
                    # Check if the location is already a feature
                    if location_id == feature.properties["lokationId"]:
                        isAlreadyFeature = True
                        break

                if isAlreadyFeature:
                    # If the location is already a feature, just add the record description
                    feature.properties["belege"][record_id] = record_description
                else:
                    # If not, create new feature and add all the data
                    feature1 = Feature(geom, {"lokationId": location_id, "lokationName": location_name, "belege": {record_id: record_description}})
                    features.append(feature1)

                isAlreadyFeature = False

        feature_collection = FeatureCollection(features)
        levenshtein_data = dumps(feature_collection)

        return levenshtein_data
