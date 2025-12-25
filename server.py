import socket, threading, os, json, hashlib
from cryptography.fernet import Fernet

# ================= CONFIG =================
HOST = "0.0.0.0"
PORT = 5555
USERS_FILE = "users.enc"
KEY_FILE = "master.key"

# ================= AES =================
def load_key():
    if not os.path.exists(KEY_FILE):
        open(KEY_FILE, "wb").write(Fernet.generate_key())
    return open(KEY_FILE, "rb").read()

fernet = Fernet(load_key())

def encrypt(d): return fernet.encrypt(json.dumps(d).encode())
def decrypt(d): return json.loads(fernet.decrypt(d).decode())

# ================= USERS =================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    return decrypt(open(USERS_FILE, "rb").read())

def save_users(u):
    open(USERS_FILE, "wb").write(encrypt(u))

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def create_user(u, p, r):
    users = load_users()
    if u in users: return False
    users[u] = {"password": hash_pw(p), "role": r}
    save_users(users)
    return True

if "root" not in load_users():
    create_user("root", "toor", "root")

# ================= MONERO =================
try:
    from monero.wallet import Wallet
    from monero.backends.jsonrpc import JSONRPCWallet
    wallet = Wallet(JSONRPCWallet("127.0.0.1", 18082))
    RPC_OK = True
except:
    RPC_OK = False

# ================= NET =================
def send(c, m):
    c.sendall((m + "\n").encode())

def recv(c):
    return c.recv(1024).decode().strip()

# ================= MENUS =================
def login_menu(c):
    send(c, "=== MONERO TCP UI ===")
    send(c, "Username:")
    u = recv(c)
    send(c, "Password:")
    p = recv(c)

    users = load_users()
    if u in users and users[u]["password"] == hash_pw(p):
        return {"name": u, "role": users[u]["role"]}
    return None

def monero_menu(c, role):
    if not RPC_OK:
        send(c, "RPC OFFLINE")
        return

    while True:
        send(c, "\n--- MONERO DASHBOARD ---")
        send(c, "1) Balance")
        if role in ["pro", "root"]:
            send(c, "2) History")
        if role == "root":
            send(c, "3) Transfer")
        send(c, "0) Back")

        ch = recv(c)

        if ch == "1":
            send(c, f"Balance: {wallet.balance()}")
            send(c, f"Unlocked: {wallet.unlocked_balance()}")

        elif ch == "2" and role in ["pro", "root"]:
            for tx in wallet.incoming():
                send(c, f"+ {tx.amount} {tx.hash}")
            for tx in wallet.outgoing():
                send(c, f"- {tx.amount} {tx.hash}")

        elif ch == "3" and role == "root":
            send(c, "Address:")
            addr = recv(c)
            send(c, "Amount:")
            amt = float(recv(c))
            try:
                tx = wallet.transfer(addr, amt)
                send(c, f"TX HASH: {tx.hash}")
            except Exception as e:
                send(c, f"ERR {e}")

        elif ch == "0":
            break

def root_menu(c):
    while True:
        send(c, "\n=== ROOT DASHBOARD ===")
        send(c, "1) Create User")
        send(c, "2) Monero Dashboard")
        send(c, "0) Logout")

        ch = recv(c)

        if ch == "1":
            send(c, "Username:")
            u = recv(c)
            send(c, "Password:")
            p = recv(c)
            send(c, "Role (low/pro/root):")
            r = recv(c)

            if r not in ["low", "pro", "root"]:
                send(c, "INVALID ROLE")
            elif create_user(u, p, r):
                send(c, "USER CREATED")
            else:
                send(c, "USER EXISTS")

        elif ch == "2":
            monero_menu(c, "root")

        elif ch == "0":
            break

# ================= CLIENT =================
def handle_client(c, addr):
    user = login_menu(c)
    if not user:
        send(c, "LOGIN FAILED")
        c.close()
        return

    send(c, f"LOGIN OK | ROLE={user['role']}")

    if user["role"] == "root":
        root_menu(c)
    else:
        monero_menu(c, user["role"])

    send(c, "BYE")
    c.close()

# ================= SERVER =================
def start():
    print(f"[+] Server listening on {PORT}")
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()

    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, a), daemon=True).start()

start()
