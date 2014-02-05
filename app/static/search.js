$(document).ready(function(){
	var regex = $("#regex");
	regex.change(regex.val(), function(value){
		var uriregex = encodeURIComponent(value);
		
		$.get("api/regex?regex="+uriregex)
		.success(function(data){
		
		
		})
		.fail(function(data){
		
		
		
		});
	});


});