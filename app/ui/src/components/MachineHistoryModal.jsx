import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { X, History, Download, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function MachineHistoryModal({ show, onClose, machine }) {
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [isInitialLoad, setIsInitialLoad] = useState(true);

    // Separate states for Table (paginated) and Chart (full range)
    const [historicalData, setHistoricalData] = useState([]); // Table data
    const [fullChartData, setFullChartData] = useState([]);   // Chart data

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [dateRange, setDateRange] = useState({
        start_time: new Date(new Date().setHours(new Date().getHours() - 24)).toISOString().slice(0, 16),
        end_time: new Date().toISOString().slice(0, 16),
        interval: 'raw'
    });

    // Fetch Table Data (Paginated)
    const fetchTableData = useCallback(async (currentOffset = 0, isReset = false) => {
        if (!machine) return;

        setLoading(true);
        setError('');

        try {
            const params = {
                start_time: new Date(dateRange.start_time).toISOString(),
                end_time: new Date(dateRange.end_time).toISOString(),
                interval: dateRange.interval,
                fields: 'all',
                limit: 10,
                offset: currentOffset
            };

            const response = await axios.get(`/api/v1/data/machine/${machine.machine_id}`, { params });

            if (response.data.status === 'success') {
                const newData = response.data.data;
                const pagination = response.data.pagination;

                if (isReset) {
                    setHistoricalData(newData);
                } else {
                    setHistoricalData(prev => [...prev, ...newData]);
                }

                setHasMore(pagination.has_more);
                setOffset(currentOffset + 10);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to fetch historical data');
        } finally {
            setLoading(false);
            setIsInitialLoad(false);
        }
    }, [machine, dateRange]);

    // Fetch Chart Data (Full Range, Unlimited)
    const fetchChartData = useCallback(async () => {
        if (!machine) return;

        try {
            const params = {
                start_time: new Date(dateRange.start_time).toISOString(),
                end_time: new Date(dateRange.end_time).toISOString(),
                interval: dateRange.interval,
                fields: 'all',
                limit: -1, // Unlimited (handled by backend)
                offset: 0
            };

            const response = await axios.get(`/api/v1/data/machine/${machine.machine_id}`, { params });

            if (response.data.status === 'success') {
                setFullChartData(response.data.data);
            }
        } catch (err) {
            console.error('Failed to fetch chart data', err);
        }
    }, [machine, dateRange]);

    // Infinite Scroll Refs
    const observer = useRef();
    const lastElementRef = useCallback(node => {
        if (loading) return;
        if (observer.current) observer.current.disconnect();

        observer.current = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && hasMore) {
                fetchTableData(offset, false);
            }
        });

        if (node) observer.current.observe(node);
    }, [loading, hasMore, offset, fetchTableData]);

    useEffect(() => {
        if (show && machine) {
            // Reset state when opening modal or changing machine
            setHistoricalData([]);
            setFullChartData([]);
            setOffset(0);
            setHasMore(true);
            setIsInitialLoad(true);

            // Trigger both fetches
            fetchTableData(0, true);
            fetchChartData();
        }
    }, [show, machine, fetchTableData, fetchChartData]);

    const downloadCSV = () => {
        if (historicalData.length === 0 && fullChartData.length === 0) return;

        // Export full data if available
        const exportData = fullChartData.length > 0 ? fullChartData : historicalData;

        const headers = ['Timestamp', 'Temperature (°C)', 'Pressure (kPa)', 'Speed (RPM)'];
        const rows = exportData.map(d => [
            d.timestamp,
            d.temperature || '',
            d.pressure || '',
            d.speed || ''
        ]);

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${machine.name}_${Date.now()}.csv`;
        a.click();
    };

    // Prepare Chart Data (Chronological)
    const chartData = [...fullChartData].reverse().map(d => ({
        time: new Date(d.timestamp).toLocaleTimeString(),
        temperature: d.temperature,
        pressure: d.pressure,
        speed: d.speed
    }));

    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                    <div>
                        <h2 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            <History className="w-5 h-5 md:w-6 md:h-6" />
                            Historical Data
                        </h2>
                        {machine && (
                            <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {machine.name} • {machine.location}
                            </p>
                        )}
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto flex-1">
                    {error && (
                        <div className="bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded mb-4">
                            {error}
                        </div>
                    )}

                    {/* Date Range Filter */}
                    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-6">
                        <div className="flex items-center gap-2 mb-3">
                            <Calendar className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                            <h3 className="font-semibold text-gray-900 dark:text-white">Time Range</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div>
                                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Start Time</label>
                                <input
                                    type="datetime-local"
                                    value={dateRange.start_time}
                                    onChange={(e) => setDateRange({ ...dateRange, start_time: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">End Time</label>
                                <input
                                    type="datetime-local"
                                    value={dateRange.end_time}
                                    onChange={(e) => setDateRange({ ...dateRange, end_time: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Interval</label>
                                <select
                                    value={dateRange.interval}
                                    onChange={(e) => setDateRange({ ...dateRange, interval: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                                >
                                    <option value="raw">Raw Data</option>
                                    <option value="1m">1 Minute</option>
                                    <option value="5m">5 Minutes</option>
                                    <option value="1h">1 Hour</option>
                                    <option value="1d">1 Day</option>
                                </select>
                            </div>
                            <div className="flex items-end">
                                <button
                                    onClick={() => {
                                        fetchTableData(0, true);
                                        fetchChartData();
                                    }}
                                    disabled={loading}
                                    className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 transition"
                                >
                                    {loading && isInitialLoad ? 'Loading...' : 'Apply Filter'}
                                </button>
                            </div>
                        </div>
                    </div>

                    {loading && isInitialLoad ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : (
                        <>
                            {/* Chart */}
                            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="font-semibold text-gray-900 dark:text-white">Data Visualization</h3>
                                    <button
                                        onClick={downloadCSV}
                                        className="flex items-center gap-2 px-3 py-2 text-xs md:text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                                    >
                                        <Download className="w-3 h-3 md:w-4 md:h-4" />
                                        <span className="hidden sm:inline">Export CSV</span>
                                        <span className="sm:hidden">Export</span>
                                    </button>
                                </div>
                                <ResponsiveContainer width="100%" height={300}>
                                    <LineChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                                        <XAxis dataKey="time" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                                        <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                                        <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
                                        <Legend />
                                        <Line type="monotone" dataKey="temperature" stroke="#EF4444" name="Temp (°C)" dot={false} />
                                        <Line type="monotone" dataKey="pressure" stroke="#3B82F6" name="Pressure (kPa)" dot={false} />
                                        <Line type="monotone" dataKey="speed" stroke="#10B981" name="Speed (RPM)" dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Data Table */}
                            {historicalData.length > 0 ? (
                                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                                    <div className="overflow-x-auto">
                                        <table className="w-full">
                                            <thead className="bg-gray-50 dark:bg-gray-900">
                                                <tr>
                                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Timestamp</th>
                                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Temperature (°C)</th>
                                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Pressure (kPa)</th>
                                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-white">Speed (RPM)</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                                {historicalData.map((item, idx) => (
                                                    <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                                                        <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">
                                                            {new Date(item.timestamp).toLocaleString()}
                                                        </td>
                                                        <td className="px-4 py-3 text-sm text-red-600 dark:text-red-400 font-mono">
                                                            {item.temperature?.toFixed(2) || '--'}
                                                        </td>
                                                        <td className="px-4 py-3 text-sm text-blue-600 dark:text-blue-400 font-mono">
                                                            {item.pressure?.toFixed(2) || '--'}
                                                        </td>
                                                        <td className="px-4 py-3 text-sm text-green-600 dark:text-green-400 font-mono">
                                                            {item.speed?.toFixed(0) || '--'}
                                                        </td>
                                                    </tr>
                                                ))}
                                                {/* Sentinel element for infinite scroll */}
                                                {hasMore && (
                                                    <tr ref={lastElementRef} className="bg-transparent">
                                                        <td colSpan="4" className="text-center py-4">
                                                            {loading && (
                                                                <div className="flex justify-center items-center gap-2">
                                                                    <div className="w-4 h-4 border-2 border-gray-500 border-t-transparent rounded-full animate-spin"></div>
                                                                    <span className="text-sm text-gray-400">Loading more...</span>
                                                                </div>
                                                            )}
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                                    <History className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                    <p>No historical data found for the selected time range</p>
                                    <p className="text-sm mt-2">Try adjusting the date range or interval</p>
                                </div>
                            )}

                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-4 text-center">
                                Showing {historicalData.length} records in table
                            </p>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
