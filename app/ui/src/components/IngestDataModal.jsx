import { useState } from 'react';
import axios from 'axios';
import { X, Upload } from 'lucide-react';

export default function IngestDataModal({ show, onClose, machines, onDataIngested }) {
    const [formData, setFormData] = useState({
        gateway_id: 'Dashboard-Manual',
        machine_id: '',
        temperature: '',
        pressure: '',
        speed: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const selectedMachine = machines.find(m => m.machine_id === formData.machine_id);

            // Postman format
            const payload = {
                gateway_id: formData.gateway_id,
                timestamp: new Date().toISOString(),
                batch: [
                    {
                        machine_id: formData.machine_id,
                        sensor_type: selectedMachine?.sensor_type || 'Temperature',
                        location: selectedMachine?.location || 'Manual Entry',
                        readings: [
                            {
                                timestamp: new Date().toISOString(),
                                temperature: formData.temperature ? parseFloat(formData.temperature) : null,
                                pressure: formData.pressure ? parseFloat(formData.pressure) : null,
                                speed: formData.speed ? parseFloat(formData.speed) : null
                            }
                        ]
                    }
                ]
            };

            const response = await axios.post('/api/v1/data/ingest', payload);

            if (response.data.status === 'success') {
                setSuccess(`Successfully ingested ${response.data.summary.total_readings} reading(s)`);
                setFormData({ gateway_id: 'Dashboard-Manual', machine_id: '', temperature: '', pressure: '', speed: '' });

                if (onDataIngested) onDataIngested(response.data);

                setTimeout(() => {
                    onClose();
                    setSuccess('');
                }, 2000);
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to ingest data');
        } finally {
            setLoading(false);
        }
    };

    if (!show) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                        <Upload className="w-6 h-6" />
                        Manual Data Ingest
                    </h2>
                    <button onClick={onClose} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {error && (
                    <div className="bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-800 text-green-800 dark:text-green-200 px-4 py-3 rounded mb-4">
                        ✓ {success}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Select Machine *
                        </label>
                        <select
                            value={formData.machine_id}
                            onChange={(e) => setFormData({ ...formData, machine_id: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                            required
                        >
                            <option value="">-- Select Machine --</option>
                            {machines.map(machine => (
                                <option key={machine.machine_id} value={machine.machine_id}>
                                    {machine.name} ({machine.location})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                            Sensor Readings (at least one required)
                        </p>

                        <div className="space-y-3">
                            <div>
                                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                                    Temperature (°C)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.temperature}
                                    onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    placeholder="e.g., 72.5"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                                    Pressure (kPa)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.pressure}
                                    onChange={(e) => setFormData({ ...formData, pressure: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    placeholder="e.g., 101.3"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                                    Speed (RPM)
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.speed}
                                    onChange={(e) => setFormData({ ...formData, speed: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    placeholder="e.g., 1500"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-3 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading || !formData.machine_id || (!formData.temperature && !formData.pressure && !formData.speed)}
                            className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 transition"
                        >
                            {loading ? 'Ingesting...' : 'Ingest Data'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
