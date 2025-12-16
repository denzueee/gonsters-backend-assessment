import { useState, useEffect } from 'react';
import { X, Save, RotateCcw, Settings, AlertTriangle, Thermometer, Gauge, Clock } from 'lucide-react';
import axios from 'axios';

export default function ConfigSettingsModal({ show, onClose }) {
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [config, setConfig] = useState({
        max_temperature_threshold: '80.0',
        min_temperature_threshold: '50.0',
        max_pressure_threshold: '150.0',
        inactivity_timeout: '3600',
        alert_email: 'alerts@factory.com',
        data_retention_days: '365',
    });
    const [originalConfig, setOriginalConfig] = useState({});
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (show) {
            fetchConfig();
        }
    }, [show]);

    const fetchConfig = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await axios.get('/api/v1/config');
            const configData = response.data.config;
            setConfig(configData);
            setOriginalConfig(configData);
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to load configuration');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (settingName, settingValue) => {
        setSaving(true);
        setError('');
        setSuccess('');
        try {
            await axios.post('/api/v1/config/update', {
                setting_name: settingName,
                setting_value: settingValue,
            });
            setSuccess(`${settingName} updated successfully!`);
            setOriginalConfig({ ...originalConfig, [settingName]: settingValue });
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to update configuration');
        } finally {
            setSaving(false);
        }
    };

    const handleReset = async () => {
        if (!confirm('Are you sure you want to reset all settings to default values?')) {
            return;
        }

        setSaving(true);
        setError('');
        setSuccess('');
        try {
            await axios.post('/api/v1/config/reset');
            setSuccess('Configuration reset to defaults!');
            await fetchConfig();
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to reset configuration');
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (key, value) => {
        setConfig({ ...config, [key]: value });
    };

    const hasChanges = (key) => {
        return config[key] !== originalConfig[key];
    };

    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden border border-gray-200 dark:border-gray-700">
                {/* Header */}
                <div className="bg-gradient-to-br from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 p-6 text-white">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                                <Settings className="w-6 h-6" />
                            </div>
                            <div>
                                <h2 className="text-xl md:text-2xl font-bold">System Configuration</h2>
                                <p className="text-primary-100 text-xs md:text-sm mt-1">
                                    Manage alert thresholds and system settings
                                </p>
                            </div>
                        </div>
                        <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
                    {/* Status Messages */}
                    {error && (
                        <div className="mb-4 p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-lg flex items-start gap-3">
                            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                                <p className="font-semibold text-red-900 dark:text-red-100 text-sm">Error</p>
                                <p className="text-red-700 dark:text-red-300 text-sm mt-1">{error}</p>
                            </div>
                        </div>
                    )}

                    {success && (
                        <div className="mb-4 p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900/50 rounded-lg flex items-start gap-3">
                            <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                <svg
                                    className="w-3 h-3 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={3}
                                        d="M5 13l4 4L19 7"
                                    />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <p className="font-semibold text-green-900 dark:text-green-100 text-sm">Success</p>
                                <p className="text-green-700 dark:text-green-300 text-sm mt-1">{success}</p>
                            </div>
                        </div>
                    )}

                    {loading ? (
                        <div className="flex justify-center items-center py-12">
                            <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Temperature Thresholds Section */}
                            <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/20 dark:to-red-950/20 rounded-xl p-5 border border-orange-200 dark:border-orange-900/50">
                                <div className="flex items-center gap-2 mb-4">
                                    <Thermometer className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                        Temperature Thresholds
                                    </h3>
                                </div>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Maximum Temperature (°C)
                                        </label>
                                        <div className="flex flex-col sm:flex-row gap-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={config.max_temperature_threshold}
                                                onChange={(e) =>
                                                    handleChange('max_temperature_threshold', e.target.value)
                                                }
                                                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white font-medium text-lg"
                                            />
                                            {hasChanges('max_temperature_threshold') && (
                                                <button
                                                    onClick={() =>
                                                        handleSave(
                                                            'max_temperature_threshold',
                                                            config.max_temperature_threshold
                                                        )
                                                    }
                                                    disabled={saving}
                                                    className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                                                >
                                                    <Save className="w-4 h-4" />
                                                    Save
                                                </button>
                                            )}
                                        </div>
                                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                                            Alert will trigger when temperature exceeds this value
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Minimum Temperature (°C)
                                        </label>
                                        <div className="flex flex-col sm:flex-row gap-2">
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={config.min_temperature_threshold}
                                                onChange={(e) =>
                                                    handleChange('min_temperature_threshold', e.target.value)
                                                }
                                                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white font-medium text-lg"
                                            />
                                            {hasChanges('min_temperature_threshold') && (
                                                <button
                                                    onClick={() =>
                                                        handleSave(
                                                            'min_temperature_threshold',
                                                            config.min_temperature_threshold
                                                        )
                                                    }
                                                    disabled={saving}
                                                    className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                                                >
                                                    <Save className="w-4 h-4" />
                                                    Save
                                                </button>
                                            )}
                                        </div>
                                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                                            Alert will trigger when temperature falls below this value
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Pressure Threshold Section */}
                            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-xl p-5 border border-blue-200 dark:border-blue-900/50">
                                <div className="flex items-center gap-2 mb-4">
                                    <Gauge className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                        Pressure Threshold
                                    </h3>
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                        Maximum Pressure (PSI)
                                    </label>
                                    <div className="flex flex-col sm:flex-row gap-2">
                                        <input
                                            type="number"
                                            step="0.1"
                                            value={config.max_pressure_threshold}
                                            onChange={(e) => handleChange('max_pressure_threshold', e.target.value)}
                                            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white font-medium text-lg"
                                        />
                                        {hasChanges('max_pressure_threshold') && (
                                            <button
                                                onClick={() =>
                                                    handleSave('max_pressure_threshold', config.max_pressure_threshold)
                                                }
                                                disabled={saving}
                                                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                                            >
                                                <Save className="w-4 h-4" />
                                                Save
                                            </button>
                                        )}
                                    </div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                                        Alert will trigger when pressure exceeds this value
                                    </p>
                                </div>
                            </div>

                            {/* Monitoring Settings Section */}
                            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-950/20 dark:to-indigo-950/20 rounded-xl p-5 border border-purple-200 dark:border-purple-900/50">
                                <div className="flex items-center gap-2 mb-4">
                                    <Clock className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                        Monitoring Settings
                                    </h3>
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                        Inactivity Timeout (Seconds)
                                    </label>
                                    <div className="flex flex-col sm:flex-row gap-2">
                                        <input
                                            type="number"
                                            value={config.inactivity_timeout}
                                            onChange={(e) => handleChange('inactivity_timeout', e.target.value)}
                                            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white font-medium text-lg"
                                        />
                                        {hasChanges('inactivity_timeout') && (
                                            <button
                                                onClick={() =>
                                                    handleSave('inactivity_timeout', config.inactivity_timeout)
                                                }
                                                disabled={saving}
                                                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                                            >
                                                <Save className="w-4 h-4" />
                                                Save
                                            </button>
                                        )}
                                    </div>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                                        Machine will be marked as "Inactive" if no data is received for this duration
                                    </p>
                                </div>
                            </div>

                            {/* Other Settings Section */}
                            <div className="bg-gradient-to-br from-gray-50 to-slate-50 dark:from-gray-800 dark:to-slate-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
                                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Other Settings</h3>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Alert Email
                                        </label>
                                        <div className="flex flex-col sm:flex-row gap-2">
                                            <input
                                                type="email"
                                                value={config.alert_email}
                                                onChange={(e) => handleChange('alert_email', e.target.value)}
                                                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                                            />
                                            {hasChanges('alert_email') && (
                                                <button
                                                    onClick={() => handleSave('alert_email', config.alert_email)}
                                                    disabled={saving}
                                                    className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                                                >
                                                    <Save className="w-4 h-4" />
                                                    Save
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                            Data Retention (Days)
                                        </label>
                                        <div className="flex flex-col sm:flex-row gap-2">
                                            <input
                                                type="number"
                                                value={config.data_retention_days}
                                                onChange={(e) => handleChange('data_retention_days', e.target.value)}
                                                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                                            />
                                            {hasChanges('data_retention_days') && (
                                                <button
                                                    onClick={() =>
                                                        handleSave('data_retention_days', config.data_retention_days)
                                                    }
                                                    disabled={saving}
                                                    className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                                                >
                                                    <Save className="w-4 h-4" />
                                                    Save
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-850">
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-2">
                        <button
                            onClick={handleReset}
                            disabled={saving}
                            className="px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 rounded-lg transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Reset to Defaults
                        </button>
                        <button
                            onClick={onClose}
                            className="px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
