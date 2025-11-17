# Control AI - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Basic Features](#basic-features)
4. [Advanced Features](#advanced-features)
5. [Voice Control](#voice-control)
6. [Settings & Customization](#settings--customization)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Tricks](#tips--tricks)

## Getting Started

### First Launch

When you first launch Control AI, you'll see:

1. **Welcome Screen**: A brief introduction to the application
2. **Floating Button**: A circular button on your desktop
3. **System Tray Icon**: Access to quick actions and settings

### Initial Setup

1. **Configure API Keys**:
   - Open Settings → Account
   - Enter your Gemini API key
   - Sign in with Google for sync features

2. **Choose Your Theme**:
   - Go to Settings → General
   - Select Light, Dark, or Super theme

3. **Set Hotkeys**:
   - Default: `Ctrl+Shift+C` (Toggle Chat)
   - Customize in Settings → Hotkeys

## Interface Overview

### Floating Button

The floating button is your main interaction point:

- **Single Click**: Open/close chat window
- **Double Click**: Open settings
- **Drag**: Move button to preferred position
- **Right Click**: Context menu (Windows/Linux)

**Visual States:**
- 🔵 **Blue**: Idle and ready
- 🟢 **Green**: Active processing
- 🔴 **Red**: Error or offline

### Chat Window

The chat window is where you interact with the AI:

**Components:**
- **Header**: Status indicators and window controls
- **Messages Area**: Conversation history
- **Input Area**: Text input, voice button, attachments
- **Action Status**: Real-time feedback on AI actions

**Window Controls:**
- **Drag**: Move window by dragging the header
- **Resize**: Drag bottom-right corner
- **Minimize**: Click the `-` button
- **Close**: Click the `×` button

### Settings Window

Access settings by:
- Double-clicking the floating button
- Right-click → Settings
- System tray → Settings

**Tab Organization:**
- **General**: Theme, appearance, notifications
- **Hotkeys**: Keyboard shortcuts
- **Account**: Authentication, subscription
- **Advanced**: API keys, debug options

## Basic Features

### Chat with AI

The chat interface works like a messaging app:

1. **Type your request** in the input field
2. **Press Enter** to send
3. **AI responds** and performs actions
4. **View results** in the messages area

**Example Requests:**
- "Take a screenshot"
- "Open Chrome browser"
- "Type 'Hello World' in Notepad"
- "Scroll down on this webpage"

### Taking Screenshots

**Methods:**
1. **Voice Command**: "Take a screenshot"
2. **Chat Request**: Type "screenshot"
3. **Hotkey**: `Ctrl+Shift+S` (default)
4. **Screenshot Button**: In main interface

**Screenshot Types:**
- **Full Screen**: Captures entire desktop
- **Active Window**: Captures focused window
- **Region Select**: Select area to capture (coming soon)

**Storage:**
- Screenshots saved to `screenshots/` folder
- Automatic naming with timestamp
- PNG format for quality

### Computer Control

Control AI can perform various computer actions:

**Mouse Actions:**
- **Click**: Single click at coordinates
- **Right Click**: Context menu click
- **Double Click**: Rapid double-click
- **Drag**: Click and drag to position

**Keyboard Actions:**
- **Type**: Enter text at cursor position
- **Hotkeys**: Press key combinations
- **Special Keys**: Enter, Tab, Escape, etc.

**Navigation:**
- **Scroll**: Scroll up/down by pixels
- **Navigate**: Switch between applications
- **Focus**: Bring windows to front

### Window Management

**Built-in Actions:**
- "Open [application name]"
- "Close current window"
- "Minimize this window"
- "Maximize the window"
- "Switch to next application"

## Advanced Features

### Multi-Step Commands

Control AI can execute complex, multi-step instructions:

**Examples:**
```
"Open Chrome, go to google.com, search for 'Control AI', 
take a screenshot of the results"
```

```
"Open Notepad, type 'Meeting Notes', save the file as 
'meeting.txt' on the desktop"
```

### Conditional Logic

The AI can make decisions based on screen content:

**Examples:**
- "If the download button is visible, click it"
- "Wait for the page to load, then click the first link"
- "Check if there are any error messages on screen"

### File Operations

**File Management:**
- "Create a new folder called 'Project' on desktop"
- "Move screenshot.png to Documents folder"
- "Delete the temporary files"
- "Rename the file to 'backup.pdf'"

**Application Integration:**
- "Open the last edited Word document"
- "Save current Excel file"
- "Print the active document"

## Voice Control

### Setting Up Voice Input

1. **Microphone Permissions**:
   - Grant microphone access when prompted
   - Check system sound settings

2. **Voice Languages**:
   - Default: English (US)
   - Additional languages in settings

3. **Voice Training**:
   - Read sample phrases for better accuracy
   - Adjust sensitivity in settings

### Using Voice Commands

**Start Recording:**
- Click microphone button in chat
- Use hotkey `Ctrl+Shift+V`
- Say "Hey Control" (if enabled)

**Voice Commands:**
- **Basic Actions**: "Take screenshot", "Open Chrome"
- **Text Input**: "Type 'Hello World'"
- **Navigation**: "Scroll down", "Click the button"
- **System**: "Close the window", "Minimize everything"

**Voice Feedback:**
- Audio confirmation for actions
- Spoken responses for AI replies
- Error announcements

### Voice Tips

**For Better Recognition:**
- Speak clearly and at moderate pace
- Minimize background noise
- Use consistent terminology
- Keep commands concise

**Common Issues:**
- Background noise interference
- Microphone too far/loud
- Complex commands with poor structure

## Settings & Customization

### Appearance Settings

**Themes:**
- **Light**: Clean, bright interface
- **Dark**: Easy on the eyes, modern look
- **Super**: Gradient background, enhanced visuals

**Floating Button:**
- **Position**: Drag to preferred location
- **Size**: Adjust from small to large
- **Opacity**: Make more or less transparent
- **Auto-hide**: Hide when not in use

### Hotkey Customization

**Default Hotkeys:**
- `Ctrl+Shift+C`: Toggle chat
- `Ctrl+Shift+S`: Screenshot
- `Ctrl+Shift+V`: Voice input
- `Ctrl+Shift+Q`: Quit application

**Custom Hotkeys:**
1. Go to Settings → Hotkeys
2. Click "Change" next to action
3. Press desired key combination
4. Confirm to save

**Modifier Keys:**
- **Ctrl/Control**: Standard modifier
- **Alt**: Alternative modifier
- **Shift**: Secondary modifier
- **Meta/Cmd**: macOS Command key

### Notification Settings

**Desktop Notifications:**
- Enable/disable system notifications
- Choose notification types
- Set duration for auto-dismiss

**Sound Effects:**
- Button click sounds
- Action completion sounds
- Error alert sounds
- Custom sound files

### Privacy Settings

**Data Collection:**
- Usage analytics (anonymous)
- Error reporting
- Performance metrics
- Crude location data

**Security Options:**
- API key encryption
- Local data storage
- Session timeout
- Auto-lock settings

## Troubleshooting

### Common Issues

**Floating Button Not Visible:**
- Check if application is running
- Verify floating button is enabled in settings
- Restart the application
- Check display scaling settings

**Chat Window Won't Open:**
- Verify hotkey configuration
- Check if window is minimized
- Restart the application
- Check system permissions

**Voice Input Not Working:**
- Verify microphone permissions
- Check audio input devices
- Test microphone with system recorder
- Adjust microphone sensitivity

**Screenshots Not Working:**
- Check screen recording permissions (macOS)
- Run as administrator (Windows)
- Verify storage permissions
- Check available disk space

**API Errors:**
- Verify API key is valid
- Check internet connection
- Verify API quota not exceeded
- Check service status

### Performance Issues

**Slow Response Times:**
- Check internet connection speed
- Close unnecessary applications
- Restart the application
- Check system resources

**High CPU Usage:**
- Update to latest version
- Disable unnecessary features
- Check for conflicting software
- Restart your computer

**Memory Leaks:**
- Restart application periodically
- Clear conversation history
- Disable logging in debug mode
- Report persistent issues

### Debug Mode

Enable debug mode for troubleshooting:

1. Go to Settings → Advanced
2. Enable "Developer Mode"
3. Check "Enable Logging"
4. Restart application
5. Check log files:

**Log Locations:**
- **Windows**: `%APPDATA%/control-ai/logs/`
- **macOS**: `~/Library/Logs/control-ai/`
- **Linux**: `~/.local/share/control-ai/logs/`

### Getting Help

**Self-Help Resources:**
- [Online Documentation](https://control-ai.com/docs)
- [Video Tutorials](https://youtube.com/control-ai)
- [Community Forum](https://forum.control-ai.com)
- [FAQ Page](https://control-ai.com/faq)

**Contact Support:**
- Email: support@control-ai.com
- Discord: [Community Server](https://discord.gg/control-ai)
- Bug Reports: [GitHub Issues](https://github.com/your-username/control-ai/issues)

## Tips & Tricks

### Productivity Tips

**Quick Actions:**
- Use floating button for instant access
- Customize hotkeys for frequent actions
- Create voice command shortcuts
- Use multi-step commands for complex tasks

**Workflow Optimization:**
- Group similar actions together
- Use conditional commands for automation
- Create custom command sequences
- Leverage screenshots for documentation

**Time Saving:**
- Use voice input for hands-free operation
- Create templates for common requests
- Use keyboard shortcuts throughout
- Enable auto-completion suggestions

### Advanced Usage

**Command Chaining:**
```
"Take screenshot, save to desktop, open in image viewer"
```

**Context-Aware Commands:**
```
"Based on the current webpage, extract all links and save them to a file"
```

**Batch Operations:**
```
"Select all files in Downloads folder that are PDFs, move them to Documents"
```

### Integration Tips

**With Other Applications:**
- Use Control AI to automate repetitive tasks
- Integrate with your development workflow
- Automate data entry and form filling
- Create custom macros for specific applications

**Developer Workflow:**
- "Open terminal, navigate to project folder, run npm test"
- "Take screenshot of error message, save to bug report folder"
- "Open browser, navigate to documentation, search for current error"

### Security Best Practices

**API Key Management:**
- Use separate keys for different environments
- Rotate keys regularly
- Monitor usage and quotas
- Use environment variables for keys

**Privacy Protection:**
- Review permission requests carefully
- Disable unnecessary data collection
- Use local processing when possible
- Regularly clear conversation history

**System Security:**
- Keep application updated
- Use reputable sources for downloads
- Review permission requirements
- Monitor system resource usage

### Customization Ideas

**Personal Themes:**
- Create custom color schemes
- Add personal branding
- Customize button appearance
- Create seasonal themes

**Workflow Automations:**
- Morning routine automation
- Development workflow setup
- Meeting preparation sequence
- End-of-day cleanup routine

**Accessibility Options:**
- High contrast themes
- Larger text options
- Keyboard-only navigation
- Screen reader compatibility

## Keyboard Shortcuts Reference

### Global Hotkeys
| Action | Default | Customizable |
|--------|---------|-------------|
| Toggle Chat | `Ctrl+Shift+C` | ✅ |
| Screenshot | `Ctrl+Shift+S` | ✅ |
| Voice Input | `Ctrl+Shift+V` | ✅ |
| Settings | `Ctrl+Shift+,` | ✅ |
| Quit App | `Ctrl+Shift+Q` | ✅ |

### In-Chat Shortcuts
| Action | Shortcut |
|--------|----------|
| Send Message | `Enter` |
| New Line | `Shift+Enter` |
| Clear Input | `Esc` |
| Voice Toggle | `Ctrl+M` |
| Attach File | `Ctrl+F` |

### Window Management
| Action | Shortcut |
|--------|----------|
| Close Window | `Alt+F4` |
| Minimize | `Ctrl+M` |
| Maximize | `Ctrl+Shift+M` |
| Move Window | `Alt+Space` |

## Frequently Asked Questions

**Q: Can Control AI work offline?**
A: Basic features work offline, but AI processing requires internet connection.

**Q: Is my data secure?**
A: Yes, data is processed locally when possible and encrypted when transmitted.

**Q: Can I use Control AI on multiple computers?**
A: Yes, with the same account settings will sync across devices.

**Q: What languages are supported?**
A: Currently English is fully supported, with more languages coming soon.

**Q: How accurate is voice recognition?**
A: Accuracy depends on microphone quality and background noise, typically 95%+ in good conditions.

---

For more help and updates, visit [control-ai.com](https://control-ai.com) or join our [Discord community](https://discord.gg/control-ai).