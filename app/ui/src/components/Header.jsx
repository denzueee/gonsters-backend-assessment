import { Activity, LogOut, Moon, Sun, Clock, Settings } from 'lucide-react';

export default function Header({ user, connected, darkMode, toggleDarkMode, onLogout, onOpenSettings }) {
    const currentTime = new Date().toLocaleTimeString();

    return (
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
            <div className="px-3 lg:px-6 py-3 lg:py-4 flex items-center justify-between gap-2">
                {/* Logo - Compact on mobile */}
                <div className="flex items-center gap-2 flex-shrink-0">
                    <Activity className="w-6 h-6 lg:w-8 lg:h-8 text-primary-600" />
                    <h1 className="text-lg lg:text-2xl font-bold text-gray-900 dark:text-white">GONSTERS</h1>
                </div>

                {/* Right side controls */}
                <div className="flex items-center gap-2 lg:gap-6">
                    {/* Connection status - Hide text on mobile */}
                    <div className={`flex items-center gap-1 lg:gap-2 px-2 lg:px-3 py-1 rounded-full text-xs lg:text-sm ${connected
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
                        }`}>
                        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span className="hidden sm:inline">{connected ? 'Connected' : 'Disconnected'}</span>
                    </div>

                    {/* Time - Hide on mobile */}
                    <div className="hidden md:flex items-center gap-2 text-gray-600 dark:text-gray-400">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm font-mono">{currentTime}</span>
                    </div>

                    {/* Dark mode toggle */}
                    <button
                        onClick={toggleDarkMode}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition flex-shrink-0"
                        title={darkMode ? 'Light mode' : 'Dark mode'}
                    >
                        {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                    </button>

                    {/* Settings Button - Only for Management role */}
                    {user?.role === 'Management' && onOpenSettings && (
                        <button
                            onClick={onOpenSettings}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 flex-shrink-0"
                            title="System Settings"
                        >
                            <Settings className="w-5 h-5" />
                        </button>
                    )}

                    {/* User info and logout */}
                    <div className="flex items-center gap-2 lg:gap-3 border-l border-gray-200 dark:border-gray-700 pl-2 lg:pl-6">
                        {/* User info - Hide on small mobile */}
                        <div className="hidden sm:block text-xs lg:text-sm text-right">
                            <div className="font-medium text-gray-900 dark:text-white">{user?.username}</div>
                            <div className="text-gray-500 dark:text-gray-400">{user?.role}</div>
                        </div>

                        {/* Logout button */}
                        <button
                            onClick={onLogout}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition flex-shrink-0"
                            title="Logout"
                        >
                            <LogOut className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
}
