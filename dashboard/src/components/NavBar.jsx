import React from 'react';
import { useNavigate } from 'react-router-dom';

const NavBar = () => {
    const navigate = useNavigate();

    return (
        <header className="bg-darkBackground text-white p-4 border-b border-white">
            <nav>
                <ul className="flex justify-between">
                    <li><button onClick={() => navigate('/dashboard')}>Dashboard</button></li>
                    <li><button onClick={() => navigate('/strategies')}>Strategies</button></li>
                    <li><button onClick={() => navigate('/login')}>Login</button></li>
                    <li><button onClick={() => navigate('/logout')}>Logout</button></li>
                </ul>
            </nav>
        </header>
    );
};
export default NavBar;



// function HeaderBar({ onStrategiesClick }) {

//   return (
//     <div className={styles.headerBar}>
//       <div className={styles.title}>
//         Trader Dashboard
//       </div>
//       <div className={styles.controls}>
//         <NavLink to="/dashboard" className={({ isActive }) => isActive ? `${styles.button} ${styles.activeButton}` : styles.button}>Dashboard</NavLink>
//         <NavLink to="/strategies" 
//               className={({ isActive }) => isActive ? `${styles.button} ${styles.activeButton}` : styles.button} 
//               onClick={onStrategiesClick}
//         >Strategies</NavLink>
//         <button className={styles.button}>Settings</button>
//       </div>
//     </div>
//   );
// }

// export default HeaderBar;





