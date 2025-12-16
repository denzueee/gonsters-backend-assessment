import { useState } from 'react';
import { Bell, AlertTriangle, AlertCircle, Info, X, Filter, Trash2, CheckCircle } from 'lucide-react';
import { useWebSocket } from '../contexts/WebSocketContext';

export default function AlertPanel() {
    const { alerts, clearAlerts } = useWebSocket();
    const [filter, setFilter] = useState('all'); // all, critical, warning, info

    const getSeverityIcon = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical':
                return <AlertCircle className="w-5 h-5 text-red-500" />;
            case 'warning':
                return <AlertTriangle className="w-5 h-5 text-amber-500" />;
            case 'info':
                return <Info className="w-5 h-5 text-blue-500" />;
            default:
                return <Info className="w-5 h-5 text-blue-500" />;
        }
    };

    const getSeverityBg = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical':
                return 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-900/50 hover:bg-red-100 dark:hover:bg-red-950/40';
            case 'warning':
                return 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/50 hover:bg-amber-100 dark:hover:bg-amber-950/40';
            case 'info':
                return 'bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50 hover:bg-blue-100 dark:hover:bg-blue-950/40';
            default:
                return 'bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50 hover:bg-blue-100 dark:hover:bg-blue-950/40';
        }
    };

    const getSeverityTextColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical':
                return 'text-red-900 dark:text-red-100';
            case 'warning':
                return 'text-amber-900 dark:text-amber-100';
            case 'info':
                return 'text-blue-900 dark:text-blue-100';
            default:
                return 'text-blue-900 dark:text-blue-100';
        }
    };

    const filteredAlerts = filter === 'all'
        ? alerts
        : alerts.filter(a => a.severity?.toLowerCase() === filter);

    const criticalCount = alerts.filter(a => a.severity?.toLowerCase() === 'critical').length;
    const warningCount = alerts.filter(a => a.severity?.toLowerCase() === 'warning').length;

    return (
        <div className="w-96 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col shadow-xl" style={{ height: 'calc(100vh - 73px)' }}>
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-850">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                            <Bell className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                                Alerts
                            </h2>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                Real-time monitoring
                            </p>
                        </div>
                    </div>
                    {alerts.length > 0 && (
                        <button
                            onClick={clearAlerts}
                            className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-all duration-200"
                            title="Clear all alerts"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    )}
                </div>

                {/* Status Summary */}
                <div className="grid grid-cols-3 gap-2 mt-3">
                    <div className="bg-white dark:bg-gray-900/50 rounded-lg p-2 text-center border border-gray-200 dark:border-gray-700">
                        <div className="text-lg font-bold text-gray-900 dark:text-white">{alerts.length}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Total</div>
                    </div>
                    <div className="bg-red-50 dark:bg-red-950/30 rounded-lg p-2 text-center border border-red-200 dark:border-red-900/50">
                        <div className="text-lg font-bold text-red-600 dark:text-red-400">{criticalCount}</div>
                        <div className="text-xs text-red-600 dark:text-red-400">Critical</div>
                    </div>
                    <div className="bg-amber-50 dark:bg-amber-950/30 rounded-lg p-2 text-center border border-amber-200 dark:border-amber-900/50">
                        <div className="text-lg font-bold text-amber-600 dark:text-amber-400">{warningCount}</div>
                        <div className="text-xs text-amber-600 dark:text-amber-400">Warning</div>
                    </div>
                </div>

                {/* Filter Tabs */}
                <div className="flex gap-2 mt-3">
                    <button
                        onClick={() => setFilter('all')}
                        className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-all duration-200 ${filter === 'all'
                                ? 'bg-primary-600 text-white shadow-sm'
                                : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600'
                            }`}
                    >
                        All ({alerts.length})
                    </button>
                    <button
                        onClick={() => setFilter('critical')}
                        className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-all duration-200 ${filter === 'critical'
                                ? 'bg-red-600 text-white shadow-sm'
                                : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600'
                            }`}
                    >
                        Critical
                    </button>
                    <button
                        onClick={() => setFilter('warning')}
                        className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-medium transition-all duration-200 ${filter === 'warning'
                                ? 'bg-amber-600 text-white shadow-sm'
                                : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 border border-gray-200 dark:border-gray-600'
                            }`}
                    >
                        Warning
                    </button>
                </div>
            </div>

            {/* Alerts List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {filteredAlerts.length > 0 ? (
                    filteredAlerts.map((alert, idx) => (
                        <div
                            key={idx}
                            className={`p-3 rounded-lg border transition-all duration-200 ${getSeverityBg(alert.severity)}`}
                        >
                            <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 mt-0.5">
                                    {getSeverityIcon(alert.severity)}
                                </div>
                                <div className="flex-1 min-w-0">
                                    {/* Alert Message */}
                                    <div className={`font-semibold text-sm leading-snug mb-2 ${getSeverityTextColor(alert.severity)}`}>
                                        {alert.message}
                                    </div>

                                    {/* Metric Details */}
                                    {alert.metric && (
                                        <div className="flex items-center gap-2 mb-2">
                                            <div className="text-xs font-medium text-gray-700 dark:text-gray-300 bg-white/50 dark:bg-gray-800/50 px-2 py-1 rounded">
                                                {alert.value?.toFixed(1)} {alert.metric === 'temperature' ? '°C' : alert.metric === 'pressure' ? 'PSI' : ''}
                                            </div>
                                            <span className="text-xs text-gray-500 dark:text-gray-400">
                                                / {alert.threshold} {alert.metric === 'temperature' ? '°C' : 'PSI'}
                                            </span>
                                        </div>
                                    )}

                                    {/* Machine Info */}
                                    {alert.machine_name && (
                                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1 flex items-center gap-1">
                                            <span className="font-medium">🏭</span>
                                            <span className="font-medium">{alert.machine_name}</span>
                                            {alert.location && (
                                                <>
                                                    <span className="text-gray-400 dark:text-gray-500">•</span>
                                                    <span>📍 {alert.location}</span>
                                                </>
                                            )}
                                        </div>
                                    )}

                                    {/* Timestamp */}
                                    <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                        <span>🕐</span>
                                        <span>{new Date(alert.timestamp || Date.now()).toLocaleString('id-ID', {
                                            hour: '2-digit',
                                            minute: '2-digit',
                                            second: '2-digit',
                                            day: '2-digit',
                                            month: 'short'
                                        })}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                        <div className="relative mb-4">
                            <div className="w-20 h-20 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-full flex items-center justify-center">
                                <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
                            </div>
                            <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full animate-ping opacity-75"></div>
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 font-semibold text-sm mb-1">
                            {filter === 'all' ? 'All Systems Normal' : `No ${filter} alerts`}
                        </p>
                        <p className="text-gray-500 dark:text-gray-400 text-xs max-w-xs">
                            {filter === 'all'
                                ? 'All machines are operating within normal parameters'
                                : `No ${filter} level alerts at this time`
                            }
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
