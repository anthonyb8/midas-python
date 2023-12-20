import React from 'react';
import Plot from 'react-plotly.js';

const darkThemeLayout = {
  paper_bgcolor: "#1e1e1e",
  plot_bgcolor: "#1e1e1e",
  font: {
    color: "#ddd"
  },
  xaxis: {
    showgrid: false,   // This hides the vertical grid lines
    showspikes: true,
    spikemode: 'across',
    spikesnap: 'cursor',
    spikethickness: 1,        // This makes the line thinner
    spikecolor: 'rgba(255, 255, 255, 0.5)',  // This makes the line slightly transparent
    spikedash: 'solid',      // This makes the line solid
   
  },
  yaxis: {
    gridcolor: "#444",
    tickcolor: "#444",
    zerolinecolor: "#444",
  },
  margin: {
    b: 50, // Adjust this value to your liking. The smaller the number, the less space below the x-axis.
    t: 5, // Top margin, adjust as needed
    l: 50, // Left margin, adjust as needed
    r: 5 // Right margin, adjust as needed
  },
  hovermode: 'closest',
};

function LineChart({ data, layout }) {
  const mergedXAxis = { ...darkThemeLayout.xaxis, ...layout.xaxis};
  const mergedYAxis = { ...darkThemeLayout.yaxis, ...layout.yaxis};

  const finalLayout = {
    ...darkThemeLayout,
    ...layout,
    xaxis: mergedXAxis,
    yaxis: mergedYAxis
  };

  return (
    <div className="dark:bg-darkBackground border border-gray-700 rounded mx-auto my-5">
      <div className="text-gray-300 py-1 px-2.5 border-b border-gray-700">
        Test
      </div>
      <Plot 
      data={data}
      layout={finalLayout}
    />
    </div>

  );
}


export default LineChart;
