import React, { useEffect, useState, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './contexts/AuthContext';
import { BacktestProvider } from './contexts/BacktestContext'; 
import LoginUser from './pages/LoginUser';
import FilterView from './pages/Filter/Filter';
import Dashboard from './pages/Dashboard/Dashboard';
import AuthenticatedNavBar from './components/AuthenticatedNavBar';
import UnauthenticatedNavBar from './components/UnauthenticatedNavBar';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/LandingPage';

const App = () => {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <Router>
      <BacktestProvider> 
        { isAuthenticated ? <AuthenticatedNavBar /> : <UnauthenticatedNavBar /> }
        <Routes>
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard/></ProtectedRoute>}/>
          <Route path="/filter" element={<ProtectedRoute><FilterView /></ProtectedRoute>}/>
          <Route path="/login" element={<LoginUser />}/>
          <Route path="" element={isAuthenticated ? <Navigate to="/filter" /> :<LandingPage/>}/>
        </Routes>
      </BacktestProvider>
    </Router>
  );
};

export default App;
