import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.0

Rectangle {
	id: profile
	width: 400
	height: 400
	color: "transparent"
	property var league
	property var cards
	property var backup: false
	
	FontLoader {
        id: fontAwesome
        source: 'http://maxcdn.bootstrapcdn.com/font-awesome/4.1.0/fonts/fontawesome-webfont.ttf'
    }
    
	onCardsChanged: {
		var hw = cards.length/2;
		for (var x = 0; x < cards.length; x++) {
			if ( x < hw ) {
				pathView.model.append(cards[x]);
			} else {
				pathView2.model.append(cards[x]);
			}
			
		}						
	}
	
    Rectangle {
    	x: 5
    	y: 5
    	width: 30
    	height: 30
    	color: "black"
    	id: bk
    	radius: 15
    	visible: backup
    	Text {
    		font.pointSize: 12
    		color: "white"
    		anchors.centerIn: parent
    		text: "BK"
    	}
    }	
    
    Image {
    	anchors.centerIn: parent
    	width: 280
    	height: 200
    	sourceSize.width: width
		sourceSize.height: height
    	source: 'http://' + league.site + '/' + league.league + '/logo_standard/' + league.league + '.svg'
    }  
    
    Component {
        id: pathDelegate
        Column {
            width: 50 
            height: width * .968
            Image {
            	id: image
            	anchors.fill: parent
                source: {
                	'http://' + site + '/' + league  + '/card/' + twitter + '.png'
                }
            }
        }
    }    
    
    PathView {
		id: pathView
        anchors.fill: parent
        model: ListModel {}
        delegate: pathDelegate
        path: Path {
            startX: 50; startY: 80                
		    PathArc {
        		x: 350; y: 80
        		radiusX: 200; radiusY: 130
        		useLargeArc: false
    		}		    
        }
    }    

    PathView {
		id: pathView2
        anchors.fill: parent
        model: ListModel {}
        delegate: pathDelegate
        path: Path {
            startX: 340; startY: 320                
		    PathArc {
        		x: 40; y: 320
        		radiusX: 200; radiusY: 150
        		useLargeArc: false
    		}		    
        }
    }    
	        
}