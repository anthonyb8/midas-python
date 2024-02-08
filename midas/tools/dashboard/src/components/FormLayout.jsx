// FormLayout.js
import React from 'react';

export const FormLayout = ({ title, children }) => {
    return (
        <div className=" m-y-100 bg-darkSecondaryBg text-darkTextColor max-w-md mx-auto my-10 p-8 border shadow-lg rounded-lg flex items-center justify-center h-1/2">
            <div className=" form-container ">
                {title && <h2 className="text-center text-2xl  mb-6">{title}</h2>}
                {children}
            </div>
        </div>
    );
};
