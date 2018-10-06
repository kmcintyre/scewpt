function rules_banner() {	
	var ctx = document.getElementById('rules').getContext('2d');
	ctx.font = '18pt Geneva, Tahoma, Verdana, sans-serif';
	ctx.rotate(Math.PI / 3.33);
	ctx.fillStyle = 'orange';
	ctx.fillText("Morning", 25, 10);
	ctx.save();	
	ctx.rotate(-Math.PI / 2);
	ctx.fillStyle = 'orange';
	ctx.fillText("Google", -60, 145);
}

function check_url(val) {
  if( val.indexOf('http://') < 0 && val.indexOf('https://') < 0  ) {
  	return check_url('http://' + val);
  } else if ( val.indexOf('.') < 0 ) {
  	return check_url(val + '.com');
  } else {
    return val;
  }
}

msg = function (evt) {
	if ( $("#frontpage").is(":visible") ) {
		$("#frontpage").slideToggle();
	}	
	console.info('event');
	var new_frontpage = JSON.parse(evt.data);
	console.info(evt.data);
	$("#frontpage").data('latest_subject', new_frontpage )
	
	$link = $('<a href="' +
		'http://www.scewpt.com/' + new_frontpage["file_dest"] + '.html' +
		'">' +
		new_frontpage['subject'] +
		'</a><span style="font-size:.8em;padding-left:1em">from:' + new_frontpage['derived_from'] + '</span>');				
	$("#frontpage").html(
		$link
	);
	$("#frontpage").slideToggle();
}		

sub = function () {
	ret = { 'filter': { 'to': 'scewpt.com'} }
	if ( $("#frontpage").data('latest_subject') == undefined ) {
		ret['last'] = 1;
	}
	console.info('sending:' + ret);
	return ret
}

function htmlEncode(value){
 		return $('<div/>').text(value).html();
}

$( document ).ready(function() {
	rules_banner();		
	$(window).resize(function() {
		$('#slogan').css('top', $('#leadcard').outerHeight() + 75);
	});
	$(window).resize();
	$('#rules').click(function (evt) { document.location.href='/mg/'; } );
	$('#whale').click(function (evt) { document.location.href='https://docs.google.com/document/d/1SuEMLBbW-9uBs2dM3RIIS8Iv11LO0itRJeh_5ZxDbuw/edit?usp=sharing'; } );
	console.info('staring ws');	
	wsconnect(
		'ws://mail.scewpt.com:8080',
		sub, 
		msg 
		);
});	
