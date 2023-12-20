import React, { useMemo, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import APIClient from './services/backtestServices';
import { SummariesProvider } from './contexts/SummariesProvider';
import { BacktestsProvider } from './contexts/BacktestsProvider';
import Dashboard from './pages/Dashboard';
import StrategiesView from './pages/Strategies';
import NavBar from './components/NavBar';

const App = () => {
  const client = useMemo(() => new APIClient(), []);

  // const navigate = useNavigate();
  const [openedBacktests, setOpenedBacktests] = useState([]);

  const handleBacktestSelection = async (backtest_id) => {
    setOpenedBacktests(prev => [...new Set([...prev, backtest_id])]);
    localStorage.setItem('selectedBacktest', backtest_id);
  };

  const removeBacktest = (backtest_id) => {
    setOpenedBacktests(prev => prev.filter(id => id !== backtest_id));
    if (localStorage.getItem('selectedBacktest') === backtest_id.toString()) {
      localStorage.removeItem('selectedBacktest');
    }
  };

  // const handleStrategiesClick = () => {
  //   localStorage.removeItem('selectedBacktest');
  //   navigate('/strategies');
  // };

  return (
      // <AuthProvider>
      <SummariesProvider client={client}>
        <BacktestsProvider client={client}>
          <Router>
              <NavBar />
              <Routes>
                  <Route path="/dashboard" element={openedBacktests.length > 0 ? <Dashboard backtests={openedBacktests} removeBacktest={removeBacktest} /> : <StrategiesView onBacktestSelection={handleBacktestSelection} />} />
                  <Route path="/strategies" element={<StrategiesView onBacktestSelection={handleBacktestSelection} />} />
                  {/* <Route path="/login" element={<LoginUser />} /> */}
                  {/* <Route path="/logout" element={<Logout />} /> */}
              </Routes>
          </Router>
        </BacktestsProvider>
      </SummariesProvider>
      /* // </AuthProvider> */
  );
};

export default App;



// function App() {
//   //Create API instance should not change, all data calls made by this client //
//   const client = useMemo(() => new APIClient(), []);

//   const navigate = useNavigate();
//   const [openedBacktests, setOpenedBacktests] = useState([]);

//   const handleBacktestSelection = async (backtest_id) => {
//     setOpenedBacktests(prev => [...new Set([...prev, backtest_id])]);
//     localStorage.setItem('selectedBacktest', backtest_id);
//   };

//   const removeBacktest = (backtest_id) => {
//     setOpenedBacktests(prev => prev.filter(id => id !== backtest_id));
//     if (localStorage.getItem('selectedBacktest') === backtest_id.toString()) {
//       localStorage.removeItem('selectedBacktest');
//     }
//   };

//   const handleStrategiesClick = () => {
//     localStorage.removeItem('selectedBacktest');
//     navigate('/strategies');
//   };

//   return (

//     // Instantiate summaries proivder, this is responsible for pulling summaries from API client. Returns a context
//     <SummariesProvider client={client}>
//       {/* Instantiate backtests provider, responsible for pulling specific backtest data */}
//       <BacktestsProvider client={client}>
//         <Router>
//           <HeaderBar onStrategiesClick={handleStrategiesClick} />
//           <Routes>
//             <Route path="/strategies" element={<StrategiesView onBacktestSelection={handleBacktestSelection} />} />
//             <Route path="/dashboard" element={openedBacktests.length > 0 ? <Dashboard backtests={openedBacktests} removeBacktest={removeBacktest} /> : <StrategiesView onBacktestSelection={handleBacktestSelection} />} />
//             <Route path="*" element={<StrategiesView onBacktestSelection={handleBacktestSelection} />} />
//           </Routes>
//         </Router>
//       </BacktestsProvider>
//     </SummariesProvider>
//   );
// }

// export default App;
