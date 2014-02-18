
function popForm(){
  if(window.currentInd <= 0){window.currentInd = "0";}
  if(window.currentInd >= window.lastInd){window.currentInd = window.lastInd.toString();}
  var annoDic = window.batchDict[window.currentInd];
  $("#index").html(parseInt(window.currentInd)+1);
  $("#lastInd").html(window.lastInd+1);
  $("#sent").val(annoDic.sent);
  editor.setValue(annoDic.anno);
  $("#newswire").val(annoDic.newswire);
  $("#comment").val(annoDic.comment);
  $("#result").css("display", "none");
  $('#answer img').remove();
  document.getElementById("save").disabled=true;
  $("#interface").css("background-color", "#fff")
  window.batchDict[window.currentInd].accessed.push(Math.round(+new Date()/1000));
  updateBatch();
}
function noSave(){
	var container = $("#interface");
  //container.css("border", "1em groove maroon");
  container.css("background-color", "#fcc");
  document.getElementById("save").disabled=true;
}
function yesSave(){
	var container = $("#interface");
	//container.css("border", "1em groove green");
	container.css("background-color", "#cfc");
	document.getElementById("save").disabled=false;
}
function toConsole(){console.log(window.batchDict)}

function nextAnno(){
  window.currentInd = parseInt(window.currentInd) + 1;
  window.currentInd = window.currentInd.toString();
  popForm();
}
function prevAnno(){
  window.currentInd = parseInt(window.currentInd) - 1;
  window.currentInd = window.currentInd.toString();
  popForm();
}
function updateBatch(){
  $.post("/api/updateBatch", {'batch':JSON.stringify(window.batchDict)})
    .success(function(data) {
      //console.log(JSON.stringify(window.batchDict));
    })
    .fail(function(data){
      window.alert("Connection interrupted?");
    });
}
function loadImage() {
	var sentenceStr = encodeURIComponent($("#sent").val());
	var annotationStr = encodeURIComponent(editor.getValue());
	var result = $("#result");

	window.batchDict[window.currentInd].analyzed.push(Math.round(+new Date()/1000));
	$.get("/api/analyzegfl.png?sentence=" + sentenceStr + "&anno="+ annotationStr)
	.success(function(data){
		result.html("<img style=\"border-radius:1em;border:2px solid black;\" src=\"/api/analyzegfl.png?sentence=" + sentenceStr + "&anno="+ annotationStr + "\"/>");
		result.css('display', 'block');
    yesSave();
		})
	.fail(function(data){
		result.html(data.responseText);
		result.css("display", "block");
		result.css("border", "2px solid black");
		noSave();
		window.alert(data.responseText);
		document.getElementById("save").disabled=true;
		});
	updateBatch();
}

function assignBatch(dataset, batch) {
	var user = $("#"+dataset+"_"+batch).val();
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
}



function postAnno() {
  window.batchDict[window.currentInd].anno = editor.getValue();
  window.batchDict[window.currentInd].newswire = $("#newswire").val();
  window.batchDict[window.currentInd].comment = $("#comment").val();
  window.batchDict[window.currentInd].submitted.push(Math.round(+new Date()/1000));
  //console.log(window.batchDict[window.currentInd]);
  $.post("/api/submit", {"anno":JSON.stringify(window.batchDict[window.currentInd])})
    .success(function(data){
      //window.alert("Success! "+data);
      
    })
    .fail(function(data){
      console.log(data);
    });
  nextAnno();
}

function addUser() {
  var username = $("#username");
  var alias = $("#alias");
  var newUser = username.val();
  var newAlias = alias.val();
  username.val("");
  alias.val("");
  $.get("api/newUser?newUser="+encodeURIComponent(newUser)+"&alias="+encodeURIComponent(newAlias))
  .success(function(data){
    window.alert("User added: "+newUser+"!");
  })
  .fail(function(data){
    console.log(data);
  });
}
