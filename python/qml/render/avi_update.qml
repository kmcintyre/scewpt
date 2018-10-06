import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.0

Item {
	property url current
	property bool hasprevious: false
	property url previous
	property color bgcolor
	property url font
	property string site
	property string league
	property string count
	property string twitter
	property string friends
	
	Component.onCompleted: console.log("Component Running!")
	
	FontLoader {
		id: fontAwesome
		source: 'http://maxcdn.bootstrapcdn.com/font-awesome/4.1.0/fonts/fontawesome-webfont.ttf'
	}		
	FontLoader {
		id: leagueFont
		source: font
	}	
    onCurrentChanged: {
    	current_avi.loadImage(current)
    }
    onPreviousChanged: {
    	hasprevious = true;
    	previous_avi.loadImage(previous)
    }
    onSiteChanged: {
    	site_logo.loadImage(site)
    }        
    onFriendsChanged: {
    	var friends_json = JSON.parse(friends);
    	friendtext.text = friends_json.length + ' friends' 
    	for (var x = 0; x < friends_json.length; x++) {
    		var fu = 'http://' + site + '/tw/' + friends_json[x] + '/avatar_large.png' 
    		listView.model.append( { url: fu })    	
    	}        	
    }    
    RowLayout {
    	transform: Translate { x: hasprevious ? 0 : -120 }
    	z: 2
		x: 25
		y: 15
		Item {
		    width: 200
		    height: 200
		    visible: true
		    Canvas {
		        anchors.fill: parent
		        id: previous_avi
		        antialiasing: true
		        property int corner: 4
		        onImageLoaded : requestPaint();
		        onPaint: {
		        	if (hasprevious) {
						var ctx = getContext('2d');
		        		ctx.drawImage(previous, 0, 0, previous_avi.width, previous_avi.height)		        	
		        	}
		        }
		    }
		}		    
		Rectangle {
			color: 'transparent'
			Layout.fillHeight: true			
			width: 120
			Item {
				id: site_item
				width: 120
				height: 94
			    Canvas {
			        anchors.fill: parent
			        id: site_logo
			        antialiasing: true
			        property int corner: 4
			        onImageLoaded : requestPaint();
			        onPaint: {
			        	var ctx = getContext('2d');
			        	ctx.drawImage('http://' + site + '/logo/site.png', 0, 0, site_logo.width, site_logo.height)
			        }
			    }			
			}
	        Text {
	        	anchors.topMargin: 30
	        	anchors.top: site_item.bottom
	        	anchors.horizontalCenter: parent.horizontalCenter
	            font.pointSize: 30
	            font.family: fontAwesome.name
	            text: '\uf18e'
	        }	        
		}
		Item {
		    width: 200
		    height: 200
		    visible: true
		    Canvas {
		        anchors.fill: parent
		        id: current_avi
		        antialiasing: true
		        property int corner: 4
		        onImageLoaded : requestPaint();
		        onPaint: {
		        	var ctx = getContext('2d');
		        	ctx.drawImage(current, 0, 0, current_avi.width, current_avi.height)
		        }
		    }
		}
    }
    Rectangle {
    	y: 230
    	x: -2
    	width: 594
    	height: 40
    	z: 2
    	border.color: 'black'
    	border.width: 2
    	Label {
    		transform: Translate { 
    			x: twitter.length * 4 
    		}
    		id: label
    		anchors.top: parent.top
        	anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 20
            font.family: leagueFont.name
            text: 'AVI #' + count + ' @' + twitter + ' '
            color: 'black'
	    }
        Text {
        	transform: Translate { 
        		y: -3
        		x: twitter.length * 4 
        	}
        	anchors.left: label.right        	
            font.pointSize: 30
            color: '#0084b4'
            font.family: fontAwesome.name
            text: '\uf099'
        }	    
    }
    Rectangle {
    	transform: Translate { y: -35 }
    	z: 3
    	y: 270
    	x: 3
    	height: 30
    	width: 120
    	border.color: 'transparent'
    	border.width: 5
    	radius: 10
    	visible: friends ? true: false
    	color: 'black'
    	Label {
    		transform: Translate { y: 2 }
    		id: friendtext
    		anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 14
            font.family: leagueFont.name
            color: 'white'
	    }    	
    }
    Rectangle {
    	z: 1
    	y: 100
    	color: bgcolor
		width: 590
		height: 280     	
	    LinearGradient {
	        anchors.fill: parent
	        start: Qt.point(0, 0)
	        end: Qt.point(0, 280)
	        gradient: Gradient {
	            GradientStop { position: 0.0; color: 'white' }
	            GradientStop { position: 1.0; color: bgcolor }
	        }
	    }	 	    		   
    }
    Rectangle {
    	z: 2
    	y: 270
    	height: 110
    	width: 590
    	color: 'transparent'
	    ListView {
			id: listView
			anchors.fill: parent
			anchors.topMargin: 5
			anchors.bottomMargin: 5			
			orientation: ListView.Horizontal			
		    model: ListModel {}
		    delegate: ColumnLayout {
		    	Item {
		    		width:110
		    		height:100
					Canvas {
			    		anchors.fill: parent
				        onImageLoaded : requestPaint();
				        onPaint: {		        	
				        	var ctx = getContext('2d');
				        	ctx.drawImage(url, 5, 0, 105, 100);
				        }
						Component.onCompleted: {
							loadImage(url);        	
						}
				    }	    		
		    	}
		    }
		}    	
    }
	
}
