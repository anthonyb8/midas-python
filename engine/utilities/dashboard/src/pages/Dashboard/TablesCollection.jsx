import React, { useState } from 'react';
import OverviewTable from '../../components/Tables/OverviewTable';
import TradeTable from '../../components/Tables/TradeTable';
import SignalsTable from '../../components/Tables/SignalsTable';

function TablesCollection({overview_data, trades_data, signals_data}) {
  const [selectedTable, setSelectedTable] = useState('overview');

  return (
    <div className="text-darkTextColor border-darkBorder rounded mx-auto my-5 w-3/4 flex flex-col items-stretch p-2.5">
      <div className="py-2.5 px-4 font-bold border-b ">
        <button className="relative py-2 px-4 cursor-pointer border-none bg-darkSecondaryBg text-base " onClick={() => setSelectedTable('overview')}>Overview</button>
        <button className="relative py-2 px-4 cursor-pointer border-none bg-transparent text-base " onClick={() => setSelectedTable('trades')}>Trades</button>
        <button className="relative py-2 px-4 cursor-pointer border-none bg-transparent text-base " onClick={() => setSelectedTable('signals')}>Signals</button>
      </div>

      {selectedTable === 'overview' && <OverviewTable overview_data={overview_data}/>}
      {selectedTable === 'trades' && <TradeTable trades_data={trades_data} />}
      {selectedTable === 'signals' && <SignalsTable signals_data={signals_data} />} 
    </div>
  );
}

export default TablesCollection;