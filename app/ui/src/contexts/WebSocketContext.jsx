import { createContext, useContext, useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);
    const [connected, setConnected] = useState(false);
    const [sensorData, setSensorData] = useState([]);
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const newSocket = io('/', {
            query: { token },
            transports: ['websocket', 'polling']
        });

        newSocket.on('connect', () => {
            console.log('WebSocket connected');
            setConnected(true);
            newSocket.emit('subscribe_all');
        });

        newSocket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            setConnected(false);
        });

        newSocket.on('sensor_data', (data) => {
            setSensorData(prev => {
                const newData = [...prev, data].slice(-30); // Keep last 30 points
                return newData;
            });
        });

        newSocket.on('alert', (alert) => {
            setAlerts(prev => [alert, ...prev].slice(0, 50)); // Keep last 50 alerts

            // Browser notification
            if (Notification.permission === 'granted') {
                new Notification('GONSTERS Alert', {
                    body: alert.message,
                    icon: '/vite.svg'
                });
            }
        });

        setSocket(newSocket);

        return () => {
            newSocket.disconnect();
        };
    }, []);

    // Request notification permission
    useEffect(() => {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }, []);

    const subscribeMachine = (machineId) => {
        if (socket) {
            socket.emit('subscribe_machine', { machine_id: machineId });
        }
    };

    return (
        <WebSocketContext.Provider value={{ socket, connected, sensorData, alerts, subscribeMachine }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within WebSocketProvider');
    }
    return context;
};
