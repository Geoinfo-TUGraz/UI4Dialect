from flask import Flask, render_template, jsonify, request
from werkzeug.exceptions import InternalServerError
import locale
import glob
import json
import flask
import os

from python_files.init_functions import init_get_places, init_get_municipalies, init_get_regions, init_get_lemmata
from python_files.nl2sparql import *
from python_files.location import Location
from python_files.lemma import Lemma
from python_files.visualquery import Visualquery
from python_files.similaritysearch import SimilaritySearch
from python_files.statistics import Statistics
from python_files.recorddetails import Recorddetails
from python_files.runquery import RunQuery


app = Flask(__name__)

# Load language files
app_path = os.path.dirname(__file__)
app_language = 'de'
languages = {}
locale.setlocale(locale.LC_ALL, app_language)
language_list = glob.glob1(app_path + r"\static\language", "*.js")
# Loop through language files
for lang in language_list:
    lang_code = lang.split('.')[0]

    # Load language data
    with open(app_path + r"\static\language\\" + lang, 'r', encoding='utf8') as file:
        js_data = file.read()
        js_data = js_data.replace("lang = ", "")
        languages[lang_code] = json.loads(js_data)


@app.route("/")
def start():
    """Redirects user to startpage

    Returns:
        Response: Startpage
    """
    return flask.redirect("/de")


@app.route("/<language>")
def home(language):
    """Loads the startpage

    Args:
        language (str): Language of the page (en, de)

    Returns:
        []: index.html
    """
    if language not in languages:  # If language not in list, take the default language de
        language = app_language
    return render_template('index.html', **languages[language])


@app.route("/<language>/simple")
def simple(language):
    """Loads the Simple UI

    Args:
        language (str): Language of the page (en, de)

    Returns:
        []: simple.html
    """
    if language not in languages:
        language = app_language
    return render_template('simple.html', **languages[language])


@app.route("/<language>/advanced")
def advanced(language):
    """Loads the Advanced UI

    Args:
        language (str): Language of the page (en, de)

    Returns:
        []: advanced.html
    """
    if language not in languages:
        language = app_language
    return render_template('advanced.html', **languages[language])


@app.route("/init_loadLocations")
def init_loadLocations():
    """Loads all places, municipalities, regions for autocomplete search

    Returns:
        str: JSON including places, municipalities and regions
    """
    location_list = []

    # --Places--
    places = init_get_places()
    # Save Place ID and Place name + municipality name in list
    for place in places["results"]["bindings"]:
        location_list.append({"label": str(place["ortName"]["value"]) + " (Gem. " + str(
            place["gemeindeName"]["value"]) + ")", "value": str(place["ortId"]["value"])})

    # --Municipalities--
    municipalities = init_get_municipalies()
    # Save Municipality ID and Municipality name in list
    for municipality in municipalities["results"]["bindings"]:
        location_list.append({"label": str(municipality["gemeindeName"]["value"]), "value": str(
            municipality["gemeindeId"]["value"])})

    # --Regions--
    regions = init_get_regions()
    # Save Region ID and Regionname in list
    for region in regions["results"]["bindings"]:
        location_list.append({"label": str(
            region["regionName"]["value"]), "value": str(region["regionId"]["value"])})

    return jsonify(location_list)


@app.route("/init_loadLemmata")
def init_loadLemmata():
    """Loads all lemmata for autocomplete search

    Returns:
        str: JSON including lemmata
    """
    lemma_list = []

    # --Lemmata--
    lemmata = init_get_lemmata()
    for lemma in lemmata["results"]["bindings"]:
        lemma_list.append({"label": str(
            lemma["lemmaDBO"]["value"]), "value": str(lemma["lemmaId"]["value"])})

    return jsonify(lemma_list)


@app.route("/searchLocation", methods=['POST'])
def searchLocation():
    """Location

    Returns:
        str: GeoJSON data
    """
    response = request.get_json()
    location_id = response['locationId']
    location_level = response['locationLevel']

    #Query data
    location = Location(location_id, location_level)
    location.get_data_from_db()
    location_data = location.create_geojson()

    return location_data


@app.route("/searchLemma", methods=['POST'])
def searchLemma():
    """Lemma

    Returns:
        str: GeoJSON data
    """
    response = request.get_json()
    lemma_id = response['lemmaId']

    lemma = Lemma(lemma_id)
    lemma.get_data_from_db()
    lemma_data = lemma.create_geojson()

    return lemma_data


@app.route("/searchRecorddetails", methods=['POST'])
def searchRecorddetails():
    """Recorddetails

    Returns:
        str: JSON data
    """
    response = request.get_json()
    record_id = response['recordId']

    recorddetails = Recorddetails(record_id)
    recorddetail_data = recorddetails.get_data_from_db()

    return recorddetail_data


@app.route("/searchVisualquery", methods=['POST'])
def searchVisualquery():
    """Visualquery

    Returns:
        str: JSON data
    """
    response = request.get_json()
    query_polygon = response['queryPolygon']

    visualquery = Visualquery(query_polygon)
    visualqueryData = visualquery.get_data_from_db()

    return visualqueryData


@app.route("/searchSimilarity", methods=['POST'])
def searchLevenshtein():
    """Search similar dialect words

    Returns:
        str: GeoJSON data
    """
    response = request.get_json()
    input_value = response['inputValue']
    levenshtein_value = int(response['levenshteinValue'])
    levenshtein_select = response['levenshteinSelect']

    similarity_search = SimilaritySearch(input_value, levenshtein_value, levenshtein_select)
    similarity_search.get_data_from_db()
    similarity_data = similarity_search.search_records()

    return similarity_data


@app.route("/searchStatistics", methods=['POST'])
def searchStatistics():
    """Statistics

    Returns:
        str: GeoJSON data
    """
    response = request.get_json()
    level = response['locationLevel']

    statistics = Statistics(level)
    statistics_data = statistics.get_data_from_db()

    return statistics_data


@app.route("/nl2sparql", methods=['POST'])
def nl2sparql():
    """NL2SPARQL

    Returns:
        str: GeoJSON data
    """
    response = request.get_json()
    nl_question = response['nl_question']
    try:
        nl2sp = NL2SPARQL()

        nl2sp.create_query_from_question(nl_question)
        querystring = nl2sp.get_query()
        querystring = querystring.strip()

        runquery = RunQuery(querystring)
        queryResult = runquery.get_data_from_db() 
        return queryResult
    except IndexError as e:
        return jsonify(description=e.args[0]), 500
    except InternalServerError as e:
        return jsonify(description=e.description), 500
    except Exception as e:
        return jsonify(description=str(e)), 500


if __name__ == '__main__':
    app.run()
