import { Activity, TrendingUp, AlertTriangle, XCircle } from 'lucide-react';

export default function StatsCards({ machines }) {
    const stats = {
        total: machines.length,
        active: machines.filter(m => m.status?.toLowerCase() === 'active').length,
        maintenance: machines.filter(m => m.status?.toLowerCase() === 'maintenance').length,
        inactive: machines.filter(m => m.status?.toLowerCase() === 'inactive').length
    };

    const cards = [
        { label: 'Total Machines', value: stats.total, icon: Activity, color: 'text-primary-600', bg: 'bg-primary-50 dark:bg-primary-900/20' },
        { label: 'Active', value: stats.active, icon: TrendingUp, color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-900/20' },
        { label: 'Maintenance', value: stats.maintenance, icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50 dark:bg-yellow-900/20' },
        { label: 'Inactive', value: stats.inactive, icon: XCircle, color: 'text-gray-600', bg: 'bg-gray-50 dark:bg-gray-900/20' }
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-6">
            {cards.map((card, idx) => {
                const Icon = card.icon;
                return (
                    <div key={idx} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 lg:p-6 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-xs lg:text-sm text-gray-600 dark:text-gray-400">{card.label}</div>
                                <div className={`text-2xl lg:text-3xl font-bold mt-1 lg:mt-2 ${card.color}`}>{card.value}</div>
                            </div>
                            <div className={`p-2 lg:p-3 rounded-lg ${card.bg}`}>
                                <Icon className={`w-5 h-5 lg:w-6 lg:h-6 ${card.color}`} />
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
