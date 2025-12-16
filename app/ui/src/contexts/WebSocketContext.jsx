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
                const newData = [...prev, data].slice(-1000); // Keep last 1000 points
                return newData;
            });
        });

        newSocket.on('alert', (alert) => {
            setAlerts(prev => [alert, ...prev].slice(0, 50)); // Keep last 50 alerts

            // Play sound for critical and warning alerts
            if (alert.severity === 'critical' || alert.severity === 'warning') {
                playAlertSound(alert.severity);
            }

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

    // Audio alert helper function
    const playAlertSound = (severity) => {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // Critical: Higher pitch, multiple beeps
            // Warning: Single beep
            const frequency = severity === 'critical' ? 880 : 440; // A5 vs A4
            const beepCount = severity === 'critical' ? 3 : 1;
            const beepDuration = 0.15;
            const beepInterval = 0.2;

            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';

            for (let i = 0; i < beepCount; i++) {
                const startTime = audioContext.currentTime + (i * beepInterval);
                const endTime = startTime + beepDuration;

                gainNode.gain.setValueAtTime(0, startTime);
                gainNode.gain.linearRampToValueAtTime(0.3, startTime + 0.01);
                gainNode.gain.linearRampToValueAtTime(0, endTime);
            }

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + (beepCount * beepInterval) + 0.1);
        } catch (error) {
            console.error('Audio playback failed:', error);
        }
    };

    const subscribeMachine = (machineId) => {
        if (socket) {
            socket.emit('subscribe_machine', { machine_id: machineId });
        }
    };

    const clearAlerts = () => {
        setAlerts([]);
    };

    return (
        <WebSocketContext.Provider value={{ socket, connected, sensorData, alerts, subscribeMachine, clearAlerts }}>
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
