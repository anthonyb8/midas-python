import React from 'react';

function PerformanceBar({ values }) { 
  
  const itemsToShow = {
    'Ending Equity': values[0].ending_equity || 'N/A',
    'Total Fees': values[0].total_fees || 'N/A',
    'Net Profit': values[0].net_profit || 'N/A',
    'Total Return': values[0].total_return || 'N/A',
    'Total Trades': values[0].total_trades || 'N/A',
  };

  return (
    <div className="flex items-center border-t border-b border-darkBorderColor justify-between px-2.5">
      {Object.entries(itemsToShow).map(([name, value], index) => (
        <div key={index} className="flex flex-col items-center py-2.5 mx-1.5">
          <div className={`text-xl font-bold ${value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {value}
          </div>
          <div className="mt-1.5 text-sm">{name}</div>
        </div>
      ))}
    </div>
  );
};

export default PerformanceBar;

