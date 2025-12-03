#!/usr/bin/env python3
from pathlib import Path
import datetime, base64, pyotp, sys
SEED_FILE=Path("/data/seed.txt"); OUT_FILE=Path("/cron/last_code.txt")
def get_code():
    if not SEED_FILE.exists(): raise FileNotFoundError("Seed missing")
    hex_seed=SEED_FILE.read_text().strip()
    seed_b32=base64.b32encode(bytes.fromhex(hex_seed)).decode()
    totp=pyotp.TOTP(seed_b32)
    return totp.now()
def main():
    ts=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    try:
        code=get_code(); OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with OUT_FILE.open("a", encoding="utf-8") as f: f.write(f"{ts} - 2FA Code: {code}\n")
    except Exception as e:
        print(f"{ts} - ERROR: {e}", file=sys.stderr)
if __name__=="__main__": main()
