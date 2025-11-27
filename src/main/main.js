const { app, BrowserWindow, globalShortcut, session, ipcMain, Menu, shell, nativeTheme } = require('electron');
const path = require('path');
const fs = require('fs');
const { PythonShell } = require('python-shell');
const Store = require('electron-store');
const { execSync } = require('child_process');

const store = new Store();

class ControlApp {
    constructor() {
        this.mainWindow = null;
        this.chatWindow = null;
        this.settingsWindow = null;
        this.floatingButton = null;
        this.pythonBackend = null;
        this.isReady = false;
        this.pythonReady = false;
        this.pythonPath = null;
        this.user = null;
        this.interactionEnabled = true; // Green state (can't interact with desktop)
        
        this.settings = {
            hotkey: 'CommandOrControl+Space',
            interactionHotkey: 'Alt+A',
            theme: 'dark',
            autoStart: true,
            googleApiKey: '',
            geminiApiKey: '',
            plan: 'free',
            floatingButton: {
                enabled: true,
                position: { x: 100, y: 100 },
                size: 50,
                edgeSticking: true
            }
        };
        
        this.loadSettings();
        this.setupEventHandlers();
    }
    
    loadSettings() {
        const stored = store.get('settings');
        if (stored) {
            this.settings = { ...this.settings, ...stored };
        }
        
        // Load user data if available
        const userData = store.get('userData');
        if (userData) {
            this.user = userData;
        }
    }
    
    saveSettings() {
        store.set('settings', this.settings);
    }
    
    saveUserData(userData) {
        this.user = userData;
        store.set('userData', userData);
    }
    
    getPythonPath() {
        if (this.pythonPath) {
            return this.pythonPath;
        }

        const isWindows = process.platform === 'win32';
        const candidates = isWindows ? ['python', 'python3', 'py'] : ['python3', 'python'];
        
        for (const cmd of candidates) {
            try {
                execSync(`${cmd} --version`, { stdio: 'pipe' });
                this.pythonPath = cmd;
                console.log(`[MAIN] Found Python at: ${cmd}`);
                return cmd;
            } catch (e) {
                continue;
            }
        }

        console.log('[MAIN] Python not found in standard paths, attempting default');
        return candidates[0];
    }
    
    setupEventHandlers() {
        app.whenReady().then(() => {
            this.initialize();
        });
        
        app.on('window-all-closed', () => {
            // Don't quit on window close - keep main process running
            if (process.platform === 'darwin') {
                app.dock.hide();
            }
        });
        
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0 && this.user) {
                this.createFloatingButton();
            }
        });
        
        app.on('before-quit', () => {
            this.cleanup();
        });
        
        this.setupIPCHandlers();
    }
    
    async initialize() {
        try {
            console.log('[MAIN] Initializing Control AI...');
            
            // Hide dock icon on macOS
            if (process.platform === 'darwin') {
                app.dock.hide();
            }
            
            await this.initializePythonBackend();
            
            // Only show entry point if user is not authenticated
            if (!this.user) {
                this.createMainWindow();
            } else {
                // User is authenticated, create floating button directly
                this.createFloatingButton();
            }
            
            this.setupGlobalHotkeys();
            
            this.isReady = true;
            console.log('[MAIN] Control AI initialized successfully');
            
        } catch (error) {
            console.error('[MAIN] Initialization error:', error);
        }
    }
    
    async initializePythonBackend() {
        return new Promise((resolve, reject) => {
            try {
                const pythonPath = this.getPythonPath();
                
                console.log('[MAIN] Starting Python backend with:', pythonPath);
                
                const options = {
                    mode: 'text',
                    pythonPath: pythonPath,
                    pythonOptions: ['-u'],
                    scriptPath: path.join(__dirname, '../../'),
                    args: []
                };
                
                this.pythonBackend = new PythonShell('main.py', options);
                
                this.pythonBackend.on('message', (message) => {
                    console.log('[MAIN] Python Backend:', message);
                    
                    if (this.chatWindow && this.chatWindow.webContents) {
                        try {
                            this.chatWindow.webContents.send('backend-message', message);
                        } catch (e) {
                            console.error('[MAIN] Error sending to chat window:', e);
                        }
                    }
                });
                
                this.pythonBackend.on('stderr', (stderr) => {
                    console.error('[MAIN] Python Error:', stderr);
                });
                
                this.pythonBackend.on('close', () => {
                    console.log('[MAIN] Python Backend closed');
                    this.pythonReady = false;
                });
                
                this.pythonBackend.on('error', (err) => {
                    console.error('[MAIN] Python spawn error:', err);
                });
                
                console.log('[MAIN] Python backend started, waiting for initialization...');
                this.pythonReady = true;
                
                setTimeout(() => {
                    console.log('[MAIN] Python backend ready');
                    resolve();
                }, 2000);
                
            } catch (error) {
                console.error('[MAIN] Error initializing Python backend:', error);
                reject(error);
            }
        });
    }
    
    createMainWindow() {
        console.log('[MAIN] Creating main authentication window...');
        
        this.mainWindow = new BrowserWindow({
            width: 450,
            height: 600,
            show: false,
            frame: true,
            alwaysOnTop: false,
            skipTaskbar: false,
            resizable: false,
            center: true,
            webSecurity: false,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                preload: path.join(__dirname, '../preload/preload.js')
            }
        });
        
        const indexPath = path.join(__dirname, '../renderer/index.html');
        console.log('[MAIN] Loading index from:', indexPath);
        
        this.mainWindow.loadFile(indexPath).catch(err => {
            console.error('[MAIN] Failed to load main window:', err);
        });
        
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
        });
        
        this.mainWindow.on('close', (event) => {
            if (!app.isQuitting) {
                event.preventDefault();
                this.mainWindow.hide();
                // Create floating button when entry point is hidden
                if (this.user) {
                    this.createFloatingButton();
                }
            }
        });
        
        console.log('[MAIN] Main authentication window created');
    }
    
    createFloatingButton() {
        if (this.floatingButton && !this.floatingButton.isDestroyed()) {
            return;
        }
        
        console.log('[MAIN] Creating floating button window...');
        
        const { x, y } = this.settings.floatingButton.position;
        const size = this.settings.floatingButton.size;
        
        this.floatingButton = new BrowserWindow({
            width: size,
            height: size,
            x: x,
            y: y,
            frame: false,
            alwaysOnTop: true,
            skipTaskbar: true,
            resizable: false,
            movable: false,
            transparent: true,
            hasShadow: false,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                preload: path.join(__dirname, '../preload/preload.js')
            }
        });
        
        const floatingPath = path.join(__dirname, '../renderer/floating-button.html');
        this.floatingButton.loadFile(floatingPath).catch(err => {
            console.error('[MAIN] Failed to load floating button:', err);
        });
        
        this.floatingButton.setIgnoreMouseEvents(false);
        
        // Setup edge sticking
        this.setupEdgeSticking();
        
        this.floatingButton.on('moved', () => {
            const bounds = this.floatingButton.getBounds();
            
            if (this.settings.floatingButton.edgeSticking) {
                const { screen } = require('electron');
                const primaryDisplay = screen.getPrimaryDisplay();
                const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
                
                // Stick to edges with magnetic effect
                const snapDistance = 30;
                
                if (bounds.x < snapDistance) bounds.x = 0;
                if (bounds.y < snapDistance) bounds.y = 0;
                if (bounds.x + size > screenWidth - snapDistance) bounds.x = screenWidth - size;
                if (bounds.y + size > screenHeight - snapDistance) bounds.y = screenHeight - size;
                
                this.floatingButton.setPosition(bounds.x, bounds.y);
            }
            
            this.settings.floatingButton.position = { x: bounds.x, y: bounds.y };
            this.saveSettings();
        });
        
        // Hide floating button when chat window is shown
        if (this.chatWindow && this.chatWindow.isVisible()) {
            this.floatingButton.hide();
        }
        
        console.log('[MAIN] Floating button created');
    }
    
    setupEdgeSticking() {
        const { screen } = require('electron');
        
        // Monitor screen changes for edge sticking
        screen.on('display-metrics-changed', () => {
            if (this.floatingButton && !this.floatingButton.isDestroyed()) {
                const bounds = this.floatingButton.getBounds();
                const primaryDisplay = screen.getPrimaryDisplay();
                const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
                const size = this.settings.floatingButton.size;
                
                // Keep button within screen bounds
                bounds.x = Math.max(0, Math.min(bounds.x, screenWidth - size));
                bounds.y = Math.max(0, Math.min(bounds.y, screenHeight - size));
                
                this.floatingButton.setPosition(bounds.x, bounds.y);
                this.settings.floatingButton.position = { x: bounds.x, y: bounds.y };
                this.saveSettings();
            }
        });
    }
    
    createChatWindow() {
        console.log('[MAIN] Creating chat window...');
        
        if (this.chatWindow) {
            if (this.chatWindow.isVisible()) {
                this.chatWindow.focus();
            } else {
                this.chatWindow.show();
                this.chatWindow.focus();
            }
            return;
        }
        
        const { screen } = require('electron');
        const primaryDisplay = screen.getPrimaryDisplay();
        const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
        
        this.chatWindow = new BrowserWindow({
            width: screenWidth,
            height: screenHeight,
            x: 0,
            y: 0,
            frame: false,
            alwaysOnTop: true,
            skipTaskbar: true,
            resizable: false,
            movable: false,
            transparent: true,
            hasShadow: false,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                preload: path.join(__dirname, '../preload/preload.js')
            }
        });
        
        const chatPath = path.join(__dirname, '../renderer/chat.html');
        this.chatWindow.loadFile(chatPath).catch(err => {
            console.error('[MAIN] Failed to load chat window:', err);
        });
        
        this.chatWindow.on('closed', () => {
            this.chatWindow = null;
            console.log('[MAIN] Chat window closed');
        });
        
        // Hide floating button when chat window is shown
        if (this.floatingButton && !this.floatingButton.isDestroyed()) {
            this.floatingButton.hide();
        }
        
        console.log('[MAIN] Chat window created');
    }
    
    hideChatWindow() {
        if (this.chatWindow && !this.chatWindow.isDestroyed()) {
            this.chatWindow.hide();
            
            // Show floating button when chat window is hidden
            if (this.floatingButton && !this.floatingButton.isDestroyed()) {
                this.floatingButton.show();
            }
            
            console.log('[MAIN] Chat window hidden');
        }
    }
    
    createSettingsWindow() {
        console.log('[MAIN] Creating settings window...');
        
        if (this.settingsWindow) {
            this.settingsWindow.focus();
            return;
        }
        
        const { screen } = require('electron');
        const primaryDisplay = screen.getPrimaryDisplay();
        const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
        
        this.settingsWindow = new BrowserWindow({
            width: screenWidth,
            height: screenHeight,
            x: 0,
            y: 0,
            frame: false,
            alwaysOnTop: true,
            skipTaskbar: true,
            resizable: false,
            movable: false,
            transparent: true,
            hasShadow: false,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                preload: path.join(__dirname, '../preload/preload.js')
            }
        });
        
        const settingsPath = path.join(__dirname, '../renderer/settings.html');
        this.settingsWindow.loadFile(settingsPath).catch(err => {
            console.error('[MAIN] Failed to load settings window:', err);
        });
        
        this.settingsWindow.on('closed', () => {
            this.settingsWindow = null;
            console.log('[MAIN] Settings window closed');
        });
        
        console.log('[MAIN] Settings window created');
    }
    
    setupGlobalHotkeys() {
        console.log('[MAIN] Setting up global hotkeys...');
        
        // Chat window toggle hotkey (Ctrl+Space or Cmd+Space)
        if (this.chatHotkey) {
            globalShortcut.unregister(this.chatHotkey);
        }
        
        const chatRet = globalShortcut.register(this.settings.hotkey, () => {
            console.log('[MAIN] Chat hotkey pressed:', this.settings.hotkey);
            this.toggleChatWindow();
        });
        
        if (!chatRet) {
            console.error('[MAIN] Failed to register chat hotkey:', this.settings.hotkey);
        } else {
            console.log('[MAIN] Chat hotkey registered successfully');
            this.chatHotkey = this.settings.hotkey;
        }
        
        // Interaction toggle hotkey (Alt+A)
        if (this.interactionHotkey) {
            globalShortcut.unregister(this.interactionHotkey);
        }
        
        const interactionRet = globalShortcut.register(this.settings.interactionHotkey, () => {
            console.log('[MAIN] Interaction hotkey pressed:', this.settings.interactionHotkey);
            this.toggleInteraction();
        });
        
        if (!interactionRet) {
            console.error('[MAIN] Failed to register interaction hotkey:', this.settings.interactionHotkey);
        } else {
            console.log('[MAIN] Interaction hotkey registered successfully');
            this.interactionHotkey = this.settings.interactionHotkey;
        }
    }
    
    toggleChatWindow() {
        console.log('[MAIN] Toggling chat window...');
        
        if (!this.user) {
            console.log('[MAIN] User not authenticated, showing main window');
            if (this.mainWindow) {
                this.mainWindow.show();
                this.mainWindow.focus();
            } else {
                this.createMainWindow();
            }
            return;
        }
        
        if (this.chatWindow) {
            if (this.chatWindow.isVisible()) {
                this.hideChatWindow();
            } else {
                this.chatWindow.show();
                this.chatWindow.focus();
                if (this.floatingButton && !this.floatingButton.isDestroyed()) {
                    this.floatingButton.hide();
                }
            }
        } else {
            this.createChatWindow();
        }
    }
    
    toggleInteraction() {
        this.interactionEnabled = !this.interactionEnabled;
        
        // Update all windows with new interaction state
        if (this.chatWindow && !this.chatWindow.isDestroyed()) {
            this.chatWindow.webContents.send('interaction-toggled', this.interactionEnabled);
        }
        
        if (this.settingsWindow && !this.settingsWindow.isDestroyed()) {
            this.settingsWindow.webContents.send('interaction-toggled', this.interactionEnabled);
        }
        
        console.log('[MAIN] Interaction toggled:', this.interactionEnabled ? 'ENABLED (Green)' : 'DISABLED (Red)');
    }
    
    setupIPCHandlers() {
        console.log('[MAIN] Setting up IPC handlers...');
        
        ipcMain.handle('get-settings', () => {
            console.log('[IPC] get-settings');
            return this.settings;
        });
        
        ipcMain.handle('get-user-data', () => {
            console.log('[IPC] get-user-data');
            return this.user;
        });
        
        ipcMain.handle('save-settings', (event, newSettings) => {
            console.log('[IPC] save-settings:', newSettings);
            this.settings = { ...this.settings, ...newSettings };
            this.saveSettings();
            
            // Re-register hotkeys if they changed
            if (newSettings.hotkey && newSettings.hotkey !== this.chatHotkey) {
                console.log('[IPC] Chat hotkey changed, re-registering...');
                this.setupGlobalHotkeys();
            }
            
            if (newSettings.interactionHotkey && newSettings.interactionHotkey !== this.interactionHotkey) {
                console.log('[IPC] Interaction hotkey changed, re-registering...');
                this.setupGlobalHotkeys();
            }
            
            return true;
        });
        
        ipcMain.handle('authenticate-user', async (event, userData) => {
            console.log('[IPC] authenticate-user');
            
            try {
                this.saveUserData(userData);
                
                // Hide main window and show floating button
                if (this.mainWindow && !this.mainWindow.isDestroyed()) {
                    this.mainWindow.hide();
                }
                
                this.createFloatingButton();
                
                return { success: true };
            } catch (error) {
                console.error('[IPC] Authentication error:', error);
                return { success: false, error: error.message };
            }
        });
        
        ipcMain.handle('sign-out', async () => {
            console.log('[IPC] sign-out');
            
            try {
                this.user = null;
                store.delete('userData');
                
                // Hide all windows
                if (this.chatWindow && !this.chatWindow.isDestroyed()) {
                    this.chatWindow.hide();
                }
                if (this.settingsWindow && !this.settingsWindow.isDestroyed()) {
                    this.settingsWindow.close();
                }
                if (this.floatingButton && !this.floatingButton.isDestroyed()) {
                    this.floatingButton.hide();
                }
                
                // Show main window
                if (this.mainWindow) {
                    this.mainWindow.show();
                    this.mainWindow.focus();
                } else {
                    this.createMainWindow();
                }
                
                return { success: true };
            } catch (error) {
                console.error('[IPC] Sign out error:', error);
                return { success: false, error: error.message };
            }
        });
        
        ipcMain.handle('send-to-backend', async (event, message) => {
            console.log('[IPC] send-to-backend:', message.substring(0, 50));
            
            if (this.pythonBackend) {
                try {
                    this.pythonBackend.send(message);
                    return { success: true };
                } catch (error) {
                    console.error('[IPC] Error sending to backend:', error);
                    return { success: false, error: error.message };
                }
            }
            return { success: false, error: 'Backend not available' };
        });
        
        ipcMain.handle('take-screenshot', async () => {
            console.log('[IPC] take-screenshot');
            
            if (this.pythonBackend) {
                try {
                    this.pythonBackend.send(JSON.stringify({ type: 'screenshot' }));
                    return { success: true };
                } catch (error) {
                    console.error('[IPC] Error taking screenshot:', error);
                    return { success: false, error: error.message };
                }
            }
            return { success: false, error: 'Backend not available' };
        });
        
        ipcMain.handle('close-window', (event, windowName) => {
            console.log('[IPC] close-window:', windowName);
            
            switch (windowName) {
                case 'chat':
                    this.hideChatWindow();
                    break;
                case 'settings':
                    if (this.settingsWindow) {
                        this.settingsWindow.close();
                    }
                    break;
                case 'main':
                    if (this.mainWindow) {
                        this.mainWindow.hide();
                        if (this.user) {
                            this.createFloatingButton();
                        }
                    }
                    break;
            }
            return true;
        });
        
        ipcMain.handle('open-external', (event, url) => {
            console.log('[IPC] open-external:', url);
            shell.openExternal(url);
            return true;
        });
        
        // Legacy event handlers for floating button
        ipcMain.on('toggle-chat', () => {
            console.log('[IPC] toggle-chat from floating button');
            this.toggleChatWindow();
        });
        
        ipcMain.on('open-settings', () => {
            console.log('[IPC] open-settings from floating button');
            this.createSettingsWindow();
        });
        
        console.log('[MAIN] IPC handlers set up');
    }
    
    cleanup() {
        console.log('[MAIN] Cleaning up...');
        
        app.isQuitting = true;
        
        if (this.chatHotkey) {
            globalShortcut.unregister(this.chatHotkey);
        }
        if (this.interactionHotkey) {
            globalShortcut.unregister(this.interactionHotkey);
        }
        globalShortcut.unregisterAll();
        
        if (this.pythonBackend) {
            try {
                this.pythonBackend.kill();
            } catch (error) {
                console.error('[MAIN] Error closing Python backend:', error);
            }
        }
        
        if (this.mainWindow) this.mainWindow.destroy();
        if (this.chatWindow) this.chatWindow.destroy();
        if (this.settingsWindow) this.settingsWindow.destroy();
        if (this.floatingButton) this.floatingButton.destroy();
        
        console.log('[MAIN] Cleanup complete');
    }
}

const controlApp = new ControlApp();