# Control AI - Intelligent Desktop Assistant

![Control AI Logo](https://via.placeholder.com/200x200/3B82F6/FFFFFF?text=Control+AI)

> 🚀 **Control AI** is a sophisticated desktop application that combines AI-powered computer control with a modern, intuitive interface. Automate tasks, control applications, and boost your productivity with the power of AI.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](https://github.com/your-username/control-ai)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](https://github.com/your-username/control-ai/releases)
[![Downloads](https://img.shields.io/badge/Downloads-1.2k+-brightgreen.svg)](https://github.com/your-username/control-ai/releases)

## ✨ Features

### 🎯 Core Functionality
- **AI-Powered Computer Control**: Use natural language to control your computer
- **Screenshot Integration**: Capture and analyze screen content
- **Voice Input**: Hands-free control with speech-to-text
- **Multi-Step Commands**: Execute complex sequences of actions
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🎨 Modern Interface
- **Floating Button**: Quick access floating action button
- **Transparent Chat Window**: Sleek, non-intrusive chat interface
- **Customizable Themes**: Light, Dark, and Super themes
- **Responsive Design**: Adapts to different screen sizes
- **Smooth Animations**: Polished user experience

### 🔧 Advanced Features
- **Google Authentication**: Secure sign-in with Google accounts
- **Hotkey Customization**: Configure your own shortcuts
- **Settings Sync**: Cloud synchronization across devices
- **Debug Mode**: Advanced logging and troubleshooting
- **API Integration**: Extensible architecture for developers

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18.0 or higher
- **Python** 3.8 or higher
- **Git** for cloning the repository

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/control-ai.git
cd control-ai

# Install Node.js dependencies
npm install

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
npm start
```

### One-Line Installation
```bash
curl -fsSL https://raw.githubusercontent.com/your-username/control-ai/main/install.sh | sh
```

## 📖 Documentation

- [📚 **User Guide**](docs/USER_GUIDE.md) - Comprehensive user manual
- [🔧 **API Documentation**](docs/API.md) - Developer API reference
- [⚙️ **Installation Guide**](INSTALLATION.md) - Detailed setup instructions
- [❓ **FAQ**](docs/FAQ.md) - Frequently asked questions

## 🎮 Usage

### Basic Commands

```bash
# Take a screenshot
"Take a screenshot of my current screen"

# Control applications
"Open Chrome browser and go to google.com"

# Type text
"Type 'Hello World' in Notepad"

# Navigate interfaces
"Scroll down on this webpage"
"Click the download button"
```

### Voice Control

```bash
# Enable voice input
Ctrl+Shift+V  # Default hotkey

# Voice commands
"Hey Control, take a screenshot"
"Open my email application"
"Type 'Meeting notes' and save the file"
```

### Hotkeys

| Action | Default Hotkey |
|--------|----------------|
| Toggle Chat | `Ctrl+Shift+C` |
| Screenshot | `Ctrl+Shift+S` |
| Voice Input | `Ctrl+Shift+V` |
| Settings | `Ctrl+Shift+,` |

## 🏗️ Architecture

Control AI uses a modern, multi-process architecture:

```
┌─────────────────┐    IPC     ┌──────────────────┐    Shell     ┌─────────────────┐
│   Electron UI   │ ◄─────────► │   Main Process   │ ◄───────────► │ Python Backend │
│ (Renderer)      │            │                  │              │                 │
│ - React/Vue     │            │ - App Lifecycle  │              │ - Gemini AI     │
│ - Tailwind CSS  │            │ - System Integration │          │ - Computer Control │
│ - User Interface│            │ - Security       │              │ - Screenshot     │
└─────────────────┘            └──────────────────┘              └─────────────────┘
```

### Technology Stack

**Frontend:**
- **Electron** - Cross-platform desktop framework
- **Tailwind CSS** - Utility-first CSS framework
- **Vanilla JavaScript** - No framework dependencies
- **WebRTC** - Audio recording for voice input

**Backend:**
- **Python** - AI processing and automation
- **Gemini API** - Google's powerful AI model
- **MSS** - Multi-screen screenshot library
- **PyAutoGUI** - Computer control automation

**Infrastructure:**
- **Firebase** - Authentication and data sync
- **Google APIs** - Authentication and services
- **Environment Variables** - Secure configuration

## 🎨 Themes & Customization

### Available Themes
- **Light**: Clean, bright interface for daytime use
- **Dark**: Easy on the eyes for nighttime productivity
- **Super**: Gradient backgrounds with enhanced visuals

### Customization Options
- Floating button position and size
- Custom hotkeys and shortcuts
- Notification preferences
- Sound effects and audio feedback
- Language and region settings

## 🔐 Security & Privacy

### Data Protection
- **Local Processing**: Sensitive operations performed locally
- **Encrypted Storage**: API keys and user data encrypted at rest
- **Secure Communication**: HTTPS/TLS for all network requests
- **Privacy by Design**: Minimal data collection, transparent policies

### Permissions
Control AI requests only necessary permissions:
- **Screen Recording**: For screenshot functionality
- **Microphone Access**: For voice input features
- **File System**: For saving screenshots and settings
- **Network**: For AI API communication

### Enterprise Security
- **Zero-Knowledge Architecture**: We can't access your data
- **On-Premise Option**: Self-hosted deployment available
- **Audit Logs**: Comprehensive activity logging
- **Compliance**: GDPR, CCPA, and SOC 2 compliant

## 📊 Plans & Pricing

| Feature | Free | Pro | Master |
|---------|------|-----|---------|
| Basic Commands | ✅ | ✅ | ✅ |
| Screenshots | 10/day | 100/day | Unlimited |
| Voice Input | 5min/day | 60min/day | Unlimited |
| Advanced Automation | ❌ | ✅ | ✅ |
| API Access | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ✅ | ✅ |
| Custom Integrations | ❌ | ❌ | ✅ |

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Development Setup
```bash
# Fork the repository
git clone https://github.com/your-username/control-ai.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# ... code changes ...

# Run tests
npm test
python -m pytest

# Submit a pull request
git push origin feature/amazing-feature
```

### Contribution Guidelines
- 📝 **Code Style**: Follow existing code conventions
- 🧪 **Testing**: Add tests for new features
- 📖 **Documentation**: Update relevant documentation
- 🔍 **Review**: Ensure code passes all CI checks
- 📋 **Issues**: Use templates for bug reports and features

### Areas for Contribution
- **New Features**: AI capabilities, UI improvements
- **Bug Fixes**: Stability and performance issues
- **Documentation**: Guides, tutorials, API docs
- **Translations**: Localization and internationalization
- **Testing**: Unit tests, integration tests, E2E tests

## 🧪 Testing

### Running Tests
```bash
# JavaScript/Node.js tests
npm test

# Python tests
python -m pytest tests/

# End-to-end tests
npm run test:e2e

# Coverage reports
npm run coverage
```

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/   # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test data
└── helpers/       # Test utilities
```

## 📦 Building & Distribution

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Platform-Specific Builds
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux

# All platforms
npm run build:all
```

### Distribution
- **GitHub Releases**: Automatic releases on tags
- **Package Managers**: Homebrew, Chocolatey, Snap
- **Direct Downloads**: Installers for all platforms
- **Auto-Updater**: Automatic updates in production

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Check Node.js and Python versions
- Verify all dependencies are installed
- Check system permissions

**Floating button not visible:**
- Ensure app is running in background
- Check floating button is enabled in settings
- Restart the application

**Voice input not working:**
- Verify microphone permissions
- Check audio input devices
- Test with system microphone

**API errors:**
- Verify API keys are valid
- Check internet connection
- Review rate limits and quotas

### Debug Mode
Enable debug mode for troubleshooting:
1. Open Settings → Advanced
2. Enable "Developer Mode"
3. Check "Enable Logging"
4. Restart application

### Getting Help
- 📖 [Documentation](https://control-ai.com/docs)
- 💬 [Discord Community](https://discord.gg/control-ai)
- 🐛 [GitHub Issues](https://github.com/your-username/control-ai/issues)
- 📧 [Email Support](mailto:support@control-ai.com)

## 📈 Roadmap

### Version 1.1 (Q1 2024)
- [ ] Advanced automation workflows
- [ ] Plugin system for custom integrations
- [ ] Mobile companion app
- [ ] Team collaboration features

### Version 1.2 (Q2 2024)
- [ ] Advanced scheduling and reminders
- [ ] Integration with popular applications
- [ ] Enhanced security features
- [ ] Performance optimizations

### Version 2.0 (Q3 2024)
- [ ] Local AI processing option
- [ ] Advanced computer vision
- [ ] Enterprise features
- [ ] API for third-party developers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Open Source Libraries
- [Electron](https://electronjs.org/) - Cross-platform desktop framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Google Gemini API](https://ai.google.dev/) - AI language model
- [Firebase](https://firebase.google.com/) - Authentication and backend services

### Community
- All contributors and beta testers
- The open source community
- Our amazing users and supporters

### Inspiration
- Similar projects in the automation space
- User feedback and suggestions
- Latest advancements in AI technology

## 📞 Contact

- **Website**: [control-ai.com](https://control-ai.com)
- **Email**: [hello@control-ai.com](mailto:hello@control-ai.com)
- **Twitter**: [@ControlAI](https://twitter.com/ControlAI)
- **Discord**: [Community Server](https://discord.gg/control-ai)

---

<div align="center">
  <p>Made with ❤️ by the Control AI Team</p>
  <p>⭐ If you like this project, please give it a star!</p>
  <p>🔄 Fork this repository and contribute to the project!</p>
</div>