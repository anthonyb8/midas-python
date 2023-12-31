import React, { createContext, useContext, useState, useEffect } from 'react';

const BacktestsContext = createContext();

export const useBacktests = () => {
  const context = useContext(BacktestsContext);
  if (!context) {
    throw new Error('useBacktests must be used within a BacktestsProvider');
  }
  return context;
};

export const BacktestsProvider = ({ client, children }) => {
  const [backtestsCache, setBacktestsCache] = useState({});
  
  useEffect(() => {
    console.log('Backtests Cache Updated:', backtestsCache);
  }, [backtestsCache]);


  const getBacktest = async (backtest_id) => {
    if (backtestsCache[backtest_id]) {
      return backtestsCache[backtest_id];
    } else {
      try {
        const response = await client.getBacktest(backtest_id);
        if (response.success) {
          setBacktestsCache((prevCache) => ({
            ...prevCache,
            [backtest_id]: response.data,
          }));
          return response.data;
        } else {
          console.error('Error fetching backtest:', response.error);
          return null;
        }
      } catch (error) {
        console.error('Error fetching backtest:', error);
        return null;
      }
    }
  };

  const contextValue = {
    getBacktest,
  };

  return (
    <BacktestsContext.Provider value={contextValue}>
      {children}
    </BacktestsContext.Provider>
  );
};
