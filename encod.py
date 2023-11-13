import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64

# 生成RSA私钥


if not os.path.exists('private.pem'):
    # 将私钥序列化为PEM格式
    print("生成私钥")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open('private.pem', 'wb') as f:
        f.write(private_pem)
else:
    print("读取私钥")
    with open('private.pem', 'rb') as f:
        private_pem = f.read()
    private_key = serialization.load_pem_private_key(
        private_pem,
        password=None,
        backend=default_backend()
    )


# 加密消息
def encode(message) -> str:
    message = message.encode()
    ciphertext = private_key.public_key().encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(ciphertext).decode()


# 解密消息
def decode(ciphertext: str):
    ciphertext = base64.b64decode(ciphertext)
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode()
