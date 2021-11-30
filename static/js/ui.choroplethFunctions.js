//FUNCTIONS FOR CHOROPLETH MAPS (Levenshtein & Statistics)
//Source: https://leafletjs.com/examples/choropleth/

/** Info Div */
function onAddInfo(map) {
	this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
	this.update();
	return this._div;
};
function updateInfo(properties) {
	if (currentlyActiveOption == 'levenshtein') {
		this._div.innerHTML = (properties ?
			'<b>' + properties.lokationName + '</b><br />' + Object.keys(properties.belege).length.toString() + " " + lang.voucher_s
			: lang.hoverPolygon);
	}
	else if (currentlyActiveOption == 'statistics') {
		this._div.innerHTML = (properties ?
			'<b>' + properties.lokationName + '</b><br />' + lang.amountVouchers + " " + properties.anzahlBelege + ''
			: lang.hoverPolygon);
	}

};

/** Add legend */
function onAddLegend(map) {

	if (currentlyActiveOption == 'levenshtein') {
		var div = L.DomUtil.create('div', 'info legend'),
			grades = [1, 2, 3, 4, 5, 6, 7],
			labels = [];

		div.innerHTML += '<h6>' + lang.vouchers + '</h6>'
		// loop through our density intervals and generate a label with a colored square for each interval
		for (var i = 0; i < grades.length; i = i + 2) {
			div.innerHTML +=
				'<i style="background:' + getColor(grades[i]) + '"></i> ' +
				grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');


		}
	}
	else {
		var div = L.DomUtil.create('div', 'info legend'),
			//grades = [1, 2, 3, 4, 5, 10, 20],
			grades = [1, 4, 5, 10, 11, 20, 21],
			labels = [];

		div.innerHTML += '<h6>' + lang.vouchers + '</h6>'
		// loop through our density intervals and generate a label with a colored square for each interval
		for (var i = 0; i < grades.length; i = i + 2) {
			div.innerHTML +=
				'<i style="background:' + getColor(grades[i]) + '"></i> ' +
				grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
		}
	}


	return div;
};


function getColor(d) {
	if (currentlyActiveOption == 'levenshtein') {
		return d > 6 ? '#800026' :
			d > 4 ? '#E31A1C' :
				d > 2 ? '#FD8D3C' :
					'#FED976';
	}
	else {
		return d > 20 ? '#800026' :
			d > 10 ? '#E31A1C' :
				d > 4 ? '#FD8D3C' :
					'#FED976';
	}
}

/** Styles the polygons */
function style(feature) {
	if (currentlyActiveOption == 'levenshtein') {
		return {
			fillColor: getColor(Object.keys(feature.properties.belege).length),
			weight: 2,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7
		};
	}
	else {
		return {
			fillColor: getColor(feature.properties.anzahlBelege),
			weight: 2,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7
		};
	}
}

function highlightFeature(e) {
	var layer = e.target;

	layer.setStyle({
		weight: 5,
		color: '#666',
		dashArray: '',
		fillOpacity: 0.7
	});

	if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
		layer.bringToFront();
	}
	info.update(layer.feature.properties);
}

function resetHighlight(e) {
	if (currentlyActiveOption == 'levenshtein') { levenshteinLayer.resetStyle(e.target); }
	else { statisticsLayer.resetStyle(e.target); }

	info.update();
}

/** For each feature, create a popup */
function onEachFeature(feature, layer) {
	if (currentlyActiveOption == 'levenshtein') {
		var locationName = feature.properties.lokationName;
		
		var popString = "<div><p class='popup-title'>" + locationName + "</p><p class='popup-text'>" + lang.voucher_s + "</p><ul class='popup-list-items'>";
		for (const [voucherId, voucherdescription] of Object.entries(feature.properties.belege)) {
			popString += "<li><a href='#' data-voucher-id='" + voucherId + "'>" + voucherdescription + "</a></li>"
		}
		popString += "</ul></div>"

		// specify popup options 
		var popupOptions =
		{
			'className': 'custom-popup-style'
		}

		layer.bindPopup($(popString).click(function (e) {
			popupClickLevenshtein(e);
		})[0], popupOptions);
	}
	else {
		var locationName = feature.properties.lokationName;
		var popString = "<div><p class='popup-title'>" + locationName + "</p>";
		popString += "<p class='popup-text'>" + lang.vouchers + ": " + feature.properties.anzahlBelege + "</p></div>";

		// specify popup options 
		var popupOptions =
		{
			'className': 'custom-popup-style'
		}
		layer.bindPopup(popString, popupOptions);
	}

	//Mousover and mouseout events
	layer.on({
		mouseover: highlightFeature,
		mouseout: resetHighlight,
	});

}

/** Styles the points */
function stylePoint(feature, latlng) {
	if (currentlyActiveOption == 'levenshtein') {

		var geojsonMarkerOptions = {
			fillColor: getColor(Object.keys(feature.properties.belege).length),
			color: "white",
			weight: 2,
			fillOpacity: 0.7,
			opacity: 1,
			dashArray: '3',
		};
	}
	else {
		var geojsonMarkerOptions = {
			fillColor: getColor(feature.properties.anzahlBelege),
			color: "white",
			weight: 2,
			fillOpacity: 0.7,
			opacity: 1,
			dashArray: '3',
		};
	}
	return L.circleMarker(latlng, geojsonMarkerOptions);
}
