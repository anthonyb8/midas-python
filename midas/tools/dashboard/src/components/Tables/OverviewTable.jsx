import React from 'react';

function transformOverviewData(overviewData) {
  
  const transformedData = [];
  const keys = Object.keys(overviewData[0]);

  // Iterate over the keys in pairs
  for (let i = 0; i < keys.length; i += 2) {
    const key1 = keys[i];
    const value1 = overviewData[0][key1];
    const key2 = keys[i + 1] || '';
    const value2 = key2 ? overviewData[0][key2] : '';

    const row = {
      key1: key1,
      value1: value1,
      key2: key2,
      value2: value2
    };
    transformedData.push(row);
  }

  return transformedData;
}


function OverviewTable({overview_data}) {
  const data = transformOverviewData(overview_data);

  return (
    <table className="w-full bg-darkSecondaryBg">
      <tbody>
        {data.map((row, index) => (
          <tr key={index}>
            <td className={`py-2 px-3 uppercase ${index === data.length - 1 ? 'border-b-0' : 'border-b border-opacity-10'}`}>{row.key1.replace(/_/g," ")}</td>
            <td className={`py-2 px-3 ${index === data.length - 1 ? 'border-b-0' : 'border-b border-opacity-10'}`}>{row.value1}</td>
            <td className={`py-2 px-3 uppercase ${index === data.length - 1 ? 'border-b-0' : 'border-b border-opacity-10'}`}>{row.key2.replace(/_/g, " ")}</td>
            <td className={`py-2 px-3 ${index === data.length - 1 ? 'border-b-0' : 'border-b border-opacity-100'}`}>{row.value2}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
  
}

export default OverviewTable;

