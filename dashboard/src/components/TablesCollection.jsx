import React, { useState } from 'react';
import OverviewTable from './OverviewTable';
import TradeTable from './TradeTable';
import SignalsTable from './SignalsTable';

function TablesCollection({overview_data, trades_data, signals_data}) {
  const [selectedTable, setSelectedTable] = useState('overview');

  return (
    <div className="bg-transparent border border-gray-700 rounded mx-auto my-5 w-3/4 flex flex-col items-stretch p-2.5">
      <div className="py-2.5 px-4 font-bold border-b border-gray-700">
        <button className="relative py-2 px-4 cursor-pointer border-none bg-transparent text-base text-gray-700" onClick={() => setSelectedTable('overview')}>Overview</button>
        <button className="relative py-2 px-4 cursor-pointer border-none bg-transparent text-base text-gray-700" onClick={() => setSelectedTable('trades')}>Trades</button>
        <button className="relative py-2 px-4 cursor-pointer border-none bg-transparent text-base text-gray-700" onClick={() => setSelectedTable('signals')}>Signals</button>
      </div>

      {selectedTable === 'overview' && <OverviewTable overview_data={overview_data}/>}
      {selectedTable === 'trades' && <TradeTable trades_data={trades_data} />}
      {selectedTable === 'signals' && <SignalsTable signals_data={signals_data} />} 
    </div>
  );
}

export default TablesCollection;