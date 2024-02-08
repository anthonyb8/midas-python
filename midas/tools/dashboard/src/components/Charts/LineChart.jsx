import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

function LineChart({ data , title}) {
    const chartContainerRef = useRef();
    const chartRef = useRef(null); // To store the chart instance

    useEffect(() => {
        if (chartContainerRef.current) {
            let chart;
            if (!chartRef.current) {
                // Create a new chart if it doesn't exist
                chart = createChart(chartContainerRef.current, {
                    width: 789,
                    height: 400,
                    layout: {
                        background: { type: 'solid', color: '#1e1e1e' },
                        textColor: '#ddd',
                    },
                    grid: {
                        horzLines: { color: '#444' },
                        vertLines: { color: '#444' },
                    },
                    priceScale: {
                        borderColor: '#444',
                    },
                    timeScale: {
                        borderColor: '#444',
                    },
                });
                chartRef.current = chart;
            } else {
                // Use the existing chart
                chart = chartRef.current;
            }

            let chartSeries;
            if (!chartSeries) {
                chartSeries = chart.addLineSeries({
                    color: 'white',
                    lineWidth: 2,
                    priceLineVisible: false,
                    lastValueVisible: false,
                });
            }

            // Transform the data and set it to the chart
            const seriesData = data.map(series => {
                const date = new Date(series.time);
                return {
                    time: date.toISOString().split('T')[0], // Format time as YYYY-MM-DD
                    value: parseFloat(series.value),
                };
            });

            chartSeries.setData(seriesData); // Set all data points at once
        }

        // Cleanup function
        return () => {
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [data]);

    if (!data) {
        return <div>Loading...</div>;
    }

    return (
        <div className="border rounded mx-auto my-5" style={{ width: '790px', height: '430px' }}>
            <div className="text-darkTextColor py-1 px-2.5 border-b uppercase">{title}</div>
            <div ref={chartContainerRef} />
        </div>
    );
}

export default LineChart;

