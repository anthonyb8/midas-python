import React, { createContext, useState, useEffect } from 'react';
import api from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [authToken, setAuthToken] = useState(null);

    // Function to log in the user
    const login = async (username, password, navigate) => {
        try {
            const response = await api.post('api/account/login/', { username, password });
            const token = response.data.token;
            if (token) {
                setIsAuthenticated(true);
                setAuthToken(token);
                sessionStorage.setItem('token', token); // Save token to sessionStorage
                navigate('/filter');
            }
        } catch (error) {
            console.error("Login error", error);
            // Optionally, handle login errors (e.g., show a message to the user)
        }
    };

    // Function to log out the user
    const logout = (navigate) => {
        setIsAuthenticated(false);
        setAuthToken(null);
        sessionStorage.removeItem('token'); // Remove token from sessionStorage
        navigate(''); // Redirect to home page or login page after logout
    };

    // Check token on initial load
    useEffect(() => {
        const token = sessionStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            setAuthToken(token);
        }
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated,authToken, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};



