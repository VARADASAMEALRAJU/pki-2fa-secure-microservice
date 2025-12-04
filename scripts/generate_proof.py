#!/usr/bin/env python3
import sys, base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def load_private(path):
    data = Path(path).read_bytes()
    return serialization.load_pem_private_key(data, password=None)

def load_public(path):
    data = Path(path).read_bytes()
    return serialization.load_pem_public_key(data)

def sign_message(message: str, private_key) -> bytes:
    msg = message.encode('utf-8')
    sig = private_key.sign(
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return sig

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    ct = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ct

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_proof.py <commit-hash>", file=sys.stderr)
        sys.exit(2)
    commit_hash = sys.argv[1].strip()
    if len(commit_hash) != 40:
        print("WARNING: commit hash length != 40", file=sys.stderr)
    priv = load_private("/app/student_private.pem")
    pub = load_public("/app/instructor_public.pem")
    signature = sign_message(commit_hash, priv)
    encrypted = encrypt_with_public_key(signature, pub)
    b64 = base64.b64encode(encrypted).decode('ascii')
    # Output exactly two lines: commit hash and encrypted-signature-base64
    print("Commit-Hash:", commit_hash)
    print("Encrypted-Signature-Base64:", b64)

if __name__ == '__main__':
    main()
