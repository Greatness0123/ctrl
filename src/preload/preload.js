const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Settings
    getSettings: () => ipcRenderer.invoke('get-settings'),
    saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
    
    // User data
    getUserData: () => ipcRenderer.invoke('get-user-data'),
    authenticateUser: (userData) => ipcRenderer.invoke('authenticate-user', userData),
    signOut: () => ipcRenderer.invoke('sign-out'),
    
    // Backend communication
    sendToBackend: (message) => ipcRenderer.invoke('send-to-backend', message),
    takeScreenshot: () => ipcRenderer.invoke('take-screenshot'),
    
    // Window management
    closeWindow: (windowName) => ipcRenderer.invoke('close-window', windowName),
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // Legacy for floating button
    sendToMain: (channel, data) => {
        const validChannels = ['toggle-chat', 'open-settings'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    
    // Listen for messages from main process
    onBackendMessage: (callback) => {
        ipcRenderer.on('backend-message', (event, message) => callback(message));
    },
    
    onInteractionToggled: (callback) => {
        ipcRenderer.on('interaction-toggled', (event, enabled) => callback(enabled));
    },
    
    // Remove listeners
    removeAllListeners: (channel) => {
        ipcRenderer.removeAllListeners(channel);
    }
});