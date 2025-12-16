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
import ConfigSettingsModal from '../components/ConfigSettingsModal';

export default function Dashboard() {
    const [machines, setMachines] = useState([]);
    const [selectedMachine, setSelectedMachine] = useState(null);
    const [loading, setLoading] = useState(true);

    // Dark mode with persistence
    const [darkMode, setDarkMode] = useState(() => {
        const saved = localStorage.getItem('darkMode');
        return saved ? JSON.parse(saved) : false;
    });

    // Sidebar states with mobile-responsive defaults
    const [leftSidebarOpen, setLeftSidebarOpen] = useState(() => {
        const isWideScreen = window.innerWidth >= 1600;
        const saved = localStorage.getItem('leftSidebarOpen');

        // If desktop and no saved state, or saved state is invalid, default to open
        if (saved === null) {
            return isWideScreen;
        }

        const savedState = JSON.parse(saved);
        // Override saved state if it doesn't match screen size expectation
        if (isWideScreen && !savedState) {
            // Desktop should default to open
            localStorage.setItem('leftSidebarOpen', 'true');
            return true;
        }

        return savedState;
    });

    const [rightSidebarOpen, setRightSidebarOpen] = useState(() => {
        const isWideScreen = window.innerWidth >= 1600;
        const saved = localStorage.getItem('rightSidebarOpen');

        // If desktop and no saved state, or saved state is invalid, default to open
        if (saved === null) {
            return isWideScreen;
        }

        const savedState = JSON.parse(saved);
        // Override saved state if it doesn't match screen size expectation
        if (isWideScreen && !savedState) {
            // Desktop should default to open
            localStorage.setItem('rightSidebarOpen', 'true');
            return true;
        }

        return savedState;
    });

    const [page, setPage] = useState(1);
    const [offset, setOffset] = useState(0);
    const [hasMoreMachines, setHasMoreMachines] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);

    // Modal states
    const [showAddMachine, setShowAddMachine] = useState(false);
    const [showIngestData, setShowIngestData] = useState(false);
    const [showMachineHistory, setShowMachineHistory] = useState(false);
    const [showConfigSettings, setShowConfigSettings] = useState(false);

    // Toggle handlers with persistence
    const toggleLeftSidebar = () => {
        setLeftSidebarOpen(prev => {
            const newState = !prev;
            localStorage.setItem('leftSidebarOpen', JSON.stringify(newState));
            return newState;
        });
    };

    const toggleRightSidebar = () => {
        setRightSidebarOpen(prev => {
            const newState = !prev;
            localStorage.setItem('rightSidebarOpen', JSON.stringify(newState));
            return newState;
        });
    };

    // Close sidebars on mobile when clicking overlay
    const handleOverlayClick = () => {
        if (window.innerWidth < 1600) {
            setLeftSidebarOpen(false);
            setRightSidebarOpen(false);
        }
    };

    const { connected, sensorData, alerts } = useWebSocket();
    const { user, logout } = useAuth();

    useEffect(() => {
        fetchMachines(0, true);

        // Check for dark mode preference
        const isDark = localStorage.getItem('darkMode') === 'true';
        setDarkMode(isDark);
        if (isDark) {
            document.documentElement.classList.add('dark');
        }

        // Force correct state based on screen width on mount
        if (window.innerWidth >= 1600) {
            // Wide screen: ensure both open
            localStorage.setItem('leftSidebarOpen', 'true');
            localStorage.setItem('rightSidebarOpen', 'true');
            setLeftSidebarOpen(true);
            setRightSidebarOpen(true);
        } else {
            // Narrow screen: ensure both closed
            localStorage.setItem('leftSidebarOpen', 'false');
            localStorage.setItem('rightSidebarOpen', 'false');
            setLeftSidebarOpen(false);
            setRightSidebarOpen(false);
        }

        // Auto-adjust sidebars based on screen size
        const handleResize = () => {
            if (window.innerWidth >= 1600) {
                // Wide screen: open both sidebars
                setLeftSidebarOpen(true);
                setRightSidebarOpen(true);
            } else {
                // Narrow screen: close both sidebars
                setLeftSidebarOpen(false);
                setRightSidebarOpen(false);
            }
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
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
        setShowIngestData(false);
        fetchMachines(0, true);
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
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 overflow-x-hidden">
            <Header
                user={user}
                connected={connected}
                darkMode={darkMode}
                toggleDarkMode={toggleDarkMode}
                onLogout={handleLogout}
                onOpenSettings={() => setShowConfigSettings(true)}
            />

            {/* Main Container - Prevents horizontal scroll */}
            <div className="flex h-[calc(100vh-73px)] overflow-hidden">
                {/* Mobile Overlay/Backdrop */}
                {(leftSidebarOpen || rightSidebarOpen) && (
                    <div
                        className="wide:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-30 transition-opacity duration-300"
                        onClick={handleOverlayClick}
                        aria-label="Close sidebar"
                    />
                )}

                {/* Left Sidebar - Machines List */}
                <aside
                    className={`
                        fixed wide:relative top-0 left-0 h-full
                        bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
                        transition-all duration-300 ease-in-out z-40
                        ${leftSidebarOpen ? 'translate-x-0 w-80' : '-translate-x-full wide:translate-x-0 w-0 wide:w-0'}
                        overflow-hidden flex-shrink-0
                    `}
                >
                    {leftSidebarOpen && (
                        <Sidebar
                            machines={machines}
                            selectedMachine={selectedMachine}
                            onSelectMachine={(machine) => {
                                setSelectedMachine(machine);
                                if (window.innerWidth < 1600) {
                                    setLeftSidebarOpen(false);
                                }
                            }}
                            hasMore={hasMoreMachines}
                            onLoadMore={loadMoreMachines}
                            loadingMore={loadingMore}
                        />
                    )}
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 overflow-y-auto overflow-x-hidden relative min-w-0">
                    {/* Top Action Bar with Toggle Buttons */}
                    <div className="sticky top-0 z-20 bg-gradient-to-r from-gray-50 to-white dark:from-gray-900 dark:to-gray-850 border-b border-gray-200 dark:border-gray-700 px-4 lg:px-6 py-3">
                        <div className="flex items-center gap-3">
                            {/* Left Sidebar Toggle */}
                            <button
                                onClick={toggleLeftSidebar}
                                className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0"
                                title={leftSidebarOpen ? "Close Machines Panel" : "Open Machines Panel"}
                                aria-label={leftSidebarOpen ? "Close sidebar" : "Open sidebar"}
                            >
                                <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>

                            {/* Breadcrumb/Title */}
                            <div className="flex-1 min-w-0">
                                <h1 className="text-base lg:text-xl font-bold text-gray-900 dark:text-white truncate">
                                    {selectedMachine ? selectedMachine.name : 'Dashboard'}
                                </h1>
                                {selectedMachine && (
                                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                                        {selectedMachine.location} • {selectedMachine.sensor_type}
                                    </p>
                                )}
                            </div>

                            {/* Right Sidebar Toggle */}
                            <button
                                onClick={toggleRightSidebar}
                                className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0 relative"
                                title={rightSidebarOpen ? "Close Alerts Panel" : "Open Alerts Panel"}
                                aria-label={rightSidebarOpen ? "Close alerts" : "Open alerts"}
                            >
                                <svg className="w-6 h-6 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                </svg>
                                {alerts.length > 0 && (
                                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs min-w-[20px] h-5 rounded-full flex items-center justify-center font-bold px-1">
                                        {alerts.length > 9 ? '9+' : alerts.length}
                                    </span>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Main Content with Padding */}
                    <div className="p-4 lg:p-6">
                        <StatsCards machines={machines} />

                        {/* Action Buttons */}
                        <div className="flex flex-wrap gap-2 lg:gap-4 my-4 lg:my-6">
                            <button
                                onClick={() => setShowAddMachine(true)}
                                className="flex items-center gap-2 px-3 lg:px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition shadow-sm text-sm"
                            >
                                <Plus className="w-4 h-4 lg:w-5 lg:h-5" />
                                <span className="hidden sm:inline">Add Machine</span>
                                <span className="sm:hidden">Add</span>
                            </button>
                            <button
                                onClick={() => setShowIngestData(true)}
                                className="flex items-center gap-2 px-3 lg:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-sm text-sm"
                            >
                                <Upload className="w-4 h-4 lg:w-5 lg:h-5" />
                                <span className="hidden sm:inline">Ingest Data</span>
                                <span className="sm:hidden">Ingest</span>
                            </button>
                            {selectedMachine && (
                                <button
                                    onClick={() => setShowMachineHistory(true)}
                                    className="flex items-center gap-2 px-3 lg:px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition shadow-sm text-sm"
                                >
                                    <History className="w-4 h-4 lg:w-5 lg:h-5" />
                                    <span className="hidden sm:inline">Machine History</span>
                                    <span className="sm:hidden">History</span>
                                </button>
                            )}
                        </div>

                        {/* Selected Machine Details */}
                        {selectedMachine && (
                            <div>
                                <Charts data={machineSensorData} />

                                {/* Real-time Info */}
                                <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-3 lg:p-4 mt-4 lg:mt-6 border border-primary-200 dark:border-primary-800">
                                    <div className="text-xs lg:text-sm text-primary-900 dark:text-primary-100">
                                        📡 Real-time: {machineSensorData.length} data points received
                                        {machineSensorData.length > 0 && (
                                            <span className="hidden sm:inline"> • Last update: {new Date(machineSensorData[machineSensorData.length - 1].timestamp).toLocaleTimeString()}</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </main>

                {/* Right Sidebar - Alert Panel */}
                <aside
                    className={`
                        ${rightSidebarOpen ? 'fixed wide:relative' : 'hidden wide:block wide:relative'}
                        top-0 right-0 h-full
                        bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700
                        transition-all duration-300 ease-in-out z-40
                        ${rightSidebarOpen ? 'w-80' : 'wide:w-0'}
                        overflow-hidden flex-shrink-0
                    `}
                >
                    {rightSidebarOpen && (
                        <AlertPanel onClose={() => window.innerWidth < 1600 && setRightSidebarOpen(false)} />
                    )}
                </aside>
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

            <ConfigSettingsModal
                show={showConfigSettings}
                onClose={() => setShowConfigSettings(false)}
            />
        </div>
    );
}
