/** Performs ajax request for loading additional data on a dialect record from the database */
function ajaxRequestForRecorddetails(recordId, recordDescription, source) {
	loadingGraphicOnOff(source, "on");

	disableAllControlElementsOnSite();

	$.ajax({
		url: '/searchRecorddetails',
		type: 'POST',
		contentType: "application/json",
		data: JSON.stringify({ "recordId": recordId })
	}).done(function (recorddetailsJSON) {
		//Create HTML Code and add it to searchresult
		htmlData = createHTMLCodeForSearchresultRecorddetails(recordDescription, recorddetailsJSON)
		$("#searchresult-recorddetails").html(htmlData);

		//Set margin-top for div depending on source div
		sourceDivMarginTop = $('#searchresult').css('margin-top');
		$("#searchresult-recorddetails").css('margin-top', sourceDivMarginTop);
		setHeightOfSearchresultRecorddetails(source);

		$("#searchresult-recorddetails").show();
		$('#searchresult').hide();
		$("#searchresult-recorddetails").attr("data-is-active", "true"); //Set Recorddetails div to active

	}).fail(function (jqXHR, textStatus, errorThrown) {
		$("#errorbox").html(lang.loadErrorRecorddetails + errorThrown);
		$("#errorbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}).always(function (jqXHR, textStatus) {
		loadingGraphicOnOff(source, "off")
		enableAllControlElementsOnSite();
	});
}

function createHTMLCodeForSearchresultRecorddetails(recordDescription, recorddetailsJSON) {
	var htmlData = "<button type='button' id='btn-back' class='page-link arrow left'><i class='bi bi-arrow-left'></i></button><p class='header-recorddetails'>" + lang.record+"</p>";

	//Table 1 (Details)
	htmlData += "<h5 class='tableheadings-recorddetails'>" + lang.details + ":</h5>"
	htmlData += "<table><tr><th>" + lang.record_description + "</th><td>" + recordDescription + "</td></tr>"
	htmlData += "<tr><th>" + lang.mainLemma + "</th><td>" + recorddetailsJSON["hauptlemma"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.secondaryLemma + "</th><td>" + recorddetailsJSON["nebenlemma"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.standardGerman + "</th><td>" + recorddetailsJSON["hochdeutsch"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.meaning + "</th><td>" + recorddetailsJSON["beschreibung"]["value"] + "</td></tr>"
	htmlData += "</table><br>"

	//Table 2 (Source)
	htmlData += "<h5 class='tableheadings-recorddetails'>" + lang.source + "</h5>"
	htmlData += "<table><tr><th>" + lang.title + "</th><td>" + recorddetailsJSON["titel"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.author + "</th><td>" + recorddetailsJSON["autor"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.releaseYear + "</th><td>" + recorddetailsJSON["erscheinungsjahr"]["value"] + "</td></tr>"
	htmlData += "</table><br>"

	//Table 3 (Location)
	htmlData += "<h5 class='tableheadings-recorddetails'>" + lang.usedIn + "</h5>"
	htmlData += "<table><tr><th>" + lang.place + "</th><td>" + recorddetailsJSON["ortName"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.municipality + "</th><td>" + recorddetailsJSON["gemeindeName"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.region + "</th><td>" + recorddetailsJSON["regionName"]["value"] + "</td></tr>"
	htmlData += "</table><br>"

	//Table 4 (Additional info)
	htmlData += "<h5 class='tableheadings-recorddetails'>" + lang.additionalInformation + "</h5>"
	htmlData += "<table><tr><th>" + lang.dbpedia + "</th><td><a href='" + recorddetailsJSON["dbpedia"]["value"] + "'target='_blank'>" + recorddetailsJSON["dbpedia"]["value"] + "</a></td></tr>"
	htmlData += "<tr><th>" + lang.picture + "</th><td><img src='" + recorddetailsJSON["dbpediaImage"]["value"] + "' alt='' width='250px'></td></tr>"
	htmlData += "</table><br>"

	return htmlData;
}

/** Listens to clicks on record button group */
$(document).on('click', '.button-record', function (e) {

	var recordId = e.target.getAttribute('data-record-id');
	var recordDescription = e.target.innerText

	var source = $(this).attr("data-source"); //get source div (location or vq)
	ajaxRequestForRecorddetails(recordId, recordDescription, source)
});

/** Click on back button in searchresult-recorddetails */
$(document).on('click', '#btn-back', function (e) {
	$("#searchresult-recorddetails").hide(); //hide div
	$('#searchresult').show(); //show div
	$("#searchresult-recorddetails").attr("data-is-active", "false");
});

/** Switches loading graphics on/off */
function loadingGraphicOnOff(source, action) {
	if (action == "on") {
		switch (source) {
			case "location":
				$("#spinner-location").show();
				break;
			case "lemma":
				$("#spinner-lemma").show();
				break;
			case "visualquery":
				$("#spinner-visualquery").show();
				break;
			case "levenshtein":
				$("#spinner-levenshtein").show();
				break;
			case "statistics":
				$("#spinner-statistics").show();
				break;
		}
	}
	else {
		switch (source) {
			case "location":
				$("#spinner-location").hide();
				break;
			case "lemma":
				$("#spinner-lemma").hide();
				break;
			case "visualquery":
				$("#spinner-visualquery").hide();
				break;
			case "levenshtein":
				$("#spinner-levenshtein").hide();
				break;
			case "statistics":
				$("#spinner-statistics").hide();
				break;
		}
	}
}

/** Sets the height of the searchresult-recorddetails div depending on the searchresult div */
function setHeightOfSearchresultRecorddetails(source) {
	switch (source) {
		case "location":
			$("#searchresult-recorddetails").css('max-height', '70vh');
			break;
		case "lemma":
			$("#searchresult-recorddetails").css('height', '70vh');
			break;
		case "visualquery":
			$("#searchresult-recorddetails").css('height', '70vh');
			break;
		case "levenshtein":
			$("#searchresult-recorddetails").css('max-height', '40vh');
			break;
		case "statistics":
			$("#searchresult-recorddetails").css('max-height', '37vh');
			break;
	}
}