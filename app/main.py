from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
from app.crypto_utils import decrypt_and_store, generate_totp_from_hex, verify_totp_from_hex

app = FastAPI()
SEED_FILE = "/data/seed.txt"
PRIVATE_KEY_PATH = "/app/student_private.pem"

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(payload: dict):
    enc = payload.get("encrypted_seed")
    if not enc:
        return JSONResponse(status_code=400, content={"error":"Missing encrypted_seed"})
    try:
        decrypt_and_store(enc, private_key_path=PRIVATE_KEY_PATH, seed_file=SEED_FILE)
    except Exception:
        return JSONResponse(status_code=500, content={"error":"Decryption failed"})
    return {"status":"ok"}

@app.get("/generate-2fa")
async def generate_2fa():
    p=Path(SEED_FILE)
    if not p.exists():
        return JSONResponse(status_code=500, content={"error":"Seed not decrypted yet"})
    hex_seed=p.read_text().strip()
    code,valid_for=generate_totp_from_hex(hex_seed)
    return {"code":code,"valid_for":valid_for}

@app.post("/verify-2fa")
async def verify_2fa(payload: dict):
    code=payload.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"error":"Missing code"})
    p=Path(SEED_FILE)
    if not p.exists():
        return JSONResponse(status_code=500, content={"error":"Seed not decrypted yet"})
    hex_seed=p.read_text().strip()
    valid=verify_totp_from_hex(hex_seed,code,valid_window=1)
    return {"valid":bool(valid)}
