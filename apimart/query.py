#!/usr/bin/env python3

import os
import sys
import json
import time
import re
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def print_help():
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║           API Mart Query Tool (q.py) - Help                    ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  q.py "Your prompt" [OPTIONS]

ARGUMENTS:
  PROMPT (required)     The text prompt to send to the API

OPTIONS:
  --model MODEL         Specify the AI model to use
                        Default: gemini-3-pro-preview-11-2025
                        
  --stream              Enable streaming mode for real-time responses
                        Default: disabled (non-streaming)
                        
  --debug               Enable extensive debugging output
                        Logs all requests, responses, retries, and timing
                        
  --timeout SECONDS     Set read timeout in seconds (default: 300 for stream, 60 for non-stream)
                        
  --retries NUMBER      Set number of retry attempts (default: 5)
                        
  --help, -h            Show this help message

EXAMPLES:
  # Basic usage (default model, non-streaming)
  q.py "write a python function to sort a list"
  
  # Use a specific model
  q.py "create a svg of switzerland" gemini-3-pro-preview-11-2025
  
  # Enable streaming for real-time output
  q.py "explain quantum entanglement" --model gpt-4o --stream
  
  # Debug mode (for troubleshooting)
  q.py "hello" --debug
  q.py "hello" --model gpt-4o --stream --debug
  
  # Custom timeout for slow models
  q.py "create detailed svg" --model gemini-3-pro-preview-11-2025 --timeout 600
  
  # Combine options
  q.py "write code" --model claude-3-5-sonnet --stream

ENVIRONMENT:
  APIMART_API_KEY       Your API key (required)
                        Set with: export APIMART_API_KEY=sk-...

OUTPUT:
  All responses are saved to: ./output/response_YYYYMMDD_HHMMSS.txt
  JSON responses saved to:    ./output/response_YYYYMMDD_HHMMSS.json
  Debug logs are saved to:    ./output/debug_YYYYMMDD_HHMMSS.log

FEATURES:
  ✓ Automatic retry logic (3 attempts with exponential backoff)
  ✓ Streaming and non-streaming modes
  ✓ Multiple model support
  ✓ Custom endpoint support
  ✓ Response logging to file
  ✓ Error handling for timeouts and connection issues
  ✓ Extensive debugging for troubleshooting

COMMON MODELS:
  - gemini-3-pro-preview-11-2025 (default)
  - gpt-4o
  - claude-3-5-sonnet
  - gemini-2-pro
  
  Use ./list-models.sh to see all available models

TROUBLESHOOTING:
  Common Issues:
  
  1. Gateway Timeout (HTTP 504):
     - Some models (like gemini-3-pro-preview) may timeout on complex tasks
     - Try without --stream: q.py "prompt" --model gemini-3-pro-preview-11-2025
     - Try faster model: q.py "prompt" --model gpt-4o
     - Increase timeout: q.py "prompt" --model MODEL --timeout 600
  
  2. Server Errors (HTTP 500-503):
     - Wait a few minutes and retry
     - Try a different model
  
  3. Connection Issues:
     - Check API key: echo $APIMART_API_KEY
     - Enable debug mode: q.py "prompt" --debug
     - Check debug log: cat output/debug_*.log
  
  4. Model Availability:
     - List available models: ./list-models.sh
     - View raw response: cat output/response_*.txt
     - Service status: Check if API Mart is operational
"""
    print(help_text)

class DebugLogger:
    def __init__(self, debug_mode, debug_file=None):
        self.debug_mode = debug_mode
        self.debug_file = debug_file
        self.start_time = time.time()
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        elapsed = time.time() - self.start_time
        log_msg = f"[{timestamp}] [{elapsed:7.3f}s] [{level:8s}] {message}"
        
        if self.debug_mode:
            print(log_msg, file=sys.stderr)
        
        if self.debug_file:
            with open(self.debug_file, "a") as f:
                f.write(log_msg + "\n")
    
    def debug(self, message):
        self.log(message, "DEBUG")
    
    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARN")
    
    def error(self, message):
        self.log(message, "ERROR")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print_help()
        sys.exit(0)
    
    api_key = os.getenv("APIMART_API_KEY")
    if not api_key:
        print("ERROR: Set your API Mart key!")
        print("   export APIMART_API_KEY=sk-...")
        print("\nFor help: q.py --help")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: q.py \"Your prompt\" [OPTIONS]")
        print("")
        print("Options:")
        print("  --model MODEL      Specify the AI model")
        print("  --stream           Enable streaming mode")
        print("  --timeout SECONDS  Set read timeout (default: 300 for stream, 60 for non-stream)")
        print("  --retries NUMBER   Set number of retry attempts (default: 5)")
        print("  --debug            Enable detailed debugging")
        print("  --help, -h         Show detailed help")
        print("")
        print("Example: q.py \"write python code\" --model gpt-4o --stream")
        print("")
        print("For full help: q.py --help")
        sys.exit(1)
    
    prompt = sys.argv[1]
    model = "gemini-3-pro-preview-11-2025"
    stream = False
    endpoint = "https://api.apimart.ai/v1/chat/completions"
    debug_mode = False
    custom_timeout = None
    max_retries = 5
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--stream":
            stream = True
        elif arg == "--debug":
            debug_mode = True
        elif arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 1
        elif arg == "--timeout" and i + 1 < len(sys.argv):
            custom_timeout = int(sys.argv[i + 1])
            i += 1
        elif arg == "--retries" and i + 1 < len(sys.argv):
            max_retries = int(sys.argv[i + 1])
            i += 1
        elif not arg.startswith("--"):
            model = arg
        i += 1
    
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"response_{timestamp}.txt"
    json_file = output_dir / f"response_{timestamp}.json"
    debug_file = output_dir / f"debug_{timestamp}.log" if debug_mode else None
    
    debug = DebugLogger(debug_mode, debug_file)
    
    debug.info("=== API Mart Query Tool Started ===")
    debug.info(f"Debug Mode: {debug_mode}")
    debug.info(f"Python Version: {sys.version}")
    debug.info(f"Requests Library Version: {requests.__version__}")
    debug.info(f"Output Directory: {output_dir.absolute()}")
    
    print("Gemini 3 Pro Preview (Nov 2025) via API Mart")
    print(f"Model: {model}")
    print(f"Prompt: {prompt}")
    print(f"Streaming: {stream}")
    if debug_mode:
        print(f"Debug Log: {debug_file}")
    print(f"Output: {output_file}")
    print("----------------------------------------")
    
    debug.debug(f"Configuration:")
    debug.debug(f"  - Model: {model}")
    debug.debug(f"  - Streaming: {stream}")
    debug.debug(f"  - Endpoint: {endpoint}")
    debug.debug(f"  - API Key (masked): {api_key[:10]}...{api_key[-5:]}")
    
    # Model-specific timeout defaults (for non-streaming mode)
    model_timeouts = {
        "gemini-3-pro-preview-11-2025": 300,  # Gemini 3 needs more time
        "gemini-2-pro": 120,
        "claude-3-opus": 120,
    }
    
    # Get model-specific timeout or use default
    if custom_timeout:
        read_timeout = custom_timeout
    elif stream:
        read_timeout = 300
    else:
        read_timeout = model_timeouts.get(model, 60)
    
    timeout = (10, read_timeout)
    debug.debug(f"  - Timeout: {timeout}")
    
    with open(output_file, "w") as f:
        f.write(f"Gemini 3 Pro Preview (Nov 2025) via API Mart\n")
        f.write(f"Model: {model}\n")
        f.write(f"Prompt: {prompt}\n")
        f.write(f"Streaming: {stream}\n")
        f.write(f"Output: {output_file}\n")
        f.write(f"JSON: {json_file}\n")
        if debug_mode:
            f.write(f"Debug Log: {debug_file}\n")
        f.write("----------------------------------------\n")
    
    # Model-specific max_tokens configuration
    model_max_tokens = {
        "gpt-4o": 16384,
        "gpt-4o-mini": 16384,
        "gpt-4-turbo": 4096,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 4096,
        "claude-3-5-sonnet": 8192,
        "claude-3-opus": 4096,
        "claude-3-sonnet": 4096,
        "claude-3-haiku": 4096,
        "gemini-3-pro-preview-11-2025": 65536,
        "gemini-2-pro": 8192,
        "gemini-pro": 8192,
    }
    
    # Get max_tokens for the selected model, default to 4096 if not found
    max_tokens = model_max_tokens.get(model, 4096)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    debug.debug(f"Request Headers (masked):")
    debug.debug(f"  - Content-Type: application/json")
    debug.debug(f"  - Authorization: Bearer {api_key[:10]}...{api_key[-5:]}")
    debug.debug(f"Request Payload:")
    debug.debug(f"  - Model: {payload['model']}")
    debug.debug(f"  - Temperature: {payload['temperature']}")
    debug.debug(f"  - Max Tokens: {payload['max_tokens']}")
    debug.debug(f"  - Stream: {payload['stream']}")
    debug.debug(f"  - Prompt Length: {len(prompt)} chars")
    
    retry_count = 0
    response = None
    
    debug.info(f"Starting API request with {max_retries} max retries")
    
    while retry_count < max_retries:
        try:
            debug.info(f"Attempt {retry_count + 1}/{max_retries}: Sending request to {endpoint}")
            debug.debug(f"  - Connect Timeout: {timeout[0]}s")
            debug.debug(f"  - Read Timeout: {timeout[1]}s")
            
            request_start = time.time()
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=timeout,
                stream=stream
            )
            request_duration = time.time() - request_start
            
            debug.info(f"Attempt {retry_count + 1}/{max_retries}: Received response (HTTP {response.status_code}) in {request_duration:.2f}s")
            debug.debug(f"  - Response Headers: {dict(response.headers)}")
            debug.debug(f"  - Response Size: {len(response.content) if response.content else 0} bytes")
            
            if response.status_code < 500:
                debug.info(f"Success: HTTP {response.status_code}")
                break
            
            debug.warning(f"Server error (HTTP {response.status_code})")
            if retry_count < max_retries - 1:
                wait_time = 2 ** retry_count
                debug.warning(f"Will retry in {wait_time}s (attempt {retry_count + 2}/{max_retries})")
                print(f"Server error (HTTP {response.status_code}). Retrying in {wait_time}s... (attempt {retry_count + 1}/{max_retries})")
                with open(output_file, "a") as f:
                    f.write(f"Server error (HTTP {response.status_code}). Retrying in {wait_time}s...\n")
                time.sleep(wait_time)
            
            retry_count += 1
        except requests.exceptions.Timeout as e:
            debug.error(f"Timeout exception: {str(e)}")
            if retry_count < max_retries - 1:
                wait_time = 2 ** retry_count
                debug.warning(f"Will retry in {wait_time}s (attempt {retry_count + 2}/{max_retries})")
                print(f"Request timeout. Retrying in {wait_time}s... (attempt {retry_count + 1}/{max_retries})")
                with open(output_file, "a") as f:
                    f.write(f"Request timeout. Retrying in {wait_time}s...\n")
                time.sleep(wait_time)
            retry_count += 1
            continue
        except requests.exceptions.ConnectionError as e:
            debug.error(f"Connection error: {str(e)}")
            if retry_count < max_retries - 1:
                wait_time = 2 ** retry_count
                debug.warning(f"Will retry in {wait_time}s (attempt {retry_count + 2}/{max_retries})")
                print(f"Connection failed. Retrying in {wait_time}s... (attempt {retry_count + 1}/{max_retries})")
                with open(output_file, "a") as f:
                    f.write(f"Connection failed. Retrying in {wait_time}s...\n")
                time.sleep(wait_time)
            retry_count += 1
            continue
        except Exception as e:
            debug.error(f"Unexpected exception: {type(e).__name__}: {str(e)}")
            retry_count += 1
            continue
    
    if response is None:
        error_msg = "\nError: Failed to connect after retries"
        print(error_msg)
        debug.error("Failed to get response after all retries")
        with open(output_file, "a") as f:
            f.write(error_msg + "\n")
        sys.exit(1)
    
    def extract_and_save_files(content):
        saved_files = []
        if not content:
            return saved_files
        
        language_ext_map = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'bash': 'sh',
            'shell': 'sh',
            'html': 'html',
            'xml': 'xml',
            'json': 'json',
            'yaml': 'yml',
            'markdown': 'md',
            'sql': 'sql',
            'css': 'css',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'rust': 'rs',
            'go': 'go',
            'ruby': 'rb',
            'php': 'php',
        }
        
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        code_blocks = {}
        for match in re.finditer(code_block_pattern, content, re.DOTALL):
            language = match.group(1) or 'txt'
            code = match.group(2)
            ext = language_ext_map.get(language.lower(), language.lower())
            # Store only the last code block for each language
            code_blocks[ext] = (language, code)
        
        # Save one file per language type (last occurrence)
        for ext, (language, code) in code_blocks.items():
            file_path = output_dir / f"output_{timestamp}_code.{ext}"
            
            with open(file_path, "w") as f:
                f.write(code)
            
            debug.info(f"Code file saved ({language}): {file_path}")
            saved_files.append(str(file_path))
        
        if "<svg" in content.lower():
            start_idx = content.lower().find("<svg")
            if start_idx != -1:
                end_idx = content.find("</svg>", start_idx)
                if end_idx != -1:
                    svg_content = content[start_idx:end_idx + 6]
                    svg_file = output_dir / f"output_{timestamp}.svg"
                    
                    with open(svg_file, "w") as f:
                        f.write(svg_content)
                    
                    debug.info(f"SVG file saved: {svg_file}")
                    saved_files.append(str(svg_file))
        
        if "<html" in content.lower():
            start_idx = content.lower().find("<html")
            if start_idx != -1:
                end_idx = content.find("</html>", start_idx)
                if end_idx == -1:
                    end_idx = len(content)
                else:
                    end_idx += 7
                
                html_content = content[start_idx:end_idx]
                html_file = output_dir / f"output_{timestamp}.html"
                
                with open(html_file, "w") as f:
                    f.write(html_content)
                
                debug.info(f"HTML file saved: {html_file}")
                saved_files.append(str(html_file))
        
        return saved_files
    
    try:
        debug.info(f"Processing response (HTTP {response.status_code})")
        
        if response.status_code == 200:
            if stream:
                debug.info("Processing streaming response")
                print("\nResponse:\n")
                full_content = ""
                with open(output_file, "a") as f:
                    f.write("\nResponse:\n\n")
                    chunk_count = 0
                    for line in response.iter_lines():
                        if line:
                            chunk_count += 1
                            line = line.decode("utf-8") if isinstance(line, bytes) else line
                            debug.debug(f"Received chunk {chunk_count}: {line[:100]}...")
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    choices = data.get("choices", [])
                                    if choices and len(choices) > 0:
                                        content = choices[0].get("delta", {}).get("content", "")
                                        if content:
                                            print(content, end="", flush=True)
                                            f.write(content)
                                            full_content += content
                                except json.JSONDecodeError as e:
                                    debug.warning(f"Failed to parse JSON chunk: {e}")
                                    pass
                    debug.info(f"Streaming complete: received {chunk_count} chunks")
                
                svg_file = extract_and_save_files(full_content)
                if svg_file:
                    for file in svg_file:
                        print(f"✓ File saved: {file}")
                        with open(output_file, "a") as f:
                            f.write(f"✓ File saved: {file}\n")
                
                print("\nDone.")
                with open(output_file, "a") as f:
                    f.write("\nDone.\n")
                debug.info("Streaming response processed successfully")
            else:
                debug.info("Processing non-streaming response")
                try:
                    data = response.json()
                    debug.debug(f"Response JSON: {json.dumps(data, indent=2)[:500]}...")
                    # Save the full JSON response to file
                    with open(json_file, "w") as f:
                        json.dump(data, f, indent=2)
                    debug.info(f"JSON response saved to: {json_file}")
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        print(f"\nResponse:\n")
                        print(content[:500])
                        debug.info(f"Response content received ({len(content)} chars)")
                        with open(output_file, "a") as f:
                            f.write(f"\nResponse:\n\n{content}\n")

                        svg_file = extract_and_save_files(content)
                        if svg_file:
                            for file in svg_file:
                                print(f"✓ File saved: {file}")
                                with open(output_file, "a") as f:
                                    f.write(f"✓ File saved: {file}\n")
                    else:
                        print("\nFailed to parse response:")
                        print(response.text)
                        debug.error("No content found in response")
                        with open(output_file, "a") as f:
                            f.write(f"\nFailed to parse response:\n{response.text}\n")
                except json.JSONDecodeError as e:
                    debug.error(f"Failed to parse response JSON: {e}")
                    print("\nFailed to parse response:")
                    print(response.text[:500])
                    with open(output_file, "a") as f:
                        f.write(f"\nFailed to parse response:\n{response.text}\n")
        else:
            debug.error(f"HTTP {response.status_code} error")
            print(f"\nFailed (HTTP {response.status_code})")
            
            error_advice = []
            
            if response.status_code == 504:
                print("Gateway timeout - the server took too long to respond")
                error_advice.append("Gateway timeout - the server took too long to respond")
                error_advice.append("\nTroubleshooting suggestions:")
                
                if stream:
                    suggestion1 = f"  1. Try without --stream flag (faster, less overhead):"
                    suggestion1_cmd = f"     ./q.py \"{prompt}\" --model {model}"
                    print(suggestion1)
                    print(suggestion1_cmd)
                    error_advice.append(suggestion1)
                    error_advice.append(suggestion1_cmd)
                    
                    suggestion2 = f"  2. Try a faster model:"
                    suggestion2_cmd = f"     ./q.py \"{prompt}\" --model gpt-4o --stream"
                    print(suggestion2)
                    print(suggestion2_cmd)
                    error_advice.append(suggestion2)
                    error_advice.append(suggestion2_cmd)
                else:
                    suggestion1 = f"  1. Try a faster model (recommended):"
                    suggestion1_cmd = f"     ./q.py \"{prompt}\" --model gpt-4o"
                    print(suggestion1)
                    print(suggestion1_cmd)
                    error_advice.append(suggestion1)
                    error_advice.append(suggestion1_cmd)
                    
                    suggestion2 = f"  2. Increase the timeout:"
                    suggestion2_cmd = f"     ./q.py \"{prompt}\" --model {model} --timeout 600"
                    print(suggestion2)
                    print(suggestion2_cmd)
                    error_advice.append(suggestion2)
                    error_advice.append(suggestion2_cmd)
                    
                    suggestion3 = f"  3. Try with streaming:"
                    suggestion3_cmd = f"     ./q.py \"{prompt}\" --model {model} --stream"
                    print(suggestion3)
                    print(suggestion3_cmd)
                    error_advice.append(suggestion3)
                    error_advice.append(suggestion3_cmd)
                
                debug.error("Gateway timeout detected")
            elif response.status_code >= 500:
                print("Server error - API may be temporarily unavailable")
                error_advice.append("Server error - API may be temporarily unavailable")
                error_advice.append("\nTroubleshooting suggestions:")
                error_advice.append("  1. Wait a few minutes and try again")
                error_advice.append("  2. Try a different model")
                error_advice.append(f"     ./q.py \"{prompt}\" --model gpt-4o")
                for line in error_advice[1:]:
                    print(line)
                debug.error("Server-side error detected")
            
            response_text = response.text
            is_html = response_text.strip().startswith("<")
            
            debug.debug(f"Response is HTML: {is_html}")
            debug.debug(f"Response size: {len(response_text)} chars")
            
            if is_html:
                print(f"(HTML error response - see {output_file} for details)")
                debug.debug(f"HTML response preview: {response_text[:200]}...")
            else:
                print(response_text)
                debug.debug(f"Full response: {response_text}")
            
            with open(output_file, "a") as f:
                f.write(f"\nFailed (HTTP {response.status_code})\n")
                if error_advice:
                    for advice_line in error_advice:
                        f.write(advice_line + "\n")
                f.write(f"\n{response_text}\n")
    
    except Exception as e:
        debug.error(f"Exception during response processing: {type(e).__name__}: {e}")
        print(f"\nError: {e}")
        with open(output_file, "a") as f:
            f.write(f"\nError: {e}\n")
    
    debug.info("=== API Mart Query Tool Completed ===")
    if debug_mode:
        print(f"\nDebug log saved to: {debug_file}")

if __name__ == "__main__":
    main()
