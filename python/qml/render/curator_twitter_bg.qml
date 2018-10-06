import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.0

Rectangle {
	id: profile
	width: 1500
	height: 500
	color: "transparent"
	property var bgcolor
	property var curator
	property var leagues
	property var players
	
	FontLoader {
        id: fontAwesome
        source: 'http://maxcdn.bootstrapcdn.com/font-awesome/4.1.0/fonts/fontawesome-webfont.ttf'
    }
    
    FontLoader {
    	source: 'http://dev.athleets.com/polymer/font/Roboto-Regular.ttf?raw=true'
    	id: roboto
    }
    		
	onLeaguesChanged: {
		for (var x = 0; x < leagues.length; x++) {
			pathView.model.append(leagues[x]);
		}						
	}	
	onPlayersChanged: {
		while ( gridView.model.count < 500 ) {
			for (var x = 0; x < players.length; x++) {
				gridView.model.append(players[x])
			}
		}							
	}

    Component {
        id: pathDelegate
        Column {
        	z: -index + 1000
            id: wrapper
            width: 105 
            height: 105
            Image {
            	id: image
            	visible: false
            	width: 105
            	height: 105                
                source: {
                	large_url
                }
            }
		    Glow {
		        anchors.fill: image
		        radius: 8
		        samples: 17
		        color: "black"
		        source: image		        
		    }   
		    transform: Rotation { 
		    	angle: index
		    }               
        }
    }
    
    GridView {
    	z:-1
    	opacity: 0.5
    	id: gridView
    	y: 2
    	x: 2
    	width: 1500
    	height: 500
    	cellHeight: 50
		cellWidth: 50
		model: ListModel {
			
		}
    	delegate: Image {
			width: 48
			height: 48 
			source: {
				small_url				
			}     		
    	}
	}
    
	PathView {
		z:1
		id: pathView
		visible: false
        anchors.fill: parent
        model: ListModel {}
        delegate: pathDelegate
        path: Path {
            startX: 120; startY: 295                
		    PathArc {
        		x: 1410; y: 295
        		radiusX: 855; radiusY: 310
        		useLargeArc: false
    		}		    
        }
    }
    
    DropShadow {
        anchors.fill: pathView
        horizontalOffset: 3
        verticalOffset: 6
        radius: 8.0
        samples: 17
        color: "#80000000"
        source: pathView
	    transform: Rotation { 
	    	angle: -3
	    }                               
    }
    
    Rectangle {    	
    	visible: {
    		return typeof profile.curator !== 'undefined';
    	}
    	color: "white"
    	height: android.height + 3
    	width: {
    		domain.contentWidth + android.contentWidth + apple.contentWidth + 37
    	}
    	anchors.right: parent.right
    	y: 352
		Text {
			id: android
	    	anchors.right: parent.right    	
	        font.pointSize: 30
	        font.family: fontAwesome.name
	        color: '#A4C639'
	        text: '\uf17b'
	        rightPadding: 10
		}
		Text {
			id: apple
	    	anchors.right: android.left
	        font.pointSize: 30
	        font.family: fontAwesome.name
	        text: '\uf179'
	        rightPadding: 10
		}
		Text {
			id: domain
	    	anchors.right: apple.left
	        font.pointSize: 40
	        font.family: roboto.name
	        text: profile.curator.role
	        rightPadding: 10
	        y: -15
	        color: profile.bgcolor
	        font.capitalization: Font.SmallCaps
		}	
		    	
    }    
	        
}