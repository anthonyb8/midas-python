
import React from "react";

function ParametersBar({ parameters }) {
    return (
        <div className="grid grid-cols-4 text-center py-2.5 mx-1.5 border-t border-b border-darkBorderColor">
            <div className="flex flex-col items-center">
                <div>{parameters.start_date}</div>
                <div className="uppercase opacity-50 text-sm mb-1.5">START</div>
            </div>
            <div className="flex flex-col items-center">
                <div>{parameters.end_date}</div>
                <div className="uppercase opacity-50 text-sm mb-1.5">END</div>
            </div>
            <div className="flex flex-col items-center">
                <div>
                    {parameters.symbols.map((symbol, index) => (
                        <span key={index}>{index > 0 ? ' | ' : ''}{symbol}</span>
                        ))}
                    <div className="uppercase opacity-50 text-sm mb-1.5">SYMBOLS</div>
                </div>
            </div>
            <div className="flex flex-col items-center">
                <div>{parameters?.capital}</div>
                <div className="uppercase opacity-50 text-sm mb-1.5">CAPITAL</div>
            </div>
        </div>
    );
}

export default ParametersBar;

