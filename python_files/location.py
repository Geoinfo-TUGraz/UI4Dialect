from python_files.init_functions import query_endpoint
from shapely.geometry import Point
from shapely_geojson import dumps, Feature, FeatureCollection
import shapely.wkt


class Location:
    """
    A class for querying data associated to a location.

    Args:
        location_id(str): The ID of the location for which data should be queried
        location_level(str): Level of the location ('1' == Place, '2' == Municipality, '3' == Region)

    Attributes:
        location_id(str): The ID of the location for which data should be queried
        location_level(str): Level of the location ('1' == Place, '2' == Municipality, '3' == Region)
        records(dict): Dict for storing the associated dialect record data
        locations(dict): Dict for storing the associated locations
        people(dict): Dict for storing the associated people
        geom(Point, Polygon): Geometry of the location
    """

    def __init__(self, location_id, location_level):
        self.location_id = location_id
        self.location_level = location_level
        self.records = {}
        self.locations = {}
        self.people = {}
        self.geom = None

    def get_data_from_db(self):
        """Calls the methods for querying the database"""
        self.records = self.__get_records()
        self.locations = self.__get_locations()
        self.people = self.__get_people()
        self.geom = self.__get_geometry()

    def __get_records(self):
        """Queries the database to get dialect records associated with the location

        Returns:
            dict: Dictionary with dialect data
        """
        # Define predicate for query depending on location_level
        if self.location_level == '1':
            add_predicate = 'dboe:hatLokationOrt'
        elif self.location_level == '2':
            add_predicate = 'dboe:hatLokationGemeinde'
        else:
            add_predicate = 'dboe:hatLokationRegion'

        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>

        Select ?belegId ?belegbezeichnung WHERE {
            ?belegId dboe:hatBelegzettel ?belegzettel.
            ?belegId dboe:hatBelegbezeichnung ?belegbezeichnung.
            ?belegzettel ''' + add_predicate + ''' <''' + self.location_id + '''>.
        }
        ORDER BY ?belegbezeichnung'''

        results = query_endpoint(querystring)

        # Store the record data in a dictionary
        records = {}
        for result in results["results"]["bindings"]:
            records[result["belegId"]["value"]] = result["belegbezeichnung"]["value"]

        return records

    def __get_locations(self):
        """Queries the database to get locations associated with the location

        Returns:
            dict: Dictionary for storing the associated locations
        """
        # Choose query depending on location_level
        if self.location_level == '1':  # Places
            querystring = '''
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>

            SELECT ?ortId ?ortName ?gemeindeId ?gemeindeName ?regionId ?regionName WHERE {
                <''' + self.location_id + '''> dboe:istOrtIn ?gemeindeId.
                ?gemeindeId dboe:hatNameLang ?gemeindeName.
                ?gemeindeId dboe:istGemeindeIn ?regionId.
                ?regionId dboe:hatNameLang ?regionName.
            }
            ORDER BY ?ortName ?gemeindeName ?regionName
            '''
        elif self.location_level == '2':  # Municipalities
            querystring = '''
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>

            SELECT ?ortId ?ortName ?gemeindeId ?gemeindeName ?regionId ?regionName WHERE {
                ?ortId dboe:istOrtIn <''' + self.location_id + '''>.
                ?ortId dboe:hatNameLang ?ortName.
                <''' + self.location_id + '''> dboe:istGemeindeIn ?regionId.
                <''' + self.location_id + '''> dboe:hatNameLang ?gemeindeName.
                ?regionId dboe:hatNameLang ?regionName.
            }
            ORDER BY ?ortName ?gemeindeName ?regionName
            '''
        else:  # Regions
            querystring = '''
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>

            SELECT ?ortId ?ortName ?gemeindeId ?gemeindeName ?regionId ?regionName WHERE {
                ?ortId dboe:istOrtIn ?gemeindeId.
                ?ortId dboe:hatNameLang ?ortName.
                ?gemeindeId dboe:hatNameLang ?gemeindeName.
                ?gemeindeId dboe:istGemeindeIn <''' + self.location_id + '''>.
            }
            ORDER BY ?ortName ?gemeindeName ?regionName
            '''

        results = query_endpoint(querystring)

        # Store data in dictionaries
        dict_places = {}
        dict_municipalities = {}
        dict_regions = {}
        # Loop through results
        for result in results["results"]["bindings"]:
            if self.location_level == '1':  # Places
                dict_places = {}
                dict_municipalities[result["gemeindeId"]["value"]] = result["gemeindeName"]["value"]
                dict_regions[result["regionId"]["value"]] = result["regionName"]["value"]
            elif self.location_level == '2':  # Municipalities
                dict_places[result["ortId"]["value"]] = [result["ortName"]["value"], result["gemeindeName"]["value"]]
                dict_municipalities = {}
                dict_regions[result["regionId"]["value"]] = result["regionName"]["value"]
            else:  # Regions
                dict_places[result["ortId"]["value"]] = [result["ortName"]["value"], result["gemeindeName"]["value"]]
                dict_municipalities[result["gemeindeId"]["value"]] = result["gemeindeName"]["value"]
                dict_regions = {}

        return {"orte": dict_places, "gemeinden": dict_municipalities, "regionen": dict_regions}

    def __get_people(self):
        """Queries the database to get people associated with the location

        Returns:
            dict: Dictionary for storing the associated people
        """
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>

        SELECT ?vorname ?nachname ?gestorben ?geboren WHERE {
            {
                ?person dboe:hatTodesort <''' + self.location_id + '''>.
                ?person dboe:person_vorname ?vorname.
                ?person dboe:person_nachname ?nachname.
                BIND ("true" as ?gestorben).
            }
        UNION
            {
                ?person dboe:hatGeburtsort <''' + self.location_id + '''>.
                ?person dboe:person_vorname ?vorname.
                ?person dboe:person_nachname ?nachname.
                BIND ("true" as ?geboren).
            }
        }
        ORDER BY ?nachname'''

        results = query_endpoint(querystring)

        # Store data of people in lists
        people_born = []
        people_died = []
        for result in results["results"]["bindings"]:
            if "geboren" in result:
                people_born.append(
                    result["vorname"]["value"] + " " + result["nachname"]["value"])
            if "gestorben" in result:
                people_died.append(
                    result["vorname"]["value"] + " " + result["nachname"]["value"])

        return {"geboren": people_born, "gestorben": people_died}

    def __get_geometry(self):
        """Queries the database to get the geometry of the location

        Returns:
            Point, Polygon: Geometry of the location
        """
        # Define predicate for query depending on location_level
        if self.location_level == '1':
            add_predicate = 'dboe:ort'
        elif self.location_level == '2':
            add_predicate = 'dboe:gemeinde'
        else:
            add_predicate = 'dboe:region'

        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>

        Select ?geom WHERE {
            <''' + self.location_id + '''> rdf:type ''' + add_predicate + '''.
            <''' + self.location_id + '''> geo:hasGeometry ?geodaten.

            SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                ?geodaten geo:asWKT ?geom.
            }
        }'''

        results = query_endpoint(querystring)

        if results["results"]["bindings"] == []:
            # If empty geometry-->Point(0,0)
            geometry = Point(0, 0)
        else:
            # Convert geometry to a Shapely geometry object
            geometry = shapely.wkt.loads(results['results']['bindings'][0]['geom']['value'])

        return geometry

    def create_geojson(self):
        """Creates a GeoJSON dictionary from the queried data

        Returns:
            str: GeoJSON dictionary
        """
        features = []
        feature = Feature(self.geom, properties={"belege": self.records, "lokationen": self.locations, "personen": self.people})
        features.append(feature)
        feature_collection = FeatureCollection(features)
        location_data = dumps(feature_collection)

        return location_data
