from python_files.init_functions import query_endpoint
from shapely_geojson import dumps, Feature, FeatureCollection
import shapely.wkt
from shapely.geometry import Point


class Lemma:
    """
    A class for querying lemma data from the database.

    Args:
        lemma_id : The id of the lemma for which data should be queried

    Attributes:
        lemma_id (str): The id of the lemma for which data should be queried
        lemma_dbo (str): The dbo lemma associated to the lemma_id
        standard_german (str): The standard german word of the lemma
        dbpedia (str): The dbpedia link for the lemma
        dict_places (dict): Dict used for storing the lemma data associated to places
        dict_municipalities (dict): Dict used for storing the lemma data associated to municipalities
        dict_regions (dict): Dict used for storing the lemma data associated to regions
    """

    def __init__(self, lemma_id):
        self.lemma_id = lemma_id
        self.lemma_dbo = ""
        self.standard_german = ""
        self.dbpedia = ""
        self.dict_places = {}
        self.dict_municipalities = {}
        self.dict_regions = {}

    def get_data_from_db(self):
        """Calls the methods for querying the database"""
        self.__get_lemma_data()
        self.__get_location_data()

    def __get_lemma_data(self):
        """Queries the database to get data associated with the lemma"""
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        Select ?lemmaDBO ?hochdeutsch ?dbpedia ?belegbezeichnung WHERE {
            <''' + self.lemma_id + '''> rdf:type dboe:lemma.
            <''' + self.lemma_id + '''> dboe:hatDBOlemma ?lemmaDBO.
            OPTIONAL{<''' + self.lemma_id + '''> dboe:hatHochdeutschlemma ?hochdeutsch.}
            OPTIONAL{<''' + self.lemma_id + '''> owl:sameAs ?dbpedia.}
        }
        '''

        results = query_endpoint(querystring)

        # Get data from queryresults
        # DBO Lemma should always be available
        self.lemma_dbo = results["results"]["bindings"][0]["lemmaDBO"]["value"]

        # If no data is available insert empty string
        if "hochdeutsch" in results["results"]["bindings"][0]:
            self.standard_german = results["results"]["bindings"][0]["hochdeutsch"]["value"]

        if "dbpedia" in results["results"]["bindings"][0]:
            self.dbpedia = results["results"]["bindings"][0]["dbpedia"]["value"]

    def __get_location_data(self):
        """Queries the database to get location data associated with the lemma"""
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        Select ?belegId ?belegbezeichnung ?ortId ?ortName ?ortGeom ?gemeindeId ?gemeindeName ?gemeindeGeom ?regionId ?regionName ?regionGeom WHERE 
        {
            {
                <''' + self.lemma_id + '''> rdf:type dboe:lemma.
                ?belegId dboe:hatHauptlemma <''' + self.lemma_id + '''>.
                ?belegId dboe:hatBelegbezeichnung ?belegbezeichnung.
                ?belegzettelId dboe:istBelegzettelVon ?belegId.
                ?belegzettelId dboe:hatLokationOrt ?ortId.
                ?ortId dboe:hatNameLang ?ortName.
                OPTIONAL{?ortId geo:hasGeometry ?ortGeodaten.}
                BIND(IF(BOUND(?ortGeodaten), ?ortGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                OPTIONAL{
                SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                ?geodaten geo:asWKT ?ortGeom.}}
            }
            UNION
            {   
                <''' + self.lemma_id + '''> rdf:type dboe:lemma.
                ?belegId dboe:hatHauptlemma <''' + self.lemma_id + '''>.
                ?belegId dboe:hatBelegbezeichnung ?belegbezeichnung.
                ?belegzettelId dboe:istBelegzettelVon ?belegId.
                ?belegzettelId dboe:hatLokationGemeinde ?gemeindeId.
                ?gemeindeId dboe:hatNameLang ?gemeindeName.
                OPTIONAL{?gemeindeId geo:hasGeometry ?gemeindeGeodaten.}

                BIND(IF(BOUND(?gemeindeGeodaten), ?gemeindeGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                OPTIONAL{SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                ?geodaten geo:asWKT ?gemeindeGeom.}}
            }
            UNION
            {
                <''' + self.lemma_id + '''> rdf:type dboe:lemma.
                ?belegId dboe:hatHauptlemma <''' + self.lemma_id + '''>.
                ?belegId dboe:hatBelegbezeichnung ?belegbezeichnung.
                ?belegzettelId dboe:istBelegzettelVon ?belegId.
                ?belegzettelId dboe:hatLokationRegion ?regionId.
                ?regionId dboe:hatNameLang ?regionName.
                OPTIONAL{?regionId geo:hasGeometry ?regionGeodaten.}

                BIND(IF(BOUND(?regionGeodaten), ?regionGeodaten, "no geodata"^^xsd:string) AS ?geodaten).
                OPTIONAL{SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                ?geodaten geo:asWKT ?regionGeom.}}
            }
        }
        order by ?ortName ?gemeindeName ?regionName
        '''

        results = query_endpoint(querystring)

        # Store data in dictionaries
        dict_places = {}
        dict_municipalities = {}
        dict_regions = {}
        for result in results["results"]["bindings"]:
            # Store data associated to a place in dict_places
            if "ortId" in result:
                place_id = result["ortId"]["value"]
                place_name = result["ortName"]["value"]

                # Get geometry from result; if no geom is available --> set artificial geometry Point(0,0)
                if "ortGeom" in result:
                    place_geom = result["ortGeom"]["value"]
                else:
                    place_geom = 'POINT (0 0)'

                record_id = result["belegId"]["value"]
                record_description = result["belegbezeichnung"]["value"]

                if place_id in dict_places:
                    dict_places[place_id]["belege"][record_id] = record_description
                else:
                    dict_places[place_id] = {"belege": {}}
                    dict_places[place_id]["belege"][record_id] = record_description
                    dict_places[place_id]["locationName"] = place_name
                    dict_places[place_id]["geom"] = place_geom

            # Store data associated to a municipality in dict_municipalities
            if "gemeindeId" in result:
                municipality_id = result["gemeindeId"]["value"]
                municipality_name = result["gemeindeName"]["value"]

                # Get geometry from result; if no geom is available --> set artificial geometry Point(0,0)
                if "gemeindeGeom" in result:
                    municipality_geom = result["gemeindeGeom"]["value"]
                else:
                    municipality_geom = 'POINT (0 0)'

                record_id = result["belegId"]["value"]
                record_description = result["belegbezeichnung"]["value"]

                if municipality_id in dict_municipalities:
                    dict_municipalities[municipality_id]["belege"][record_id] = record_description
                else:
                    dict_municipalities[municipality_id] = {"belege": {}}
                    dict_municipalities[municipality_id]["belege"][record_id] = record_description
                    dict_municipalities[municipality_id]["locationName"] = municipality_name
                    dict_municipalities[municipality_id]["geom"] = municipality_geom

            # Store data associated to a region in dict_regions
            if "regionId" in result:
                region_id = result["regionId"]["value"]
                region_name = result["regionName"]["value"]

                # Get geometry from result; if no geom is available --> set artificial geometry Point(0,0)
                if "regionGeom" in result:
                    region_geom = result["regionGeom"]["value"]
                else:
                    region_geom = 'POINT (0 0)'

                record_id = result["belegId"]["value"]
                record_description = result["belegbezeichnung"]["value"]

                if region_id in dict_regions:
                    dict_regions[region_id]["belege"][record_id] = record_description
                else:
                    dict_regions[region_id] = {"belege": {}}
                    dict_regions[region_id]["belege"][record_id] = record_description
                    dict_regions[region_id]["locationName"] = region_name
                    dict_regions[region_id]["geom"] = region_geom

        self.dict_places = dict_places
        self.dict_municipalities = dict_municipalities
        self.dict_regions = dict_regions

    def create_geojson(self):
        """Creates a GeoJSON dictionary from the queried data

        Returns:
            str: GeoJSON dictionary
        """
        # Create GeoJSON features for places, municipalities and regions
        features = []
        for key in self.dict_places:
            location_id = key
            location_name = self.dict_places[key]["locationName"]
            records = self.dict_places[key]["belege"]
            geom = shapely.wkt.loads(self.dict_places[key]["geom"])

            feature = Feature(geom, {"lemmaDBO": self.lemma_dbo, "hochdeutsch": self.standard_german, "dbpedia": self.dbpedia,
                              "lokationId": location_id, "lokationName": location_name, "belege": records, "lokationTyp": "place"})
            features.append(feature)

        for key in self.dict_municipalities:
            location_id = key
            location_name = self.dict_municipalities[key]["locationName"]
            records = self.dict_municipalities[key]["belege"]
            geom = shapely.wkt.loads(self.dict_municipalities[key]["geom"])

            feature = Feature(geom, {"lemmaDBO": self.lemma_dbo, "hochdeutsch": self.standard_german, "dbpedia": self.dbpedia,
                              "lokationId": location_id, "lokationName": location_name, "belege": records, "lokationTyp": "municipality"})
            features.append(feature)

        for key in self.dict_regions:
            location_id = key
            location_name = self.dict_regions[key]["locationName"]
            records = self.dict_regions[key]["belege"]
            geom = shapely.wkt.loads(self.dict_regions[key]["geom"])

            feature = Feature(geom, {"lemmaDBO": self.lemma_dbo, "hochdeutsch": self.standard_german, "dbpedia": self.dbpedia,
                              "lokationId": location_id, "lokationName": location_name, "belege": records, "lokationTyp": "region"})
            features.append(feature)

        # If no locations are attached to the lemma, set geometry to Point(0,0)
        if not features:
            feature = Feature(Point(0, 0), {"lemmaDBO": self.lemma_dbo, "hochdeutsch": self.standard_german,
                              "dbpedia": self.dbpedia, "lokationId": "", "lokationName": "", "belege": "", "lokationTyp": "noLocation"})
            features.append(feature)

        # Create a FeatureCollection from the features list
        feature_collection = FeatureCollection(features)
        lemma_data = dumps(feature_collection)

        return lemma_data
