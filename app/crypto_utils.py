import base64, os, time
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

HEX_CHARS=set("0123456789abcdef")
def load_private_key_from_file(path:str):
    data=Path(path).read_bytes()
    return serialization.load_pem_private_key(data,password=None)
def decrypt_seed(encrypted_seed_b64:str, private_key):
    ciphertext=base64.b64decode(encrypted_seed_b64, validate=True)
    plaintext=private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )
    seed=plaintext.decode("utf-8").strip().lower()
    if len(seed)!=64 or any(ch not in HEX_CHARS for ch in seed):
        raise ValueError("Invalid seed format")
    return seed
def persist_seed_atomic(hex_seed:str, dest_path:str="/data/seed.txt"):
    dest=Path(dest_path); dest.parent.mkdir(parents=True, exist_ok=True)
    tmp=dest.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(hex_seed); f.flush(); os.fsync(f.fileno())
    tmp.replace(dest)
def decrypt_and_store(encrypted_seed_b64:str, private_key_path:str="/app/student_private.pem", seed_file:str="/data/seed.txt"):
    pk=load_private_key_from_file(private_key_path)
    seed=decrypt_seed(encrypted_seed_b64, pk)
    persist_seed_atomic(seed, seed_file)
def generate_totp_from_hex(hex_seed:str):
    seed_b32=base64.b32encode(bytes.fromhex(hex_seed)).decode()
    totp=pyotp.TOTP(seed_b32)
    code=totp.now()
    period=30; valid_for=period-(int(time.time())%period)
    return code, valid_for
def verify_totp_from_hex(hex_seed:str, code:str, valid_window:int=1):
    seed_b32=base64.b32encode(bytes.fromhex(hex_seed)).decode()
    totp=pyotp.TOTP(seed_b32)
    return totp.verify(code, valid_window=valid_window)
