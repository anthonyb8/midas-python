// LoginUser.js
import React, { useState, useContext, useEffect } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { FormLayout } from '../components/FormLayout';
import { useNavigate } from 'react-router-dom';

const LoginUser = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login, isAuthenticated } = useContext(AuthContext);
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/filter');
        } 
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Passing navigate as an argument to the login function
            await login(username, password, navigate);
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return (

        <FormLayout className= "bg-darkSecondaryBg" title="LOGIN">
            <form onSubmit={handleSubmit}  className="flex flex-col items-center">
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className='bg-darkBackground'
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className='bg-darkBackground m-0.5'
                />
                <div className='flex justify-center w-full'>
                    <button className="rounded-lg py-1.5 px-3 border border-darkBorderColor bg-darkSecondaryBg text-darkTextColor cursor-pointer text-base outline-none hover:bg-gray-400 focus:bg-gray-700 hover:text-white focus:text-white" type="submit">Submit</button>
                </div>
            </form>
        </FormLayout>
    );
};

export default LoginUser;
