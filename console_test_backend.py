#!/usr/bin/env python3
"""
Console Test Backend - Control Project
Enhanced AI agent with precise task execution, error recovery, and adaptive planning
"""

import sys
import json
import time
import asyncio
import logging
import os
import subprocess
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

try:
    GUI_AVAILABLE = False
    
    import mss
    try:
        import pyperclip
    except ImportError:
        pyperclip = None
    from PIL import Image
    import google.generativeai as genai
    
    try:
        import pyautogui
        GUI_AVAILABLE = True
    except ImportError:
        pyautogui = None
        GUI_AVAILABLE = False
    
except ImportError as e:
    print(f"Missing dependency: {e}", file=sys.stderr)
    print("Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [CONTROL] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('control.log')
    ]
)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Control, an intelligent AI assistant that can:
1. ANSWER QUESTIONS: Respond to queries, provide information, explanations
2. EXECUTE TASKS: Control computer - click, type, open apps, manipulate files

**DETERMINE REQUEST TYPE:**
- QUESTION: "What is X?", "How do I?", "Explain", "Tell me about", "Why is", "Information requests"
  → Respond naturally with information/explanation
- TASK: "Open X", "Create Y", "Send message", "Move file", "Click button", "Action requests"
  → Execute computer actions

**FOR QUESTIONS - RESPOND WITH:**
{
  "type": "question",
  "response": "Your detailed answer to the user",
  "requires_action": false
}

**FOR TASKS - RESPOND WITH:**
{
  "type": "task",
  "analysis": "Brief analysis of current state and optimal approach",
  "plan": "Concise step-by-step plan",
  "actions": [
    {
      "step": 1,
      "description": "Brief description",
      "action": "screenshot|click|type|key_press|double_click|mouse_move|scroll|terminal|wait|focus_window",
      "parameters": {}
    }
  ]
}

**TASK PRINCIPLES:**
- System Tasks (OS level): Use terminal for opening apps, file operations, folder manipulation, system commands
- Application Tasks: Simulate real user - click, type, shortcuts - ALWAYS ensure correct app window is in focus first
- Always click text fields before typing to ensure focus
- Use native app shortcuts when possible
- Be concise and efficient - avoid unnecessary steps
- If a method fails, try alternative approaches

**ACTIONS:**
1. screenshot - Capture screen. params: {}
2. click - Single click. params: {"coordinates": [x, y]}
3. double_click - Double click. params: {"coordinates": [x, y]}
4. mouse_move - Move cursor. params: {"coordinates": [x, y]}
5. scroll - Scroll wheel. params: {"coordinates": [x, y], "direction": "up|down", "amount": 3}
6. type - Type text. params: {"text": "hello", "clear_first": false}
7. key_press - Keys/shortcuts. params: {"keys": ["ctrl", "a"], "combo": true}
8. terminal - OS command. params: {"command": "command"}
9. wait - Pause. params: {"duration": 1}
10. focus_window - Switch to app window. params: {"app_name": "Chrome", "method": "alt_tab|search"}

**RULES:**
- First determine if request is a QUESTION or TASK
- For questions: Provide natural, helpful response
- For tasks: Use terminal for system operations, UI interaction for applications
- System tasks: Use terminal commands (fastest, most reliable)
- App interactions: ALWAYS screenshot first to see current state
- Before app interaction: Check window focus, switch if needed using focus_window action
- ALWAYS click text fields before typing
- Use keyboard shortcuts for efficiency
- If action fails: Try alternative method
- Speed and precision are both important"""

class ConsoleTestBackend:
    
    def __init__(self):
        self.running = True
        self.screenshot_dir = project_root / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        self.execution_history = []
        
        self.setup_gemini_api()
        self.setup_computer_control()
        
        logger.info("Control Backend initialized successfully")
    
    def setup_gemini_api(self):
        api_key = os.getenv('GEMINI_FREE_KEY')
        if not api_key:
            api_key = "test_api_key"
            logger.warning("No API key found")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash', 
                                             system_instruction=SYSTEM_PROMPT)
            print("[API] Ready\n")
            logger.info("API configured")
        except Exception as e:
            print(f"[API] ERROR: {e}\n")
            self.model = None
    
    def setup_computer_control(self):
        try:
            if GUI_AVAILABLE and pyautogui:
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = 0.05
                print("[CONTROL] GUI libraries ready\n")
            
            try:
                with mss.mss() as sct:
                    monitors = sct.monitors
                    print(f"[CONTROL] {len(monitors)-1} monitor(s) detected\n")
            except Exception as e:
                print(f"[CONTROL] WARNING: {e}\n")
        except Exception as e:
            print(f"[CONTROL] ERROR: {e}\n")
    
    def take_screenshot(self) -> str:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                img.save(filepath)
            
            logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return ""
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        result = {"success": False, "message": "", "action": action.get('action')}
        
        try:
            action_type = action.get('action', '').lower()
            params = action.get('parameters', {})
            
            if action_type == 'screenshot':
                filepath = self.take_screenshot()
                result["success"] = bool(filepath)
                result["message"] = filepath
                print(f"[SCREENSHOT] Captured\n")
            
            elif action_type == 'click':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [0, 0])
                    pyautogui.click(x, y)
                    result["success"] = True
                    result["message"] = f"Clicked ({x}, {y})"
                    print(f"[CLICK] ({x}, {y})\n")
            
            elif action_type == 'double_click':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [0, 0])
                    pyautogui.click(x, y, clicks=2)
                    result["success"] = True
                    result["message"] = f"Double-clicked ({x}, {y})"
                    print(f"[DOUBLE_CLICK] ({x}, {y})\n")
            
            elif action_type == 'mouse_move':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [0, 0])
                    pyautogui.moveTo(x, y)
                    result["success"] = True
                    result["message"] = f"Moved to ({x}, {y})"
                    print(f"[MOUSE_MOVE] ({x}, {y})\n")
            
            elif action_type == 'scroll':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [500, 500])
                    direction = params.get('direction', 'down')
                    amount = params.get('amount', 3)
                    scroll_amount = amount if direction == 'down' else -amount
                    pyautogui.moveTo(x, y)
                    pyautogui.scroll(scroll_amount)
                    result["success"] = True
                    result["message"] = f"Scrolled {direction} by {amount}"
                    print(f"[SCROLL] {direction} x{amount}\n")
            
            elif action_type == 'type':
                if GUI_AVAILABLE and pyautogui:
                    text = params.get('text', '')
                    clear_first = params.get('clear_first', False)
                    if clear_first:
                        pyautogui.hotkey('ctrl', 'a')
                        time.sleep(0.1)
                    pyautogui.write(text)
                    result["success"] = True
                    result["message"] = f"Typed: {text[:30]}"
                    print(f"[TYPE] {text[:30]}\n")
            
            elif action_type == 'key_press':
                if GUI_AVAILABLE and pyautogui:
                    keys = params.get('keys', [])
                    combo = params.get('combo', len(keys) > 1)
                    if combo and len(keys) > 1:
                        pyautogui.hotkey(*keys)
                    else:
                        for key in keys:
                            pyautogui.press(key)
                    result["success"] = True
                    result["message"] = f"Keys: {'+'.join(keys)}"
                    print(f"[KEY_PRESS] {'+'.join(keys)}\n")
            
            elif action_type == 'terminal':
                command = params.get('command', '')
                try:
                    output = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                    result["success"] = output.returncode == 0
                    result["message"] = output.stdout[:200] if output.stdout else output.stderr[:200]
                    print(f"[TERMINAL] {command}\n")
                except Exception as e:
                    result["message"] = str(e)
            
            elif action_type == 'wait':
                duration = params.get('duration', 1)
                time.sleep(duration)
                result["success"] = True
                result["message"] = f"Waited {duration}s"
                print(f"[WAIT] {duration}s\n")
            
            elif action_type == 'focus_window':
                if GUI_AVAILABLE and pyautogui:
                    app_name = params.get('app_name', '')
                    method = params.get('method', 'alt_tab')
                    
                    if method == 'alt_tab':
                        pyautogui.hotkey('alt', 'tab')
                        result["success"] = True
                        result["message"] = f"Alt+Tab to switch window"
                        print(f"[FOCUS_WINDOW] Alt+Tab\n")
                    elif method == 'search':
                        pyautogui.hotkey('win')
                        time.sleep(0.3)
                        pyautogui.write(app_name)
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        result["success"] = True
                        result["message"] = f"Opened/focused {app_name}"
                        print(f"[FOCUS_WINDOW] Searching for {app_name}\n")
                    else:
                        result["message"] = f"Unknown focus method: {method}"
            
            else:
                result["message"] = f"Unknown action: {action_type}"
        
        except Exception as e:
            result["message"] = str(e)
            print(f"[ERROR] {e}\n")
            logger.error(f"Action error: {e}")
        
        return result
    
    def send_to_llm(self, prompt: str, screenshot_path: str = None, retry_info: str = None) -> Dict[str, Any]:
        try:
            if not self.model:
                return {"status": "error", "actions": []}
            
            print(f"[LLM] Processing...\n")
            
            content_parts = [prompt]
            
            if retry_info:
                content_parts.insert(0, f"RETRY NOTICE: {retry_info}\nPlease revise your plan based on this feedback.")
            
            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, 'rb') as f:
                    image_data = f.read()
                content_parts.append({
                    "mime_type": "image/png",
                    "data": image_data
                })
            
            response = self.model.generate_content(content_parts)
            response_text = response.text.strip()
            
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                else:
                    raise ValueError("No JSON found")
            
            llm_response = json.loads(json_str)
            action_count = len(llm_response.get('actions', []))
            print(f"[LLM] Plan: {action_count} steps\n")
            logger.info("LLM response received")
            return llm_response
        
        except Exception as e:
            print(f"[LLM] ERROR: {e}\n")
            logger.error(f"LLM error: {e}")
            return {"status": "error", "actions": []}
    
    def execute_task(self, user_request: str) -> None:
        print(f"\n{'='*80}")
        print(f" REQUEST: {user_request}")
        print(f"{'='*80}\n")
        
        screenshot_path = self.take_screenshot()
        if not screenshot_path:
            print("[ERROR] Cannot capture initial screenshot\n")
            return
        
        prompt = f"""User Request: {user_request}

Determine if this is a QUESTION or a TASK:
- QUESTION: Information request, explanation, asking for knowledge
- TASK: Action request, computer control needed, something to do on the system

Respond with the appropriate JSON format:
- For QUESTION: {{"type": "question", "response": "Your answer", "requires_action": false}}
- For TASK: {{"type": "task", "analysis": "...", "plan": "...", "actions": [...]}}"""
        
        initial_response = self.send_to_llm(prompt, screenshot_path)
        
        if initial_response.get('status') == 'error':
            print(f"[ERROR] Failed to process request\n")
            return
        
        request_type = initial_response.get('type', 'unknown')
        
        if request_type == 'question':
            print(f"[TYPE] Question detected\n")
            response = initial_response.get('response', '')
            print(f"[ANSWER]\n{response}\n")
            print(f"{'='*80}\n")
            return
        
        elif request_type == 'task':
            print(f"[TYPE] Task detected\n")
            self._execute_task_actions(user_request, initial_response, screenshot_path)
        
        else:
            print(f"[ERROR] Unknown request type: {request_type}\n")
    
    def _execute_task_actions(self, task: str, llm_response: Dict[str, Any], initial_screenshot: str) -> None:
        analysis = llm_response.get('analysis', '')
        plan = llm_response.get('plan', '')
        actions = llm_response.get('actions', [])
        
        print(f"[ANALYSIS] {analysis}\n")
        print(f"[PLAN] {plan}\n")
        print(f"[EXECUTING] {len(actions)} steps\n")
        
        step_results = []
        failed_steps = []
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            if retry_count == 0:
                actions_to_execute = actions
                step_results = []
                failed_steps = []
            else:
                actions_to_execute = retry_actions
                print(f"\n[RECOVERY ATTEMPT {retry_count}] Executing alternative plan...\n")
            
            for i, action in enumerate(actions_to_execute, 1):
                step_desc = action.get('description', f'Step {i}')
                print(f"[{i}/{len(actions_to_execute)}] {step_desc}")
                
                result = self.execute_action(action)
                step_results.append(result)
                
                if not result['success']:
                    failed_steps.append({
                        'step': i,
                        'action': result['action'],
                        'message': result['message']
                    })
                    print(f"[FAIL] {result['message']}\n")
                else:
                    print(f"[OK]\n")
                
                time.sleep(0.2)
            
            if not failed_steps:
                print(f"\n[SUCCESS] All steps completed successfully!\n")
                break
            
            if retry_count < max_retries - 1:
                print(f"\n{'='*80}")
                print(f" FAILURE RECOVERY - ATTEMPT {retry_count + 1}")
                print(f"{'='*80}\n")
                print(f"[RECOVERY] {len(failed_steps)} step(s) failed. Trying alternative approach...\n")
                
                retry_screenshot = self.take_screenshot()
                retry_info = f"Previous plan failed at steps: {[f['step'] for f in failed_steps]}. Errors: {json.dumps(failed_steps)}"
                
                retry_prompt = f"""Task: {task}

Previous execution had failures. Analyze current screen and create a COMPLETELY DIFFERENT plan.
Failed steps details:
{json.dumps(failed_steps, indent=2)}

Try a completely different approach:
- If you used UI before, try terminal
- If you used terminal, try UI
- Change the method/tool used
- Be more precise with coordinates(calculate perfectly becausea wrong coordinate means a wrong click note you are using pyautogui for the mouse control so understand how it works)
- Check app window focus before interacting

Create a better plan that avoids these failures using alternative methods.
Respond ONLY with JSON for a TASK (type: "task")."""
                
                retry_response = self.send_to_llm(retry_prompt, retry_screenshot, retry_info)
                
                if retry_response.get('status') != 'error' and retry_response.get('type') == 'task':
                    retry_actions = retry_response.get('actions', [])
                    print(f"[RECOVERY] Alternative plan: {len(retry_actions)} steps\n")
                    retry_count += 1
                    continue
                else:
                    print(f"[ERROR] Could not generate recovery plan\n")
                    break
            else:
                print(f"\n[ERROR] Max retry attempts ({max_retries}) reached. Task may not be completable.\n")
                break
        
        final_screenshot = self.take_screenshot()
        
        print(f"\n{'='*80}")
        print(f" COMPLETION CHECK")
        print(f"{'='*80}\n")
        
        completion_prompt = f"""Task was: {task}

Analyze final screenshot and confirm:
1. Was task completed successfully?
2. Current system state?
3. Any issues?

Respond ONLY with JSON:
{{
  "type": "question",
  "response": "Your assessment (this is just for verification)",
  "completed": true/false,
  "state": "Your assessment",
  "status": "success/partial/failed"
}}"""
        
        verification = self.send_to_llm(completion_prompt, final_screenshot)
        
        print(f"[COMPLETION] Completed: {verification.get('completed', False)}")
        print(f"[STATE] {verification.get('state', 'Unknown')}\n")
        
        print(f"\n{'='*80}")
        print(f" SUMMARY")
        print(f"{'='*80}")
        print(f"Total Actions: {len(step_results)}")
        print(f"Successful: {sum(1 for r in step_results if r['success'])}")
        print(f"Failed: {sum(1 for r in step_results if not r['success'])}")
        print(f"Retry Attempts: {retry_count}")
        print(f"Status: {verification.get('status', 'unknown')}")
        print(f"{'='*80}\n")
    
    def run_console_loop(self) -> None:
        print("\n" + "="*80)
        print(" CONTROL - Intelligent AI Assistant & Task Executor")
        print("="*80)
        print("Answer questions OR execute tasks - AI decides based on request type")
        print("Commands: 'help' | 'screenshot' | 'quit'\n")
        
        while self.running:
            try:
                user_input = input(">> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("• screenshot - Capture current screen")
                    print("• quit/exit - Exit program")
                    print("\nQuestion Examples:")
                    print("• 'What is Python?'")
                    print("• 'How do I make pasta?'")
                    print("• 'Explain quantum computing'")
                    print("\nTask Examples:")
                    print("• 'Open Chrome'")
                    print("• 'Send a message on WhatsApp'")
                    print("• 'Create a new folder'\n")
                    continue
                
                elif user_input.lower() == 'screenshot':
                    path = self.take_screenshot()
                    print(f"Saved to {path}\n")
                    continue
                
                self.execute_task(user_input)
            
            except KeyboardInterrupt:
                print("\nExit!")
                break
            except Exception as e:
                print(f"[ERROR] {e}\n")
                logger.error(f"Error: {e}")

def main():
    try:
        backend = ConsoleTestBackend()
        backend.run_console_loop()
    except Exception as e:
        print(f"[FATAL] {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()