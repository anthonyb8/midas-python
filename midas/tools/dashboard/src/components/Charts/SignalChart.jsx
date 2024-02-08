import React, { useEffect, useRef, useState } from 'react';
import { createChart} from 'lightweight-charts';

const colors = ['white', 'gray', 'red', 'orange', 'purple', 'cyan', 'magenta'];

function getColorForTicker(ticker, index) {
    return colors[index % colors.length];
}

function convertToChartDateFormat(dateTimeString) {
  const date = new Date(dateTimeString);
  return date.toISOString().split('T')[0]; // Format time as 'YYYY-MM-DD'
}

function SignalChart({ price_data, signals_data }) {
    console.log(price_data)
    const chartContainerRef = useRef();
    const chartRef = useRef(null); // To store the chart instance
    const [legendContent, setLegendContent] = useState([]);

    useEffect(() => {
      if (chartContainerRef.current) {
          let chart;
          if (!chartRef.current) {
              // Create a new chart if it doesn't exist
              chart = createChart(chartContainerRef.current, {
                  width: 789,
                  height: 400,
                  layout: {
                      background: { type: 'solid', color: '#1e1e1e' },
                      textColor: '#ddd',
                  },
                  grid: {
                      horzLines: { color: '#444' },
                      vertLines: { color: '#444' },
                  },
                  priceScale: {
                      borderColor: '#444',
                  },
                  timeScale: {
                      borderColor: '#444',
                  },
              });
              chartRef.current = chart;
          } else {
              // Use the existing chart
              chart = chartRef.current;
          }

          // Group price_data by ticker
          const groupedByTicker = price_data.reduce((acc, item) => {
            acc[item.symbol] = acc[item.symbol] || [];
            acc[item.symbol].push(item);
            return acc;
          }, {});

          // Flatten trade_instructions and attach timestamp to each trade
          const flattenedSignals = signals_data.flatMap(signal => 
            signal.trade_instructions.map(instruction => ({
                ...instruction,
                timestamp: signal.timestamp
            }))
        );
          
          Object.keys(groupedByTicker).forEach((ticker, index) => {
            // Sort the data for each ticker by timestamp
            const sortedData = groupedByTicker[ticker]
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
                .map(item => ({
                    time: convertToChartDateFormat(item.timestamp),
                    value: parseFloat(item.close)
                }));

            // Create a series for each ticker
            const series = chart.addLineSeries({
                color: getColorForTicker(ticker, index),
                lineWidth: 2,
                priceLineVisible: false,
                lastValueVisible: false,
            });

            series.setData(sortedData);
            console.log(signals_data)
            // Filter and map flattened signals to markers
            const tickerMarkers = flattenedSignals
              .filter(signal => signal.ticker === ticker)
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
                  text: signal.direction,
              }));
          console.log(tickerMarkers)
          series.setMarkers(tickerMarkers);
      });

          setLegendContent(Object.keys(groupedByTicker).map((ticker, index) => ({
            color: getColorForTicker(ticker, index),
            ticker: ticker
          })));
      }
  }, [price_data, signals_data]);

  return (
    <div className="border rounded mx-auto my-5" style={{ width: '790px', height: '430px' }}>   
         <div className="flex flex-col h-full">
             <div className="text-darkTextColor py-1 px-2.5 border-b flex justify-between items-center">
                 <div>Signals</div>
                 <div className="flex">                     {legendContent.map((item, index) => (
                        <div key={index} className="mr-4" style={{ color: item.color }}>
                            {item.ticker}
                        </div>
                     ))}
                </div>
                </div>
          <div ref={chartContainerRef} /></div>
    </div>
  );
}

export default SignalChart;

