import json, os, hashlib
from cryptography.fernet import Fernet

KEY_FILE = "master.key"
DB_FILE = "users.json.enc"

def load_master_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        open(KEY_FILE, "wb").write(key)
    return open(KEY_FILE, "rb").read()

fernet = Fernet(load_master_key())

def _load_users():
    if not os.path.exists(DB_FILE):
        return {}
    data = fernet.decrypt(open(DB_FILE, "rb").read())
    return json.loads(data.decode())

def _save_users(users):
    enc = fernet.encrypt(json.dumps(users).encode())
    open(DB_FILE, "wb").write(enc)

def hash_pw(pw, salt):
    return hashlib.sha256((pw + salt).encode()).hexdigest()

def create_user(username, password, role):
    users = _load_users()
    if username in users:
        return False
    salt = os.urandom(8).hex()
    users[username] = {
        "hash": hash_pw(password, salt),
        "salt": salt,
        "role": role
    }
    _save_users(users)
    return True

def auth_user(username, password):
    users = _load_users()
    u = users.get(username)
    if not u:
        return None
    if hash_pw(password, u["salt"]) == u["hash"]:
        return u["role"]
    return None
