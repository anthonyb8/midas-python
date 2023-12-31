import React, { useState , useEffect} from 'react';
import { useNavigate } from 'react-router-dom';
import StrategyTable from '../components/StrategiesTable';
import { useSummaries } from '../contexts/SummariesProvider';

function StrategiesView({ onBacktestSelection }) {
  // Access state and functions from the SummariesProvider
  const { groupedSummaries } = useSummaries();
  // Initialize selectedStrategyName with the first strategy's name, or null if none exist
  const [selectedStrategyName, setSelectedStrategyName] = useState(Object.keys(groupedSummaries)[0] || null);
  // Hook for navigating programmatically
  const navigate = useNavigate();

  // Handler to navigate to the dashboard when a backtest is selected for detailed view
  const handleBacktestViewClick = (backtest) => {
    onBacktestSelection(backtest);
    navigate('/dashboard');
  };

  // Upon initial render or when groupedSummaries updates, set the first strategy as selected
  useEffect(() => {
    const firstStrategyName = Object.keys(groupedSummaries)[0];
    if (firstStrategyName) {
      setSelectedStrategyName(firstStrategyName);
    }
  }, [groupedSummaries]); 

  return (
    <div className="bg-gray-800 text-gray-300 min-h-screen p-5">
      <div className="bg-transparent border border-gray-700 rounded mx-auto my-5 mt-12 w-3/4 flex flex-col items-stretch p-2.5">
        <div className="py-2.5 px-4 font-bold border-b border-gray-700">
          {Object.keys(groupedSummaries).map(strategyName => (
            <button
              key={strategyName}
              className={`relative py-2 px-4 cursor-pointer border-none bg-transparent text-base ${selectedStrategyName === strategyName ? 'text-white' : 'text-gray-700'} outline-none`}
              onClick={() => setSelectedStrategyName(strategyName)}
            >
              {strategyName}
            </button>
          ))}
        </div>
        {selectedStrategyName && <StrategyTable strategy={groupedSummaries[selectedStrategyName]} onBacktestViewClick={handleBacktestViewClick} />}
      </div>
    </div>
  );
}
  export default StrategiesView;
  
