## **📌 PKI-2FA Secure Microservice**

This project implements a **secure 2FA microservice** using:

* RSA/OAEP (SHA-256) for decrypting encrypted seed
* RSA-PSS (SHA-256) for commit signing
* TOTP generation (pyotp)
* Docker multi-stage build
* Cron job to log 2FA codes every minute
* FastAPI server running at port **8080**
* Persistent seed storage using Docker volumes

---

## **🚀 Features**

### **1. API Endpoints**

| Endpoint        | Method | Description                                       |
| --------------- | ------ | ------------------------------------------------- |
| `/decrypt-seed` | POST   | Decrypts encrypted seed using student private key |
| `/generate-2fa` | GET    | Generates current TOTP code                       |
| `/verify-2fa`   | POST   | Verifies provided 2FA code                        |

---

## **📂 Project Structure**

```
.
├── app/
│   ├── main.py
│   ├── crypto_utils.py
│   └── requirements.txt
├── cron/
│   └── 2fa-cron
├── scripts/
│   ├── log_2fa_cron.py
│   └── generate_proof.py
├── Dockerfile
├── docker-compose.yml
├── student_private.pem
├── student_public.pem
├── instructor_public.pem
└── README.md
```

---

## **🔐 Cryptography Used**

### **Seed Decryption**

* RSA / OAEP
* MGF1 (SHA-256)
* Hash = SHA-256
* Label = None

### **Commit Signing**

* RSA-PSS
* MGF1 (SHA-256)
* Salt length = MAX
* Message = ASCII commit hash

---

## **🕒 Cron Job**

Runs every minute:

```
* * * * * cd /app && python3 scripts/log_2fa_cron.py >> /cron/last_code.txt 2>&1
```

Logs:

```
2025-12-03 16:51:01 - 2FA Code: 123456
```

---

## **🐳 Docker Usage**

### Build container

```
docker-compose build
```

### Run container

```
docker-compose up -d
```

### Test API

```
curl http://localhost:8080/generate-2fa
```

---

## **📦 Volume Persistence**

* `/data` → stores seed
* `/cron` → stores cron log

Even after restart, seed persists:

```
docker-compose restart
docker exec pki2fa cat /data/seed.txt
```

---

## **🔏 Commit Proof**

### Commit Hash:

```
4b1d22b0d0168df4c6ac283c08951aec36e57ae5
```

### Encrypted Signature (Base64):

```
mI1ML4+U7hAUKqisn/gfGhmBKn1OQtsPIdnNlDzTf6...
```

---

## **📌 GitHub Repo**

```
https://github.com/VARADASAMEALRAJU/pki-2fa-secure-microservice
```

---

## **📝 Submission Files**

* Public key
* Encrypted seed
* Commit hash
* Encrypted signature
* Repo URL
