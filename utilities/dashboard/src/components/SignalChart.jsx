import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const colors = ['white', 'gray', 'red', 'orange', 'purple', 'cyan', 'magenta'];

function getColorForTicker(ticker, index) {
    return colors[index % colors.length];
}

function convertToChartDateFormat(dateTimeString) {
    const date = new Date(dateTimeString);
    return { year: date.getFullYear(), month: date.getMonth() + 1, day: date.getDate() };
}

function SignalChart({ price_data, signals_data }) {
    const chartContainerRef = useRef();
    const [legendContent, setLegendContent] = useState([]);

    useEffect(() => {
      if (chartContainerRef.current) {
        const chart = createChart(chartContainerRef.current, {
          height:400,
          width:600,
          rightPriceScale: {
            visible: true,
            borderColor: '#444',
          },
          leftPriceScale: {
            visible: true,
            borderColor: '#444',
          },
          layout: {
            background: {
                    type: 'solid',
                    color: '#1e1e1e',
                },
            textColor: '#eee',
          },
          grid: {
            horzLines: {
              color: '#444',
            },
            vertLines: {
              color: 'transparent',
            },
          },
          timeScale: {
            borderColor: '#444',
          },
          handleScroll: {
            vertTouchDrag: false,
          },
        });

        // Group price_data by ticker and create a series for each
        const groupedByTicker = price_data.reduce((acc, item) => {
          acc[item.ticker] = acc[item.ticker] || [];
          acc[item.ticker].push(item);
          return acc;
        }, {});

        Object.keys(groupedByTicker).forEach((ticker, index) => {
          const series = chart.addLineSeries({ 
            title: [],
            color: getColorForTicker(ticker, index),
            lastValueVisible: false});
          series.setData(groupedByTicker[ticker]
              .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
              .map(item => ({
                time: convertToChartDateFormat(item.timestamp), 
                value: item.close 
              }))
            );

            // Set markers for this specific series
            const tickerMarkers = signals_data
                .filter(signal => signal.ticker === ticker) // Filter signals for this ticker
                .map(signal => ({
                    time: convertToChartDateFormat(signal.timestamp),
                    position: 'aboveBar',
                    lineWidth: 1,
                    color: signal.direction === 'LONG' ? 'green' :
                            signal.direction === 'SHORT' ? 'red' :
                            signal.direction === 'SELL' ? 'green' : 
                            signal.direction === 'COVER' ? 'red' :
                            'yellow', 
                    shape: signal.direction === 'LONG' ? 'arrowUp' :
                            signal.direction === 'SHORT' ? 'arrowDown' :
                            signal.direction === 'SELL' ? 'arrowDown' : 
                            signal.direction === 'COVER' ? 'arrowUp' :
                            'circle',
                    // text: signal.direction,

                  }));

                  series.setMarkers(tickerMarkers);
              });

        const newLegendContent = Object.keys(groupedByTicker).map((ticker, index) => ({
          color: getColorForTicker(ticker, index),
          ticker: ticker
        }));
        
        setLegendContent(newLegendContent);
        }
    }, [price_data, signals_data]);
      
    return (
      <div className="bg-gray-800 border border-gray-700 rounded mx-auto my-5" style={{ width: '600px', height: '400px' }}>
          <div className="text-gray-300 py-1 px-2.5 border-b border-gray-700">Test</div>
          <div >
              {legendContent.map((item, index) => (
                  <div key={index} style={{ color: item.color }}>
                      {item.ticker}
                  </div>
              ))}
          </div>
          <div ref={chartContainerRef} />
      </div>
  );
}


export default SignalChart;



