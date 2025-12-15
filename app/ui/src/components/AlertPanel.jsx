import { Bell, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import { useWebSocket } from '../contexts/WebSocketContext';

export default function AlertPanel() {
    const { alerts } = useWebSocket();

    const getSeverityIcon = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return <AlertCircle className="w-5 h-5 text-red-500" />;
            case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
            default: return <Info className="w-5 h-5 text-blue-500" />;
        }
    };

    const getSeverityBg = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
            case 'warning': return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
            default: return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
        }
    };

    return (
        <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 h-screen overflow-y-auto">
            <div className="p-4">
                <div className="flex items-center gap-2 mb-4">
                    <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Alerts ({alerts.length})
                    </h2>
                </div>

                {alerts.length > 0 ? (
                    <div className="space-y-3">
                        {alerts.map((alert, idx) => (
                            <div
                                key={idx}
                                className={`p-3 rounded-lg border ${getSeverityBg(alert.severity)}`}
                            >
                                <div className="flex items-start gap-2">
                                    {getSeverityIcon(alert.severity)}
                                    <div className="flex-1">
                                        <div className="font-medium text-sm text-gray-900 dark:text-white">
                                            {alert.message}
                                        </div>
                                        {alert.machine_id && (
                                            <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                                Machine: {alert.machine_id}
                                            </div>
                                        )}
                                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                            {new Date(alert.timestamp || Date.now()).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12">
                        <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300 dark:text-gray-600" />
                        <p className="text-gray-500 dark:text-gray-400 text-sm">No alerts</p>
                        <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">
                            You'll see real-time alerts here
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
