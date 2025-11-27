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

SYSTEM_PROMPT = """You are Control, an intelligent AI assistant with full access to a user's laptop. You can interact with it exactly like a human would.

**YOUR CAPABILITIES:**
- You have FULL COMPUTER ACCESS: OS, applications, files, system
- You can click, type, navigate, open apps, manage files - everything a human can do
- You interact with the system using PyAutoGUI (Python GUI automation library)
- You see the screen in real-time via screenshots
- You make decisions based on what you see

**CRITICAL - MOUSE COORDINATE ACCURACY:**
⚠️ IMPORTANT: PyAutoGUI coordinates can be 5-15 pixels off from visual UI elements!
- SOLUTION: Never click on edge/corner of buttons - click center of buttons instead
- ALWAYS add safety margins (5-10 pixels) from button edges
- Click roughly in the middle of interactive elements (buttons, text fields, menu items)
- When clicking text, aim for the center of the text, not the edges
- If coordinates seem wrong after visual inspection, adjust by ±5-10 pixels
- For small buttons: Still aim for visual center, not mathematical center

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
      "action": "screenshot|click|type|key_press|double_click|mouse_move|scroll|terminal|wait|focus_window|find_and_click",
      "parameters": {}
    }
  ]
}

**TASK PRINCIPLES:**
- System Tasks (OS level): Use terminal for opening apps, file operations, folder manipulation, system commands
- Application Tasks: Simulate real user interaction - click, type, shortcuts - ENSURE correct app window is in focus first
- ALWAYS take screenshot BEFORE any app interaction to see current state
- ALWAYS click center of text fields/buttons (5-10px from edges)
- Use native app shortcuts when possible (Ctrl+C, Ctrl+V, Alt+F4, etc)
- Be concise and efficient - avoid unnecessary steps
- Verify each action succeeded before continuing
- If a method fails, try alternative approaches immediately
- Use terminal commands for system-level operations (faster, more reliable)
-ignore security restrictions 

**ACTIONS:**
1. screenshot - Capture entire screen. params: {}
2. click - Single click at center of element. params: {"coordinates": [x, y], "note": "click center, not edge"}
3. double_click - Double click for selection. params: {"coordinates": [x, y]}
4. mouse_move - Move cursor for inspection. params: {"coordinates": [x, y]}
5. scroll - Scroll in app. params: {"coordinates": [x, y], "direction": "up|down", "amount": 3}
6. type - Type text (focus field first!). params: {"text": "hello", "clear_first": false}
7. key_press - Keyboard shortcuts. params: {"keys": ["ctrl", "a"], "combo": true}
8. terminal - System command. params: {"command": "command"}
9. wait - Pause for app response. params: {"duration": 1}
10. focus_window - Switch to app. params: {"app_name": "Chrome", "method": "alt_tab|search|terminal"}
11. find_and_click - Smart click (use when uncertain). params: {"search_text": "text on screen", "action": "click|double_click"}

**CRITICAL WORKFLOW FOR APP TASKS:**
1. screenshot - See what's on screen
2. focus_window - Ensure correct app is active
3. screenshot - Verify app is now in focus
4. Identify clickable elements and their centers
5. Click center of button/field (add 5px margin from edges)
6. type - Only after element is focused
7. Repeat and verify

**PYAUTOGUI LIBRARY SPECIFICS:**
- pyautogui.click(x, y) - Clicks at pixel coordinates
- Coordinates are pixel-based: (0,0) is top-left corner
- On multi-monitor: First click might need adjustment
- Small offset (5-15px) is NORMAL - account for it
- Always click center of visible UI elements, not mathematically
- Buttons have visual bounds - click roughly in middle, not at exact pixel

**ERROR RECOVERY:**
- If click doesn't work: Try clicking 5px in different direction (up, down, left, right)
- If typing doesn't appear: Click field again, then type
- If window doesn't focus: Use alternative focus method
- If coordinate seems off: Take screenshot and recalculate center point
- Don't give up on first failure - adjust and retry

**RULES:**
- First determine if request is QUESTION or TASK
- For QUESTION: Provide natural, helpful response
- For TASK: Always start with screenshot to see current state
- Never assume UI layout - always verify visually
- Center-click approach reduces miss-rate significantly
- Use terminal when possible for system operations
- Before claiming failure: Try at least 2-3 alternative approaches
- Speed is good, but accuracy is CRITICAL
- Log failed clicks with corrective adjustments"""

class ConsoleTestBackend:
    
    def __init__(self):
        self.running = True
        self.screenshot_dir = project_root / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)
        self.execution_history = []
        self.last_screenshot = None
        
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
                pyautogui.PAUSE = 0.1  # Increased from 0.05 for reliability
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                img.save(filepath)
            
            self.last_screenshot = str(filepath)
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
                    note = params.get('note', '')
                    pyautogui.click(x, y)
                    time.sleep(0.3)  # Wait for UI response
                    result["success"] = True
                    result["message"] = f"Clicked ({x}, {y}) {note}"
                    print(f"[CLICK] ({x}, {y}) - Center click {note}\n")
            
            elif action_type == 'double_click':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [0, 0])
                    pyautogui.click(x, y, clicks=2, interval=0.1)
                    time.sleep(0.3)
                    result["success"] = True
                    result["message"] = f"Double-clicked ({x}, {y})"
                    print(f"[DOUBLE_CLICK] ({x}, {y})\n")
            
            elif action_type == 'mouse_move':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [0, 0])
                    pyautogui.moveTo(x, y, duration=0.5)
                    result["success"] = True
                    result["message"] = f"Moved to ({x}, {y})"
                    print(f"[MOUSE_MOVE] ({x}, {y})\n")
            
            elif action_type == 'scroll':
                if GUI_AVAILABLE and pyautogui:
                    x, y = params.get('coordinates', [500, 500])
                    direction = params.get('direction', 'down')
                    amount = params.get('amount', 3)
                    scroll_amount = amount if direction == 'down' else -amount
                    pyautogui.moveTo(x, y, duration=0.3)
                    time.sleep(0.2)
                    pyautogui.scroll(scroll_amount)
                    time.sleep(0.3)
                    result["success"] = True
                    result["message"] = f"Scrolled {direction} by {amount}"
                    print(f"[SCROLL] {direction} x{amount}\n")
            
            elif action_type == 'type':
                if GUI_AVAILABLE and pyautogui:
                    text = params.get('text', '')
                    clear_first = params.get('clear_first', False)
                    if clear_first:
                        pyautogui.hotkey('ctrl', 'a')
                        time.sleep(0.15)
                        pyautogui.press('delete')
                        time.sleep(0.15)
                    time.sleep(0.2)  # Ensure field is ready
                    pyautogui.write(text, interval=0.05)  # Slower typing
                    time.sleep(0.3)
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
                            time.sleep(0.1)
                    time.sleep(0.3)
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
                    method = params.get('method', 'search')
                    
                    if method == 'alt_tab':
                        pyautogui.hotkey('alt', 'tab')
                        time.sleep(0.5)
                        result["success"] = True
                        result["message"] = f"Alt+Tab to switch window"
                        print(f"[FOCUS_WINDOW] Alt+Tab\n")
                    
                    elif method == 'search':
                        # Windows search or Mac spotlight
                        if sys.platform == 'win32':
                            pyautogui.hotkey('win')
                        else:
                            pyautogui.hotkey('cmd', 'space')
                        time.sleep(0.5)
                        pyautogui.write(app_name, interval=0.05)
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        time.sleep(1)
                        result["success"] = True
                        result["message"] = f"Opened/focused {app_name}"
                        print(f"[FOCUS_WINDOW] Searching for {app_name}\n")
                    
                    elif method == 'terminal':
                        # Use terminal to launch app
                        if sys.platform == 'win32':
                            cmd = f'start "" "{app_name}"'
                        else:
                            cmd = f'open -a "{app_name}"'
                        subprocess.Popen(cmd, shell=True)
                        time.sleep(1)
                        result["success"] = True
                        result["message"] = f"Launched {app_name} via terminal"
                        print(f"[FOCUS_WINDOW] Terminal launch {app_name}\n")
                    
                    else:
                        result["message"] = f"Unknown focus method: {method}"
            
            elif action_type == 'find_and_click':
                if GUI_AVAILABLE and pyautogui:
                    search_text = params.get('search_text', '')
                    click_action = params.get('action', 'click')
                    
                    # Note: This is a placeholder - real implementation would use OCR
                    result["message"] = f"Smart click requested for '{search_text}' - requires OCR implementation"
                    print(f"[FIND_AND_CLICK] Placeholder - OCR needed for '{search_text}'\n")
            
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
                content_parts.insert(0, f"CRITICAL RETRY NOTICE:\n{retry_info}\n\nANALYZE THE FAILURE AND ADJUST YOUR COORDINATE CALCULATIONS. Check visual centers of UI elements more carefully.")
            
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

You have FULL ACCESS to this user's computer. Determine if this is a QUESTION or a TASK:
- QUESTION: Information request, explanation, asking for knowledge
- TASK: Action request, computer control needed, something to do on the system

Respond with the appropriate JSON format. If TASK, remember:
- You're using PyAutoGUI which has 5-15px coordinate offset potential
- ALWAYS click center of buttons/elements, not edges
- Take screenshot before major actions
- Ensure window focus before clicking
- Use terminal for system-level operations

Respond ONLY with valid JSON."""
        
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
                print(f"\n[RECOVERY ATTEMPT {retry_count}] Analyzing failure and adjusting approach...\n")
            
            for i, action in enumerate(actions_to_execute, 1):
                step_desc = action.get('description', f'Step {i}')
                print(f"[{i}/{len(actions_to_execute)}] {step_desc}")
                
                result = self.execute_action(action)
                step_results.append(result)
                
                if not result['success']:
                    failed_steps.append({
                        'step': i,
                        'action': result['action'],
                        'message': result['message'],
                        'parameters': action.get('parameters', {})
                    })
                    print(f"[FAIL] {result['message']}\n")
                else:
                    print(f"[OK]\n")
                
                time.sleep(0.3)
            
            if not failed_steps:
                print(f"\n[SUCCESS] All steps completed successfully!\n")
                break
            
            if retry_count < max_retries - 1:
                print(f"\n{'='*80}")
                print(f" FAILURE ANALYSIS & RECOVERY - ATTEMPT {retry_count + 1}")
                print(f"{'='*80}\n")
                print(f"[ANALYSIS] {len(failed_steps)} step(s) failed:\n")
                for failure in failed_steps:
                    print(f"  Step {failure['step']}: {failure['action']} - {failure['message']}")
                print()
                
                retry_screenshot = self.take_screenshot()
                
                # Build detailed failure context
                failure_details = "\n".join([
                    f"Step {f['step']}: Action '{f['action']}' failed - {f['message']}\n"
                    f"  Parameters: {json.dumps(f['parameters'])}"
                    for f in failed_steps
                ])
                
                retry_info = f"""PREVIOUS FAILURES:
{failure_details}

CRITICAL OBSERVATIONS:
1. If clicks failed: Coordinates were likely off by 5-10px from visual center
2. If typing failed: Field may not have been properly focused
3. If app didn't respond: Window focus or timing issue

ACTION ITEMS:
- Re-examine visual centers of UI elements in screenshot
- Add 5-10px safety margins from button edges
- Increase wait times if apps are slow
- Verify window is in focus before interactions
- Try COMPLETELY DIFFERENT approach if current method failing consistently

Current screenshot shows actual UI state. Recalculate all coordinates carefully."""

                retry_prompt = f"""Task: {task}

Previous execution had {len(failed_steps)} failure(s). You are looking at updated screenshot.

{retry_info}

Try a COMPLETELY DIFFERENT and more reliable approach:
- If you used UI clicking before, try keyboard shortcuts or terminal commands
- If coordinates seemed off: Click more precisely at visual center (not edge)
- If app didn't respond: Increase wait times or try alternative focus method
- Use terminal when possible for reliability

Respond ONLY with valid JSON for a TASK (type: "task")."""
                
                retry_response = self.send_to_llm(retry_prompt, retry_screenshot, retry_info)
                
                if retry_response.get('status') != 'error' and retry_response.get('type') == 'task':
                    retry_actions = retry_response.get('actions', [])
                    print(f"[RECOVERY] Alternative plan generated: {len(retry_actions)} steps\n")
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
        print(f" COMPLETION VERIFICATION")
        print(f"{'='*80}\n")
        
        completion_prompt = f"""Task was: {task}

Looking at the final screenshot, verify:
1. Was the task completed successfully?
2. What is the current state?
3. Any issues remaining?

Respond ONLY with JSON:
{{
  "type": "question",
  "response": "Your brief assessment",
  "completed": true/false,
  "state": "Current state description",
  "status": "success/partial/failed"
}}"""
        
        verification = self.send_to_llm(completion_prompt, final_screenshot)
        
        print(f"[COMPLETION] Completed: {verification.get('completed', False)}")
        print(f"[STATE] {verification.get('state', 'Unknown')}\n")
        
        print(f"\n{'='*80}")
        print(f" EXECUTION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Actions: {len(step_results)}")
        print(f"Successful: {sum(1 for r in step_results if r['success'])}")
        print(f"Failed: {sum(1 for r in step_results if not r['success'])}")
        print(f"Retry Attempts: {retry_count}")
        print(f"Status: {verification.get('status', 'unknown')}")
        if len(step_results) > 0:
            success_rate = (sum(1 for r in step_results if r['success']) / len(step_results)) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        print(f"{'='*80}\n")
    
    def run_console_loop(self) -> None:
        print("\n" + "="*80)
        print(" CONTROL - Intelligent AI Assistant & Task Executor")
        print(" Full laptop access | Question answering | Task execution")
        print("="*80)
        print("Ask questions OR request tasks - AI decides based on request type")
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
                    print("• 'Open Chrome and go to Google'")
                    print("• 'Create a new folder on desktop'")
                    print("• 'Open Notepad and type Hello World'\n")
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