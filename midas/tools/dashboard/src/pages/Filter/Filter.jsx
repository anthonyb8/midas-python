import React, { useState , useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import TableLayout from './TableLayout';
import { BacktestContext } from '../../contexts/BacktestContext';


function FitlerView() {
  const [isLoading, setIsLoading] = useState(true);
  const authToken = sessionStorage.getItem('token');
  const [groupedSummaries, setGroupedSummaries] = useState({}); 
  const [selectedStrategyName, setSelectedStrategyName] = useState(Object.keys(groupedSummaries)[0] || null);
  const {setCurrentBacktest} = useContext(BacktestContext);
  const navigate = useNavigate();

  const groupSummariesByStrategy = (summaries) => {
    return summaries.reduce((acc, summary) => {
        // Initialize a group for each strategy name if it doesn't exist
        if (!acc[summary.strategy_name]) {
            acc[summary.strategy_name] = [];
        }

        // Parse summary parameters and keep the rest of the summary unchanged
        const parsedParameters = summary.parameters ? JSON.parse(summary.parameters) : null;
        const updatedSummary = { ...summary, parameters: parsedParameters };

        // Append the updated summary to its group
        acc[summary.strategy_name].push(updatedSummary);
        return acc;
    }, {});
  };

  const handleBacktestViewClick = (backtestId) => {
    setCurrentBacktest(backtestId); // Use the context to set the current backtest ID
    navigate('/dashboard');
  };

  // Fetch summaries data from the API and group it by strategy when component mounts or summaries change
  useEffect(() => {
    const fetchSummaries = async () => {
      setIsLoading(true); // Start loading state
      try {
        console.log(authToken)
        const response = await api.get('/api/backtest',{
          headers: {
            'Authorization': `Token ${authToken}`
          }
        }); 
        console.log(response)
  
        if (response.status === 200) {
          // setSummaries(response.data); // Save fetched data
          const grouped = groupSummariesByStrategy(response.data); // Group fetched data by strategy

          sessionStorage.setItem('groupedSummaries', JSON.stringify(grouped));
          setGroupedSummaries(grouped); // Save grouped data

          const strategies = Object.keys(grouped);
          setSelectedStrategyName(strategies[0]) 
          
          setIsLoading(false);
        } else {
          console.error('Error fetching summaries:', response.error); // Log any errors from the response
        }
      } catch (error) {
        console.error('Error fetching summaries:', error); // Log errors from the fetching process
      } finally {
        setIsLoading(false); // End loading state
      }
    };

    // Check that summaries where returned from the API
    const storedSummaries = sessionStorage.getItem('groupedSummaries');
    if (storedSummaries) {
      const parsedSummaries = JSON.parse(storedSummaries);
      setGroupedSummaries(parsedSummaries);
      
      const strategies = Object.keys(parsedSummaries);
      setSelectedStrategyName(strategies[0]);

      setIsLoading(false);
    } else {
      fetchSummaries();
    } 
    
  }, [authToken]); 

  return (
    <div className="bg-darkBackground text-darkTextColor min-h-screen p-5">
      <div className="border border-darkBorderColor rounded mx-auto my-5 mt-12 w-3/4 flex flex-col items-stretch p-2.5">
        <div className="py-2.5 px-4 font-bold border-b border-darkBorderColor">
          {Object.keys(groupedSummaries).map(strategyName => (
            <button
              key={strategyName}
              className={`relative py-2 px-4 cursor-pointer border-none text-base uppercase ${selectedStrategyName === strategyName ? 'text-white' : 'text-gray-700'} outline-none`}
              onClick={() => setSelectedStrategyName(strategyName)}
            >
              {strategyName}
            </button>
          ))}
        </div>
        {selectedStrategyName && <TableLayout strategy={groupedSummaries[selectedStrategyName]} onBacktestViewClick={handleBacktestViewClick} />}
      </div>
    </div>
  );
}

export default FitlerView;
