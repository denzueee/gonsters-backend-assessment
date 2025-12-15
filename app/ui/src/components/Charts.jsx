import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function Charts({ data }) {
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

    const chartData = data.map(d => ({
        time: new Date(d.timestamp).toLocaleTimeString(),
        temperature: d.temperature,
        pressure: d.pressure,
        speed: d.speed
    }));

    const latestData = data[data.length - 1] || {};

    return (
        <div className="space-y-6">
            {/* Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Real-time Sensor Data</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                        <XAxis
                            dataKey="time"
                            stroke="#9CA3AF"
                            style={{ fontSize: '12px' }}
                        />
                        <YAxis
                            stroke="#9CA3AF"
                            style={{ fontSize: '12px' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1f2937',
                                border: 'none',
                                borderRadius: '8px',
                                color: '#fff'
                            }}
                        />
                        <Legend />
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
                            name="Pressure (kPa)"
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
            <div className="grid grid-cols-3 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Temperature</div>
                    <div className="text-3xl font-bold text-red-600 mt-2">
                        {latestData.temperature?.toFixed(1) || '--'} °C
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Last update: {latestData.timestamp ? new Date(latestData.timestamp).toLocaleTimeString() : '--'}
                    </div>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Pressure</div>
                    <div className="text-3xl font-bold text-blue-600 mt-2">
                        {latestData.pressure?.toFixed(1) || '--'} kPa
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Last update: {latestData.timestamp ? new Date(latestData.timestamp).toLocaleTimeString() : '--'}
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
