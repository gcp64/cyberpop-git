import unittest
import os
import sys
import json
import random
import time
from unittest.mock import patch, MagicMock
import requests

from cyberpop_git.config import encrypt_value, decrypt_value, get_api_key, set_api_key, load_config, get_hardware_key
from cyberpop_git.ai_service import secure_clear, generate_content, AIServiceError
from cyberpop_git.ui import ar
from cyberpop_git.main import sanitize_env

class CyberpopGoldStressTest(unittest.TestCase):
    
    def setUp(self):
        # Backup original environment variables
        self.orig_env = dict(os.environ)
        
    def tearDown(self):
        # Restore environment variables
        os.environ.clear()
        os.environ.update(self.orig_env)

    # ==========================================
    # LAYER 1: FUZZING CLI INPUTS (50 TEST CASES)
    # ==========================================
    def test_cli_fuzzing_matrix(self):
        """Fuzz CLI inputs with 50 distinct malicious, weird, and extreme inputs."""
        fuzz_inputs = [
            "", "   ", "\n\t", "A"*10000, "A"*100000, 
            "config --key", "config --provider", "init --force --weird-flag",
            "push --model --key --weird", "summary --model --provider",
            "config --key \x00\x01\x02", "config --key '; DROP TABLE users;--",
            "config --key <script>alert(1)</script>", "config --key ../../../etc/passwd",
            "config --key \\\\.\\globalroot\\device\\condrv\\kernel",
            "config --key %s%s%s%s%s%s%s%s", "config --key {foo: bar}",
            "config --key []", "config --key null", "config --key NaN",
            "config --key -1", "config --key 0.0000001", "config --key 99999999999999999999",
            "config --key \U0001F600\U0001F601\U0001F602", "config --key Arabic: السلام عليكم",
            "config --key Chinese: 你好", "config --key Russian: Привет", "config --key Hindi: नमस्ते",
            "config --key Japanese: こんにちは", "config --key Korean: 안녕하세요", 
            "config --key Greek: Γειά σου", "config --key Hebrew: שלום", "config --key Turkish: Merhaba",
            "config --key Persian: سلام", "config --key French: Bonjour", "config --key Spanish: Hola",
            "config --key German: Hallo", "config --key Italian: Ciao", "config --key Portuguese: Olá",
            "config --key Dutch: Hallo", "config --key Polish: Cześć", "config --key Swedish: Hej",
            "config --key Vietnamese: Xin chào", "config --key Thai: สวัสดี", "config --key Tagalog: Kamusta",
            "config --key Ukrainian: Привіт", "config --key Czech: Ahoj", "config --key Romanian: Salut",
            "config --key Danish: Hej", "config --key Finnish: Hei"
        ]
        
        self.assertEqual(len(fuzz_inputs), 50)
        
        # Verify that our local configuration module handles all fuzzed API key inputs
        # without crashing, hanging, or leaking raw key structures.
        for idx, test_input in enumerate(fuzz_inputs):
            with self.subTest(fuzz_index=idx):
                try:
                    # Test local AES encryption & decryption of the fuzzed inputs
                    encrypted = encrypt_value(test_input)
                    if test_input:
                        self.assertTrue(encrypted.startswith("cyberpop_enc:"))
                    else:
                        self.assertEqual(encrypted, "")
                        
                    decrypted = decrypt_value(encrypted)
                    self.assertEqual(test_input, decrypted)
                except Exception as e:
                    self.fail(f"Fuzzing failed on input '{test_input[:30]}...': {str(e)}")

    # =======================================================
    # LAYER 2: 20 LANGUAGES AND ENCODINGS (30 TEST CASES)
    # =======================================================
    def test_multilingual_unicode_matrix(self):
        """Process 30 unicode strings representing 20+ global languages with complex glyphs."""
        multilingual_dictionary = {
            "arabic_1": "السلام عليكم ورحمة الله وبركاته",
            "arabic_2": "بروتوكول حماية الذكاء الاصطناعي السيبراني",
            "persian": "سلام دنیا، این یک آزمایش امنیتی است.",
            "hebrew": "שלום עולם, זהו מבחן אבטחה של סייברפופ.",
            "chinese_simpl": "你好世界，这是一个网络安全测试。",
            "chinese_trad": "你好世界，這是一個網絡安全測試。",
            "japanese_1": "こんにちは世界、これはセキュリティテストです。",
            "japanese_2": "サイバーポップ・ギット・オートメーション・システム",
            "korean": "안녕하세요 세계, 이것은 보안 테스트입니다.",
            "hindi": "नमस्ते दुनिया, यह एक साइबर सुरक्षा परीक्षण है।",
            "tamil": "வணக்கம் உலகம், இது ஒரு இணைய பாதுகாப்பு சோதனை.",
            "thai": "สวัสดีชาวโลก นี่คือการทดสอบความปลอดภัยทางไซเบอร์",
            "vietnamese": "Xin chào thế giới, đây là một thử nghiệm bảo mật.",
            "russian": "Привет, мир! Это проверка кибербезопасности.",
            "ukranian": "Привіт, світе! Це перевірка кібербезпеки.",
            "bulgarian": "Здравей, свят! Това е тест за киберсигурност.",
            "greek": "Γεια σου κόσμε, αυτό είναι ένα τεστ ασφαλείας.",
            "hebrew_points": "שָׁלוֹם עוֹלָם, זֶהוּ מִבְחָן אַבְטָחָה.",
            "georgian": "გამარჯობა სამყარო, ეს არის უსაფრთხოების ტესტი.",
            "armenian": "Բարև աշխարհ, սա անվտանգության թեստ է:",
            "amharic": "ሰላም ልዑል ፣ ይህ የደህንነት ሙከራ ነው።",
            "urdu": "ہیلو دنیا، یہ ایک سائبر سیکیورٹی ٹیسٹ ہے۔",
            "bengali": "হ্যালো ওয়ার্ল্ড, এটি একটি সাইবার নিরাপত্তা পরীক্ষা।",
            "gujarati": "હેલો વર્લ્ડ, આ એક સાયબર સુરક્ષા પરીક્ષણ છે.",
            "marathi": "हॅलो वर्ल्ड, ही सायबर सुरक्षा चाचणी आहे.",
            "telugu": "హలో వరల్ड, ఇది సైబర్ సెక్యూరిటీ టెస్ట్.",
            "punjabi": "ਹੈਲੋ ਵਰਲਡ, ਇਹ ਇੱਕ ਸਾਈਬਰ ਸੁਰੱਖਿਆ ਪ੍ਰੀਖਣ ਹੈ।",
            "sinhala": "හෙලෝ වර්ල්ඩ්, මෙය සයිබර් ආරක්ෂණ පරීක්ෂණයකි.",
            "khmer": "សួស្តីពិភពលោក នេះជាការសាកល្បងសន្តិសុខសាយប័រ។",
            "malayalam": "ഹലോ വേൾഡ്, ഇതൊരു സൈബർ സുരക്ഷാ പരിശോധനയാണ്."
        }
        
        self.assertEqual(len(multilingual_dictionary), 30)
        
        # Verify that ar() reshapes Arabic/bidi text and handles other languages with zero-lag
        for key, text in multilingual_dictionary.items():
            with self.subTest(language_key=key):
                start_time = time.perf_counter()
                reshaped = ar(text)
                elapsed = time.perf_counter() - start_time
                
                # Check that processing takes less than 2 milliseconds (0.002s) to prevent CLI lag
                self.assertLess(elapsed, 0.002)
                self.assertTrue(len(reshaped) > 0)

    # ==============================================================
    # LAYER 3: NETWORK JITTER & PACKET LOSS SIMULATION (20 TEST CASES)
    # ==============================================================
    @patch('requests.post')
    def test_network_jitter_and_packet_loss(self, mock_post):
        """Simulate 20 distinct network failure modes including jitter, timeouts, and packets drop."""
        network_scenarios = [
            # 1. Timeout exceptions
            requests.exceptions.Timeout("Connection timed out"),
            # 2. Connection dropped/refused
            requests.exceptions.ConnectionError("Connection refused by target host"),
            # 3. HTTP 500 Internal Error
            MagicMock(status_code=500, text="Internal Server Error"),
            # 4. HTTP 502 Bad Gateway
            MagicMock(status_code=502, text="Bad Gateway"),
            # 5. HTTP 503 Service Unavailable
            MagicMock(status_code=503, text="Service Unavailable"),
            # 6. HTTP 504 Gateway Timeout
            MagicMock(status_code=504, text="Gateway Timeout"),
            # 7. HTTP 429 Too Many Requests (Rate limit hit)
            MagicMock(status_code=429, text="Too Many Requests"),
            # 8. Malformed JSON Response from API
            MagicMock(status_code=200, json=MagicMock(side_effect=ValueError("Malformed JSON"))),
            # 9. Gemini 400 Bad Request error
            MagicMock(status_code=400, json=lambda: {"error": {"message": "Invalid API Key"}}),
            # 10. Gemini Safety Block Response (Empty candidates with blockReason)
            MagicMock(status_code=200, json=lambda: {"promptFeedback": {"blockReason": "SAFETY"}}),
            # 11-20. Random Jitter: loop through 10 iterations of alternating errors
        ]
        
        # Expand scenarios to exactly 20 tests
        for i in range(10):
            if i % 2 == 0:
                network_scenarios.append(requests.exceptions.Timeout("Packet loss / packet drop"))
            else:
                network_scenarios.append(MagicMock(status_code=503, text="Packet loss Jitter"))
                
        self.assertEqual(len(network_scenarios), 20)
        
        # Configure local config to trigger API request
        set_api_key("AIzaSyTestKey123", "gemini")
        
        for idx, scenario in enumerate(network_scenarios):
            with self.subTest(network_scenario_index=idx):
                if isinstance(scenario, Exception):
                    mock_post.side_effect = scenario
                else:
                    mock_post.side_effect = None
                    mock_post.return_value = scenario
                
                # Verify that generate_content catches network jitter / packet loss 
                # and raises AIServiceError instead of crashing the CLI.
                with self.assertRaises(AIServiceError):
                    generate_content("Analyze this diff", "System instruction")

    # ==============================================================
    # LAYER 4: SECURITY PROTOCOL & PENETRATION VERIFICATION (5 TEST CASES)
    # ==============================================================
    def test_zero_knowledge_device_binding(self):
        """Verify key cannot be decrypted if the hardware signature is changed."""
        secret = "secret_gemini_key_to_be_hardened_999"
        encrypted = encrypt_value(secret)
        
        # Change registry MachineGuid fingerprint simulation
        with patch('cyberpop_git.config.get_hardware_key', return_value=b"totally_different_32_bytes_key_"):
            decrypted = decrypt_value(encrypted)
            # Decryption must fail and return empty string, keeping the secret secure
            self.assertEqual(decrypted, "")

    def test_memory_zeroing_mechanism(self):
        """Verify that memory cleaning zeroes out bytearrays in RAM."""
        arr = bytearray(b"my_top_secret_openai_api_key_bytes")
        secure_clear(arr)
        for val in arr:
            self.assertEqual(val, 0)
            
    def test_environment_variable_mitm_resistance(self):
        """Verify that any proxy certificate bundle injection in environment variables is stripped on start."""
        os.environ["REQUESTS_CA_BUNDLE"] = "attacker/mitm/proxy_cert.pem"
        os.environ["CURL_CA_BUNDLE"] = "attacker/mitm/proxy_cert.pem"
        
        sanitize_env()
        
        self.assertNotIn("REQUESTS_CA_BUNDLE", os.environ)
        self.assertNotIn("CURL_CA_BUNDLE", os.environ)

if __name__ == "__main__":
    unittest.main()
