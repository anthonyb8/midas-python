import React from 'react';
import LineChart from '../../components/Charts/LineChart';
import SignalChart from '../../components/Charts/SignalChart';

function ChartsCollection({ equity_data, price_data, signals_data }) {
  // Extracting data for different charts
  const equityArray = equity_data.map(item => ({ time: item.timestamp, value: item.equity_value }));
  const returnArray = equity_data.map(item => ({ time: item.timestamp, value: item.percent_return }));
  const drawdownArray = equity_data.map(item => ({ time: item.timestamp, value: item.percent_drawdown }));
  equityArray.pop();
  returnArray.pop();
  drawdownArray.pop();

  return (
    <div className = "grid grid-cols-2 gap-0 m-0 py-0 bg-defaultBackground text-darkTextColor min-h-screen">
        <LineChart data={equityArray} title={'Equity'} />  {/* Equity Chart */}
        <LineChart data={returnArray} title={'Return'} />  {/* Return Chart */}
        <LineChart data={drawdownArray} title={'Drawdown'} />  {/* Drawdown Chart */}
        <SignalChart price_data={price_data} signals_data={signals_data}/> {/*Signal Chart */}
    </div>
  );
}

export default ChartsCollection;
