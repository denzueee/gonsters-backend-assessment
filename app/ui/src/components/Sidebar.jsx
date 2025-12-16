import { useState, useRef, useCallback } from 'react';
import { Search, Filter } from 'lucide-react';

export default function Sidebar({
    machines,
    selectedMachine,
    onSelectMachine,
    onFilterChange,
    hasMore,
    onLoadMore,
    loadingMore,
}) {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [locationFilter, setLocationFilter] = useState('all');

    const observer = useRef();
    const lastMachineRef = useCallback(
        (node) => {
            if (loadingMore) return;
            if (observer.current) observer.current.disconnect();

            observer.current = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting && hasMore) {
                    if (onLoadMore) onLoadMore();
                }
            });

            if (node) observer.current.observe(node);
        },
        [loadingMore, hasMore, onLoadMore]
    );

    const handleSearchChange = (value) => {
        setSearchTerm(value);
        applyFilters(value, statusFilter, locationFilter);
    };

    const handleStatusChange = (value) => {
        setStatusFilter(value);
        applyFilters(searchTerm, value, locationFilter);
    };

    const handleLocationChange = (value) => {
        setLocationFilter(value);
        applyFilters(searchTerm, statusFilter, value);
    };

    const applyFilters = (search, status, location) => {
        if (onFilterChange) {
            onFilterChange({ search, status, location });
        }
    };

    const filteredMachines = machines.filter((machine) => {
        const matchesSearch =
            machine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            machine.location.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || machine.status?.toLowerCase() === statusFilter;
        const matchesLocation = locationFilter === 'all' || machine.location === locationFilter;
        return matchesSearch && matchesStatus && matchesLocation;
    });

    const uniqueLocations = [...new Set(machines.map((m) => m.location))];

    const getStatusColor = (status) => {
        switch (status?.toLowerCase()) {
            case 'active':
                return 'bg-green-500';
            case 'maintenance':
                return 'bg-yellow-500';
            case 'inactive':
                return 'bg-gray-500';
            default:
                return 'bg-gray-400';
        }
    };

    return (
        <div className="w-full h-full bg-white dark:bg-gray-800 overflow-y-auto">
            <div className="p-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Machines ({filteredMachines.length})
                </h2>

                {/* Search */}
                <div className="relative mb-3">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => handleSearchChange(e.target.value)}
                        placeholder="Search machines..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                </div>

                {/* Status Filter */}
                <div className="mb-3">
                    <div className="flex items-center gap-2 mb-2">
                        <Filter className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Status</span>
                    </div>
                    <select
                        value={statusFilter}
                        onChange={(e) => handleStatusChange(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                        <option value="all">All Status</option>
                        <option value="active">Active</option>
                        <option value="maintenance">Maintenance</option>
                        <option value="inactive">Inactive</option>
                    </select>
                </div>

                {/* Location Filter */}
                <div className="mb-4">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Location</span>
                    <select
                        value={locationFilter}
                        onChange={(e) => handleLocationChange(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                        <option value="all">All Locations</option>
                        {uniqueLocations.map((loc) => (
                            <option key={loc} value={loc}>
                                {loc}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Machine List */}
                <div className="space-y-2">
                    {filteredMachines.map((machine, index) => {
                        const isLast = index === filteredMachines.length - 1;
                        return (
                            <button
                                key={machine.machine_id}
                                ref={isLast ? lastMachineRef : null}
                                onClick={() => onSelectMachine(machine)}
                                className={`w-full text-left p-3 rounded-lg border transition ${
                                    selectedMachine?.machine_id === machine.machine_id
                                        ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500'
                                        : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                                }`}
                            >
                                <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full ${getStatusColor(machine.status)}`}></div>
                                    <div className="font-medium text-gray-900 dark:text-white text-sm">
                                        {machine.name}
                                    </div>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{machine.location}</div>
                                <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                                    {machine.sensor_type}
                                </div>
                            </button>
                        );
                    })}

                    {loadingMore && (
                        <div className="flex justify-center p-2">
                            <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    )}
                </div>

                {filteredMachines.length === 0 && (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">No machines found</div>
                )}
            </div>
        </div>
    );
}
