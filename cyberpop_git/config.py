"""
Cyberpop Config Module
Handles local loading and saving of user configuration data,
including Gemini/OpenAI API keys, preferred models, and user parameters.
Stored securely on client-side at ~/.cyberpop-git/config.json
"""

import os
import json
import base64
import hashlib
import uuid
import sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

CONFIG_DIR = Path.home() / ".cyberpop-git"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENCRYPTION_PREFIX = "cyberpop_enc:"

DEFAULT_CONFIG = {
    "provider": "gemini",
    "gemini_model": "gemini-2.5-flash",
    "openai_model": "gpt-4o-mini",
    "gemini_api_key": "",
    "openai_api_key": "",
    "proxy": ""
}

def get_hardware_key() -> bytes:
    """Generates a stable, unique 32-byte key (AES-256) specific to this Windows machine."""
    machine_guid = ""
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        except Exception:
            pass
    if not machine_guid:
        machine_guid = os.environ.get("COMPUTERNAME", "default_cyberpop_guid")
        
    mac = str(uuid.getnode())
    username = os.getlogin() if hasattr(os, "getlogin") else os.environ.get("USERNAME", "default_cyberpop_user")
    
    combined = f"{machine_guid}-{mac}-{username}"
    return hashlib.sha256(combined.encode("utf-8")).digest()

def encrypt_value(plain_text: str) -> str:
    """Encrypts plain_text using AES-256-GCM and returns a base64 encoded string with a prefix."""
    if not plain_text:
        return ""
    try:
        key = get_hardware_key()
        nonce = os.urandom(12)  # GCM standard nonce size (96 bits)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plain_text.encode("utf-8")) + encryptor.finalize()
        # Pack nonce + tag + ciphertext
        packed = nonce + encryptor.tag + ciphertext
        return ENCRYPTION_PREFIX + base64.b64encode(packed).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Encryption failed: {str(e)}")

def decrypt_value(cipher_text: str) -> str:
    """Decrypts a base64 encoded AES-256-GCM string if it starts with the prefix."""
    if not cipher_text:
        return ""
    if not cipher_text.startswith(ENCRYPTION_PREFIX):
        return cipher_text
    try:
        raw_b64 = cipher_text[len(ENCRYPTION_PREFIX):]
        key = get_hardware_key()
        packed = base64.b64decode(raw_b64.encode("utf-8"))
        if len(packed) < 28:
            return ""
        nonce = packed[:12]
        tag = packed[12:28]
        ciphertext = packed[28:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted.decode("utf-8")
    except Exception:
        return ""

def ensure_config_dir():
    """Ensures the configuration directory exists."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """Loads configuration from the local JSON file. Fallbacks to default values if not found."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """Saves configuration data back to config.json."""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Failed to write configuration file: {str(e)}")

def get_api_key(provider: str = None) -> str:
    """Retrieves the API key for the selected provider. Fallbacks to environment variables if config is empty."""
    config = load_config()
    target_provider = provider or config.get("provider", "gemini")
    
    raw_key = ""
    if target_provider == "gemini":
        raw_key = config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
    elif target_provider == "openai":
        raw_key = config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
        
    if not raw_key:
        return ""
        
    return decrypt_value(raw_key.strip())

def set_api_key(key: str, provider: str = "gemini"):
    """Saves the API key locally."""
    config = load_config()
    encrypted = encrypt_value(key)
    if provider == "gemini":
        config["gemini_api_key"] = encrypted
    elif provider == "openai":
        config["openai_api_key"] = encrypted
    save_config(config)

def get_active_model() -> str:
    """Gets the active AI model name based on selected provider."""
    config = load_config()
    provider = config.get("provider", "gemini")
    if provider == "gemini":
        return config.get("gemini_model", "gemini-2.5-flash")
    return config.get("openai_model", "gpt-4o-mini")

def update_setting(key: str, value: str):
    """Updates a single setting key and saves configuration."""
    config = load_config()
    config[key] = value
    save_config(config)
