# Control AI - API Documentation

## Overview

Control AI provides a comprehensive API for integrating AI-powered computer control into your applications. This document covers all available endpoints, events, and integration methods.

## Table of Contents

1. [Architecture](#architecture)
2. [IPC API](#ipc-api)
3. [Python Backend API](#python-backend-api)
4. [Events](#events)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

## Architecture

Control AI uses a multi-process architecture:

```
┌─────────────────┐    IPC     ┌──────────────────┐    Shell     ┌─────────────────┐
│   Electron UI   │ ◄─────────► │   Main Process   │ ◄───────────► │ Python Backend │
│ (Renderer)      │            │                  │              │                 │
└─────────────────┘            └──────────────────┘              └─────────────────┘
```

- **Electron UI**: User interface and interactions
- **Main Process**: Application lifecycle and system integration
- **Python Backend**: AI processing and computer control

## IPC API

The Inter-Process Communication (IPC) API connects the Electron frontend with the main process.

### Settings API

#### Get Settings
```javascript
const settings = await window.electronAPI.getSettings();
```

**Returns:**
```javascript
{
  hotkey: "CommandOrControl+Shift+C",
  theme: "dark",
  autoStart: true,
  googleApiKey: "...",
  geminiApiKey: "...",
  plan: "free",
  floatingButton: {
    enabled: true,
    position: { x: 100, y: 100 },
    size: 60
  }
}
```

#### Save Settings
```javascript
const newSettings = {
  theme: "light",
  hotkey: "Ctrl+Alt+C"
};
const result = await window.electronAPI.saveSettings(newSettings);
```

**Returns:** `{ success: boolean }`

### Chat & Backend API

#### Send Message to Backend
```javascript
const result = await window.electronAPI.sendToBackend("Take a screenshot");
```

**Returns:** `{ success: boolean, error?: string }`

#### Take Screenshot
```javascript
const result = await window.electronAPI.takeScreenshot();
```

**Returns:** `{ success: boolean, error?: string }`

### Window Control API

#### Close Window
```javascript
await window.electronAPI.closeWindow("chat"); // "chat", "settings", or "main"
```

#### Minimize Window
```javascript
await window.electronAPI.minimizeWindow("chat");
```

### Authentication API

#### Authenticate with Google
```javascript
const result = await window.electronAPI.authenticateGoogle(idToken);
```

**Returns:** `{ success: boolean }`

### Audio API

#### Start Audio Recording
```javascript
const success = await window.electronAPI.startAudioRecording();
```

**Returns:** `boolean` - true if recording started successfully

#### Stop Audio Recording
```javascript
await window.electronAPI.stopAudioRecording();
```

**Returns:** `Promise<Blob>` - Audio blob containing the recording

### Utility API

#### Get Current Theme
```javascript
const theme = window.electronAPI.getCurrentTheme(); // "light", "dark", or "super"
```

#### Set Theme
```javascript
window.electronAPI.setTheme("dark");
```

#### Get Platform
```javascript
const platform = window.electronAPI.getPlatform(); // "win32", "darwin", "linux"
```

#### Storage Operations
```javascript
// Set value
window.electronAPI.setStoredValue("userPreference", "value");

// Get value
const value = window.electronAPI.getStoredValue("userPreference");
```

## Python Backend API

The Python backend processes AI requests and executes computer control actions.

### Message Format

All messages to the backend should be plain text strings. The backend responds with JSON-formatted responses.

### Response Format

```javascript
{
  "action_log": "Description of what AI is doing",
  "status": "loading|success|error|complete",
  "response": "AI's text response to the user",
  "computer_use": {
    "type": "screenshot|click|type|scroll|wait",
    "coordinates": [x, y], // for click actions
    "text": "text to type", // for type actions
    "amount": pixels, // for scroll actions
    "duration": seconds // for wait actions
  }
}
```

### Computer Control Actions

#### Screenshot
```javascript
{
  "action_log": "Taking screenshot of the screen",
  "status": "loading",
  "response": "Capturing screen...",
  "computer_use": {
    "type": "screenshot"
  }
}
```

#### Mouse Click
```javascript
{
  "action_log": "Clicking at coordinates (100, 200)",
  "status": "loading",
  "response": "Clicking the specified location",
  "computer_use": {
    "type": "click",
    "coordinates": [100, 200]
  }
}
```

#### Type Text
```javascript
{
  "action_log": "Typing 'Hello World'",
  "status": "loading",
  "response": "Entering text...",
  "computer_use": {
    "type": "type",
    "text": "Hello World"
  }
}
```

#### Scroll
```javascript
{
  "action_log": "Scrolling down by 100 pixels",
  "status": "loading",
  "response": "Scrolling the page...",
  "computer_use": {
    "type": "scroll",
    "amount": 100
  }
}
```

#### Wait
```javascript
{
  "action_log": "Waiting for 2 seconds",
  "status": "loading",
  "response": "Please wait...",
  "computer_use": {
    "type": "wait",
    "duration": 2
  }
}
```

## Events

### Backend Message Events

Listen for messages from the Python backend:

```javascript
window.electronAPI.onBackendMessage((message) => {
  console.log("Backend message:", message);
  
  try {
    const parsedMessage = JSON.parse(message);
    handleBackendResponse(parsedMessage);
  } catch {
    // Handle plain text messages
    displayMessage(message);
  }
});
```

### Window Events

```javascript
window.electronAPI.onWindowMessage('window-close', (data) => {
  console.log("Window close requested:", data);
});
```

## Authentication

### Google Sign-In Integration

1. Initialize Google Auth:
```javascript
await window.electronAPI.initGoogleAuth('your-client-id');
```

2. Render sign-in button:
```javascript
window.electronAPI.renderGoogleButton('gSignInWrapper');
```

3. Handle authentication:
```javascript
// The callback is handled automatically by the preload script
```

### Firebase Integration

The application uses Firebase for:
- Google Authentication
- Settings synchronization
- Usage tracking

## Error Handling

### Standard Error Response

```javascript
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `BACKEND_UNAVAILABLE` | Python backend is not running |
| `API_KEY_INVALID` | Invalid or missing API key |
| `PERMISSION_DENIED` | Missing system permissions |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `INVALID_INPUT` | Invalid input parameters |

### Error Handling Example

```javascript
try {
  const result = await window.electronAPI.sendToBackend(message);
  if (!result.success) {
    handleError(result.error);
  }
} catch (error) {
  console.error("API call failed:", error);
  showUserError("Failed to communicate with AI");
}
```

## Examples

### Basic Chat Integration

```javascript
class ControlAIChat {
  constructor() {
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    window.electronAPI.onBackendMessage(this.handleBackendMessage.bind(this));
  }
  
  async sendMessage(text) {
    this.showTypingIndicator();
    
    try {
      const result = await window.electronAPI.sendToBackend(text);
      if (!result.success) {
        throw new Error(result.error);
      }
    } catch (error) {
      this.showError(error.message);
    }
  }
  
  handleBackendMessage(message) {
    try {
      const response = JSON.parse(message);
      
      if (response.computer_use) {
        this.handleComputerAction(response.computer_use);
      }
      
      if (response.response) {
        this.displayMessage(response.response);
      }
      
      if (response.status === 'complete') {
        this.hideTypingIndicator();
      }
    } catch {
      this.displayMessage(message);
    }
  }
  
  handleComputerAction(action) {
    console.log("Executing action:", action.type);
    // Visual feedback for actions
  }
}

// Usage
const chat = new ControlAIChat();
chat.sendMessage("Take a screenshot of my current screen");
```

### Settings Management

```javascript
class SettingsManager {
  async loadSettings() {
    try {
      this.settings = await window.electronAPI.getSettings();
      this.updateUI();
    } catch (error) {
      console.error("Failed to load settings:", error);
    }
  }
  
  async saveTheme(theme) {
    try {
      await window.electronAPI.saveSettings({ theme });
      this.applyTheme(theme);
    } catch (error) {
      console.error("Failed to save theme:", error);
    }
  }
  
  async updateHotkey(hotkey) {
    try {
      await window.electronAPI.saveSettings({ hotkey });
      this.showSuccess("Hotkey updated successfully");
    } catch (error) {
      this.showError("Failed to update hotkey");
    }
  }
}
```

### Custom Computer Control

```javascript
class ComputerController {
  async takeScreenshot() {
    try {
      const result = await window.electronAPI.takeScreenshot();
      if (result.success) {
        this.showNotification("Screenshot captured!");
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      this.showNotification("Failed to capture screenshot: " + error.message);
    }
  }
  
  async performAction(actionType, params) {
    const message = this.constructActionMessage(actionType, params);
    await window.electronAPI.sendToBackend(message);
  }
  
  constructActionMessage(type, params) {
    switch (type) {
      case 'click':
        return `Click at coordinates ${params.x}, ${params.y}`;
      case 'type':
        return `Type the text: "${params.text}"`;
      case 'scroll':
        return `Scroll ${params.amount} pixels ${params.direction}`;
      default:
        return `Perform ${type} action`;
    }
  }
}
```

### Voice Integration

```javascript
class VoiceController {
  constructor() {
    this.isRecording = false;
  }
  
  async toggleRecording() {
    if (this.isRecording) {
      await this.stopRecording();
    } else {
      await this.startRecording();
    }
  }
  
  async startRecording() {
    try {
      await window.electronAPI.startAudioRecording();
      this.isRecording = true;
      this.showRecordingIndicator();
    } catch (error) {
      this.showError("Failed to start recording: " + error.message);
    }
  }
  
  async stopRecording() {
    try {
      const audioBlob = await window.electronAPI.stopAudioRecording();
      this.isRecording = false;
      this.hideRecordingIndicator();
      
      // Send audio for transcription
      const transcript = await this.transcribeAudio(audioBlob);
      await window.electronAPI.sendToBackend(transcript);
    } catch (error) {
      this.showError("Failed to process audio: " + error.message);
    }
  }
  
  async transcribeAudio(audioBlob) {
    // Implement speech-to-text here
    return "Transcribed text from audio";
  }
}
```

## Security Considerations

### API Key Management
- Store API keys in environment variables
- Never expose keys in client-side code
- Use different keys for different environments

### Permissions
- Request minimum required permissions
- Explain why each permission is needed
- Allow users to revoke permissions

### Data Privacy
- Process sensitive data locally when possible
- Clear sensitive data from memory when done
- Provide option to disable data collection

## Rate Limiting

API calls are rate-limited to prevent abuse:

| Plan | Requests/Minute | Requests/Hour |
|------|----------------|---------------|
| Free | 10 | 100 |
| Pro | 50 | 500 |
| Master | 100 | 1000 |

Rate limit status is included in API responses:

```javascript
{
  "success": true,
  "data": "...",
  "rateLimit": {
    "remaining": 45,
    "resetTime": "2024-01-01T12:00:00Z"
  }
}
```

## Versioning

API versioning follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features
- **Patch**: Bug fixes

Current version: `v1.0.0`

## Support

For API support:
- Documentation: [Project Wiki](https://github.com/your-username/control-ai/wiki)
- Issues: [GitHub Issues](https://github.com/your-username/control-ai/issues)
- Email: api-support@control-ai.com

## Changelog

### v1.0.0 (2024-01-01)
- Initial API release
- Core computer control features
- Authentication system
- Settings management