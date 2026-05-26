"""
Cyberpop AI Service Module
Communicates directly with Google Gemini API (default) or OpenAI API
via lightweight HTTP requests using the `requests` library.
Zero heavy SDK overhead for ultra-fast startup.
"""

import requests
import json
import gc
import certifi
from cyberpop_git.config import get_api_key, load_config, get_active_model

class AIServiceError(Exception):
    """Custom exception for AI Service errors."""
    pass

def secure_clear(*objs):
    """Zeroes out any mutable bytearrays and dicts, and calls gc.collect() to clear references."""
    for obj in objs:
        if isinstance(obj, bytearray):
            for i in range(len(obj)):
                obj[i] = 0
        elif isinstance(obj, dict):
            for k in list(obj.keys()):
                obj[k] = None
            obj.clear()
    gc.collect()

def generate_content(prompt: str, system_instruction: str = "") -> str:
    """
    Sends a request to the configured AI API provider (Gemini or OpenAI)
    and returns the generated string.
    """
    config = load_config()
    provider = config.get("provider", "gemini")
    api_key = get_api_key(provider)
    
    if not api_key:
        raise AIServiceError(
            f"API key is missing for provider '{provider}'.\n"
            f"Please set your API key first using: cyberpop-git config --key <YOUR_KEY>"
        )

    try:
        if provider == "gemini":
            model = config.get("gemini_model", "gemini-2.5-flash")
            return _call_gemini_api(api_key, model, prompt, system_instruction)
        elif provider == "openai":
            model = config.get("openai_model", "gpt-4o-mini")
            return _call_openai_api(api_key, model, prompt, system_instruction)
        else:
            raise AIServiceError(f"Unsupported AI provider: {provider}")
    finally:
        # Zero out plain text api_key from memory in parent scope
        if 'api_key' in locals():
            api_key = ""
        gc.collect()

def _call_gemini_api(api_key: str, model: str, prompt: str, system_instruction: str) -> str:
    """Direct HTTP POST request to Google Gemini API with memory hardening and strict SSL verification."""
    key_bytes = bytearray(api_key.encode("utf-8"))
    api_key = ""
    
    url_key = key_bytes.decode("utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={url_key}"
    url_key = ""
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\nUser Input / Request:\n{prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.95,
            "maxOutputTokens": 2048
        }
    }
    
    config = load_config()
    proxy = config.get("proxy", "")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30, proxies=proxies, verify=certifi.where())
        
        # Handle API errors
        if response.status_code == 400:
            error_info = response.json()
            error_msg = error_info.get("error", {}).get("message", "Bad Request")
            raise AIServiceError(f"Gemini Server Error (400): {error_msg}")
        elif response.status_code == 401 or response.status_code == 403:
            raise AIServiceError("Invalid or unauthorized Gemini API key. Please check your key configuration.")
        elif response.status_code != 200:
            raise AIServiceError(f"Gemini Server returned status code {response.status_code}: {response.text}")
            
        result = response.json()
        
        # Safely extract text from the payload
        candidates = result.get("candidates", [])
        if not candidates:
            # Check if blocked by safety
            prompt_feedback = result.get("promptFeedback", {})
            if prompt_feedback.get("blockReason"):
                raise AIServiceError(f"Request blocked by Gemini safety settings: {prompt_feedback.get('blockReason')}")
            raise AIServiceError("No response candidates returned by Gemini. Staged content might be blocked or empty.")
            
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts or "text" not in parts[0]:
            raise AIServiceError("Unexpected or empty AI service response format.")
            
        return parts[0]["text"].strip()
        
    except requests.exceptions.Timeout:
        raise AIServiceError("AI connection timed out. Please verify your internet connection or proxy settings.")
    except requests.exceptions.ConnectionError:
        raise AIServiceError("Network connection failed. Please check your internet connection or configured proxy.")
    except Exception as e:
        if not isinstance(e, AIServiceError):
            raise AIServiceError(f"An unexpected error occurred while communicating with the neural network: {str(e)}")
        raise e
    finally:
        secure_clear(key_bytes, headers)

def _call_openai_api(api_key: str, model: str, prompt: str, system_instruction: str) -> str:
    """Direct HTTP POST request to OpenAI Chat Completions API with memory hardening and strict SSL verification."""
    key_bytes = bytearray(api_key.encode("utf-8"))
    api_key = ""
    
    url = "https://api.openai.com/v1/chat/completions"
    
    auth_header = f"Bearer {key_bytes.decode('utf-8')}"
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    auth_header = ""
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2
    }
    
    config = load_config()
    proxy = config.get("proxy", "")
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30, proxies=proxies, verify=certifi.where())
        
        if response.status_code == 401:
            raise AIServiceError("Invalid or unauthorized OpenAI API key. Please check your key configuration.")
        elif response.status_code != 200:
            raise AIServiceError(f"OpenAI Server returned status code {response.status_code}: {response.text}")
            
        result = response.json()
        choices = result.get("choices", [])
        if not choices:
            raise AIServiceError("No response returned from OpenAI server.")
            
        return choices[0]["message"]["content"].strip()
        
    except requests.exceptions.Timeout:
        raise AIServiceError("AI connection timed out. Please verify your internet connection or proxy settings.")
    except requests.exceptions.ConnectionError:
        raise AIServiceError("Network connection failed. Please check your internet connection or configured proxy.")
    except Exception as e:
        if not isinstance(e, AIServiceError):
            raise AIServiceError(f"An unexpected error occurred while communicating with the neural network: {str(e)}")
        raise e
    finally:
        secure_clear(key_bytes, headers)

def generate_commit_message(diff_text: str) -> str:
    """
    Generates a high-quality Conventional Commit message based on a git diff.
    """
    system_instruction = (
        "You are an expert system architect and senior Git automation AI.\n"
        "Analyze the provided git diff and generate a professional Conventional Commit message.\n\n"
        "Strict Guidelines:\n"
        "1. Write in English.\n"
        "2. Follow this standard structure:\n"
        "   <type>(<scope>): <short description in present tense, lowercased>\n"
        "   \n"
        "   [Optional detailed bullet points, if the diff has major changes]\n"
        "3. Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, refactor.\n"
        "4. The summary line (first line) MUST be extremely concise, 72 characters or less.\n"
        "5. Output ONLY the commit message itself. Do NOT include markdown blocks, quotes, or conversational preamble."
    )
    
    # If diff is extremely large, truncate it to fit within token limits while preserving context
    if len(diff_text) > 40000:
        diff_text = diff_text[:40000] + "\n\n... [DIFF TRUNCATED FOR LENGTH] ..."
        
    return generate_content(diff_text, system_instruction)

def generate_daily_standup(commits: list[str]) -> str:
    """
    Generates a beautifully structured Daily Standup Report based on today's commits.
    """
    system_instruction = (
        "You are an expert technical director and senior software development team leader.\n"
        "Analyze the list of commit messages completed today and synthesize a premium, engaging, and structured Daily Standup Report.\n\n"
        "Required Report Structure (formatted in markdown):\n"
        "1. A catchy Cyberpunk-themed report title.\n"
        "2. **🚀 Achievements Today (Done Today)**: Bullet points detailing achievements accurately and professionally.\n"
        "3. **🚧 Future Outlook / Next Steps**: Actionable recommendations on what should be worked on next based on today's modifications.\n"
        "4. **💡 Architectural Insights**: Technical analysis of codebase health, patterns, and code quality changes.\n\n"
        "Guidelines:\n"
        "- Maintain an energetic, technical, and highly professional tone.\n"
        "- Do NOT enclose the entire output in Markdown code blocks (e.g. ```markdown)."
    )
    
    commits_list_str = "\n".join(f"- {c}" for c in commits)
    return generate_content(commits_list_str, system_instruction)
