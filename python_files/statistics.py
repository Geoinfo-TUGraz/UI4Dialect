from python_files.init_functions import query_endpoint
from shapely_geojson import dumps, Feature, FeatureCollection
import shapely.wkt


class Statistics:
    """
    A class for querying statistics data from the database.

    Args:
        location_level(str): Level of the location ('1' == Place, '2' == Municipality, '3' == Region)

    Attributes:
        location_level(str): Level of the location ('1' == Place, '2' == Municipality, '3' == Region)
    """

    def __init__(self, location_level):
        self.location_level = location_level

    def get_data_from_db(self):
        """Queries the database to get the statistics data

        Returns:
            str: GeoJSON dictionary
        """
        # Set querystring depending on location_level
        if self.location_level == '1':
            querystring = '''
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>

            SELECT ?locationId ?locationName (count(?belegId) AS ?counter) ?geom WHERE {
                ?belegId dboe:hatBelegzettel ?belegzettelId.
                ?belegzettelId dboe:hatLokationOrt ?locationId.
                ?locationId dboe:hatNameLang ?locationName.
                ?locationId geo:hasGeometry ?geodaten.

                SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                    ?geodaten geo:asWKT ?geom.
                }
            }
            group by ?locationId ?locationName ?geom
            order by ?locationName
            '''
        elif self.location_level == '2':
            querystring = '''
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>

            SELECT ?locationId ?locationName (count(?belegId) AS ?counter) ?geom WHERE {
                ?belegId dboe:hatBelegzettel ?belegzettelId.
                ?belegzettelId dboe:hatLokationGemeinde ?locationId.
                ?locationId dboe:hatNameLang ?locationName.
                ?locationId geo:hasGeometry ?geodaten.

                SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                    ?geodaten geo:asWKT ?geom.
                }
            }
            group by ?locationId ?locationName ?geom
            order by ?locationName
            '''
        else:
            querystring = '''
            PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
            PREFIX geo: <http://www.opengis.net/ont/geosparql#>

            SELECT ?locationId ?locationName (count(?belegId) AS ?counter) ?geom WHERE {
                ?belegId dboe:hatBelegzettel ?belegzettelId.
                ?belegzettelId dboe:hatLokationRegion ?locationId.
                ?locationId dboe:hatNameLang ?locationName.
                ?locationId geo:hasGeometry ?geodaten.

                SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
                    ?geodaten geo:asWKT ?geom.
                }
            }
            group by ?locationId ?locationName ?geom
            order by ?locationName
            '''

        results = query_endpoint(querystring)

        # Create GeoJSON with the data
        features = []
        for result in results["results"]["bindings"]:
            location_id = result["locationId"]["value"]
            location_name = result["locationName"]["value"]
            counter = result["counter"]["value"]
            geom = shapely.wkt.loads(result["geom"]["value"])

            feature1 = Feature(geom, {"lokationId": location_id, "lokationName": location_name, "anzahlBelege": counter})
            features.append(feature1)

        feature_collection = FeatureCollection(features)
        statistics_data = dumps(feature_collection)
        return statistics_data
