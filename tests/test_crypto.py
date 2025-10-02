import pytest
import base64
import json
import os
from unittest.mock import AsyncMock

import websockets
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from quillion.core.crypto import Crypto


class TestCrypto:
    @pytest.fixture
    def crypto(self):
        return Crypto()

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock(spec=websockets.WebSocketServerProtocol)
        websocket.remote_address = ("127.0.0.1", 8080)
        return websocket

    @pytest.fixture
    def mock_x25519_keys(self):
        private_key = x25519.X25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    @pytest.fixture
    def test_aes_key(self):
        return os.urandom(32)

    def test_initialization(self, crypto):
        assert crypto.client_x25519_private_keys == {}
        assert crypto.client_aes_keys == {}

    @pytest.mark.asyncio
    async def test_handle_key_exchange_success(self, crypto, mock_websocket, mock_x25519_keys):
        _, client_public_key = mock_x25519_keys
        client_public_key_bytes = client_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        client_public_key_b64 = base64.b64encode(client_public_key_bytes).decode('utf-8')
        
        test_data = {
            "action": "public_key",
            "key": client_public_key_b64
        }

        mock_websocket.send = AsyncMock()

        result = await crypto.handle_key_exchange(mock_websocket, test_data)

        assert result is True
        assert mock_websocket in crypto.client_x25519_private_keys
        assert mock_websocket in crypto.client_aes_keys
        assert len(crypto.client_aes_keys[mock_websocket]) == 32

        mock_websocket.send.assert_called_once()
        call_args = mock_websocket.send.call_args[0][0]
        sent_data = json.loads(call_args)
        assert sent_data["action"] == "server_public_key"
        assert "server_public_key" in sent_data

    @pytest.mark.asyncio
    async def test_handle_key_exchange_wrong_action(self, crypto, mock_websocket):
        test_data = {
            "action": "wrong_action",
            "key": "test_key"
        }

        result = await crypto.handle_key_exchange(mock_websocket, test_data)

        assert result is False
        assert mock_websocket not in crypto.client_x25519_private_keys
        assert mock_websocket not in crypto.client_aes_keys

    @pytest.mark.asyncio
    async def test_decrypt_message_success(self, crypto, mock_websocket, test_aes_key):
        crypto.client_aes_keys[mock_websocket] = test_aes_key
        
        test_payload = {"test": "data", "number": 123}
        plaintext = json.dumps(test_payload).encode('utf-8')
        
        nonce = os.urandom(12)
        aesgcm = AESGCM(test_aes_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        encrypted_data_b64 = base64.b64encode(ciphertext).decode('utf-8')
        nonce_b64 = base64.b64encode(nonce).decode('utf-8')
        
        test_data = {
            "action": "encrypted_message",
            "data": encrypted_data_b64,
            "nonce": nonce_b64
        }

        result = await crypto.decrypt_message(mock_websocket, test_data)

        assert result == test_payload

    @pytest.mark.asyncio
    async def test_decrypt_message_wrong_action(self, crypto, mock_websocket):
        test_data = {
            "action": "wrong_action",
            "data": "test_data",
            "nonce": "test_nonce"
        }

        result = await crypto.decrypt_message(mock_websocket, test_data)

        assert result is None

    def test_encrypt_response_success(self, crypto, mock_websocket, test_aes_key):
        crypto.client_aes_keys[mock_websocket] = test_aes_key
        
        test_content = {"response": "data", "status": "success"}
        
        result = crypto.encrypt_response(mock_websocket, test_content)
        
        assert result["action"] == "encrypted_response"
        assert "encrypted_payload" in result
        assert "nonce" in result
        
        encrypted_payload = base64.b64decode(result["encrypted_payload"])
        nonce = base64.b64decode(result["nonce"])
        
        aesgcm = AESGCM(test_aes_key)
        decrypted_bytes = aesgcm.decrypt(nonce, encrypted_payload, None)
        decrypted_content = json.loads(decrypted_bytes.decode('utf-8'))
        
        assert decrypted_content == test_content

    def test_encrypt_response_no_aes_key(self, crypto, mock_websocket):
        test_content = {"response": "data"}
        
        with pytest.raises(Exception):
            crypto.encrypt_response(mock_websocket, test_content)

    def test_encrypt_response_different_content_types(self, crypto, mock_websocket, test_aes_key):
        crypto.client_aes_keys[mock_websocket] = test_aes_key
        
        test_cases = [
            {"simple": "data"},
            {"nested": {"deep": {"data": True}}},
            {"list": [1, 2, 3], "string": "test"},
            {"number": 123.45, "boolean": False, "null": None}
        ]
        
        for test_content in test_cases:
            result = crypto.encrypt_response(mock_websocket, test_content)
            
            assert result["action"] == "encrypted_response"
            assert "encrypted_payload" in result
            assert "nonce" in result
            
            encrypted_payload = base64.b64decode(result["encrypted_payload"])
            nonce = base64.b64decode(result["nonce"])
            
            aesgcm = AESGCM(test_aes_key)
            decrypted_bytes = aesgcm.decrypt(nonce, encrypted_payload, None)
            decrypted_content = json.loads(decrypted_bytes.decode('utf-8'))
            
            assert decrypted_content == test_content

    def test_cleanup_existing_connection(self, crypto, mock_websocket, mock_x25519_keys):
        private_key, _ = mock_x25519_keys
        test_aes_key = os.urandom(32)
        
        crypto.client_x25519_private_keys[mock_websocket] = private_key
        crypto.client_aes_keys[mock_websocket] = test_aes_key
        
        assert mock_websocket in crypto.client_x25519_private_keys
        assert mock_websocket in crypto.client_aes_keys
        
        crypto.cleanup(mock_websocket)
        
        assert mock_websocket not in crypto.client_x25519_private_keys
        assert mock_websocket not in crypto.client_aes_keys

    def test_cleanup_non_existing_connection(self, crypto, mock_websocket):
        assert mock_websocket not in crypto.client_x25519_private_keys
        assert mock_websocket not in crypto.client_aes_keys
        
        crypto.cleanup(mock_websocket)
        
        assert mock_websocket not in crypto.client_x25519_private_keys
        assert mock_websocket not in crypto.client_aes_keys

    def test_cleanup_partial_data(self, crypto, mock_websocket, mock_x25519_keys):
        private_key, _ = mock_x25519_keys
        
        crypto.client_x25519_private_keys[mock_websocket] = private_key
        
        assert mock_websocket in crypto.client_x25519_private_keys
        assert mock_websocket not in crypto.client_aes_keys
        
        crypto.cleanup(mock_websocket)
        
        assert mock_websocket not in crypto.client_x25519_private_keys
        assert mock_websocket not in crypto.client_aes_keys

    @pytest.mark.asyncio
    async def test_full_encryption_decryption_cycle(self, crypto, mock_websocket, mock_x25519_keys):
        _, client_public_key = mock_x25519_keys
        client_public_key_bytes = client_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        client_public_key_b64 = base64.b64encode(client_public_key_bytes).decode('utf-8')
        
        key_exchange_data = {
            "action": "public_key",
            "key": client_public_key_b64
        }

        mock_websocket.send = AsyncMock()
        await crypto.handle_key_exchange(mock_websocket, key_exchange_data)
        
        test_content = {"message": "Hello, World!", "timestamp": 1234567890}
        encrypted_response = crypto.encrypt_response(mock_websocket, test_content)
        
        decrypt_data = {
            "action": "encrypted_message",
            "data": encrypted_response["encrypted_payload"],
            "nonce": encrypted_response["nonce"]
        }
        
        decrypted_content = await crypto.decrypt_message(mock_websocket, decrypt_data)
        
        assert decrypted_content == test_content

    def test_multiple_connections_isolation(self, crypto):
        websocket1 = AsyncMock(spec=websockets.WebSocketServerProtocol)
        websocket1.remote_address = ("127.0.0.1", 8081)
        
        websocket2 = AsyncMock(spec=websockets.WebSocketServerProtocol)
        websocket2.remote_address = ("127.0.0.1", 8082)
        
        private_key1 = x25519.X25519PrivateKey.generate()
        private_key2 = x25519.X25519PrivateKey.generate()
        aes_key1 = os.urandom(32)
        aes_key2 = os.urandom(32)
        
        crypto.client_x25519_private_keys[websocket1] = private_key1
        crypto.client_aes_keys[websocket1] = aes_key1
        
        crypto.client_x25519_private_keys[websocket2] = private_key2
        crypto.client_aes_keys[websocket2] = aes_key2
        
        assert crypto.client_x25519_private_keys[websocket1] is private_key1
        assert crypto.client_x25519_private_keys[websocket2] is private_key2
        assert crypto.client_aes_keys[websocket1] is aes_key1
        assert crypto.client_aes_keys[websocket2] is aes_key2
        
        crypto.cleanup(websocket1)
        
        assert websocket1 not in crypto.client_x25519_private_keys
        assert websocket1 not in crypto.client_aes_keys
        assert websocket2 in crypto.client_x25519_private_keys
        assert websocket2 in crypto.client_aes_keys