from SPARQLWrapper import SPARQLWrapper, JSON


def query_endpoint(querystring):
    """Queries the SPARQL endpoint

    Args:
        querystring (str): The querystring for the query

    Returns:
        dict: Results of the query
    """
    sparql = SPARQLWrapper("http://localhost:2020/sparql")

    sparql.setQuery(querystring)
    sparql.setReturnFormat(JSON)  # Format of the query result
    results = sparql.query().convert()
    return results


def init_get_places():
    """Loads all places from the database

    Returns:
        dict: Results of the query
    """
    querystring = '''
    PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?ortId ?ortName ?gemeindeName WHERE {
    ?ortId rdf:type dboe:ort.
    ?ortId dboe:hatNameLang ?ortName.
    ?ortId dboe:istOrtIn ?gemeindeId.
    ?gemeindeId dboe:hatNameLang ?gemeindeName.
    } 
    '''
    results = query_endpoint(querystring)

    return results


def init_get_municipalies():
    """Loads all municipalities from the database

    Returns:
        dict: Results of the query
    """
    querystring = '''
    PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?gemeindeId ?gemeindeName WHERE {
    ?gemeindeId rdf:type dboe:gemeinde.
    ?gemeindeId dboe:hatNameLang ?gemeindeName.
    }'''

    results = query_endpoint(querystring)

    return results


def init_get_regions():
    """Loads all regions from the database

    Returns:
        dict: Results of the query
    """
    querystring = '''
    PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?regionId ?regionName WHERE {
    ?regionId rdf:type dboe:region.
    ?regionId dboe:hatNameLang ?regionName.
    }'''

    results = query_endpoint(querystring)

    return results


def init_get_lemmata():
    """Loads all lemmata from the database

    Returns:
        dict: Results of the query
    """
    querystring = '''
    PREFIX dboe: <http://40.91.234.77/ontology/dboe#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?lemmaId ?lemmaDBO WHERE {
    ?lemmaId rdf:type dboe:lemma.
    ?lemmaId dboe:hatDBOlemma ?lemmaDBO.
    }'''

    results = query_endpoint(querystring)

    return results
