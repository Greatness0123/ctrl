#!/usr/bin/env python3
"""
Console Test Backend - Control Project
A console-based replica of the main.py for testing LLM communication and screenshot functionality.
This version includes console logging and user input to test the complete workflow.
"""

import sys
import json
import time
import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Skip GUI libraries in headless environment
    GUI_AVAILABLE = False
    
    # Core libraries that should work in any environment
    import mss
    import psutil
    try:
        import pyperclip
    except ImportError:
        pyperclip = None
    from PIL import Image
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    print("Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging with console formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [CONSOLE_TEST] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('console_test.log')
    ]
)
logger = logging.getLogger(__name__)

# System prompt for the AI
SYSTEM_PROMPT = """You are Control, an advanced Computer Use Agent with the ability to both answer questions and perform actions on the user's device.

**CRITICAL: You must respond in valid JSON format ONLY. No additional text before or after the JSON.**

**Response Format:**
{
  "action_log": "Description of what you're doing",
  "status": "loading|success|error|complete",
  "response": "Your text response to the user",
  "computer_use": {
    "type": "screenshot|click|type|scroll|wait",
    "coordinates": [x, y] (for click),
    "text": "text to type" (for type),
    "amount": pixels (for scroll),
    "duration": seconds (for wait)
  }
}

**Computer Control Capabilities:**
- Take screenshots to see the screen
- Click at specific coordinates  
- Type text using keyboard
- Scroll the mouse wheel
- Wait for specified durations

**Guidelines:**
- Always describe what you're doing in the action_log
- Start with status="loading" when beginning an action
- Update to status="success" or "error" after completion
- Use status="complete" when finished with the request
- Take screenshots before performing actions when needed
- Be precise with coordinates and actions
- Explain your reasoning for actions taken"""

class ConsoleTestBackend:
    """Console-based backend for testing LLM communication and computer control."""
    
    def __init__(self):
        """Initialize the console test backend."""
        self.running = True
        self.screenshot_dir = project_root / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Configure Gemini API
        self.setup_gemini_api()
        
        # Computer control setup
        self.setup_computer_control()
        
        logger.info("Console Test Backend initialized successfully")
        logger.info("Screenshot directory: %s", self.screenshot_dir)
        logger.info("Gemini API configured and ready")
    
    def setup_gemini_api(self):
        """Configure Gemini API with appropriate key based on plan."""
        # For testing, use the free key
        api_key = os.getenv('GEMINI_FREE_KEY')
        if not api_key:
            # Fallback to a test key if environment not set
            api_key = "test_api_key"
            logger.warning("No Gemini API key found in environment. Using test key.")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash', 
                                             system_instruction=SYSTEM_PROMPT)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.model = None
    
    def setup_computer_control(self):
        """Setup computer control libraries."""
        try:
            if GUI_AVAILABLE:
                # Configure pyautogui for safety
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.1
                logger.info("GUI control libraries available")
            else:
                logger.info("GUI control libraries not available - headless mode")
            
            # Test mss for screenshots (should work in headless)
            try:
                with mss.mss() as sct:
                    monitors = sct.monitors
                    logger.info(f"Found {len(monitors)-1} monitor(s) for screenshots")
                logger.info("Screenshot functionality available")
            except Exception as e:
                logger.warning(f"Screenshot not available: {e}")
            
            logger.info("Computer control setup completed")
        except Exception as e:
            logger.error(f"Failed to setup computer control: {e}")
    
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot using mss library."""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.screenshot_dir / filename
            
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1]  # Primary monitor
                sct_img = sct.grab(monitor)
                
                # Save to PIL Image
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                img.save(filepath)
            
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            # In headless environment, create a dummy screenshot
            try:
                # Create a simple test image
                dummy_img = Image.new('RGB', (800, 600), color = 'lightblue')
                dummy_img.save(filepath)
                logger.info(f"Created dummy screenshot: {filepath}")
                return str(filepath)
            except Exception as dummy_e:
                logger.error(f"Failed to create dummy screenshot: {dummy_e}")
                return ""
    
    def execute_computer_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute computer control actions."""
        result = {"success": False, "message": ""}
        
        try:
            action_type = action.get("type", "").lower()
            
            if action_type == "screenshot":
                filepath = self.take_screenshot()
                result["success"] = bool(filepath)
                result["message"] = f"Screenshot saved to {filepath}" if filepath else "Failed to save screenshot"
            
            elif action_type == "click":
                if GUI_AVAILABLE:
                    x, y = action.get("coordinates", [0, 0])
                    pyautogui.click(x, y)
                    result["success"] = True
                    result["message"] = f"Clicked at coordinates ({x}, {y})"
                else:
                    result["success"] = False
                    result["message"] = "GUI control not available in headless mode"
            
            elif action_type == "type":
                if GUI_AVAILABLE:
                    text = action.get("text", "")
                    pyautogui.typewrite(text)
                    result["success"] = True
                    result["message"] = f"Typed: {text}"
                else:
                    result["success"] = False
                    result["message"] = "GUI control not available in headless mode"
            
            elif action_type == "scroll":
                if GUI_AVAILABLE:
                    amount = action.get("amount", 0)
                    pyautogui.scroll(amount)
                    result["success"] = True
                    result["message"] = f"Scrolled {amount} pixels"
                else:
                    result["success"] = False
                    result["message"] = "GUI control not available in headless mode"
            
            elif action_type == "wait":
                duration = action.get("duration", 1)
                time.sleep(duration)
                result["success"] = True
                result["message"] = f"Waited {duration} seconds"
            
            else:
                result["message"] = f"Unknown action type: {action_type}"
        
        except Exception as e:
            result["message"] = f"Error executing {action_type}: {e}"
            logger.error(f"Computer action error: {e}")
        
        return result
    
    def send_to_llm(self, user_message: str) -> Dict[str, Any]:
        """Send message to Gemini LLM and get response."""
        try:
            if not self.model:
                return {
                    "action_log": "LLM not available",
                    "status": "error",
                    "response": "Gemini API not configured. Please check your API keys.",
                    "computer_use": None
                }
            
            logger.info(f"Sending to LLM: {user_message[:100]}...")
            
            # Send message to Gemini
            response = self.model.generate_content(user_message)
            response_text = response.text.strip()
            
            # Parse JSON response
            try:
                llm_response = json.loads(response_text)
                logger.info(f"LLM response parsed successfully")
                return llm_response
            except json.JSONDecodeError:
                # Fallback if response is not valid JSON
                logger.warning("LLM response not valid JSON, creating fallback response")
                return {
                    "action_log": "Processing user request",
                    "status": "complete",
                    "response": response_text,
                    "computer_use": None
                }
        
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}")
            return {
                "action_log": "Error communicating with AI",
                "status": "error",
                "response": f"Error: {e}",
                "computer_use": None
            }
    
    def process_user_request(self, user_message: str) -> None:
        """Process a complete user request with LLM and computer actions."""
        print(f"\n{'='*60}")
        print(f"Processing: {user_message}")
        print(f"{'='*60}")
        
        # Step 1: Send to LLM
        llm_response = self.send_to_llm(user_message)
        
        # Display LLM response
        action_log = llm_response.get("action_log", "")
        status = llm_response.get("status", "unknown")
        response = llm_response.get("response", "")
        computer_use = llm_response.get("computer_use")
        
        print(f"\n Action Log: {action_log}")
        print(f" Status: {status}")
        print(f" Response: {response}")
        
        # Step 2: Execute computer actions if present
        if computer_use and status != "error":
            print(f"\nExecuting Computer Action...")
            
            action_result = self.execute_computer_action(computer_use)
            print(f"Success: {action_result['success']}")
            print(f" Message: {action_result['message']}")
        
        print(f"\n{'='*60}\n")
    
    def run_console_loop(self) -> None:
        """Main console interaction loop."""
        print("\n" + "="*80)
        print(" CONTROL - Console Test Backend")
        print("="*80)
        print("This is a testing environment for the Control AI agent.")
        print("Type your commands below, or 'help' for available commands.")
        print("Type 'quit' or 'exit' to stop the test.\n")
        
        while self.running:
            try:
                # Get user input with proper handling
                try:
                    user_input = input(" You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(" Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                elif user_input.lower() == 'screenshot':
                    filepath = self.take_screenshot()
                    if filepath:
                        print(f"Screenshot saved: {filepath}")
                    else:
                        print("Failed to take screenshot")
                    continue
                
                elif user_input.lower() == 'test':
                    self.run_test_sequence()
                    continue
                
                # Process normal user request
                self.process_user_request(user_input)
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in console loop: {e}")
                print(f"Error: {e}")
                # Continue running even if there's an error
    
    def show_help(self) -> None:
        """Display help information."""
        print("\n" + "="*60)
        print(" Available Commands:")
        print("="*60)
        print("• help     - Show this help message")
        print("• screenshot - Take a screenshot")
        print("• test     - Run a test sequence")
        print("• quit/exit - Exit the program")
        print("\n Natural Language Examples:")
        print("• 'Take a screenshot of my screen'")
        print("• 'Click at coordinates 100, 200'")
        print("• 'Type Hello World'") 
        print("• 'Scroll down by 100 pixels'")
        print("• 'What time is it?'")
        print("="*60 + "\n")
    
    def run_test_sequence(self) -> None:
        """Run a test sequence to verify functionality."""
        print("\n Running Test Sequence...")
        
        test_commands = [
            "Take a screenshot of the current screen",
            "Type 'Hello from Control AI'",
            "Wait for 2 seconds"
        ]
        
        for command in test_commands:
            print(f"\nTesting: {command}")
            self.process_user_request(command)
            time.sleep(1)
        
        print("Test sequence completed!")


def main():
    """Main entry point for the console test backend."""
    try:
        backend = ConsoleTestBackend()
        backend.run_console_loop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()