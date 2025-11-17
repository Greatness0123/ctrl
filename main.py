#!/usr/bin/env python3
"""
Computer Use Agent - Python Backend
Handles device control, screenshot capture, and AI communication
"""

import sys
import json
import time
import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv

def find_and_load_env():
    possible_paths = [
        project_root / '.env',
        project_root.parent / '.env',
        Path.home() / '.env',
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"\n[ENV] Loaded .env from: {env_path}\n")
            return env_path
    
    print("\n[ENV] WARNING: No .env file found in standard locations\n")
    return None

find_and_load_env()

try:
    import pyautogui
    import keyboard
    import mouse
    import mss
    import psutil
    import pyperclip
    from PIL import Image
    import google.generativeai as genai
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}", file=sys.stderr)
    print("[ERROR] Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Control, an advanced Computer Use Agent with the ability to both answer questions and perform actions on the user's device.

**CRITICAL: You must respond in valid JSON format ONLY. No additional text before or after the JSON.**

**Response Format:**

For QUESTIONS (when user asks for information, explanation, advice):
{
    "type": "question",
    "response": "Your detailed answer here",
    "action_log": "Processed user question"
}

For ACTIONS (when user wants you to perform tasks on their device):
{
    "type": "action",
    "response": "Brief description of what you're doing",
    "action_log": "Planning execution",
    "steps": [
        {
            "action": "screenshot|mouse_click|keyboard_type|terminal_command|wait",
            "description": "What this step does",
            "parameters": {},
            "timing": 0.5
        }
    ]
}

**Available Actions:**

1. screenshot: Capture current screen state
   {"action": "screenshot", "description": "Taking screenshot", "parameters": {}, "timing": 0.3}

2. mouse_click: Click at coordinates
   {"action": "mouse_click", "description": "Clicking button", "parameters": {"x": 500, "y": 300, "button": "left", "clicks": 1}, "timing": 0.5}

3. keyboard_type: Type text
   {"action": "keyboard_type", "description": "Typing text", "parameters": {"text": "Hello", "interval": 0.01}, "timing": 0.5}

4. keyboard_press: Press specific keys
   {"action": "keyboard_press", "description": "Pressing keys", "parameters": {"keys": ["ctrl", "c"], "combination": true}, "timing": 0.5}

5. terminal_command: Execute command
   {"action": "terminal_command", "description": "Running command", "parameters": {"command": "dir"}, "timing": 1.0}

6. wait: Pause execution
   {"action": "wait", "description": "Waiting", "parameters": {"duration": 2.0}, "timing": 0}

**Guidelines:**
- Always start actions with a screenshot to see current state
- Break complex tasks into sequential steps
- Use appropriate timing between actions (0.3-1.0 seconds)
- For questions, provide clear answers without action steps
- Be precise with coordinates for mouse clicks
"""


class ComputerUseAgent:
    def __init__(self):
        self.running = True
        self.gemini_client = None
        self.screenshot_dir = project_root / "screenshots"
        self.api_key = None
        
        self.screenshot_dir.mkdir(exist_ok=True)
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.initialize_ai()
        
        print("[INIT] Computer Use Agent initialized\n")
        logger.info("[INIT] Computer Use Agent initialized")

    def initialize_ai(self, api_key=None):
        try:
            key = api_key or os.getenv('GEMINI_FREE_KEY')
            if not key:
                print("[AI] WARNING: No Gemini API key found in environment\n")
                logger.warning("[AI] No Gemini API key found in environment")
                return
                
            genai.configure(api_key=key)
            self.gemini_client = genai.GenerativeModel(
                'gemini-2.0-flash',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                }
            )
            self.api_key = key
            print("[AI] Gemini AI client initialized successfully\n")
            logger.info("[AI] Gemini AI client initialized successfully")
        except Exception as e:
            print(f"[AI] ERROR: Failed to initialize AI client: {e}\n")
            logger.error(f"[AI] Failed to initialize AI client: {e}")

    async def check_internet(self) -> bool:
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    async def validate_api_key(self, key: str) -> bool:
        if not key:
            return False
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content("test")
            return True
        except Exception as e:
            print(f"[AI] ERROR: API key validation failed: {e}\n")
            logger.error(f"[AI] API key validation failed: {e}")
            return False

    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            message_type = message_data.get('type')
            content = message_data.get('content', '')
            api_key = message_data.get('apiKey')
            
            print(f"[MSG] Processing message type: {message_type}")
            logger.info(f"[MSG] Processing message type: {message_type}")
            
            if not await self.check_internet():
                print("[MSG] ERROR: No internet connection\n")
                logger.error("[MSG] No internet connection")
                return {
                    'type': 'error',
                    'message': 'No internet connection available',
                }
            
            if message_type == 'update_api_key':
                key = message_data.get('key')
                print(f"[API] Validating API key...\n")
                if key and await self.validate_api_key(key):
                    self.initialize_ai(key)
                    print("[API] API key updated successfully\n")
                    logger.info("[API] API key updated successfully")
                    return {'type': 'api_key_update', 'success': True}
                print("[API] ERROR: Invalid API key\n")
                return {'type': 'api_key_update', 'success': False, 'error': 'Invalid API key'}
            
            if message_type == 'user_message':
                if not self.api_key and not api_key:
                    print("[MSG] ERROR: No API key configured\n")
                    logger.error("[MSG] No API key configured")
                    return {
                        'type': 'error',
                        'message': 'Please configure your API key in settings',
                    }
                
                if api_key and api_key != self.api_key:
                    print(f"[MSG] New API key provided, validating...\n")
                    if await self.validate_api_key(api_key):
                        self.api_key = api_key
                        genai.configure(api_key=api_key)
                        self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
                        print("[MSG] API key updated\n")
                    else:
                        print("[MSG] ERROR: Invalid API key\n")
                        return {
                            'type': 'error',
                            'message': 'Invalid Gemini API key',
                        }
                
                return await self.handle_user_message(content)
            
            elif message_type == 'screenshot_request':
                print("[MSG] Screenshot requested\n")
                return await self.take_screenshot()
            else:
                print(f"[MSG] ERROR: Unknown message type: {message_type}\n")
                return {'type': 'error', 'message': f'Unknown message type: {message_type}'}
                
        except Exception as e:
            print(f"[MSG] ERROR: Error processing message: {e}\n")
            logger.error(f"[MSG] Error processing message: {e}")
            return {'type': 'error', 'message': str(e)}

    async def handle_user_message(self, message: str) -> Dict[str, Any]:
        try:
            if not self.gemini_client:
                print("[LLM] ERROR: AI service not available\n")
                logger.error("[LLM] AI service not available")
                return {
                    'type': 'error',
                    'message': 'AI service is not available',
                }

            print(f"[LLM] Sending to Gemini: {message[:60]}...\n")
            logger.info(f"[LLM] Sending message to Gemini: {message[:50]}...")
            
            full_prompt = f"""{SYSTEM_PROMPT}

**User Message:** {message}

Analyze and respond in the appropriate JSON format (question or action type)."""

            response = self.gemini_client.generate_content(full_prompt)
            response_text = response.text.strip()
            
            print("[LLM] Response received from Gemini\n")
            logger.info("[LLM] Received response from Gemini")
            
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                else:
                    raise ValueError("No valid JSON found in AI response")
            
            ai_response = json.loads(json_str)
            response_type = ai_response.get('type')
            
            print(f"[LLM] Response type: {response_type}\n")
            logger.info(f"[LLM] Response type: {response_type}")
            
            if response_type == 'question':
                print("[LLM] Processing as QUESTION\n")
                logger.info("[LLM] Processing as question")
                return {
                    'type': 'ai_response',
                    'content': ai_response.get('response', ''),
                }
                
            elif response_type == 'action':
                print("[LLM] Processing as ACTION SEQUENCE\n")
                logger.info("[LLM] Processing as action sequence")
                return await self.execute_action_sequence(ai_response)
            
            else:
                raise ValueError(f"Unknown response type: {response_type}")
                
        except json.JSONDecodeError as e:
            print(f"[LLM] ERROR: JSON parsing error: {e}\n")
            logger.error(f"[LLM] JSON parsing error: {e}")
            return {
                'type': 'error',
                'message': "Failed to parse AI response",
            }
        except Exception as e:
            print(f"[LLM] ERROR: Error handling user message: {e}\n")
            logger.error(f"[LLM] Error handling user message: {e}")
            return {
                'type': 'error',
                'message': str(e),
            }

    async def execute_action_sequence(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        try:
            steps = ai_response.get('steps', [])
            response_message = ai_response.get('response', 'Executing your request...')
            
            print(f"[ACTION] Starting action sequence with {len(steps)} steps\n")
            logger.info(f"[ACTION] Starting action sequence with {len(steps)} steps")
            
            if not steps:
                print("[ACTION] ERROR: No action steps provided\n")
                return {
                    'type': 'error',
                    'message': 'No action steps provided',
                }
            
            execution_results = []
            
            for i, step in enumerate(steps):
                action = step.get('action')
                description = step.get('description', f'Step {i+1}')
                parameters = step.get('parameters', {})
                timing = step.get('timing', 0.5)
                
                print(f"[ACTION] Step {i+1}/{len(steps)}: {description}")
                logger.info(f"[ACTION] Step {i+1}/{len(steps)}: {description}")
                
                result = await self.execute_single_action(action, parameters)
                execution_results.append({
                    'step': i + 1,
                    'description': description,
                    'result': result
                })
                
                if not result.get('success'):
                    print(f"[ACTION] ERROR: Action failed at step {i+1}: {result.get('message')}\n")
                    logger.error(f"[ACTION] Action failed at step {i+1}")
                    return {
                        'type': 'error',
                        'message': f"Failed at step {i+1}: {result.get('message')}",
                    }
                
                print(f"[ACTION] Step {i+1} SUCCESS: {result.get('message')}\n")
                
                if timing > 0:
                    await asyncio.sleep(timing)
            
            print(f"[ACTION] All {len(steps)} actions completed successfully\n")
            logger.info("[ACTION] All actions completed successfully")
            return {
                'type': 'ai_response',
                'content': f"{response_message}\n\nAll {len(steps)} actions completed successfully!",
            }
            
        except Exception as e:
            print(f"[ACTION] ERROR: Error executing sequence: {e}\n")
            logger.error(f"[ACTION] Error executing sequence: {e}")
            return {
                'type': 'error',
                'message': f"Execution failed: {str(e)}",
            }

    async def execute_single_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"[EXEC] Executing action: {action}")
            
            if action == 'screenshot':
                return await self.take_screenshot()
            
            elif action == 'mouse_click':
                x = parameters.get('x')
                y = parameters.get('y')
                button = parameters.get('button', 'left')
                clicks = parameters.get('clicks', 1)
                
                if x is not None and y is not None:
                    pyautogui.click(x, y, button=button, clicks=clicks)
                    logger.info(f"[EXEC] Clicked at ({x}, {y})")
                
                return {'success': True, 'message': f'Clicked {button} button'}
            
            elif action == 'keyboard_type':
                text = parameters.get('text', '')
                interval = parameters.get('interval', 0.01)
                
                pyautogui.write(text, interval=interval)
                logger.info(f"[EXEC] Typed: {text}")
                
                return {'success': True, 'message': f'Typed: "{text}"'}
            
            elif action == 'keyboard_press':
                keys = parameters.get('keys', [])
                combination = parameters.get('combination', False)
                
                if combination and len(keys) > 1:
                    pyautogui.hotkey(*keys)
                else:
                    for key in keys:
                        pyautogui.press(key)
                
                logger.info(f"[EXEC] Pressed keys: {keys}")
                return {'success': True, 'message': f'Pressed: {", ".join(keys)}'}
            
            elif action == 'terminal_command':
                command = parameters.get('command', '')
                return await self.execute_terminal_command(command)
            
            elif action == 'wait':
                duration = parameters.get('duration', 1.0)
                await asyncio.sleep(duration)
                logger.info(f"[EXEC] Waited {duration} seconds")
                return {'success': True, 'message': f'Waited {duration} seconds'}
            
            else:
                return {'success': False, 'message': f'Unknown action: {action}'}
                
        except Exception as e:
            print(f"[EXEC] ERROR: Error executing {action}: {e}\n")
            logger.error(f"[EXEC] Error executing {action}: {e}")
            return {'success': False, 'message': str(e)}

    async def execute_terminal_command(self, command: str) -> Dict[str, Any]:
        try:
            print(f"[EXEC] Running command: {command}\n")
            logger.info(f"[EXEC] Running command: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            success = process.returncode == 0
            logger.info(f"[EXEC] Command executed with exit code: {process.returncode}")
            
            return {
                'success': success,
                'message': f"Command executed with exit code {process.returncode}"
            }
            
        except Exception as e:
            print(f"[EXEC] ERROR: Terminal command error: {e}\n")
            logger.error(f"[EXEC] Terminal command error: {e}")
            return {'success': False, 'message': str(e)}

    async def take_screenshot(self) -> Dict[str, Any]:
        try:
            timestamp = int(time.time())
            screenshot_path = self.screenshot_dir / f"screenshot_{timestamp}.png"
            
            print(f"[SCREENSHOT] Capturing screen...\n")
            logger.info(f"[SCREENSHOT] Capturing screen...")
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                img.save(screenshot_path)
            
            print(f"[SCREENSHOT] Saved to {screenshot_path}\n")
            logger.info(f"[SCREENSHOT] Saved to {screenshot_path}")
            return {
                'success': True,
                'path': str(screenshot_path),
                'message': 'Screenshot captured'
            }
            
        except Exception as e:
            print(f"[SCREENSHOT] ERROR: {e}\n")
            logger.error(f"[SCREENSHOT] Error: {e}")
            return {'success': False, 'message': str(e)}

    def run(self):
        print("[START] Computer Use Agent started - waiting for messages...\n")
        logger.info("[START] Computer Use Agent started")
        
        try:
            while self.running:
                try:
                    line = input().strip()
                    if line:
                        print(f"[INPUT] Received: {line[:80]}...\n")
                        logger.info(f"[INPUT] Received message")
                        
                        message_data = json.loads(line)
                        result = asyncio.run(self.process_message(message_data))
                        
                        print(f"[OUTPUT] Sending response\n")
                        logger.info("[OUTPUT] Sending response")
                        
                        print(json.dumps(result))
                        sys.stdout.flush()
                        
                except EOFError:
                    print("[STOP] EOF received\n")
                    break
                except json.JSONDecodeError as e:
                    print(f"[INPUT] ERROR: Invalid JSON: {e}\n")
                    logger.error(f"[INPUT] Invalid JSON: {e}")
                    print(json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
                    sys.stdout.flush()
                except Exception as e:
                    print(f"[LOOP] ERROR: {e}\n")
                    logger.error(f"[LOOP] Error: {e}")
                    print(json.dumps({'type': 'error', 'message': str(e)}))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            print("\n[STOP] Shutting down...\n")
            logger.info("[STOP] Shutting down...")
        finally:
            self.running = False

if __name__ == "__main__":
    agent = ComputerUseAgent()
    agent.run()