import React, { useState } from 'react';

function TradeTable({ trades_data }) {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = trades_data.slice(indexOfFirstItem, indexOfLastItem);

  const totalPages = Math.ceil(trades_data.length / itemsPerPage);

  const goToNextPage = () => {
    setCurrentPage(currentPage => Math.min(currentPage + 1, totalPages));
  };

  const goToPreviousPage = () => {
    setCurrentPage(currentPage => Math.max(currentPage - 1, 1));
  };

  return (
    <>
      <table className="w-full border-collapse border-spacing-0">
        <thead>
          <tr>
            <th className="py-2 px-3 border-b border-gray-700">Timestamp</th>
            <th className="py-2 px-3 border-b border-gray-700">Trade ID</th>
            <th className="py-2 px-3 border-b border-gray-700">Leg ID</th>
            <th className="py-2 px-3 border-b border-gray-700">Symbol</th>
            <th className="py-2 px-3 border-b border-gray-700">Quantity</th>
            <th className="py-2 px-3 border-b border-gray-700">Price</th>
            <th className="py-2 px-3 border-b border-gray-700">Cost</th>
            <th className="py-2 px-3 border-b border-gray-700"> Direction</th>
          </tr>
        </thead>
        <tbody>
          {currentItems.map((trade, index) => (
             <tr key={index}>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.timestamp}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.trade_id}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.leg_id}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.symbol}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.quantity}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.price}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.cost}</td>
             <td className={`py-2 px-3 ${index === currentItems.length - 1 ? 'border-b-0' : 'border-b border-gray-700'}`}>{trade.direction}</td>
           </tr>

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

export default TradeTable;
