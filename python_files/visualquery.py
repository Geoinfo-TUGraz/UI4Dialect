from python_files.init_functions import query_endpoint
from flask import jsonify


class Visualquery:
    """
    A class for querying voucher data for the visual query.

    Args:
        query_polygon(str): The geometry of the query polygon as WKT

    Attributes:
        query_polygon(str): The geometry of the query polygon as WKT
    """

    def __init__(self, query_polygon):
        self.query_polygon = query_polygon

    def get_data_from_db(self):
        """Queries the database to get vouchers associated to the locations (places, municipalities) which intersect with the query polygon

        Returns:
            str: JSON with voucher data
        """
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        
        Select ?locationId ?locationType ?locationName ?belegId ?bezeichnung WHERE {
            SERVICE <http://localhost:2020/sparql>{
            {?belegId dboe:hatBelegbezeichnung ?bezeichnung.
            ?belegId dboe:hatBelegzettel ?belegzettelid.
            ?belegzettelid dboe:hatLokationOrt ?locationId.
            ?belegzettelid rdf:type dboe:belegzettel.
            ?locationId dboe:hatNameLang ?locationName.    
            ?locationId geo:hasGeometry ?geodaten.
            ?locationId rdf:type ?locationType.
            }
            UNION
            {?belegId dboe:hatBelegbezeichnung ?bezeichnung.
            ?belegId dboe:hatBelegzettel ?belegzettelid.
            ?belegzettelid dboe:hatLokationGemeinde ?locationId.
            ?belegzettelid rdf:type dboe:belegzettel.
            ?locationId dboe:hatNameLang ?locationName.    
            ?locationId geo:hasGeometry ?geodaten.
            ?locationId rdf:type ?locationType.}
            }
            SERVICE <http://localhost:8080/strabon-endpoint-3.3.1/Query>{
            ?geodaten geo:asWKT ?locationGeom.

            FILTER(geof:sfIntersects(?locationGeom, "''' + self.query_polygon + '''"^^geo:wktLiteral ))
            }
        }
        order by ?bezeichnung
        '''

        results = query_endpoint(querystring)

        # Store data in dictionary
        dict_voucher = {}
        for result in results["results"]["bindings"]:
            dict_voucher[result["belegId"]["value"]] = result["bezeichnung"]["value"]

        return jsonify(dict_voucher)
