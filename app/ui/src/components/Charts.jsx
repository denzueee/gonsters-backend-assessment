import { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
    ReferenceLine,
} from 'recharts';
import axios from 'axios';

export default function Charts({ data }) {
    const [thresholds, setThresholds] = useState({
        max_temperature: 80,
        min_temperature: 50,
        max_pressure: 150,
    });

    // Fetch thresholds from config
    useEffect(() => {
        const fetchThresholds = async () => {
            try {
                const response = await axios.get('/api/v1/config');
                const config = response.data.config;
                setThresholds({
                    max_temperature: parseFloat(config.max_temperature_threshold || 80),
                    min_temperature: parseFloat(config.min_temperature_threshold || 50),
                    max_pressure: parseFloat(config.max_pressure_threshold || 150),
                    inactivity_timeout: parseFloat(config.inactivity_timeout || 60), // Detected inactive after N seconds
                });
            } catch (error) {
                console.error('Failed to fetch thresholds:', error);
            }
        };
        fetchThresholds();
    }, []);

    if (!data || data.length === 0) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Real-time Sensor Data</h3>
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <p>Waiting for real-time data...</p>
                    <p className="text-sm mt-2">Data will appear when sensors start broadcasting</p>
                </div>
            </div>
        );
    }

    const chartData = data.map((d) => ({
        time: new Date(d.timestamp).toLocaleTimeString(),
        temperature: d.temperature,
        pressure: d.pressure,
        speed: d.speed,
    }));

    const latestData = data[data.length - 1] || {};

    const [isInactive, setIsInactive] = useState(false);

    // Watchdog timer: Check if data is stale
    useEffect(() => {
        if (!latestData.timestamp) return;

        const checkInactivity = () => {
            const lastUpdate = new Date(latestData.timestamp).getTime();
            const now = new Date().getTime();

            const timeoutMs = (thresholds.inactivity_timeout || 60) * 1000;

            if (now - lastUpdate > timeoutMs) {
                setIsInactive(true);
            } else {
                setIsInactive(false);
            }
        };

        // Check immediately and then intervals
        checkInactivity();
        const interval = setInterval(checkInactivity, 1000);

        return () => clearInterval(interval);
    }, [latestData, thresholds.inactivity_timeout]); // Dependency includes timeout setting

    // Check if current values exceed thresholds
    const isTempHigh = latestData.temperature > thresholds.max_temperature;
    const isTempLow = latestData.temperature < thresholds.min_temperature;
    const isPressureHigh = latestData.pressure > thresholds.max_pressure;

    return (
        <div className="space-y-6">
            {/* Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        Real-time Sensor Data
                        {isInactive && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300 animate-pulse border border-gray-300 dark:border-gray-500">
                                <span className="w-2 h-2 mr-1.5 rounded-full bg-gray-500"></span>
                                Connection Inactive
                            </span>
                        )}
                        {!isInactive && latestData.timestamp && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border border-green-200 dark:border-green-800">
                                <span className="w-2 h-2 mr-1.5 rounded-full bg-green-500 animate-pulse"></span>
                                Live
                            </span>
                        )}
                    </div>
                    <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                        (Dotted lines = Safety thresholds)
                    </span>
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                        <XAxis dataKey="time" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                        <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1f2937',
                                border: 'none',
                                borderRadius: '8px',
                                color: '#fff',
                            }}
                        />
                        <Legend />

                        {/* Temperature Threshold Lines */}
                        <ReferenceLine
                            y={thresholds.max_temperature}
                            stroke="#EF4444"
                            strokeDasharray="5 5"
                            strokeWidth={2}
                            label={{
                                value: `Max Temp: ${thresholds.max_temperature}°C`,
                                position: 'insideTopRight',
                                fill: '#EF4444',
                                fontSize: 11,
                                fontWeight: 'bold',
                            }}
                        />
                        <ReferenceLine
                            y={thresholds.min_temperature}
                            stroke="#FB923C"
                            strokeDasharray="5 5"
                            strokeWidth={2}
                            label={{
                                value: `Min Temp: ${thresholds.min_temperature}°C`,
                                position: 'insideBottomRight',
                                fill: '#FB923C',
                                fontSize: 11,
                                fontWeight: 'bold',
                            }}
                        />

                        {/* Pressure Threshold Line */}
                        <ReferenceLine
                            y={thresholds.max_pressure}
                            stroke="#3B82F6"
                            strokeDasharray="5 5"
                            strokeWidth={2}
                            label={{
                                value: `Max Pressure: ${thresholds.max_pressure} PSI`,
                                position: 'insideTopLeft',
                                fill: '#3B82F6',
                                fontSize: 11,
                                fontWeight: 'bold',
                            }}
                        />

                        <Line
                            type="monotone"
                            dataKey="temperature"
                            stroke="#EF4444"
                            name="Temp (°C)"
                            dot={false}
                            strokeWidth={2}
                        />
                        <Line
                            type="monotone"
                            dataKey="pressure"
                            stroke="#3B82F6"
                            name="Pressure (PSI)"
                            dot={false}
                            strokeWidth={2}
                        />
                        <Line
                            type="monotone"
                            dataKey="speed"
                            stroke="#10B981"
                            name="Speed (RPM)"
                            dot={false}
                            strokeWidth={2}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Current Values */}
            <div
                className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 lg:gap-6 ${isInactive ? 'opacity-70 grayscale transition-all duration-500' : 'transition-all duration-500'
                    }`}
            >
                <div
                    className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border-2 transition-all duration-300 ${isTempHigh
                        ? 'border-red-500 dark:border-red-500 shadow-red-200 dark:shadow-red-900/50'
                        : isTempLow
                            ? 'border-orange-500 dark:border-orange-500 shadow-orange-200 dark:shadow-orange-900/50'
                            : 'border-gray-200 dark:border-gray-700'
                        }`}
                >
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Temperature</div>
                        {(isTempHigh || isTempLow) && (
                            <span className="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-full font-semibold animate-pulse">
                                {isTempHigh ? '⚠️ HIGH' : '❄️ LOW'}
                            </span>
                        )}
                    </div>
                    <div
                        className={`text-3xl font-bold mt-2 ${isTempHigh || isTempLow ? 'text-red-600 dark:text-red-400' : 'text-red-600'
                            }`}
                    >
                        {latestData.temperature?.toFixed(1) || '--'} °C
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Threshold: {thresholds.min_temperature}°C - {thresholds.max_temperature}°C
                    </div>
                </div>

                <div
                    className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border-2 transition-all duration-300 ${isPressureHigh
                        ? 'border-blue-500 dark:border-blue-500 shadow-blue-200 dark:shadow-blue-900/50'
                        : 'border-gray-200 dark:border-gray-700'
                        }`}
                >
                    <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-600 dark:text-gray-400">Pressure</div>
                        {isPressureHigh && (
                            <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full font-semibold animate-pulse">
                                ⚠️ HIGH
                            </span>
                        )}
                    </div>
                    <div
                        className={`text-3xl font-bold mt-2 ${isPressureHigh ? 'text-blue-700 dark:text-blue-400' : 'text-blue-600'
                            }`}
                    >
                        {latestData.pressure?.toFixed(1) || '--'} PSI
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Max: {thresholds.max_pressure} PSI
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Speed</div>
                    <div className="text-3xl font-bold text-green-600 mt-2">
                        {latestData.speed?.toFixed(0) || '--'} RPM
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Last update: {latestData.timestamp ? new Date(latestData.timestamp).toLocaleTimeString() : '--'}
                    </div>
                </div>
            </div>
        </div>
    );
}
