---
title: Cryptography
description: Hashing, symmetric/asymmetric encryption, digital signatures, TLS and secure communication
---

# Cryptography <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
  </div>
</div>

---

## Hashing — one-way functions

```python
import hashlib

# SHA-256 (most common)
data = b"Hello, World!"
hash_hex = hashlib.sha256(data).hexdigest()
print(hash_hex)   # dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f

# File hashing
def hash_file(path: str, algorithm="sha256") -> str:
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

# HMAC — hash with a secret key (for authentication)
import hmac

secret = b"my-secret-key"
message = b"Important data"
signature = hmac.new(secret, message, hashlib.sha256).hexdigest()

# Verify
def verify_hmac(secret, message, expected_sig):
    computed = hmac.new(secret, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, expected_sig)   # constant-time comparison!
```

---

## Password hashing (NEVER use plain SHA for passwords)

```python
# bcrypt — industry standard for passwords
import bcrypt

password = "user_password_123"

# Hash (slow by design — prevents brute force)
salt = bcrypt.gensalt(rounds=12)   # cost factor
hashed = bcrypt.hashpw(password.encode(), salt)
print(hashed)   # b'$2b$12$...' (60 chars)

# Verify
def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

print(verify_password("user_password_123", hashed))   # True
print(verify_password("wrong_password", hashed))       # False

# argon2 — newer, recommended (winner of Password Hashing Competition)
from argon2 import PasswordHasher

ph = PasswordHasher()
hash_str = ph.hash("my_password")
print(ph.verify(hash_str, "my_password"))   # True
```

---

## Symmetric encryption (same key for encrypt/decrypt)

```python
from cryptography.fernet import Fernet

# Generate key (store securely!)
key = Fernet.generate_key()
print(key)   # b'...'  (URL-safe base64, 32 bytes)

cipher = Fernet(key)

# Encrypt
plaintext = b"Secret message that must be protected"
ciphertext = cipher.encrypt(plaintext)
print(ciphertext)   # b'gAAA...'  (includes timestamp + IV)

# Decrypt
decrypted = cipher.decrypt(ciphertext)
assert decrypted == plaintext

# With expiration (TTL)
try:
    cipher.decrypt(ciphertext, ttl=60)   # fails if > 60 seconds old
except Exception:
    print("Token expired!")
```

### AES (lower-level, more control)

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

# AES-256-CBC
key = os.urandom(32)    # 256 bits
iv = os.urandom(16)     # initialization vector

# Encrypt
padder = padding.PKCS7(128).padder()
padded_data = padder.update(b"Secret data") + padder.finalize()

cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()
ciphertext = encryptor.update(padded_data) + encryptor.finalize()

# Decrypt
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
decryptor = cipher.decryptor()
padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
print(plaintext)   # b"Secret data"
```

---

## Asymmetric encryption (public/private key pair)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization

# Generate key pair
private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
public_key = private_key.public_key()

# Encrypt with public key (anyone can encrypt)
message = b"Top secret message"
ciphertext = public_key.encrypt(
    message,
    asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

# Decrypt with private key (only holder can decrypt)
plaintext = private_key.decrypt(
    ciphertext,
    asym_padding.OAEP(
        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
assert plaintext == message

# Serialize keys
pem_private = private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.BestAvailableEncryption(b"passphrase"),
)

pem_public = public_key.public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo,
)
```

---

## Digital signatures

```python
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes

# Sign with private key (proves authenticity)
message = b"This document is authentic"
signature = private_key.sign(
    message,
    asym_padding.PSS(
        mgf=asym_padding.MGF1(hashes.SHA256()),
        salt_length=asym_padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)

# Verify with public key (anyone can verify)
try:
    public_key.verify(
        signature, message,
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    print("Signature valid!")
except Exception:
    print("Signature INVALID — data was tampered with!")
```

---

## Secure random numbers

```python
import secrets

# For tokens, passwords, API keys — NOT random module!
token = secrets.token_hex(32)         # 64-char hex string
url_safe = secrets.token_urlsafe(32)  # URL-safe base64
raw_bytes = secrets.token_bytes(32)   # 32 random bytes

# Secure password generation
import string
alphabet = string.ascii_letters + string.digits + "!@#$%"
password = "".join(secrets.choice(alphabet) for _ in range(20))
print(password)   # e.g. "kR9#mN2$xP5@wQ7&bL4"

# Secure comparison (constant-time — prevents timing attacks)
secrets.compare_digest(token_a, token_b)
```

---

## Practice Exercises

1. **Build a file encryption tool** — encrypt/decrypt files with a password-derived key (PBKDF2 + AES).
2. **Implement JWT signing** from scratch using HMAC-SHA256.
3. **Create a key exchange** between two parties using Diffie-Hellman.
4. **Build a digital signature verifier** for software packages.
5. **Implement a password manager** with master password, salt, key derivation and encrypted vault.
6. **Compare timing** of `==` vs `hmac.compare_digest` to demonstrate timing attacks.
