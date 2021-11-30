/** Creates ajax request for loading voucher data from the database */
function ajaxRequestForVoucherdetails(voucherId, voucherdescription, source) {
	loadingGraphicOnOff(source, "on");

	disableAllControlElementsOnSite();

	$.ajax({
		url: '/searchVoucherdetails',
		type: 'POST',
		contentType: "application/json",
		data: JSON.stringify({ "voucherId": voucherId })
	}).done(function (voucherdetailsJSON) {
		//Create HTML Code and add it to searchresult
		htmlData = createHTMLCodeForSearchresultVoucherdetails(voucherdescription, voucherdetailsJSON)
		$("#searchresult-voucherdetails").html(htmlData);

		//Set margin-top for div depending on source div
		sourceDivMarginTop = $('#searchresult').css('margin-top');
		$("#searchresult-voucherdetails").css('margin-top', sourceDivMarginTop);
		setHeightOfSearchresultVoucherdetails(source);

		$("#searchresult-voucherdetails").show();
		$('#searchresult').hide();
		$("#searchresult-voucherdetails").attr("data-is-active", "true"); //Set Voucherdetails div to active

	}).fail(function (jqXHR, textStatus, errorThrown) {
		$("#errorbox").html(lang.loadErrorVoucherdetails + errorThrown);
		$("#errorbox").addClass("fade_animation").on('animationend', function (e) {
			$(this).removeClass("fade_animation").off('animationend');
		});
	}).always(function (jqXHR, textStatus) {
		loadingGraphicOnOff(source, "off")
		enableAllControlElementsOnSite();
	});
}

function createHTMLCodeForSearchresultVoucherdetails(voucherdescription, voucherdetailsJSON) {
	var htmlData = "<button type='button' id='btn-back' class='page-link arrow left'><i class='bi bi-arrow-left'></i></button><p class='header-voucherdetails'>" + lang.voucher+"</p>";

	//Table 1 (Details)
	htmlData += "<h5 class='tableheadings-voucherdetails'>" + lang.details + ":</h5>"
	htmlData += "<table><tr><th>" + lang.voucher_description + "</th><td>" + voucherdescription + "</td></tr>"
	htmlData += "<tr><th>" + lang.mainLemma + "</th><td>" + voucherdetailsJSON["hauptlemma"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.secondaryLemma + "</th><td>" + voucherdetailsJSON["nebenlemma"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.standardGerman + "</th><td>" + voucherdetailsJSON["hochdeutsch"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.meaning + "</th><td>" + voucherdetailsJSON["beschreibung"]["value"] + "</td></tr>"
	htmlData += "</table><br>"

	//Table 2 (Source)
	htmlData += "<h5 class='tableheadings-voucherdetails'>" + lang.source + "</h5>"
	htmlData += "<table><tr><th>" + lang.title + "</th><td>" + voucherdetailsJSON["titel"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.author + "</th><td>" + voucherdetailsJSON["autor"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.releaseYear + "</th><td>" + voucherdetailsJSON["erscheinungsjahr"]["value"] + "</td></tr>"
	htmlData += "</table><br>"

	//Table 3 (Location)
	htmlData += "<h5 class='tableheadings-voucherdetails'>" + lang.usedIn + "</h5>"
	htmlData += "<table><tr><th>" + lang.place + "</th><td>" + voucherdetailsJSON["ortName"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.municipality + "</th><td>" + voucherdetailsJSON["gemeindeName"]["value"] + "</td></tr>"
	htmlData += "<tr><th>" + lang.region + "</th><td>" + voucherdetailsJSON["regionName"]["value"] + "</td></tr>"
	htmlData += "</table><br>"

	//Table 4 (Additional info)
	htmlData += "<h5 class='tableheadings-voucherdetails'>" + lang.additionalInformation + "</h5>"
	htmlData += "<table><tr><th>" + lang.dbpedia + "</th><td><a href='" + voucherdetailsJSON["dbpedia"]["value"] + "'target='_blank'>" + voucherdetailsJSON["dbpedia"]["value"] + "</a></td></tr>"
	htmlData += "<tr><th>" + lang.picture + "</th><td><img src='" + voucherdetailsJSON["dbpediaImage"]["value"] + "' alt='' width='250px'></td></tr>"
	htmlData += "</table><br>"

	return htmlData;
}

/** Listens to clicks on voucher button group */
$(document).on('click', '.button-voucher', function (e) {

	var voucherId = e.target.getAttribute('data-voucher-id');
	var voucherdescription = e.target.innerText

	var source = $(this).attr("data-source"); //get source div (location or vq)
	ajaxRequestForVoucherdetails(voucherId, voucherdescription, source)
});

/** Click on back button in searchresult-voucherdetails */
$(document).on('click', '#btn-back', function (e) {
	$("#searchresult-voucherdetails").hide(); //hide div
	$('#searchresult').show(); //show div
	$("#searchresult-voucherdetails").attr("data-is-active", "false");
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

/** Sets the height of the searchresult-voucherdetails div depending on the searchresult div */
function setHeightOfSearchresultVoucherdetails(source) {
	switch (source) {
		case "location":
			$("#searchresult-voucherdetails").css('max-height', '70vh');
			break;
		case "lemma":
			$("#searchresult-voucherdetails").css('height', '70vh');
			break;
		case "visualquery":
			$("#searchresult-voucherdetails").css('height', '70vh');
			break;
		case "levenshtein":
			$("#searchresult-voucherdetails").css('max-height', '40vh');
			break;
		case "statistics":
			$("#searchresult-voucherdetails").css('max-height', '37vh');
			break;
	}
}