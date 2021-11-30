/** Click on nl2sparql button */
$(document).on('click', '#btn-nl2sparql', function (e) {

	//Check if there is text in the input box
	if (!$("#input-nl2sparql").val()) {
		//No text in input
		$("#input-nl2sparql").css("background-color", "rgb(255, 143, 143)");
	}
	else {
		//Show loading graphic
		$("#spinner-nl2sparql").show();

		//Get values from control element
		var nl_question = document.getElementById("input-nl2sparql").value; //NL Question

		//Set all control elements to readonly
		disableAllControlElementsOnSite();

		//Translate Question 2 Sparql
		ajaxRequestForNL2SPARQL(nl_question);
	}
});

/** Creates ajax request for translating and executing the nl question and create a layer from it */
function ajaxRequestForNL2SPARQL(nl_question) {
	$.ajax({
		url: '/nl2sparql',
		type: 'POST',
		contentType: "application/json",
		data: JSON.stringify({ "nl_question": nl_question })
	}).done(function (sparqlGeoJSON_str) {

		var colorValueOfLayer = "#0083ae"; //set color value of layer

		//Parse GeoJSON to json obejct
		var sparqlGeoJSON = JSON.parse(sparqlGeoJSON_str);

		if (Object.keys(sparqlGeoJSON.features).length > 0) {

			//Create Leaflet Layer from GeoJSON
			var sparqlLayer = L.geoJSON(sparqlGeoJSON, {
				onEachFeature: function (feature, layer) {
					//Create Popup
					var locationName = feature.properties.locationName;
					//Bind Popup
					layer.bindPopup(locationName);
				}, style: function () {
					return {
						color: colorValueOfLayer
					}
				},
				pointToLayer: function (feature, latlng) {
					//Create Points as CircleMarker
					//Dont show point if its an artificial point (0,0)
					if (!isPoint00(feature.geometry.coordinates)) {
						return L.circleMarker(latlng, { fillColor: colorValueOfLayer, color: colorValueOfLayer, stroke: true, fill: true });
					}
					else {
						return L.circleMarker(latlng, { stroke: false, fill: false });
					}

				}
			}).addTo(mymap);

			//Set Layer ID generated by leaflet
			sparqlLayer.id = sparqlLayer._leaflet_id;

			flyToLayer(sparqlLayer.id)
			htmlData = createHTMLCodeForSearchresultSPARQL(sparqlGeoJSON, colorValueOfLayer);
			addDataToSearchresult(sparqlLayer.id, lang.query, htmlData);
			setColorOfTab(colorValueOfLayer, sparqlLayer.id);
			highlightLeafletLayer(sparqlLayer.id);

			//Add additional classes
			$('#searchresult').addClass('searchresult-nl2sparql');
			$('#searchresult-tabs').addClass('highlightable-tabs');
		}
		else {
			alert(lang.loadInfoData);
		}
	}).fail(function (jqXHR, textStatus, errorThrown) {
		if (jqXHR.hasOwnProperty('responseJSON')) {
			$("#errorbox").html(lang.loadErrorNL2SPARQL + errorThrown + " (" + jqXHR.responseJSON.description + ")");
		}
		else {
			$("#errorbox").html(lang.loadErrorNL2SPARQL + errorThrown);
		}

		$("#errorbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}).always(function (jqXHR, textStatus) {
		$("#spinner-nl2sparql").hide();
		enableAllControlElementsOnSite();
	});
}


function createHTMLCodeForSearchresultSPARQL(sparqlGeoJSON, colorValue) {

	var htmlData = "";
	//Table
	htmlData += "<br><h6>" + lang.result + "</h6>"
	htmlData += "<table><tr>"

	//Table Header
	for (const header of Object.values(sparqlGeoJSON.features[0].properties.headings)) {
		htmlData += "<th>" + header + "</th>";
	}
	//Add locationname if it is available and if its not included in the headings
	if ((sparqlGeoJSON.features[0].properties.locationName) && (!sparqlGeoJSON.features[0].properties.headings.includes("locationName"))) {
		htmlData += "<th>" + "Locationname" + "</th>";
	}
	htmlData += "</tr>"

	//Table Data
	for (const feature of Object.values(sparqlGeoJSON.features)) {
		for (const [key, value] of Object.entries(feature.properties.data)) {
			htmlData += "<tr>"
			htmlData += "<td>" + key + "</td>";
			htmlData += "<td>" + value + "</td>";

			//Add locationname if it is available and if its not included in the headings
			if (feature.properties.locationName && !feature.properties.headings.includes("locationName")) {
				htmlData += "<td>" + feature.properties.locationName + "</td>";
			}
			htmlData += "</tr>"
		}
	}
	htmlData += "</tr>"
	htmlData += "</table>"
	htmlData += "<hr>"

	//Footes buttons
	htmlData += "<label class='label-style' style='vertical-align: middle'>" + lang.layercolor + "<input type='color' class='color-picker' value='" + colorValue + "'></label></br></br>"
	htmlData += "<button class='btn-add-layer-to-layercontrol btn-success btn-footer' data-is-disabled='false' title='" + lang.saveLayer + "'><i class='bi bi-bookmark-plus'></br>" + lang.saveLayer + "</i></button>"
	htmlData += "<button class='btn-change-tabname btn-success btn-footer' title='" + lang.renameLayer + "'><i class='bi bi-pencil'></br>" + lang.renameLayer + "</i></button>";
	htmlData += "<button class='btn-download-geojson btn-success btn-footer' data-is-disabled='false' title='" + lang.downloadGeojson + "'><i class='bi bi-download'></br>" + lang.downloadGeojson + "</i></button>";

	return htmlData;
};

/** Restores the searchresult data when layer is re-enabled in layerControl */
function restoreSearchresultSparql(layer) {

	//Get GeoJSON from leaflet layer
	var sparqlGeoJSON = layer.toGeoJSON();
	//Get Color value of the layer
	var colorValueOfLayer = getColorFromLayer(layer.id);

	tabText = getLayernameFromLayerControl(layer._leaflet_id);
	htmlData = createHTMLCodeForSearchresultSPARQL(sparqlGeoJSON, colorValueOfLayer)
	addDataToSearchresult(layer.id, tabText, htmlData);
	setColorOfTab(colorValueOfLayer, layer.id);
	highlightLeafletLayer(layer.id);
	flyToLayer(layer.id);
	disableAddLayerButton(layer.id);

	//Add additional classes
	$('#searchresult').addClass('searchresult-nl2sparql');
	$('#searchresult-tabs').addClass('highlightable-tabs');
}

/** Click on nl2sparql info button */
$(document).on('click', '#btn-info', function (e) {
	var popup = document.getElementById("myPopup");
	popup.classList.toggle("show");
});

/** Sets background of input to white when there is an actual input */
$(document).on('input', '#input-nl2sparql', function (e) {
	$("#input-nl2sparql").css("background-color", "white");
});