import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from '../contexts/WebSocketContext';
import { useAuth } from '../contexts/AuthContext';
import { Plus, Upload, History } from 'lucide-react';

import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import StatsCards from '../components/StatsCards';
import Charts from '../components/Charts';
import AlertPanel from '../components/AlertPanel';
import AddMachineModal from '../components/AddMachineModal';
import IngestDataModal from '../components/IngestDataModal';
import MachineHistoryModal from '../components/MachineHistoryModal';

export default function Dashboard() {
    const [machines, setMachines] = useState([]);
    const [selectedMachine, setSelectedMachine] = useState(null);
    const [loading, setLoading] = useState(true);
    const [darkMode, setDarkMode] = useState(false);

    // Machines Pagination
    const [offset, setOffset] = useState(0);
    const [hasMoreMachines, setHasMoreMachines] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);

    // Modal states
    const [showAddMachine, setShowAddMachine] = useState(false);
    const [showIngestData, setShowIngestData] = useState(false);
    const [showMachineHistory, setShowMachineHistory] = useState(false);

    const { connected, sensorData } = useWebSocket();
    const { user, logout } = useAuth();

    useEffect(() => {
        fetchMachines(0, true);

        // Check for dark mode preference
        const isDark = localStorage.getItem('darkMode') === 'true';
        setDarkMode(isDark);
        if (isDark) {
            document.documentElement.classList.add('dark');
        }
    }, []);

    const fetchMachines = async (currentOffset = 0, isRefresh = false) => {
        try {
            if (currentOffset > 0) setLoadingMore(true);

            const params = {
                limit: 10,
                offset: currentOffset
            };

            const response = await axios.get('/api/v1/data/machines', { params });
            const newMachines = response.data.machines || [];
            const pagination = response.data.pagination;

            if (isRefresh) {
                setMachines(newMachines);
                if (newMachines.length > 0 && !selectedMachine) {
                    setSelectedMachine(newMachines[0]);
                }
            } else {
                setMachines(prev => {
                    // Filter duplicates
                    const existingIds = new Set(prev.map(m => m.machine_id));
                    const uniqueNewMachines = newMachines.filter(m => !existingIds.has(m.machine_id));
                    return [...prev, ...uniqueNewMachines];
                });
            }

            if (pagination) {
                setHasMoreMachines(pagination.has_more);
                setOffset(currentOffset + 10);
            } else {
                // Fallback if pagination object missing (shouldn't happen with new backend)
                setHasMoreMachines(false);
            }

        } catch (error) {
            console.error('Failed to fetch machines:', error);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    };

    const loadMoreMachines = () => {
        if (!loadingMore && hasMoreMachines) {
            fetchMachines(offset, false);
        }
    };

    const handleLogout = async () => {
        await logout();
        window.location.href = '/login';
    };

    const toggleDarkMode = () => {
        const newDarkMode = !darkMode;
        setDarkMode(newDarkMode);
        localStorage.setItem('darkMode', newDarkMode);
        document.documentElement.classList.toggle('dark');
    };

    const handleMachineAdded = () => {
        fetchMachines(0, true);
        setShowAddMachine(false);
    };

    const handleDataIngested = () => {
        console.log('Data ingested successfully');
    };

    const lastProcessedRef = useRef(null);

    // Update machines list with real-time data
    useEffect(() => {
        if (sensorData.length === 0) return;

        const updates = new Map();

        // Iterate backwards to find new items efficiently
        for (let i = sensorData.length - 1; i >= 0; i--) {
            const item = sensorData[i];

            // Stop if we reach the last processed item
            if (lastProcessedRef.current &&
                item.timestamp === lastProcessedRef.current.timestamp &&
                item.machine_id === lastProcessedRef.current.machine_id) {
                break;
            }

            // Map keys are unique, so we only keep the latest update for each machine from the batch
            if (!updates.has(item.machine_id)) {
                updates.set(item.machine_id, item);
            }
        }

        if (updates.size > 0) {
            // Update reference to the absolute last item we have
            const lastItem = sensorData[sensorData.length - 1];
            lastProcessedRef.current = {
                timestamp: lastItem.timestamp,
                machine_id: lastItem.machine_id
            };

            setMachines(prevMachines => prevMachines.map(m => {
                if (updates.has(m.machine_id)) {
                    const data = updates.get(m.machine_id);
                    return {
                        ...m,
                        status: data.status || 'active',
                        _lastUpdate: Date.now()
                    };
                }
                return m;
            }));
        }
    }, [sensorData]);

    const machineSensorData = selectedMachine
        ? sensorData.filter(d => d.machine_id === selectedMachine.machine_id)
        : [];

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Header
                user={user}
                connected={connected}
                darkMode={darkMode}
                toggleDarkMode={toggleDarkMode}
                onLogout={handleLogout}
            />

            <div className="flex">
                <Sidebar
                    machines={machines}
                    selectedMachine={selectedMachine}
                    onSelectMachine={setSelectedMachine}
                    hasMore={hasMoreMachines}
                    onLoadMore={loadMoreMachines}
                    loadingMore={loadingMore}
                />

                <main className="flex-1 p-6 overflow-y-auto" style={{ height: 'calc(100vh - 73px)' }}>
                    <StatsCards machines={machines} />

                    {/* Action Buttons */}
                    <div className="flex justify-end gap-4 my-6">
                        <button
                            onClick={() => setShowAddMachine(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition shadow-sm"
                        >
                            <Plus className="w-5 h-5" />
                            Add Machine
                        </button>
                        <button
                            onClick={() => setShowIngestData(true)}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-sm"
                        >
                            <Upload className="w-5 h-5" />
                            Ingest Data
                        </button>
                        {selectedMachine && (
                            <button
                                onClick={() => setShowMachineHistory(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition shadow-sm"
                            >
                                <History className="w-5 h-5" />
                                Machine History
                            </button>
                        )}
                    </div>

                    {/* Selected Machine Details */}
                    {selectedMachine && (
                        <div>
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-6 border border-gray-200 dark:border-gray-700">
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                                    {selectedMachine.name}
                                </h2>
                                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                                    <span>📍 {selectedMachine.location}</span>
                                    <span>•</span>
                                    <span>🔧 {selectedMachine.sensor_type}</span>
                                    <span>•</span>
                                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${selectedMachine.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                        selectedMachine.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                                            'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                                        }`}>
                                        {selectedMachine.status}
                                    </span>
                                </div>
                            </div>

                            {/* Charts */}
                            <Charts data={machineSensorData} />

                            {/* Real-time Info */}
                            <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 mt-6 border border-primary-200 dark:border-primary-800">
                                <div className="text-sm text-primary-900 dark:text-primary-100">
                                    📡 Real-time: {machineSensorData.length} data points received
                                    {machineSensorData.length > 0 && (
                                        <span> • Last update: {new Date(machineSensorData[machineSensorData.length - 1].timestamp).toLocaleTimeString()}</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </main>

                <AlertPanel />
            </div>

            {/* Modals */}
            <AddMachineModal
                show={showAddMachine}
                onClose={() => setShowAddMachine(false)}
                onMachineAdded={handleMachineAdded}
            />

            <IngestDataModal
                show={showIngestData}
                onClose={() => setShowIngestData(false)}
                machines={machines}
                onDataIngested={handleDataIngested}
            />

            <MachineHistoryModal
                show={showMachineHistory}
                onClose={() => setShowMachineHistory(false)}
                machine={selectedMachine}
            />
        </div>
    );
}
