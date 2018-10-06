function month(d) {
	var m = '' + (d.getMonth() + 1);
	if ( m.length == 1) {
		m = '0' + m;
	}
	return m;
}

function day(d) {
	var m = '' + d.getDate();
	if ( m.length == 1) {
		m = '0' + m;
	}
	return m;
}
	       	    
function afterStart(d) {
	if ( d.getFullYear() == 2013 && d.getMonth() == 9 && d.getDate() == 31 ) {
		return false;
	}
	return true;
}

function selectarchive(s) {
	document.getElementById("video_source").setAttribute("src",'http://www.scewpt.com/mg/' + s.options[s.selectedIndex].text + '.ogv');
	document.getElementById("video").load();
	document.getElementById("video").play();	
}

function init() {
	console.log('yo');
	var day_millis = 24 * 60 * 60 * 1000;
	var archived = new Date(sd.getTime() - day_millis);	
	while ( afterStart(archived) ) {
		var opt = document.createElement("option");
		opt.text = archived.getFullYear() + '-' + month(archived) + '-' + day(archived);
		document.getElementById("archive").add(opt);
		archived = new Date( archived.getTime() - day_millis );
	}     
}

window.onload = init;

	       	    
