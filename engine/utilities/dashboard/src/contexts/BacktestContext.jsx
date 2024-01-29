import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';

export const BacktestContext = createContext();

export const BacktestProvider = ({ children }) => {
  const [backtestsCache, setBacktestsCache] = useState({});
  const [currentBacktestId, setCurrentBacktestId] = useState(null);
  const authToken = sessionStorage.getItem('token');

  useEffect(() => {
    // This is mainly for debugging, consider removing in production
    console.log('Backtests Cache Updated:', backtestsCache);
  }, [backtestsCache]);

  const setCurrentBacktest = (id) => {
    setCurrentBacktestId(id);
    sessionStorage.setItem('currentBacktestId', id);
  };

  const getBacktest = async (backtest_id) => {
    if (backtestsCache[backtest_id]) {
      return backtestsCache[backtest_id];
    } else {
      try {
        const response = await api.get(`/api/backtest/${backtest_id}/`, {
          headers: { 'Authorization': `Token ${authToken}` }
        });
        console.log(response)
        if (response.status === 200) {
          const updatedCache = { ...backtestsCache, [backtest_id]: response.data };
          setBacktestsCache(updatedCache);
          sessionStorage.setItem('cachedBacktests', JSON.stringify(updatedCache));
          return response.data;
        } else {
          console.error('Error fetching backtest:', response.statusText);
        }
      } catch (error) {
        console.error('Error fetching backtest:', error);
      }
    }
  };

  const removeBacktest = (backtest_id) => {
    setBacktestsCache(prevCache => {
      const updatedCache = { ...prevCache };
      delete updatedCache[backtest_id];
      if (+backtest_id === +currentBacktestId) {
        const newId = Object.keys(updatedCache).length > 0 ? 
                      Object.keys(updatedCache).find(key => key !== backtest_id) : 
                      null;
        setCurrentBacktest(newId);
        sessionStorage.setItem('currentBacktestId', newId);
      }
      return updatedCache;
    });
  };

  const contextValue = {
    getBacktest,
    removeBacktest,
    currentBacktestId,
    setCurrentBacktest,
    backtestsCache
  };

  return (
    <BacktestContext.Provider value={contextValue}>
      {children}
    </BacktestContext.Provider>
  );
};
