import QtCharts 2.2
import QtQuick 2.7
import QtQuick.Controls 1.4

Rectangle {
    id: rectangle
    width: 800
	height: _height
	property var categories
	property var _height
	property var title
	property var tweets
	property var retweets
	property var unknown_retweets	
    property var conversations
    property var description
    property var padding: 50
    color: "#000000"

    FontLoader {
        id: fontAwesome
        source: 'http://maxcdn.bootstrapcdn.com/font-awesome/4.1.0/fonts/fontawesome-webfont.ttf'
    }
    onTweetsChanged: {
    	hbar.axisX.min = 0    	
    	hbar.axisX.max = 0
        for (var x = 0; x < unknown_retweets.length; x++ ) {
            if ( hbar.axisX.max < unknown_retweets[x] + padding) {            	
                hbar.axisX.max = unknown_retweets[x] + padding
                console.log('increase max retweet:', hbar.axisX.max) 
            }
        }
        for (var x = 0; x < tweets.length; x++ ) {
            if ( hbar.axisX.max < tweets[x] + padding) {
                hbar.axisX.max = tweets[x] + padding
                console.log('increase max tweet:', hbar.axisX.max)
            }
        }
        hbar.axisX.labelFormat = '%i'
    }
	ChartView {
        backgroundRoundness: 10
		id: chart
        title: rectangle.title
        titleFont.family: "Arial"
        titleFont.pointSize: 16
        anchors.topMargin: 50
        height: parent.height - 30
        width: parent.width
	    legend.alignment: Qt.AlignBottom
	    antialiasing: true

	    HorizontalBarSeries {
            id: hbar
            axisY: BarCategoryAxis {
                categories: rectangle.categories
            }
            BarSet {
                color: "#e2264d"
                label: "Conversations"
                values: rectangle.conversations
            }            
            BarSet {
	        	color: "#19cf86"
                label: "Known Retweets"
                values: rectangle.retweets
	        }
            BarSet {
	        	color: "#ffd700"
                label: "Unknown Retweets"
                values: rectangle.unknown_retweets
	        }	        
	        BarSet { 
	        	color: "#1B95E0"
	        	label: "Tweets" 
                values: rectangle.tweets
            }
	    }
	}
    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: parent.height - chart.height
        color: "transparent"
        Label {
            anchors.centerIn: parent
            font.family: "Arial"
            font.pixelSize: 18
            color: "#FFFFFF"
            text: rectangle.description
        }
    }
}
