from python_files.init_functions import query_endpoint
from shapely.geometry import Point
from shapely_geojson import dumps, Feature, FeatureCollection
import shapely.wkt


class RunQuery:
    """
    A class for executing the SPARQL query from nl2sparql.

    Args:
        querystring(str): The querystring from NL2SPARQL

    Attributes:
        querystring(str): The querystring from NL2SPARQL
        processed_question(list): Question after processing
    """

    def __init__(self, querystring):
        self.querystring = querystring

    def get_data_from_db(self):
        """Query the database and process the results

        Returns:
            str: GeoJSON dictionary
        """
        results = query_endpoint(self.querystring)

        data = {}
        features = []

        if results["results"]["bindings"]:
            # Case 1: If there is no geometry in the query result
            if "geom" not in results["head"]['vars']:
                for result in results["results"]["bindings"]:
                    # Store the data in a dictionary
                    for index, (key, value) in enumerate(result.items()):
                        if index == 0:
                            id = value["value"]
                        else:
                            data[id] = value["value"]

                # Create GeoJSON
                # Geometry is empty-->Feature cannot be created with empty geom-->set geometry to Point(0,0)
                features = []
                feature = Feature(Point(0, 0), properties={"headings": results["head"]['vars'][:2], "data": data})
                features.append(feature)
                feature_collection = FeatureCollection(features)
                geojson_no_geom = dumps(feature_collection)

                return geojson_no_geom

            else:  # Case 2: There is a geometry in the query result
                # Store all geometries in a list
                """ geometry_list=[]
                for result in results["results"]["bindings"]:
                    #Check if geometry was queried, but has no value
                    if "geom" in result:
                        geometry_list.append(result["geom"]["value"])
                    else:
                        geometry_list.append('POINT (0 0)') 
                        len(set(geometry_list)) == 1) and ("""

                # Case 2-1: Only one geometry = CCI query = no locationId in SPARQL query
                if "locationId" not in results["head"]["vars"][0]:
                    data = {}
                    locationname = results["results"]["bindings"][0]["locationName"]["value"]
                    # Check if there is a geometry value, if not -> set geometry to Point(0,0)
                    if "geom" in results["results"]["bindings"][0]:
                        geom = shapely.wkt.loads(
                            results["results"]["bindings"][0]["geom"]["value"])
                    else:
                        geom = Point(0, 0)

                    # Store data in dictionary
                    for result in results["results"]["bindings"]:
                        for index, (key, value) in enumerate(result.items()):
                            if index == 0:
                                id = value["value"]
                            elif index == 1:
                                data[id] = value["value"]

                    # Create GeoJSON
                    feature = Feature(geom, properties={"headings": results["head"]['vars'][:2], "data": data, "locationName": locationname})
                    features.append(feature)
                    feature_collection = FeatureCollection(features)
                    geojson_one_geom = dumps(feature_collection)

                    return geojson_one_geom
                else:
                    # Case 2-2: Multiple Geometries = RCI & CgeoRCI query
                    for result in results["results"]["bindings"]:
                        locationid = result["locationId"]["value"]
                        locationname = result["locationName"]["value"]
                        # Check if there is a geometry value, if not -> set geometry to Point(0,0)
                        if "geom" in result:
                            geom = shapely.wkt.loads(result["geom"]["value"])
                        else:
                            geom = Point(0, 0)

                        # Create GeoJSON features
                        feature1 = Feature(geom, {"headings": results["head"]['vars'][:2], "data": {locationid: locationname}, "locationName": locationname})
                        features.append(feature1)

                    feature_collection = FeatureCollection(features)
                    geojson_multi_geom = dumps(feature_collection)

                    return geojson_multi_geom
        else:
            # No results returned from the SPARQL query
            feature = []
            return dumps(FeatureCollection(feature))
