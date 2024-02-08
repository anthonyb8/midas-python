import React from 'react';

function TableLayout({ strategy, onBacktestViewClick }) {
  
  console.log(strategy.map((summary) => (summary.symbols)))
  
  if (!strategy || strategy.length === 0) {
    return <p>No data available for this strategy.</p>;
  }

  return (
    <table className="w-full py-2">
      <thead>
        <tr>
          <th className="py-2 px-3 border-b border-gray-700 text-left">CREATED</th>
          <th className="py-2 px-3 border-b border-gray-700 text-left">SYMBOLS</th>
          <th className="py-2 px-3 border-b border-gray-700 text-left">CAPITAL</th>
          <th className="py-2 px-3 border-b border-gray-700 text-left">START</th>
          <th className="py-2 px-3 border-b border-gray-700 text-left">END</th>
          <th className="py-2 px-3 border-b border-gray-700"></th>
        </tr>
      </thead>
      <tbody>
        {strategy.map((summary) => (
          <tr key={summary.id}>
            <td className="py-2 px-3 border-b border-gray-700 text-left">{summary.created_at}</td>
            <td className="py-2 px-3 border-b border-gray-700 text-left">{summary.symbols.join(' | ')}</td>
            <td className="py-2 px-3 border-b border-gray-700 text-left">{summary.capital}</td>
            <td className="py-2 px-3 border-b border-gray-700 text-left">{summary.start_date}</td>
            <td className="py-2 px-3 border-b border-gray-700 text-left">{summary.end_date}</td>
            <td className="py-2 px-3 border-b border-gray-700 text-left">
              <button
                className="py-1.5 px-3 border border-darkBorderColor bg-darkSecondaryBg text-darkTextColor cursor-pointer text-base outline-none hover:bg-gray-700 focus:bg-gray-700 hover:text-white focus:text-white"
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
  
export default TableLayout;
  

