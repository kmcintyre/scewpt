import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.2

Item {
	property variant avis
	onAvisChanged: {
    	var avi_json = JSON.parse(avis);
    	for (var x = 0; x < avi_json.length && x < 5; x++) {
    		listView.model.append(avi_json[x])
    	}
    	console.log(avis)
    }    
    Rectangle {    	
    	y: 10
    	x: 10
    	color: 'black'
		width: 570
		height: 140     	
	    LinearGradient {
	        anchors.fill: parent
	        start: Qt.point(0, 0)
	        end: Qt.point(0, 150)
	        gradient: Gradient {
	            GradientStop { position: 0.0; color: "white" }
	            GradientStop { position: 1.0; color: "black" }
	        }
	    }
		ListView {
			id: listView
			anchors.fill: parent
			anchors.leftMargin: 20
			anchors.rightMargin: 20			
			orientation: ListView.Horizontal			
		    model: ListModel {}
		    delegate: Label {
		    	text: name
		    }
		}	 
	    		   
    }
	
}
