
/** Gets called, when user selects a location in autocomplete */
function selectLocationInAutocomplete() {
	//Show loading graphic
	$("#spinner-location").show();

	//Get values from control elements
	var locationLevel = document.getElementById("select-location").value;
	var locationId = $("#autocomplete-location").attr('data-location-id');
	var locationName = document.getElementById("autocomplete-location").value;

	//Set all control elements to readonly
	disableAllControlElementsOnSite();

	//Load data for selected location
	ajaxRequestForLocation(locationId, locationName, locationLevel);

};

/** Creates ajax request for loading location data from database and create a layer from it */
function ajaxRequestForLocation(locationId, locationName, locationLevel) {
	$.ajax({
		url: '/searchLocation',
		type: 'POST',
		contentType: "application/json",
		data: JSON.stringify({ locationId: locationId, locationLevel: locationLevel })
	}).done(function (locationGeoJSON_str) {

		var colorValueOfLayer = "#0083ae"; //set color value of layer

		var locationGeoJSON = JSON.parse(locationGeoJSON_str);
		locationGeoJSON.features[0].properties.lokationName = locationName;

		//Get values from GeoJSON file
		var vouchers = locationGeoJSON.features[0].properties.belege;
		var locations = locationGeoJSON.features[0].properties.lokationen;
		var people = locationGeoJSON.features[0].properties.personen;
		var geom = locationGeoJSON.features[0].geometry;

		//Create Leaflet Layer from GeoJSON
		var locationLayer = L.geoJSON(locationGeoJSON, {
			style: function () {
				return {
					color: colorValueOfLayer
				}
			},
			pointToLayer: function (feature, latlng) {
				if (!isPoint00(feature.geometry.coordinates)) {
					return L.circleMarker(latlng, { fillColor: colorValueOfLayer, color: colorValueOfLayer, stroke: true, fill: true });
				}
				else {
					return L.circleMarker(latlng, { stroke: false, fill: false });
				}
			}
		}).addTo(mymap);

		//Bind Popup
		locationLayer.bindPopup(locationName.toString());
		//Set Layer ID generated by leaflet
		locationLayer.id = locationLayer._leaflet_id;

		//Fly to layer
		flyToLayer(locationLayer.id)
		//Check if location has a geometry
		if (isPoint00(geom.coordinates)) { alert(lang.loadInfoGeometry); }

		//Create HTML code for the searchresult div
		htmlData = createHTMLCodeForSearchresultLocation(vouchers, locations, people, colorValueOfLayer);
		//Add the data to the searchresult div
		addDataToSearchresult(locationLayer.id, locationName, htmlData);
		//Set the color of the tab
		setColorOfTab(colorValueOfLayer, locationLayer.id);

		//Hightlight the leaflet layer as it is the active layer
		highlightLeafletLayer(locationLayer.id);

		//Add additional classes
		$('#searchresult').addClass('searchresult-location-lemma');
		$('#searchresult-tabs').addClass('highlightable-tabs');

	}).fail(function (jqXHR, textStatus, errorThrown) {
		$("#errorbox").html(lang.loadErrorLocation + errorThrown);
		$("#errorbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}).always(function (jqXHR, textStatus) {
		//Hide loading graphic
		$("#spinner-location").hide();

		//Enable all control elements
		enableAllControlElementsOnSite();
	});
}

/** Creates HTML code for the location searchresult */
function createHTMLCodeForSearchresultLocation(vouchers, locations, people, colorValue) {

	var htmlData = "";
	htmlData += "<h5 style='margin-top: 10px;'>" + lang.vouchers + "</h5>";

	//Create Button Group with Vouchers
	htmlData += "<div class='btn-group-vertical'>";
	if (Object.keys(vouchers).length > 0) {
		for (const [voucherId, voucherdescription] of Object.entries(vouchers)) {
			htmlData += "<button type='button' class='btn button-voucher' data-source='location' data-voucher-id='" + voucherId + "'>" + voucherdescription + " </button>";
		}
	}
	else {
		htmlData += "<p>" + lang.noData + "</p>";
	}
	htmlData += "</div><hr>";


	//Create unordered lists for citys, municipalities, regions
	htmlData += "<div class='location-unordered-lists'><p></p>";
	//Regions
	if (Object.keys(locations.regionen).length > 0) {
		htmlData += "<h5>" + lang.region + "</h5>";
		htmlData += "<ul>";

		for (const [regionId, regionName] of Object.entries(locations.regionen)) {
			htmlData += "<li><a class=unordered-list-region data-region-id='" + regionId + "' href='#'>" + regionName + "</a></li>";
		}
		htmlData += "</ul>";
	}
	//Municipalities
	if (Object.keys(locations.gemeinden).length > 0) {
		if (Object.keys(locations.orte).length > 0) {
			htmlData += "<h5>" + lang.municipalities + "</h5>";
		}
		else {
			htmlData += "<h5>" + lang.municipality + "</h5>";
		}

		htmlData += "<ul>";

		for (const [municipalityId, municipalityName] of Object.entries(locations.gemeinden)) {
			htmlData += "<li ><a class=unordered-list-municipality data-municipality-id='" + municipalityId + "' href='#'>" + municipalityName + "</a></li>";
		}
		htmlData += "</ul>";
	}
	//Citys
	if (Object.keys(locations.orte).length > 0) {
		htmlData += "<h5>" + lang.places + "</h5>";
		htmlData += "<ul>";

		for (const placeId of Object.keys(locations.orte)) {
			htmlData += "<li ><a class=unordered-list-place data-place-id='" + placeId + "' data-municipality=\"" + locations.orte[placeId][1] + "\" href='#'>" + locations.orte[placeId][0] + "</a></li>";
		}
		htmlData += "</ul>";
	}
	htmlData += "<br>";
	//People born
	htmlData += "<h5>" + lang.peopleBorn + "</h5>";
	if (people.geboren.length > 0) {
		htmlData += "<ul class='unordered-list-peope-born'>";
		for (i = 0; i < people.geboren.length; i++) {
			htmlData += "<li>" + people.geboren[i] + "</li>";
		}
		htmlData += "</ul>";
	}
	else {
		htmlData += "<p>" + lang.noData + "</p>";
	}


	//People died
	htmlData += "<h5>" + lang.peopleDied + "</h5>";
	if (people.gestorben.length > 0) {
		htmlData += "<ul class='unordered-list-peope-died'>";
		for (i = 0; i < people.gestorben.length; i++) {
			htmlData += "<li>" + people.gestorben[i] + "</li>";
		}
		htmlData += "</ul>";
	}
	else {
		htmlData += "<p>" + lang.noData + "</p>";
	}
	htmlData += "</div><hr>";

	//Coler picker
	htmlData += "<label class='label-style' style='vertical-align: middle'>" + lang.layercolor + "<input type='color' class='color-picker' value='" + colorValue + "'></label></br></br>";

	//Add footer buttons
	htmlData += "<button class='btn-add-layer-to-layercontrol btn-success btn-footer' data-is-disabled='false' title='" + lang.saveLayer + "'><i class='bi bi-bookmark-plus'></br>" + lang.saveLayer + "</i></button>";
	htmlData += "<button class='btn-change-tabname btn-success btn-footer' title='" + lang.renameLayer + "'><i class='bi bi-pencil'></br>" + lang.renameLayer + "</i></button>";
	htmlData += "<button class='btn-download-geojson btn-success btn-footer' data-is-disabled='false'  title='" + lang.downloadGeojson + "'><i class='bi bi-download'></br>" + lang.downloadGeojson + "</i></button>";

	return htmlData;
};


/** Restores the location data when layer is re-enabled in layerControl */
function restoreSearchresultLocation(layer) {

	//Get GeoJSON from leaflet layer
	var locationGeoJSON = layer.toGeoJSON();
	//Get Color value of the layer
	var colorValueOfLayer = getColorFromLayer(layer.id);

	//Get data from GeoJSON
	vouchers = locationGeoJSON.features[0].properties.belege;
	locations = locationGeoJSON.features[0].properties.lokationen;
	people = locationGeoJSON.features[0].properties.personen;
	locationName = locationGeoJSON.features[0].properties.lokationName;

	//Get tabtext and create html code
	tabText = getLayernameFromLayerControl(layer._leaflet_id);
	htmlData = createHTMLCodeForSearchresultLocation(vouchers, locations, people, colorValueOfLayer);

	//Add data to the searchresult div
	addDataToSearchresult(layer.id, tabText, htmlData);
	//Set tab color
	setColorOfTab(colorValueOfLayer, layer.id);
	//Hightlight the leaflet layer as it is the active layer
	highlightLeafletLayer(layer.id);

	//Fly to restored layer
	flyToLayer(layer.id);
	//Disable the save layer button in searchresult
	disableAddLayerButton(layer.id);

	//Add additional classes
	$('#searchresult').addClass('searchresult-location-lemma');
	$('#searchresult-tabs').addClass('highlightable-tabs');
}


/** Listens to clicks on corresponding citys, municipalities, regions in unordered list */
$(document).on('click', '.unordered-list-region', function (e) {
	//Get values from target
	var regionId = e.target.getAttribute('data-region-id');
	var regionName = e.target.innerText

	//Set values of autocomplete and select
	document.getElementById("autocomplete-location").value = regionName;
	document.getElementById("select-location").value = 3;

	//Trigger the change event of the select
	$("#select-location").trigger("change");
	//Set the data-location-id of autocomplete
	$("#autocomplete-location").attr('data-location-id', regionId);

	//Trigger the function
	selectLocationInAutocomplete();
});
$(document).on('click', '.unordered-list-municipality', function (e) {
	var municipalityId = e.target.getAttribute('data-municipality-id');
	var municipalityName = e.target.innerText

	document.getElementById("autocomplete-location").value = municipalityName;
	document.getElementById("select-location").value = 2;

	$("#select-location").trigger("change");
	$("#autocomplete-location").attr('data-location-id', municipalityId);

	selectLocationInAutocomplete();
});
$(document).on('click', '.unordered-list-place', function (e) {
	var placeId = e.target.getAttribute('data-place-id');
	var placeName = e.target.innerText;
	var municipalityName = e.target.getAttribute('data-municipality');

	document.getElementById("autocomplete-location").value = placeName + " (Gem. " + municipalityName + ")";
	document.getElementById("select-location").value = 1;

	$("#select-location").trigger("change");
	$("#autocomplete-location").attr('data-location-id', placeId);

	selectLocationInAutocomplete();
});