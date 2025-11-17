# Control AI - Installation Guide

## Overview

Control AI is a sophisticated desktop application that combines AI-powered computer control with a modern user interface. This guide will walk you through the installation process.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.8 or higher
- **RAM**: 4GB minimum
- **Storage**: 500MB free space

### Recommended Requirements
- **RAM**: 8GB or more
- **Processor**: Modern multi-core CPU
- **Internet Connection**: Required for AI functionality

## Installation Steps

### 1. Prerequisites Installation

#### Install Node.js
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or download from https://nodejs.org/
```

#### Install Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (using Homebrew)
brew install python3

# Windows
# Download from https://python.org/
```

#### Install Git
```bash
# Ubuntu/Debian
sudo apt install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/
```

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/control-ai.git
cd control-ai
```

### 3. Install Dependencies

#### Node.js Dependencies
```bash
npm install
```

#### Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 4. Environment Configuration

#### Setup Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
nano .env
```

#### Required Environment Variables
```env
# Firebase Configuration (for Google Auth)
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id

# Gemini API Keys
GEMINI_FREE_KEY=your_gemini_free_api_key
GEMINI_PRO_KEY=your_gemini_pro_api_key
GEMINI_MASTER_KEY=your_gemini_master_api_key

# Application Settings
NODE_ENV=production
LOG_LEVEL=info
```

### 5. Build the Application

#### Development Build
```bash
npm run dev
```

#### Production Build
```bash
npm run build
```

#### Platform-Specific Builds
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

## Platform-Specific Setup

### Windows

#### Additional Requirements
- Windows 10/11 (x64)
- Visual Studio Build Tools (for native dependencies)

#### Installation Steps
1. Install Visual Studio Build Tools from Microsoft
2. Run the installer as Administrator
3. Configure Windows Firewall for the application

#### Auto-Start Setup
1. Press `Win + R`, type `shell:startup`
2. Create a shortcut to the Control AI executable
3. The application will now start automatically

### macOS

#### Additional Requirements
- macOS 10.14 (Mojave) or later
- Xcode Command Line Tools

#### Installation Steps
1. Install Xcode Command Line Tools:
   ```bash
   xcode-select --install
   ```

#### Permissions Setup
1. Go to `System Preferences > Security & Privacy`
2. Allow the application in `Accessibility` for screen capture
3. Grant microphone access if using voice features
4. Enable accessibility features for computer control

#### Auto-Start Setup
1. Go to `System Preferences > Users & Groups`
2. Add Control AI to Login Items
3. Check "Hide" to start in background

### Linux

#### Additional Requirements
- Ubuntu 18.04+ / Fedora 30+ / Arch Linux
- Additional system libraries for screen capture

#### Ubuntu/Debian Setup
```bash
sudo apt update
sudo apt install libxss1 libgconf-2-4 libxtst6 libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0
```

#### Fedora Setup
```bash
sudo dnf install libXScrnSaver GConf2 libXtst libXrandr alsa-lib pangocairo atk cairo-gobject gtk3 gdk-pixbuf2
```

#### Auto-Start Setup
```bash
# Create autostart entry
mkdir -p ~/.config/autostart
cp control-ai.desktop ~/.config/autostart/
```

## API Key Setup

### Get Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Setup Firebase (Optional, for cloud sync)
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication (Google Sign-In)
4. Get your configuration values
5. Add them to your `.env` file

## Testing the Installation

### 1. Test Console Backend
```bash
python console_test_backend.py
```

### 2. Test Electron App
```bash
npm start
```

### 3. Verify Features
- [ ] Floating button appears
- [ ] Chat window opens with hotkey (Ctrl+Shift+C)
- [ ] Settings window opens
- [ ] Screenshots work
- [ ] Voice input works (if configured)

## Troubleshooting

### Common Issues

#### Python Dependencies Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Electron App Won't Start
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Screen Capture Not Working
- **Windows**: Run as Administrator
- **macOS**: Grant Accessibility permissions
- **Linux**: Install required system libraries

#### Voice Input Not Working
- Check microphone permissions
- Ensure audio drivers are installed
- Test with system voice recorder first

### Debug Mode

Enable debug mode in settings:
1. Open Settings → Advanced
2. Enable "Developer Mode"
3. Check console for detailed error messages

### Log Files

- **Windows**: `%APPDATA%/control-ai/logs/`
- **macOS**: `~/Library/Logs/control-ai/`
- **Linux**: `~/.local/share/control-ai/logs/`

## Uninstallation

### Windows
1. Use Control Panel > Programs and Features
2. Or run the uninstaller from the installation folder

### macOS
1. Drag app to Trash
2. Remove preferences: `~/Library/Preferences/com.control.ai.plist`
3. Remove logs: `~/Library/Logs/control-ai/`

### Linux
```bash
# Remove application files
sudo rm -rf /opt/control-ai
sudo rm /usr/local/bin/control-ai

# Remove user data
rm -rf ~/.config/control-ai
rm -rf ~/.local/share/control-ai
```

## Getting Help

- **Documentation**: [Project Wiki](https://github.com/your-username/control-ai/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/control-ai/issues)
- **Community**: [Discord Server](https://discord.gg/control-ai)
- **Email**: support@control-ai.com

## Next Steps

After installation:
1. Configure your API keys
2. Set up your preferred hotkeys
3. Customize the appearance
4. Try the basic features
5. Explore advanced settings

Enjoy using Control AI! 🚀