const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Settings
    getSettings: () => ipcRenderer.invoke('get-settings'),
    saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
    
    // Chat and Backend
    sendToBackend: (message) => ipcRenderer.invoke('send-to-backend', message),
    takeScreenshot: () => ipcRenderer.invoke('take-screenshot'),
    
    // Window controls
    closeWindow: (windowName) => ipcRenderer.invoke('close-window', windowName),
    minimizeWindow: (windowName) => ipcRenderer.invoke('minimize-window', windowName),
    
    // Authentication
    authenticateGoogle: (idToken) => ipcRenderer.invoke('authenticate-google', idToken),
    
    // Event listeners
    onBackendMessage: (callback) => {
        ipcRenderer.on('backend-message', (event, message) => callback(message));
    },
    
    removeBackendMessageListener: () => {
        ipcRenderer.removeAllListeners('backend-message');
    },
    
    // Window events
    onWindowMessage: (channel, callback) => {
        const validChannels = ['window-close', 'window-minimize'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, data) => callback(data));
        }
    },
    
    // Theme
    getCurrentTheme: () => {
        return localStorage.getItem('theme') || 'dark';
    },
    
    setTheme: (theme) => {
        localStorage.setItem('theme', theme);
        document.body.setAttribute('data-theme', theme);
    },
    
    // Storage
    getStoredValue: (key) => {
        return localStorage.getItem(key);
    },
    
    setStoredValue: (key, value) => {
        localStorage.setItem(key, value);
    },
    
    // System info
    getPlatform: () => process.platform,
    
    // Development helpers
    isDev: () => process.env.NODE_ENV === 'development',
    
    // Window dragging
    startDrag: () => {
        if (window.electronAPI && window.electronAPI.startDrag) {
            ipcRenderer.send('start-drag');
        }
    },
    
    // Google Sign-In
    initGoogleAuth: (clientId) => {
        return new Promise((resolve, reject) => {
            // Load Google Sign-In script
            const script = document.createElement('script');
            script.src = 'https://accounts.google.com/gsi/client';
            script.onload = () => {
                window.google.accounts.id.initialize({
                    client_id: clientId,
                    callback: async (response) => {
                        try {
                            const authResult = await window.electronAPI.authenticateGoogle(response.credential);
                            resolve(authResult);
                        } catch (error) {
                            reject(error);
                        }
                    }
                });
                resolve(true);
            };
            script.onerror = () => reject(new Error('Failed to load Google Sign-In'));
            document.head.appendChild(script);
        });
    },
    
    // Render Google Sign-In button
    renderGoogleButton: (elementId) => {
        if (window.google && window.google.accounts) {
            window.google.accounts.id.renderButton(
                document.getElementById(elementId),
                { theme: 'outline', size: 'large' }
            );
        }
    },
    
    // Audio recording
    startAudioRecording: () => {
        return new Promise((resolve, reject) => {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    window.audioStream = stream;
                    window.mediaRecorder = new MediaRecorder(stream);
                    window.audioChunks = [];
                    
                    window.mediaRecorder.ondataavailable = (event) => {
                        window.audioChunks.push(event.data);
                    };
                    
                    window.mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(window.audioChunks, { type: 'audio/wav' });
                        resolve(audioBlob);
                    };
                    
                    window.mediaRecorder.start();
                    resolve(true);
                })
                .catch(reject);
        });
    },
    
    stopAudioRecording: () => {
        return new Promise((resolve) => {
            if (window.mediaRecorder && window.mediaRecorder.state !== 'inactive') {
                window.mediaRecorder.onstop = () => {
                    if (window.audioStream) {
                        window.audioStream.getTracks().forEach(track => track.stop());
                    }
                    resolve();
                };
                window.mediaRecorder.stop();
            } else {
                resolve();
            }
        });
    },
    
    // File operations
    saveFile: (data, filename) => {
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
});

// Theme initialization
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = window.electronAPI.getCurrentTheme();
    document.body.setAttribute('data-theme', savedTheme);
});

// Error handling
window.addEventListener('error', (event) => {
    console.error('Renderer process error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});