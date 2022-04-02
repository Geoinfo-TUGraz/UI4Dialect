from python_files.init_functions import query_endpoint


class Recorddetails:
    """
    A class for querying further information on a dialect word/record .

    Args:
        record_id(str): The id of the record for which data should be queried

    Attributes:
        record_id(str): The id of the record for which data should be queried
    """

    def __init__(self, record_id):
        self.record_id = record_id

    def get_data_from_db(self):
        """Queries the database to get additional information on a particular record

        Returns:
            dict: JSON with record data
        """
        querystring = '''
        PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?ortName ?gemeindeName ?regionName ?hochdeutsch ?hauptlemma ?nebenlemma ?dbpedia ?beschreibung ?titel ?autor ?erscheinungsjahr WHERE {
            SERVICE <http://localhost:2020/sparql>{
        <''' + self.record_id + '''> dboe:hatBelegzettel ?belegzettel.
        
        OPTIONAL {?belegzettel dboe:hatLokationGemeinde ?gemeindeid.
        ?gemeindeid dboe:hatNameLang ?gemeindeName}.
            
        OPTIONAL {?belegzettel dboe:hatLokationOrt ?ortid.
        ?ortid dboe:hatNameLang ?ortName}.

        OPTIONAL {?belegzettel dboe:hatLokationRegion ?regionid.
        ?regionid dboe:hatNameLang ?regionName}.

        OPTIONAL{<''' + self.record_id + '''> dboe:hatHauptlemma ?hauptlemmaid.
        ?hauptlemmaid dboe:hatHochdeutschlemma ?hochdeutsch.}

        OPTIONAL{?hauptlemmaid dboe:hatDBOlemma ?hauptlemma}.

        OPTIONAL{?hauptlemmaid owl:sameAs ?dbpedia.}

        OPTIONAL{<''' + self.record_id + '''> dboe:hatNebenlemma ?nebenlemmaid.
        ?nebenlemmaid dboe:hatDBOlemma ?nebenlemma.}

        OPTIONAL{<''' + self.record_id + '''> dboe:hatBedeutung ?bedeutungid.
        ?bedeutungid dboe:hatBeschreibung ?beschreibung.}

        OPTIONAL{?belegzettel dboe:hatQuelle ?quelleid.
        ?quelleid dboe:hatTitel ?titel.
        ?quelleid dboe:hatAutor ?autor.
        ?quelleid dboe:hatErscheinungsjahr ?erscheinungsjahr.}
        }
        }
        '''

        results = query_endpoint(querystring)

        # Check if there is the respective data in the query results, if not-->insert empty string
        if "gemeindeName" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["gemeindeName"] = {"value": ""}

        if "ortName" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["ortName"] = {"value": ""}

        if "regionName" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["regionName"] = {"value": ""}

        if "hochdeutsch" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["hochdeutsch"] = {"value": ""}

        if "hauptlemma" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["hauptlemma"] = {"value": ""}

        if "nebenlemma" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["nebenlemma"] = {"value": ""}

        if "beschreibung" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["beschreibung"] = {"value": ""}

        if "titel" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["titel"] = {"value": ""}

        if "autor" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["autor"] = {"value": ""}

        if "erscheinungsjahr" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["erscheinungsjahr"] = {"value": ""}

        if "dbpedia" not in results["results"]["bindings"][0]:
            results["results"]["bindings"][0]["dbpedia"] = {"value": ""}
            results["results"]["bindings"][0]["dbpediaImage"] = {"value": ""}
        else:
            # Query DBPedia image
            dbpedia = results["results"]["bindings"][0]["dbpedia"]["value"]
            querystring = '''       
            SELECT ?dbpediaImage WHERE{
            SERVICE <http://de.dbpedia.org/sparql>{
            OPTIONAL{<''' + dbpedia + '''> <http://dbpedia.org/ontology/thumbnail> ?dbpediaImage.}
            }
            }
            '''
            # Try to query dbpedia
            try:
                resultsDBpedia = query_endpoint(querystring)

                # If there is a dbpedia page, but no image
                if resultsDBpedia["results"]["bindings"] == [{}]:
                    results["results"]["bindings"][0]["dbpediaImage"] = ""
                else:
                    results["results"]["bindings"][0]["dbpediaImage"] = resultsDBpedia["results"]["bindings"][0]["dbpediaImage"]
            except:
                print("Error: DBPedia cannot be queried.")
                results["results"]["bindings"][0]["dbpediaImage"] = ""

        return results["results"]["bindings"][0]
