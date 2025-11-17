const { app, BrowserWindow, globalShortcut, session, ipcMain, Menu, Tray } = require('electron');
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
        this.tray = null;
        this.isReady = false;
        this.pythonReady = false;
        this.pythonPath = null;
        
        this.settings = {
            hotkey: 'CommandOrControl+Shift+C',
            theme: 'dark',
            autoStart: true,
            googleApiKey: '',
            geminiApiKey: '',
            plan: 'free',
            floatingButton: {
                enabled: true,
                position: { x: 100, y: 100 },
                size: 60
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
    }
    
    saveSettings() {
        store.set('settings', this.settings);
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
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });
        
        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createMainWindow();
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
            
            await this.initializePythonBackend();
            
            this.createMainWindow();
            
            if (this.settings.floatingButton.enabled) {
                this.createFloatingButton();
            }
            
            this.setupGlobalHotkey();
            
            this.setupSystemTray();
            
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
        console.log('[MAIN] Creating main window...');
        
        this.mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            show: true,
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
        
        this.mainWindow.on('close', (event) => {
            if (!app.isQuitting) {
                event.preventDefault();
                this.mainWindow.hide();
            }
        });
        
        console.log('[MAIN] Main window created');
    }
    
    createFloatingButton() {
        console.log('[MAIN] Creating floating button...');
        
        const { x, y } = this.settings.floatingButton.position;
        const size = this.settings.floatingButton.size;
        
        this.floatingButton = new BrowserWindow({
            width: size + 10,
            height: size + 10,
            x: x,
            y: y,
            frame: false,
            alwaysOnTop: true,
            skipTaskbar: true,
            resizable: false,
            movable: true,
            transparent: true,
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
        
        this.floatingButton.on('moved', () => {
            const bounds = this.floatingButton.getBounds();
            this.settings.floatingButton.position = { x: bounds.x, y: bounds.y };
            this.saveSettings();
            console.log('[MAIN] Floating button position saved:', this.settings.floatingButton.position);
        });
        
        console.log('[MAIN] Floating button created');
    }
    
    createChatWindow() {
        console.log('[MAIN] Creating chat window...');
        
        if (this.chatWindow) {
            this.chatWindow.focus();
            return;
        }
        
        this.chatWindow = new BrowserWindow({
            width: 500,
            height: 700,
            frame: false,
            alwaysOnTop: true,
            skipTaskbar: true,
            resizable: true,
            transparent: false,
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
        
        if (this.floatingButton && !this.floatingButton.isDestroyed()) {
            const buttonBounds = this.floatingButton.getBounds();
            this.chatWindow.setPosition(
                buttonBounds.x + buttonBounds.width + 10,
                buttonBounds.y
            );
        }
        
        console.log('[MAIN] Chat window created');
    }
    
    createSettingsWindow() {
        console.log('[MAIN] Creating settings window...');
        
        if (this.settingsWindow) {
            this.settingsWindow.focus();
            return;
        }
        
        this.settingsWindow = new BrowserWindow({
            width: 600,
            height: 500,
            resizable: false,
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
    
    setupGlobalHotkey() {
        console.log('[MAIN] Setting up global hotkey:', this.settings.hotkey);
        
        if (this.globalHotkey) {
            globalShortcut.unregister(this.globalHotkey);
        }
        
        const ret = globalShortcut.register(this.settings.hotkey, () => {
            console.log('[MAIN] Hotkey pressed:', this.settings.hotkey);
            this.toggleChatWindow();
        });
        
        if (!ret) {
            console.error('[MAIN] Failed to register global hotkey:', this.settings.hotkey);
        } else {
            console.log('[MAIN] Global hotkey registered successfully');
        }
        
        this.globalHotkey = this.settings.hotkey;
    }
    
    setupSystemTray() {
        console.log('[MAIN] Setting up system tray...');
        
        try {
            const trayIconPath = path.join(__dirname, '../../assets/icons/tray.png');
            
            if (!fs.existsSync(trayIconPath)) {
                console.log('[MAIN] Tray icon not found at:', trayIconPath);
                return;
            }
            
            this.tray = new Tray(trayIconPath);
            
            const contextMenu = Menu.buildFromTemplate([
                {
                    label: 'Show/Hide Chat',
                    click: () => this.toggleChatWindow()
                },
                {
                    label: 'Settings',
                    click: () => this.createSettingsWindow()
                },
                { type: 'separator' },
                {
                    label: 'Quit',
                    click: () => app.quit()
                }
            ]);
            
            this.tray.setToolTip('Control AI');
            this.tray.setContextMenu(contextMenu);
            
            this.tray.on('click', () => {
                this.toggleChatWindow();
            });
            
            console.log('[MAIN] System tray created');
        } catch (error) {
            console.error('[MAIN] Failed to setup system tray:', error);
        }
    }
    
    toggleChatWindow() {
        console.log('[MAIN] Toggling chat window...');
        
        if (this.chatWindow) {
            if (this.chatWindow.isVisible()) {
                this.chatWindow.hide();
                console.log('[MAIN] Chat window hidden');
            } else {
                this.chatWindow.show();
                this.chatWindow.focus();
                console.log('[MAIN] Chat window shown');
            }
        } else {
            this.createChatWindow();
            if (this.chatWindow) {
                this.chatWindow.show();
                this.chatWindow.focus();
            }
        }
    }
    
    setupIPCHandlers() {
        console.log('[MAIN] Setting up IPC handlers...');
        
        ipcMain.handle('get-settings', () => {
            console.log('[IPC] get-settings');
            return this.settings;
        });
        
        ipcMain.handle('save-settings', (event, newSettings) => {
            console.log('[IPC] save-settings:', newSettings);
            this.settings = { ...this.settings, ...newSettings };
            this.saveSettings();
            
            if (newSettings.hotkey && newSettings.hotkey !== this.globalHotkey) {
                console.log('[IPC] Hotkey changed, re-registering...');
                this.setupGlobalHotkey();
            }
            
            if (newSettings.floatingButton && this.floatingButton && !this.floatingButton.isDestroyed()) {
                const { x, y } = newSettings.floatingButton.position;
                this.floatingButton.setPosition(x, y);
            }
            
            return true;
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
                    if (this.chatWindow) {
                        this.chatWindow.close();
                    }
                    break;
                case 'settings':
                    if (this.settingsWindow) {
                        this.settingsWindow.close();
                    }
                    break;
            }
            return true;
        });
        
        ipcMain.handle('minimize-window', (event, windowName) => {
            console.log('[IPC] minimize-window:', windowName);
            
            switch (windowName) {
                case 'chat':
                    if (this.chatWindow) {
                        this.chatWindow.hide();
                    }
                    break;
            }
            return true;
        });
        
        ipcMain.handle('authenticate-google', async (event, idToken) => {
            console.log('[IPC] authenticate-google');
            
            try {
                this.settings.googleIdToken = idToken;
                this.saveSettings();
                return { success: true };
            } catch (error) {
                console.error('[IPC] Authentication error:', error);
                return { success: false, error: error.message };
            }
        });
        
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
        
        if (this.globalHotkey) {
            globalShortcut.unregister(this.globalHotkey);
            globalShortcut.unregisterAll();
        }
        
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
        if (this.tray) this.tray.destroy();
        
        console.log('[MAIN] Cleanup complete');
    }
}

const controlApp = new ControlApp();