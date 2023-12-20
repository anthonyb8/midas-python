import React, { useEffect, useState } from 'react';
import { useBacktests } from '../contexts/BacktestsProvider';
import ChartsCollection from '../components/ChartsCollection';
import TablesCollection from '../components/TablesCollection'
import PerformanceBar from '../components/PerformanceBar';

function Dashboard({ backtests, removeBacktest }) {
  const { getBacktest } = useBacktests();
  const [backtestData, setBacktestData] = useState({});
  const [selectedBacktestId, setSelectedBacktestId] = useState(backtests[0]);
  const [loading, setLoading] = useState(true);
  const [isSynced, setIsSynced] = useState(false); 
  
  useEffect(() => {
    const fetchBacktestData = async () => {
      setLoading(true);
      try {
        const data = await Promise.all(backtests.map(id => getBacktest(id)));
        const newBacktestData = Object.fromEntries(data.map((d, index) => [backtests[index], d]));
        setBacktestData(newBacktestData);

        // Update the selected backtest id and mark as synced in a single operation
        if (backtests.length > 0) {
          setSelectedBacktestId(backtests[backtests.length - 1]);
          setIsSynced(true); // Set this to true only after the data has been fetched and state updated
        }
      } catch (error) {
        console.error('Error fetching backtest data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    setIsSynced(false); // Set this to false before attempting to fetch new data
    if (backtests.length > 0) {
      fetchBacktestData();
    }
  }, [backtests, getBacktest]);

  const handleTabClick = (backtestId) => {
    setIsSynced(false); // Before making changes, set isSynced to false
    setSelectedBacktestId(backtestId);
    setIsSynced(true); // After changes, set isSynced to true
  };
  
  const handleRemoveBacktest = (backtestId) => {
    // Remove the backtest
    removeBacktest(backtestId);
  
    // Proceed only if the closed backtest is the currently selected one
    if (selectedBacktestId === backtestId) {
      const remainingBacktests = backtests.filter(id => id !== backtestId);
      let newSelectedId = null;
  
      if (remainingBacktests.length > 0) {
        const index = backtests.indexOf(backtestId);
        // If there is a tab to the left, select it; otherwise, select the tab to the right
        if (index > 0) {
          newSelectedId = backtests[index - 1];
        } else {
          // This will select the tab that now occupies the closed tab's previous position
          newSelectedId = remainingBacktests[0];
        }
      }
  
      setSelectedBacktestId(newSelectedId);
    }
  };
  
  // Instead of rendering the loading message immediately, we keep the UI stable
  // until the new data is ready and synced.
  const content = () => {
    if (!backtests.length) {
      return <p>No backtests selected. Please select a backtest to view detailed information.</p>;
    }

    if (loading) {
      // Render the loading state only initially, not during tab switches
      return <p>Loading...</p>;
    }

    if (selectedBacktestId && backtestData[selectedBacktestId]) {
      // Render the actual content
      // ...
    } else {
      return <p>Please select a backtest to view its details.</p>;
    }
  };
  
  return (
    <div className="bg-gray-800 text-gray-300 min-h-screen p-5">
      <div className="flex border-b border-gray-600 mb-5 mt-7">
        {backtests.map((id) => (
          <div
            key={id}
            className={`py-2.5 px-5 cursor-pointer border border-gray-600 border-b-0 bg-gray-900 ${selectedBacktestId === id ? 'text-gray-300' : 'text-gray-600'} rounded-tl-md rounded-tr-md mr-0.5 text-sm`}
            onClick={() => handleTabClick(id)}
          >
            Backtest {id}
            <button
              className="bg-transparent border-none text-gray-200 cursor-pointer text-base p-0 ml-2.5 hover:text-white"
              onClick={(e) => {
                e.stopPropagation(); // Prevent click from affecting the tab itself
                handleRemoveBacktest(id);
              }}
            >
              x
            </button>
          </div>
        ))}
      </div>
      <div className="py-2.5 px-5 cursor-pointer border border-gray-600 border-b-0 bg-gray-900 text-gray-600 rounded-tl-md rounded-tr-md mr-0.5 text-sm">
        {selectedBacktestId && backtestData[selectedBacktestId] ? (
          <>
            <h1 className="text-gray-300 text-center text-2xl mb-5">Dashboard - {backtestData[selectedBacktestId].strategy_name}</h1>
            <h3 className="text-gray-300 text-center mb-5">({backtestData[selectedBacktestId].parameters})</h3>
            <PerformanceBar values={backtestData[selectedBacktestId].summary_stats}/>
            <ChartsCollection equity_data={backtestData[selectedBacktestId].equity_data} price_data={backtestData[selectedBacktestId].price_data} signals_data={backtestData[selectedBacktestId].signals}/>
            <TablesCollection overview_data={backtestData[selectedBacktestId].summary_stats} trades_data ={backtestData[selectedBacktestId].trades} signals_data={backtestData[selectedBacktestId].signals}/>
          </>
        ) : (
          <p>Please select a backtest to view its details.</p>
        )}
      </div>
      <div className="py-2.5 px-5 cursor-pointer border border-gray-600 border-b-0 bg-gray-900 text-gray-600 rounded-tl-md rounded-tr-md mr-0.5 text-sm">
        {content()}
      </div>
    </div>
  );
  
}


export default Dashboard;
