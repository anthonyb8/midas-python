import React from 'react';

function StrategiesTable({ strategy, onBacktestViewClick }) {
  // If the 'strategy' prop is not provided or is an empty array, render a message indicating no data.
  if (!strategy || strategy.length === 0) {
    return <p>No data available for this strategy.</p>;
  }

  return (
    <table className="w-full">
      <thead>
        <tr>
          <th className="py-2 px-3 border-b border-gray-700">Name</th>
          <th className="py-2 px-3 border-b border-gray-700">Parameters</th>
          <th className="py-2 px-3 border-b border-gray-700">Created</th>
          <th className="py-2 px-3 border-b border-gray-700">Action</th>
        </tr>
      </thead>
      <tbody>
        {strategy.map((summary) => (
          <tr key={summary.id}>
            <td className="py-2 px-3 border-b border-gray-700">{summary.strategy_name}</td>
            <td className="py-2 px-3 border-b border-gray-700">{summary.parameters}</td>
            <td className="py-2 px-3 border-b border-gray-700">{summary.date_of_backtest}</td>
            <td className="py-2 px-3 border-b border-gray-700">
              <button
                className="py-1.5 px-3 border border-gray-600 bg-transparent text-gray-600 cursor-pointer text-base outline-none hover:bg-gray-700 focus:bg-gray-700 hover:text-white focus:text-white"
                onClick={() => onBacktestViewClick(summary.id)}
              >
                View
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
  
export default StrategiesTable;
  

