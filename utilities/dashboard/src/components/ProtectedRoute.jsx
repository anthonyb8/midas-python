// ProtectedRoute.js
import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
    const { authToken } = useContext(AuthContext);

    if (!authToken) {
        // Redirect them to the /login page if not logged in
        return <Navigate to="/login" />;
    }

    return children; // If logged in, render the passed children
};

export default ProtectedRoute;
