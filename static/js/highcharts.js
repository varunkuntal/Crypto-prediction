
var chartdata = []
var volume = []

function processData(data)
{
	var data = data.res;
	for (var i=0; i < data.length; i++)
	{
		chartdata.push([
			data[i][0], // the date
			data[i][1], // open
			data[i][2], // high
			data[i][3], // low
			data[i][4] // close
		]);
		volume.push([
			data[i][0], // the date
			data[i][5] // the volume
		]);
	}
}


function plotCharts(){
	Highcharts.stockChart('container', {
		accessibility: {
    enabled: false
  },

		yAxis: [{
			labels: {
				align: 'center'
			},
			height: '80%', 
			resize: {
        enabled: true
      }
		}, 
		{
			labels: {
				align: 'left'
			},
			top: '80%',
			height: '20%',
			offset: 0
		}],
		tooltip: {
      shape: 'square',
      headerShape: 'callout',
      borderWidth: 0,
      shadow: false,
      positioner: function (width, height, point) {
        var chart = this.chart,
          position;

        if (point.isHeader) {
          position = {
            x: Math.max(
              // Left side limit
              chart.plotLeft,
              Math.min(
                point.plotX + chart.plotLeft - width / 2,
                // Right side limit
                chart.chartWidth - width - chart.marginRight
              )
            ),
            y: point.plotY
          };
        } else {
          position = {
            x: point.series.chart.plotLeft,
            y: point.series.yAxis.top - chart.plotTop
          };
        }

        return position;
      }
    },
		series: [{
			type: 'ohlc',
			id: 'ETH-USD',
			name: 'ETH-USD',
			data: chartdata
		}, {
			type: 'column',
			id: 'ETH-USD',
			name: 'ETH-USD Volume',
			data: volume,
			yAxis: 1
		}],
		responsive: {
		  rules: [{
			condition: {
			  maxWidth: 800
			},
			chartOptions: {
			  rangeSelector: {
				inputEnabled: false
			  }
			}
		  }]
		}
	});


}



$( document ).ready(function()
{
	$.getJSON('/pipe', function(data){
		processData(data);
		plotCharts();
	});
});
 
