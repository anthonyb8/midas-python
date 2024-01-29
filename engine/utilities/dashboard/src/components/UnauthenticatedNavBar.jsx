import React from 'react';
import { useNavigate } from 'react-router-dom';

const UnauthenticatedNavBar = () => {
    const navigate = useNavigate();

    return (
        <header className="bg-darkSecondaryBg text-gray-500 p-4 border-b border-darkBorderColor sticky top-0 z-10">
            <nav>
                <ul className="flex justify-end space-x-4">
                    <li className="hover:text-darkTextColor"><button onClick={() => navigate('/login')}>Login</button></li>
                    <li className="hover:text-darkTextColor"><button onClick={() => navigate('/signup')}>Signup</button></li>
                </ul>
            </nav>
        </header>
    );
};

export default UnauthenticatedNavBar;
