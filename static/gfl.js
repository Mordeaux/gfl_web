// use jquery


function loadImage() {
	var sentenceStr = encodeURIComponent($("#sent").val());
	var annotationStr = encodeURIComponent(editor.getValue());
	var image = $("#image");
	var error = $("#error");
	
	$.get("/api/analyzegfl.png?sentence=" + sentenceStr + "&anno="+ annotationStr)
	.success(function(data){
		image.html("<img src=\"/api/analyzegfl.png?sentence=" + sentenceStr + "&anno="+ annotationStr + "\"/>");
		image.css('display', 'block');
		error.css("display", "none");
		document.getElementById("save").disabled=false;
		})
	.fail(function(data){
		console.log(data)
		error.html(data.responseText);
		image.css("display", "none");
		error.css("display", "block");
		window.alert(data.responseText);
		document.getElementById("save").disabled=true;
		});
};

function assignBatch(dataset, batch) {
	var user = $("#"+dataset+"_"+batch).val()
	var uriuser = encodeURIComponent(user);
	var uridataset = encodeURIComponent(dataset);
	var uribatch = encodeURIComponent(batch);
	
	$.get("/api/assign?dataset=" + uridataset + "&batch=" + uribatch + "&user=" + uriuser)
	.success(function(data){
		window.alert(dataset+": batch# "+batch+" assigned to "+user);
	})
	.fail(function(data){
		console.log(data);
	});
};
