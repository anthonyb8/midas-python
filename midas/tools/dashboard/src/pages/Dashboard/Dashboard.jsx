import React, { useEffect, useState, useContext } from 'react';
import ChartsCollection from './ChartsCollection';
import TablesCollection from './TablesCollection';
import ParametersBar from '../../components/ParametersBar';
import { BacktestContext } from '../../contexts/BacktestContext';

function Dashboard() {
  const [loading, setLoading] = useState(false);
  const {
    getBacktest,
    removeBacktest,
    backtestsCache, // Assuming this is added to your context
    currentBacktestId,
    setCurrentBacktest
  } = useContext(BacktestContext);

  useEffect(() => {
    const loadBacktestData = async () => {
      if (currentBacktestId && !backtestsCache[currentBacktestId]) {
        setLoading(true);
        await getBacktest(currentBacktestId);
        setLoading(false);
      }
    };

    loadBacktestData();
  }, [currentBacktestId, getBacktest, backtestsCache]);

  const handleTabClick = (id) => {
    setCurrentBacktest(id);
  };

  const renderContent = () => {
    if (loading) return <p>Loading...</p>;
    if (!currentBacktestId) return <p>Please select a backtest to view its details.</p>;

    const backtestData = backtestsCache[currentBacktestId];
    
    if (!backtestData) {
      return <p>No data available for this backtest.</p>;
    }else {
      return (
        <>
        <div className="flex border-darkBorderColor">
        {Object.keys(backtestsCache).map((id) => (
          <div
            key={id}
            className={`py-2.5 px-5 cursor-pointer border ${+currentBacktestId === +id ? 'text-gray-300 bg-darkSecondaryBg' : 'text-gray-600 bg-darkBackground'} rounded-tl-md rounded-tr-md mr-0.5 text-sm`}
            onClick={() => handleTabClick(id)}
          >
            Backtest {id}
            <button
              className="bg-transparent border-none text-gray-200 cursor-pointer text-base p-0 ml-2.5 hover:text-white"
              onClick={(e) => {
                e.stopPropagation(); // Prevent click from affecting the tab itself
                removeBacktest(id);
              }}
            >
              x
            </button>
          </div>
        ))}
      </div>
      <div className="py-2.5 px-5 bg-darkSecondaryBg cursor-pointer border border-b-0 rounded-tl-md rounded-tr-md mr-0.5 text-sm">
        <h1 className="text-gray-300 uppercase text-left text-2xl mb-5">{backtestData.parameters.strategy_name}</h1>
        <ParametersBar parameters={backtestData.parameters}/>
        <ChartsCollection equity_data={backtestData.equity_data} price_data={backtestData.price_data} signals_data={backtestData.signals}/>
        <TablesCollection overview_data={backtestData.summary_stats} trades_data ={backtestData.trades} signals_data={backtestData.signals}/>
      </div>
        
    </>
    );
    } 
  };
  
  return (
    <div className="bg-darkBackground text-darkTextColor min-h-screen p-5">
        {renderContent()}
    </div>
  );
  
  }
export default Dashboard;
