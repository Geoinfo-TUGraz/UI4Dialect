//Variables for levenshtein and statistics
var levenshteinLayer, statisticsLayer;
var info = L.control();
var legend = L.control({ position: 'bottomright' });
var currentlyActiveOption;


/** --INITIALIZE APPLICATION-- */
$(document).ready(function () {
	//Set Value of Levenshtein Output Label
	$('#slider-levenshtein-output').html($('#slider-levenshtein').val());

	//Set Placeholder
	$("#autocomplete-location").attr("placeholder", lang.loadDataLocation);

	initAddLoadingGraphics();
	disableAllControlElementsOnSite();
	initAjaxRequestForLocations();
});

/** Performs ajax request for loading location data from database */
function initAjaxRequestForLocations() {

	//Variable for state
	var isLocationdataLoaded = false;

	$.ajax({
		url: "/init_loadLocations",
	}).done(function (res) {
		$("#autocomplete-location").autocomplete({
			source: res, //input data for autocomplete
			minLength: 3, //show suggestions only after 3 input characters
			focus: function (event, ui) {
				event.preventDefault();
			},
			select: function (event, ui) {
				event.preventDefault();
				$("#autocomplete-location").val(ui.item.label); // what the user sees
				$("#autocomplete-location").attr('data-location-id', ui.item.value); // what is returned (location_id)
				$('#autocomplete-location').blur();
				selectLocationInAutocomplete();
				event.stopPropagation(); //stop the propagation --> don't show Popup
			},
		}).data("ui-autocomplete")._renderItem = renderItem;

		isLocationdataLoaded = true; //load successful

	}).fail(function (jqXHR, textStatus, errorThrown) {
		$("#errorbox").html(lang.loadErrorLocation +  errorThrown);
		$("#errorbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}).always(function (jqXHR, textStatus) {
		//Load lemma data
		initAjaxRequestForLemmata(isLocationdataLoaded);
	});
}


/** Performs ajax request for loading lemma data from database */
function initAjaxRequestForLemmata(isLocationdataLoaded) {
	//Set Placeholder
	$("#autocomplete-location").attr("placeholder", lang.loadDataLemma);

	//Variable for state
	var isLemmadataLoaded = false;

	$.ajax({
		url: "/init_loadLemmata",
	}).done(function (res) {
		$("#autocomplete-lemma").autocomplete({
			source: res, //input data for autocompelte
			minLength: 3, //show suggestions only after 3 input characters
			focus: function (event, ui) {
				event.preventDefault();
			},
			select: function (event, ui) {
				event.preventDefault();
				$("#autocomplete-lemma").val(ui.item.label); // what the user sees
				$("#autocomplete-lemma").attr('data-lemma-id', ui.item.value); // what is returned (lemma_id)
				$('#autocomplete-lemma').blur();
				selectLemmaInAutocomplete();
				event.stopPropagation(); //stop the propagation --> don't show Popup
			},
		}).data("ui-autocomplete")._renderItem = function (ul, item) {
			//Add the .ui-state-highlight class and highlight text
			var newText = String(item.label).replace(
				new RegExp(this.term, "gi"),
				"<span class='ui-state-highlight'>$&</span>");
			return $("<li>")
				.append("<a>" + newText + "</a>")
				.appendTo(ul);
		};

		isLemmadataLoaded = true; //load successful

	}).fail(function (jqXHR, textStatus, errorThrown) {
		$("#errorbox").html(lang.loadErrorLemma +  errorThrown);
		$("#errorbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}).always(function (jqXHR, textStatus) {
		initRemoveLoadingGraphics()
		enableAllControlElementsOnSite();
		setAutocompleteStatusAfterInitLoading(isLocationdataLoaded, isLemmadataLoaded)
	});

}


/** Renders the items of the autocomplete */
var renderItem = function (ul, item) {
	//Get the value of the select element (Place=1, Municipality=2, Region=3)
	var locationLevel = $('#select-location').val();

	//Add the .ui-state-highlight class and highlight text
	var newText = String(item.label).replace(
		new RegExp(this.term, "gi"), "<span class='ui-state-highlight'>$&</span>");

	//Add the value to the autocompelte depending on the level (Place, Municipality, Region)
	if ((locationLevel == 1) && (item.value.includes('ort'))) {
		return $("<li>")
			.append("<a>" + newText + "</a>")
			.appendTo(ul);
	} else {
		if ((locationLevel == 2) && (item.value.includes('gemeinde'))) {
			return $("<li>")
				.append("<a>" + newText + "</a>")
				.appendTo(ul);
		}
		else {
			if ((locationLevel == 3) && (item.value.includes('region'))) {
				return $("<li>")
					.append("<a>" + newText + "</a>")
					.appendTo(ul);
			}
			else {
				// Don't wrap in <a> if value is empty
				return $("")
					.appendTo(ul);
			}
		}
	}
}

/** Sets the status of the autocompletes after the loading process of locations and lemmata */
function setAutocompleteStatusAfterInitLoading(isLocationdataLoaded, isLemmadataLoaded) {
	if (isLocationdataLoaded) { $("#autocomplete-location").attr("placeholder", lang.autocompleteLocation); } else {
		$("#autocomplete-location").attr("placeholder", lang.loadErrorAutocomplete);
		$("#autocomplete-location").attr("readonly", true);
		$("#select-location").attr("disabled", true);
	}
	if (isLemmadataLoaded) { $("#autocomplete-lemma").attr("placeholder", lang.autocompleteLemma); } else {
		$("#autocomplete-lemma").attr("placeholder", lang.loadErrorAutocomplete);
		$("#autocomplete-lemma").attr("readonly", true);
	}
}

/** Changes list items in autocomplete list, when user changes value in dropdown field */
$('#select-location').on('change', function () {
	$("#autocomplete-location").data("ui-autocomplete")._renderItem = renderItem;
});

function initAddLoadingGraphics() {
	$("#spinner-location").show();
	$("#spinner-lemma").show();
}

function initRemoveLoadingGraphics() {
	$("#spinner-lemma").hide();
	$("#spinner-location").hide();
}