import os
import sys
import unittest
from unittest.mock import patch

from cyberpop_git.config import encrypt_value, decrypt_value, get_hardware_key
from cyberpop_git.main import sanitize_env
from cyberpop_git.ai_service import secure_clear

class TestCyberpopSecurity(unittest.TestCase):
    def test_encryption_decryption(self):
        """Verify that encrypting a key yields the encrypted prefix, and decrypting it returns the original."""
        secret = "secret_api_key_12345"
        encrypted = encrypt_value(secret)
        
        self.assertTrue(encrypted.startswith("cyberpop_enc:"))
        self.assertNotEqual(secret, encrypted)
        
        decrypted = decrypt_value(encrypted)
        self.assertEqual(secret, decrypted)

    def test_device_binding(self):
        """Verify that decryption fails if the hardware key changes (simulating key theft on another machine)."""
        secret = "secret_api_key_12345"
        encrypted = encrypt_value(secret)
        
        # Mock get_hardware_key to return a different key
        with patch('cyberpop_git.config.get_hardware_key', return_value=b"another_machine_guid_32_bytes_x"):
            decrypted = decrypt_value(encrypted)
            # Should fail to decrypt and return empty string or raise error
            self.assertEqual(decrypted, "")

    def test_environment_sanitization(self):
        """Verify that REQUESTS_CA_BUNDLE and CURL_CA_BUNDLE are wiped on startup."""
        os.environ["REQUESTS_CA_BUNDLE"] = "fake_path/charles_proxy.pem"
        os.environ["CURL_CA_BUNDLE"] = "fake_path/fiddler_proxy.pem"
        
        sanitize_env()
        
        self.assertNotIn("REQUESTS_CA_BUNDLE", os.environ)
        self.assertNotIn("CURL_CA_BUNDLE", os.environ)

    def test_memory_zeroing(self):
        """Verify that secure_clear zeroes out mutable bytearrays in RAM."""
        arr = bytearray(b"highly_sensitive_api_key")
        secure_clear(arr)
        
        # Verify all elements in bytearray are 0
        for b in arr:
            self.assertEqual(b, 0)

if __name__ == "__main__":
    unittest.main()
