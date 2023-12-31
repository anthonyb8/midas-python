import React, { useEffect, useState, createContext, useContext } from 'react';

// Create a React Context for holding and passing down summaries data
const SummariesContext = createContext();

// Custom hook for easy access to the SummariesContext and ensuring it's used within its provider
export const useSummaries = () => {
  const context = useContext(SummariesContext);
  if (!context) {
    throw new Error('useSummaries must be used within a SummariesProvider');
  }
  return context;
};


// Provider component that fetches, organizes, and supplies summaries data to its child components
export const SummariesProvider = ({ client, children }) => {
  const [summaries, setSummaries] = useState(null); // State for raw summaries data
  const [groupedSummaries, setGroupedSummaries] = useState({}); // State for summaries grouped by strategy
  const [isLoading, setIsLoading] = useState(true); // State to track data loading status

  // Fetch summaries data from the API and group it by strategy when component mounts or summaries change
  useEffect(() => {
    const fetchSummaries = async () => {
      setIsLoading(true); // Start loading state
      try {
        const response = await client.getBacktestsSummaries(); // Attempt to fetch summaries
        if (response.success) {
          setSummaries(response.data); // Save fetched data
          const grouped = groupSummariesByStrategy(response.data); // Group fetched data by strategy
          setGroupedSummaries(grouped); // Save grouped data
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
    if (!summaries) {
      fetchSummaries();
    } else {
      setIsLoading(false);
    }
    
  // Depend on 'client' to refetch if it changes, summaries is not included to prevent refetching when they are set
  }, [client]); //TODO: Removed summaries may need to put back //

  // Helper function to group summaries data by strategy name
  const groupSummariesByStrategy = (summaries) => {
    return summaries.reduce((acc, summary) => {
      // Initialize a group for each strategy name if it doesn't exist
      if (!acc[summary.strategy_name]) {
        acc[summary.strategy_name] = [];
      }
      // Append summary to its group
      acc[summary.strategy_name].push(summary);
      return acc;
    }, {});
  };

  // Prepare context value with all necessary data
  const contextValue = { summaries, groupedSummaries, isLoading };

  // Provide the context to child components
  return (
    <SummariesContext.Provider value={contextValue}>
      {children}
    </SummariesContext.Provider>
  );
};

