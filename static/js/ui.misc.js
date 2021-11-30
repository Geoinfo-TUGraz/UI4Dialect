
/*
	Event handler / functions
*/

/** Checks if Enter is pressed in autocomplete input --> show alertbox */
$("#div-location, #div-lemmasearch").keydown(function (event) {
	if (event.keyCode == 13) {
		$("#alertbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}
});

/** Click on a tab in the searchbox */
$(document).on('click', '#searchbox-tabs .nav-link', function (e) {

	hideAllSearchboxContents();
	hideDivSearchresult();
	deleteAllLayersFromMap();
	removeChoroplethControls();
	removeAllTabsFromSearchresult();
	removeAllClassesFromSearchresult();

	$("#searchresult-voucherdetails").attr("data-is-active", "false");

	var searchboxTabClicked = e.target.id;

	//Remove the draw controls for visualquery
	if (searchboxTabClicked != "searchbox-visualquery-tab") {

		if (typeof drawControl !== 'undefined') {
			mymap.removeControl(drawControl);
			mymap.removeLayer(drawnItems);
		}

	}
	else {
		if (typeof drawControl !== 'undefined') {
			mymap.removeControl(drawControl);
			mymap.removeLayer(drawnItems);
		}
	}

	mymap.removeControl(layerControlLemma);
	mymap.removeControl(layerControlLocation);
	mymap.removeControl(layerControlVisualquery);
	mymap.removeControl(layerControlLevenshtein);
	mymap.removeControl(layerControlStatistics);
	mymap.removeControl(layerControlSparql);

	//Enable LayerControl for selected tab
	switch (searchboxTabClicked) {
		case "searchbox-location-tab":
			mymap.addControl(layerControlLocation);
			$('#searchbox-location-tab-content').show();
			break;
		case "searchbox-lemma-tab":
			mymap.addControl(layerControlLemma);
			$('#searchbox-lemma-tab-content').show();
			break;
		case "searchbox-visualquery-tab":
			mymap.addControl(layerControlVisualquery);
			initVisualquery();
			$('#searchbox-visualquery-tab-content').show();
			break;
		case "searchbox-levenshtein-tab":
			mymap.addControl(layerControlLevenshtein);
			$('#searchbox-levenshtein-tab-content').show();
			break;
		case "searchbox-statistics-tab":
			mymap.addControl(layerControlStatistics);
			$('#searchbox-statistics-tab-content').show();
			break;
		case "searchbox-sparql-tab":
			mymap.addControl(layerControlSparql);
			$('#searchbox-sparql-tab-content').show();
			break;
	}

	//Set collapse button to -
	$('#collapse-tabs').html('<i class="bi bi-dash-square"></i>');
});

/** Click on collapse button */
$(document).on('click', '#collapse-tabs', function (e) {
	var currentlyActiveNavTab = getCurrentlyActiveSearchboxTab();

	if ($($('#' + currentlyActiveNavTab).attr("data-bs-target")).is(":visible")) {
		//Collapse divs
		$($('#' + currentlyActiveNavTab).attr("data-bs-target")).hide();
		$('#collapse-tabs').html('<i class="bi bi-plus-square"></i>');
		hideDivSearchresult();
	}
	else {
		//Unfold divs
		$($('#' + currentlyActiveNavTab).attr("data-bs-target")).show();
		$('#collapse-tabs').html('<i class="bi bi-dash-square"></i>');
		unfoldDivSearchresult();
	}
});

/** Click on (x) on tab in searchresult */
$(document).on('click', '.span-close', function (e) {
	layerId = $(this).parent().attr("id");
	removeDataFromSearchresult(layerId);
	removeLayerFromMap(layerId);

	var currentlyActiveSearchboxTab = getCurrentlyActiveSearchboxTab();
	if ((currentlyActiveSearchboxTab != "searchbox-levenshtein-tab") && (currentlyActiveSearchboxTab != "searchbox-statistics-tab")) {
		//Get active layer and highlight it
		activeTab = $("#searchresult-tabs button[data-is-active-tab='true']")
		activeLayerId = activeTab.attr("id");
		highlightLeafletLayer(activeLayerId);
	}

	//Stop the propagation of the event --> close the tab only
	e.stopPropagation();
});

/** Click on tab in searchresult which is highlightable */
$(document).on('click', '.highlightable-tabs', function (e) {
	var layerId = e.target.id;

	highlightLeafletLayer(layerId);
	flyToLayer(layerId);
});

$(document).on('click', '#searchresult-tabs', function (e) {
	//Close active popup
	mymap.closePopup();

	//Set the attribute data-is-active-tab correctly
	var layerId = e.target.id;
	activeTab = $("#searchresult-tabs button[data-is-active-tab='true']")
	//Set previous active tab to false
	activeTab.attr("data-is-active-tab", 'false')
	//Set new tab active
	$('#' + layerId).attr("data-is-active-tab", 'true')

});

$(document).on("change", ".color-picker", function () {
	var colorValue = $(this).val();
	var layerId = $(this).parent().parent().attr("data-layer-id");

	changeColorOfLayer(colorValue, layerId);
	setColorOfTab(colorValue, layerId);
});

/** Changes the color of a leaflet layer */
function changeColorOfLayer(colorValue, layerId) {
	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == layerId) {
			datalayer.setStyle({
				color: colorValue,
				fillColor: colorValue,
			});
		}
	});
}

/** Sets color of a searchresult tab */
function setColorOfTab(colorValue, layerId) {
	fontColor = getContrastYIQ(colorValue); //Calculate color for font (contrast)
	$("[id=" + layerId + "]").css("background-color", colorValue)
	$("[id=" + layerId + "]").css("color", fontColor)
}
/** Calculates contrast color for text (black or white) */
function getContrastYIQ(hexcolor) {
	//Source: https://24ways.org/2010/calculating-color-contrast/

	var r = parseInt(hexcolor.substr(1, 2), 16);
	var g = parseInt(hexcolor.substr(3, 2), 16);
	var b = parseInt(hexcolor.substr(5, 2), 16);
	var yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
	return (yiq >= 128) ? '#000000' : '#ffffff';
}

/** Click on save layer button */
$(document).on('click', '.btn-add-layer-to-layercontrol', function (e) {
	//Get layer id and layername
	layerId = $(this).parent().attr("data-layer-id")
	layername = $('#' + layerId).html().replace(" <span class=\"span-close\" title=\"" + lang.closeTab + "\">×</span>", "");

	//Disable add layer button
	disableAddLayerButton(layerId);

	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == layerId) { //Get layer from map which should be saved

			currentlyActiveSearchboxTab = getCurrentlyActiveSearchboxTab();

			//Add layer to layercontrol
			switch (currentlyActiveSearchboxTab) {
				case "searchbox-location-tab":
					layerControlLocation.addOverlay(datalayer, " " + layername + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>");
					break;
				case "searchbox-lemma-tab":
					layerControlLemma.addOverlay(datalayer, " " + layername + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>");
					break;
				case "searchbox-visualquery-tab":
					layerControlVisualquery.addOverlay(datalayer, " " + layername + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>");
					break;
				case "searchbox-levenshtein-tab":
					layerControlLevenshtein.addOverlay(datalayer, " " + layername + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>");
					break;
				case "searchbox-statistics-tab":
					layerControlStatistics.addOverlay(datalayer, " " + layername + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>");
					break;
				case "searchbox-sparql-tab":
					layerControlSparql.addOverlay(datalayer, " " + layername + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>");
					break;
			}
		}
	});
});

/** Click on remove layer button */
$(document).on('click', '.btn-remove-layer-from-layercontrol', function (e) {
	currentlyActiveSearchboxTab = getCurrentlyActiveSearchboxTab();
	layerId = e.target.getAttribute('data-layer-id');

	//Remove the layer from layer control
	switch (currentlyActiveSearchboxTab) {
		case "searchbox-location-tab":
			removeLayerFromLayerControl(layerControlLocation, layerId)
			break;
		case "searchbox-lemma-tab":
			removeLayerFromLayerControl(layerControlLemma, layerId)
			break;
		case "searchbox-visualquery-tab":
			removeLayerFromLayerControl(layerControlVisualquery, layerId)
			break;
		case "searchbox-levenshtein-tab":
			removeLayerFromLayerControl(layerControlLevenshtein, layerId)
			break;
		case "searchbox-statistics-tab":
			removeLayerFromLayerControl(layerControlStatistics, layerId)
			break;
		case "searchbox-sparql-tab":
			removeLayerFromLayerControl(layerControlSparql, layerId)
			break;
	}

	//Remove layer from searchresult and from map
	removeDataFromSearchresult(layerId);
	removeLayerFromMap(layerId);

	//Set Add Layer button enabled
	$('#content-' + layerId + ' .btn-add-layer-to-layercontrol').prop('disabled', false);
});

function removeLayerFromLayerControl(layercontrol, layerId) {
	// Loop thru all layers in layercontrol
	layercontrol._layers.forEach(function (obj) {
		// Check if layer is the layer to be removed
		if (obj.layer.id == layerId) {
			//Remove overlay
			layercontrol.removeLayer(obj.layer);
		}
	});
}

/** Click on change layername button */
$(document).on('click', '.btn-change-tabname', function (e) {
	//Get layer id
	var layerId = $(this).parent().attr("data-layer-id");

	//Get current name of layer
	var currentText = document.getElementById(layerId).innerHTML;
	currentText = currentText.replace(" <span class=\"span-close\" title=\"" + lang.closeTab + "\">×</span>", "");

	//Get new name with prompt
	var inputNewTitle = prompt(lang.changeText, currentText);

	if (inputNewTitle != null && inputNewTitle != "") {
		//Set new text for tab
		document.getElementById(layerId).innerHTML = inputNewTitle + " <span class=\"span-close\" title=\"" + lang.closeTab + "\">×</span>";

		//Change also text in layerControl
		currentlyActiveSearchboxTab = getCurrentlyActiveSearchboxTab();

		//Change Tabname in layerControl
		switch (currentlyActiveSearchboxTab) {
			case "searchbox-location-tab":
				changeTitleInLayerControl(layerControlLocation, layerId, inputNewTitle)
				break;
			case "searchbox-lemma-tab":
				changeTitleInLayerControl(layerControlLemma, layerId, inputNewTitle)
				break;
			case "searchbox-visualquery-tab":
				changeTitleInLayerControl(layerControlVisualquery, layerId, inputNewTitle)
				break;
			case "searchbox-levenshtein-tab":
				changeTitleInLayerControl(layerControlLevenshtein, layerId, inputNewTitle)
				break;
			case "searchbox-statistics-tab": 1
				changeTitleInLayerControl(layerControlStatistics, layerId, inputNewTitle)
				break;
			case "searchbox-sparql-tab":
				changeTitleInLayerControl(layerControlSparql, layerId, inputNewTitle)
				break;
		}
	}
});

/** Click on download GeoJSON button */
$(document).on('click', '.btn-download-geojson', function (e) {
	var layerId = $(this).parent().attr("data-layer-id");
	var layername = $('#' + layerId).html().replace(" <span class=\"span-close\" title=\"" + lang.closeTab + "\">×</span>", "")

	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == layerId) {
			var dl_geojson = datalayer.toGeoJSON();
			downloadObjectAsGeoJson(dl_geojson, layername);
		}
	});
});

/** Makes the GeoJSON object downloadable */
function downloadObjectAsGeoJson(exportObj, exportName) {
	var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
	var downloadAnchorNode = document.createElement('a');
	downloadAnchorNode.setAttribute("href", dataStr);
	downloadAnchorNode.setAttribute("download", exportName + ".geojson");
	document.body.appendChild(downloadAnchorNode); // required for firefox
	downloadAnchorNode.click();
	downloadAnchorNode.remove();
}

/** Layer gets enabled in layerControl */
mymap.on('overlayadd', function (eo) {
	currentlyActiveSearchboxTab = getCurrentlyActiveSearchboxTab();

	//Restore the searchresult of this layer
	switch (currentlyActiveSearchboxTab) {
		case "searchbox-location-tab":
			restoreSearchresultLocation(eo.layer);
			break;
		case "searchbox-lemma-tab":
			restoreSearchresultLemma(eo.layer);
			break;
		case "searchbox-visualquery-tab":
			restoreSearchresultVisualquery(eo.layer);
			break;
		case "searchbox-levenshtein-tab":
			restoreSearchresultLevenshtein(eo.layer);
			addChoroplethControls()
			break;
		case "searchbox-statistics-tab":
			restoreSearchresultStatistics(eo.layer);
			addChoroplethControls()
			break;
		case "searchbox-sparql-tab":
			restoreSearchresultSparql(eo.layer);
			break;
	}

});

/** Layer gets disabled in layerControl */
mymap.on('overlayremove', function (eo) {
	//Remove the layer data from searchresult
	//Only triggered when clicked on the layerControl, not triggered by using mymap.removeLayer
	if (layerControlLocation._handlingClick || layerControlLemma._handlingClick || layerControlVisualquery._handlingClick || layerControlSparql._handlingClick) {
		removeDataFromSearchresult(eo.layer.id);
	}
	if (layerControlLevenshtein._handlingClick || layerControlStatistics._handlingClick) {
		removeDataFromSearchresult(eo.layer.id);

		//Remove Choropleth controls when there is no tab in the searchresult anymore
		var countCurrentTabsSearchresult = document.querySelectorAll('#searchresult-tabs button').length
		if (countCurrentTabsSearchresult == 0) {
			removeChoroplethControls();
		}

	}
});


/*
	Searchbox & Searchresult functions
*/

function hideAllSearchboxContents() {
	$('#searchbox-location-tab-content').hide();
	$('#searchbox-lemma-tab-content').hide();
	$('#searchbox-visualquery-tab-content').hide();
	$('#searchbox-levenshtein-tab-content').hide();
	$('#searchbox-statistics-tab-content').hide();
	$('#searchbox-sparql-tab-content').hide();
}

function getCurrentlyActiveSearchboxTab() {
	return $('#searchbox-tabs .active').attr("id");
}

/** Adds tab and content of layer to div searchresult */
function addDataToSearchresult(layerId, tabText, innerText) {
	//Close active popup
	mymap.closePopup();

	//Get amount of tabs in searchresult div
	var countCurrentTabsSearchresult = document.querySelectorAll('#searchresult button').length

	//Shorten the tabext if its too long
	var tabText = shortenTabText(tabText);

	if (countCurrentTabsSearchresult == 0) {
		$('#searchresult').show();
		//Add tab and content
		$("#searchresult-tabs").append("<button class='nav-link' data-is-active-tab='true' id=" + layerId + " data-bs-toggle='tab' data-bs-target='#content-" + layerId + "' type='button' role='tab' aria-controls='content-" + layerId + "'	aria-selected='true'>" + tabText + " <span class='span-close' title='" + lang.closeTab + "'>×</span></button>")
		$("#searchresult-tab-content").append("<div class='tab-pane fade' data-is-active-tab='true' id='content-" + layerId + "' data-layer-id=" + layerId + " role='tabpanel' aria-labelledby=" + layerId + ">" + innerText + "</div>")
		//Set new tab to active tab
		$("#searchresult-tabs button[data-is-active-tab='true']").tab("show")
	}
	else {
		//Set currently active tab to not active
		$("#searchresult-tabs button[data-is-active-tab='true']").attr("data-is-active-tab", "false")
		$("#searchresult-tab-content div[data-is-active-tab='true']").attr("data-is-active-tab", "false")
		//Add tab and content
		$("#searchresult-tabs").append("<button class='nav-link' data-is-active-tab='true' id=" + layerId + " data-bs-toggle='tab' data-bs-target='#content-" + layerId + "' type='button' role='tab' aria-controls='content-" + layerId + "' aria-selected='true'>" + tabText + " <span class='span-close' title='" + lang.closeTab + "'>×</span></button>")
		$("#searchresult-tab-content").append("<div class='tab-pane fade' data-is-active-tab='true' id='content-" + layerId + "' data-layer-id=" + layerId + " role='tabpanel' aria-labelledby=" + layerId + ">" + innerText + "</div>")
		//Set new tab to active tab
		$("#searchresult-tabs button[data-is-active-tab='true']").tab("show")
	}

	//Set scrollbar position
	var tabWidth = $('#searchresult-tabs').width();
	$('#searchresult-tabs').scrollLeft(tabWidth);
}

function shortenTabText(tabText) {
	//If layername is longer than 15 characters, shorten it
	if (tabText.length > 15) {
		tabText = tabText.substr(0, 12) + "...";
	}
	return tabText
}

/** Removes tab and content of layer from div searchresult */
function removeDataFromSearchresult(id) {
	var countCurrentTabsSearchresult = document.querySelectorAll('#searchresult-tabs button').length

	activeTab = $("#searchresult-tabs button[data-is-active-tab='true']")

	//Check if the closed tab is the currently active tab
	if (activeTab.attr("id") == $('#' + id).attr("id")) {
		//Set previous tab active, if there is one
		if ($('#' + id).prev().length == 1) {
			$('#' + id).prev().attr("data-is-active-tab", "true")
			$('#content-' + id).prev().attr("data-is-active-tab", "true")
		}
		else {
			//If not, set next tab active, if there is one
			if ($('#' + id).next().length == 1) {
				$('#' + id).next().attr("data-is-active-tab", "true")
				$('#content-' + id).next().attr("data-is-active-tab", "true")
			}
		}

		$('#' + id).remove(); //remove tab
		$('#content-' + id).remove(); //remove content

		//Show the new active tab
		$("#searchresult-tabs button[data-is-active-tab='true']").tab("show")
	}
	else {
		$('#' + id).remove(); //remove tab
		$('#content-' + id).remove(); //remove content

		//Show the new active tab
		$("#searchresult-tabs button[data-is-active-tab='true']").tab("show")
	}

	//Check if there are no tabs left --> hide searchresult div, remove style classes and remove info+legend
	if (countCurrentTabsSearchresult == 1) {
		$('#searchresult').hide();

		removeAllClassesFromSearchresult();

		mymap.removeControl(info);
		mymap.removeControl(legend);
	}
}

function hideDivSearchresult() {
	$("#searchresult").hide();
	$('#searchresult-voucherdetails').hide();
}

function unfoldDivSearchresult() {
	if ($("#searchresult-voucherdetails").attr("data-is-active") == "true") {
		//searchresult-voucherdetails was active
		$('#searchresult-voucherdetails').show();
	}
	else {
		//searchresult-voucherdetails was not active
		var countCurrentTabsSearchresult = document.querySelectorAll('#searchresult-tabs button').length
		if (countCurrentTabsSearchresult > 0) {
			$('#searchresult').show();
		}
	}

}

function removeAllTabsFromSearchresult() {
	$('#searchresult-tabs').html("");
	$('#searchresult-tab-content').html("");
}

function removeAllClassesFromSearchresult() {
	$('#searchresult').removeClass('searchresult-location-lemma');
	$('#searchresult').removeClass('searchresult-visualquery');
	$('#searchresult').removeClass('searchresult-levenshtein');
	$('#searchresult').removeClass('searchresult-statistics');
	$('#searchresult').removeClass('searchresult-nl2sparql');
	$('#searchresult-tabs').removeClass('highlightable-tabs');
}


/*
	Layer/Map functions
*/

function deleteAllLayersFromMap() {
	mymap.eachLayer(function (layer) {
		if (!!layer.toGeoJSON) {
			mymap.removeLayer(layer);
		}
	});
};

/** Highlights specific layer on the map */
function highlightLeafletLayer(layerId) {
	mymap.eachLayer(function (datalayer) {

		if (datalayer.id == layerId) {
			//Set layer weight of specific layer
			datalayer.setStyle({
				weight: 5,
			});

			if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
				datalayer.bringToFront();
			}
		}
		else {
			//All other GeoJSON layers --> regular formatting
			if (datalayer instanceof L.GeoJSON) {
				datalayer.setStyle({
					weight: 2,
					dashArray: "",
				});
			}
		}
	});
};

function removeLayerFromMap(layerId) {
	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == layerId) {
			mymap.removeLayer(datalayer);
		}
	});
}

function getColorFromLayer(layerId) {
	mymap.eachLayer(function (datalayer) {
		if (datalayer.id === layerId) {
			datalayer.eachLayer(function (elayer) {
				layercolor = elayer.options.color;
			});
		}
	});
	return layercolor;
}

function flyToLayer(layerId) {
	//Loop through all layers on the map
	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == layerId) {

			//Check if layer has only one feature or multiple features
			if (Object.keys(datalayer._layers).length == 1) {

				datalayer.eachLayer(function (elayer) {
					if (elayer.feature.geometry.type == 'Point') {
						//Point
						//Check if it has an empty geometry
						if (hasLatLng(elayer)) { mymap.flyTo(elayer.getLatLng(), 11); }
					}
					else {
						//Polygon
						mymap.flyToBounds(datalayer.getBounds().pad(0.2));
					}
				});
			}
			else {
				//Multiple features

				//Could be a real geometry together with empty geometry -->recalculate bounds
				//Calculate new bounds of layer
				newBounds = calculateBoundsWithoutEmptyGeometries(datalayer)

				// Check if bounds are valid (could be empty)
				if (newBounds.isValid()) {
					// Valid, fit bounds
					mymap.flyToBounds(newBounds.pad(0.2));
				}
			}
			datalayer.bringToFront();
		}
	});
}

/** Fly to a specific feature in a leaflet layer */
function flyToFeature(layerId, locationId) {
	//Loop through all layers on the map
	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == layerId) {

			//Loop through all geometry features in the layer
			datalayer.eachLayer(function (layer) {
				if (layer.feature.properties.lokationId === locationId) {
					//Fly to selected layer
					if (layer.feature.geometry.type === "Point") { mymap.flyTo(layer.getLatLng(), 11); }
					else { mymap.flyToBounds(layer.getBounds().pad(0.2)); }

					layer.bringToFront();
					layer.openPopup();
				}
			});
		}
	});
}

/** Calculates new bounds for leaflet layer without Point(0,0) geometries */
function calculateBoundsWithoutEmptyGeometries(inputlayer) {
	// Create new empty bounds
	var bounds = new L.LatLngBounds();

	// Iterate the map's layers
	mymap.eachLayer(function (datalayer) {
		if (datalayer.id == inputlayer.id) {

			//Iterate the geometry features in the layer
			datalayer.eachLayer(function (layer) {
				// Check if geometry is not empty
				if (!isPoint00(layer.feature.geometry.coordinates)) {
					// Extend bounds with features's bounds
					if (layer.feature.geometry.type == 'Point') {
						bounds.extend(layer.getLatLng());
					}
					else {
						bounds.extend(layer.getBounds());
					}

				}
			});
		}
	});
	return bounds;
}

/** Checks if the geometry is an arificial geometry (Point(0,0))*/
function isPoint00(a) {
	b = [0, 0]
	return Array.isArray(a) &&
		Array.isArray(b) &&
		a.length === b.length &&
		a.every((val, index) => val === b[index]);
}

/** Checks if Leaflet layer has bounds (for flyto) */
function hasLatLng(leafletLayer) {
	bounds = leafletLayer.getLatLng()

	if ((bounds.lat == 0) && (bounds.lng == 0)) { return false; }
	else { return true; }
}


/*
	Layercontrol functions
*/

function getLayernameFromLayerControl(layerId) {
	var layerName = $("button[data-layer-id=" + layerId + "]").parent().html().replace(" <button class=\"btn-remove-layer-from-layercontrol btn-close\" data-layer-id=\"" + layerId + "\" title=\"" + lang.removeLayer + "\"></button>", "")
	return layerName.trim()
}

function changeTitleInLayerControl(layercontrol, layerId, newTitle) {
	//Change title in layercontrol div
	$("button[data-layer-id=" + layerId + "]").parent().html(" " + newTitle + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>")

	//Title must also be changed in layercontrol object
	//Loop thru all layers in layercontrol
	layercontrol._layers.forEach(function (obj) {
		//Check if layer is the layer to be changed
		if (obj.layer.id == layerId) {
			//Change title
			obj.name = newTitle + " <button class='btn-remove-layer-from-layercontrol btn-close' data-layer-id=" + layerId + " title='" + lang.removeLayer + "'></button>";
		}
	});
}



/*
	Other functions
*/

function removeChoroplethControls() {
	mymap.removeControl(info);
	mymap.removeControl(legend);
}

function addChoroplethControls() {
	currentlyActiveSearchboxTab = getCurrentlyActiveSearchboxTab();

	switch (currentlyActiveSearchboxTab) {
		case "searchbox-levenshtein-tab":
			currentlyActiveOption = 'levenshtein'
			break;
		case "searchbox-statistics-tab":
			currentlyActiveOption = 'statistics'
			break;
	}

	info.addTo(mymap);
	legend.addTo(mymap);
}

/** Sorts the elements in a select alphabetically */
function sortSelectElements(nameOfSelect) {
	var opt = $("#" + nameOfSelect + " option").sort(function (a, b) { return a.text.toUpperCase().localeCompare(b.text.toUpperCase()) });
	$("#" + nameOfSelect).append(opt);
	$("#" + nameOfSelect).find('option:first').attr('selected', 'selected');
}

function disableAddLayerButton(layerId) {
	$('#content-' + layerId + ' .btn-add-layer-to-layercontrol').prop('disabled', true);
	$('#content-' + layerId + ' .btn-add-layer-to-layercontrol').attr('data-is-disabled', true);
}

function disableAllControlElementsOnSite() {
	//disable everything on the page
	$("button").prop('disabled', 'disabled');
	$('ul').css('pointer-events', 'none');
	$('input').prop('disabled', true);
	$('select').attr("disabled", true);
	$('textarea').attr("disabled", true);
	$('a').css('pointer-events', 'none');
}

function enableAllControlElementsOnSite() {
	$("button").not('[data-is-disabled=true]').prop('disabled', false);
	$('ul').css('pointer-events', 'auto');
	$('input').prop('disabled', false);
	$('select').attr("disabled", false);
	$('textarea').attr("disabled", false);
	$('a').css('pointer-events', 'auto');
}



/*
	Modal (Source: https://www.w3schools.com/howto/howto_css_modals.asp)--- 
*/
// Get the modal
var modal = document.getElementById("modal-help");

// Get the button that opens the modal
var btn = document.getElementById("button-help");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("modal-close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function () {
	modal.style.display = "block";
}
// When the user clicks on <span> (x), close the modal
span.onclick = function () {
	modal.style.display = "none";
}
// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
	if (event.target == modal) {
		modal.style.display = "none";
	}
}