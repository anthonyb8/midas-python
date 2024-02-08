import React, { useState } from 'react';

function SignalsTable({ signals_data }) {
  console.log(signals_data)
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = signals_data.slice(indexOfFirstItem, indexOfLastItem);

  const totalPages = Math.ceil(signals_data.length / itemsPerPage);

  const goToNextPage = () => {
    setCurrentPage(currentPage => Math.min(currentPage + 1, totalPages));
  };

  const goToPreviousPage = () => {
    setCurrentPage(currentPage => Math.max(currentPage - 1, 1));
  };

  return (
    <>
      <table className="w-full border-collapse border-spacing-0">
        {/* Note: Custom CSS may be needed for border-collapse and border-spacing */}
        <thead>
          <tr>
            <th className="py-2 px-3 border-b border-gray-700">Timestamp</th>
            {/* <th className="py-2 px-3 border-b border-gray-700">Trade ID</th> */}
            <th className="py-2 px-3 border-b border-gray-700">Leg ID</th>
            <th className="py-2 px-3 border-b border-gray-700">Symbol</th>
            {/* <th className="py-2 px-3 border-b border-gray-700">Price</th> */}
            <th className="py-2 px-3 border-b border-gray-700">Direction</th>
            <th className="py-2 px-3 border-b border-gray-700">Trade Allocation</th>
          </tr>
        </thead>
        <tbody>
        {currentItems.map((trade, index) => (
          <React.Fragment key={index}>
            {trade.trade_instructions.map((instruction, idx) => (
              <tr key={idx}>
                {idx === 0 && (
                  <td rowSpan={trade.trade_instructions.length} className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>
                    {trade.timestamp}
                  </td>
                )}
                <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{instruction.leg_id}</td>
                <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{instruction.ticker}</td>
                <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{instruction.direction}</td>
                <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{instruction.allocation_percent}</td>
              </tr>
            ))}
          </React.Fragment>
        ))}

        </tbody>
      </table>
      <div className="flex justify-end mt-2.5">
        <button className="ml-1.5" onClick={goToPreviousPage} disabled={currentPage === 1}>&lt;</button>
        <button className="ml-1.5" onClick={goToNextPage} disabled={currentPage === totalPages}>&gt;</button>
      </div>
    </>
  );
  
}
export default SignalsTable;