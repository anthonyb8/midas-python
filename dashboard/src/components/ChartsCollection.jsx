import React from 'react';
import LineChart from './LineChart';
import SignalChart from './SignalChart';

function ChartsCollection({ equity_data, price_data, signals_data }) {
  // Extracting data for different charts
  const equityArray = equity_data.map(item => ({ x: item.timestamp, y: item.equity_value }));
  const returnArray = equity_data.map(item => ({ x: item.timestamp, y: item.percent_return }));
  const drawdownArray = equity_data.map(item => ({ x: item.timestamp, y: item.percent_drawdown }));

  // Preparing data for LineChart component
  const equityChartData = [{ 
    x: equityArray.map(item => item.x),
    y: equityArray.map(item => item.y),
    type: 'scatter',
    mode: 'lines+markers',
    marker: { color: 'blue' },
  }];

  const returnChartData = [{ 
    x: returnArray.map(item => item.x),
    y: returnArray.map(item => item.y),
    type: 'scatter',
    mode: 'lines+markers',
    marker: { color: 'green' },
  }];

  const drawdownChartData = [{ 
    x: drawdownArray.map(item => item.x),
    y: drawdownArray.map(item => item.y),
    type: 'scatter',
    mode: 'lines+markers',
    marker: { color: 'red' },
  }];

  return (
    <div className = "grid grid-cols-2 gap-5 dark:bg-darkBackground text-gray-300 min-h-screen">
        <LineChart data={equityChartData} layout={{ xaxis: { title: 'Timestamp' }, yaxis: {title:"Equity Value"} }} />  {/* Equity Chart */}
        <LineChart data={returnChartData} layout={{ xaxis: { title: 'Timestamp' }, yaxis: {title:"Percent Return"} }} />   {/* Return Chart */}
        <LineChart data={drawdownChartData} layout={{ xaxis: { title: 'Timestamp' }, yaxis: {title:"Percent Drawdown"} }} />  {/* Drawdown Chart */}
        <SignalChart price_data={price_data} signals_data={signals_data}/> {/* Signal Chart */}
    </div>
  );
}

export default ChartsCollection;
