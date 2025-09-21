import base64
import os
import json
import websockets
from typing import Dict, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
from typing import Callable, Dict, List, Optional, Any, Type, TypeVar, Tuple


class Crypto:
    def __init__(self):
        self.client_x25519_private_keys: Dict[
            websockets.WebSocketServerProtocol, x25519.X25519PrivateKey
        ] = {}
        self.client_aes_keys: Dict[websockets.WebSocketServerProtocol, bytes] = {}

    async def handle_key_exchange(
        self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]
    ) -> bool:
        action = data.get("action")
        if action == "public_key":
            client_public_key_bytes = base64.b64decode(data.get("key"))
            server_private_key = x25519.X25519PrivateKey.generate()
            server_public_key = server_private_key.public_key()
            self.client_x25519_private_keys[websocket] = server_private_key
            shared_secret = server_private_key.exchange(
                x25519.X25519PublicKey.from_public_bytes(client_public_key_bytes)
            )
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b"quillion-aes-key",
                backend=default_backend(),
            )
            session_aes_key = hkdf.derive(shared_secret)
            self.client_aes_keys[websocket] = session_aes_key
            server_public_key_bytes = server_public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            server_public_key_b64 = base64.b64encode(server_public_key_bytes).decode(
                "utf-8"
            )
            await websocket.send(
                json.dumps(
                    {
                        "action": "server_public_key",
                        "server_public_key": server_public_key_b64,
                    }
                )
            )
            return True
        else:
            return False

    async def decrypt_message(
        self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        action = data.get("action")
        if action == "encrypted_message":
            encrypted_data_b64 = data.get("data")
            nonce_b64 = data.get("nonce")
            encrypted_data = base64.b64decode(encrypted_data_b64)
            nonce = base64.b64decode(nonce_b64)
            session_aes_key = self.client_aes_keys.get(websocket)
            aesgcm = AESGCM(session_aes_key)
            decrypted_payload_bytes = aesgcm.decrypt(nonce, encrypted_data, None)
            decrypted_payload_str = decrypted_payload_bytes.decode("utf-8")
            inner_data = json.loads(decrypted_payload_str)
            return inner_data
        else:
            print(f"[{{websocket.remote_address[0]}:{websocket.remote_address[1]}}] Unknown action: {action}.")
        return None

    def encrypt_response(
        self, websocket: websockets.WebSocketServerProtocol, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        session_aes_key = self.client_aes_keys.get(websocket)
        plaintext = json.dumps(content).encode("utf-8")
        nonce = os.urandom(12)
        aesgcm = AESGCM(session_aes_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        encrypted_payload_b64 = base64.b64encode(ciphertext).decode("utf-8")
        nonce_b64 = base64.b64encode(nonce).decode("utf-8")
        return {
            "action": "encrypted_response",
            "encrypted_payload": encrypted_payload_b64,
            "nonce": nonce_b64,
        }

    def cleanup(self, websocket: websockets.WebSocketServerProtocol):
        if websocket in self.client_x25519_private_keys:
            del self.client_x25519_private_keys[websocket]
        if websocket in self.client_aes_keys:
            del self.client_aes_keys[websocket]
