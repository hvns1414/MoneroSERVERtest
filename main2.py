import os, json, time, hashlib
from getpass import getpass
from cryptography.fernet import Fernet

# ===================== CONFIG =====================
USERS_FILE = "users.enc"
KEY_FILE = "master.key"

# ===================== AES =====================
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        open(KEY_FILE, "wb").write(key)
    return open(KEY_FILE, "rb").read()

fernet = Fernet(load_key())

def encrypt(data):
    return fernet.encrypt(json.dumps(data).encode())

def decrypt(data):
    return json.loads(fernet.decrypt(data).decode())

# ===================== USERS =====================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    return decrypt(open(USERS_FILE, "rb").read())

def save_users(users):
    open(USERS_FILE, "wb").write(encrypt(users))

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_user(username, password, role):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_pw(password),
        "role": role
    }
    save_users(users)
    return True

# create root if missing
if "root" not in load_users():
    create_user("root", "toor", "root")

# ===================== MONERO =====================
try:
    from monero.wallet import Wallet
    from monero.backends.jsonrpc import JSONRPCWallet

    wallet = Wallet(JSONRPCWallet(
        host="127.0.0.1",
        port=18082
    ))
    RPC_OK = True
except:
    RPC_OK = False

# ===================== UI =====================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\n[ENTER] Continue...")

# ===================== LOGIN =====================
def login():
    clear()
    print(" MONERO TERMINAL UI ")
    print("====================\n")

    u = input("Username: ")
    p = getpass("Password: ")

    users = load_users()
    if u not in users:
        return None

    if users[u]["password"] != hash_pw(p):
        return None

    return {"username": u, "role": users[u]["role"]}

# ===================== ROOT =====================
def root_menu():
    while True:
        clear()
        print(" ROOT DASHBOARD ")
        print("================")
        print("1) Create user")
        print("2) Monero dashboard")
        print("0) Logout")

        c = input("> ")
        if c == "1":
            create_user_ui()
        elif c == "2":
            monero_menu("root")
        elif c == "0":
            break

def create_user_ui():
    clear()
    print(" CREATE USER ")
    print("=============")
    u = input("Username: ")
    p = getpass("Password: ")
    r = input("Role (low/pro/root): ")

    if r not in ["low", "pro", "root"]:
        print("Invalid role")
    elif create_user(u, p, r):
        print("User created")
    else:
        print("User exists")
    pause()

# ===================== MONERO =====================
def monero_menu(role):
    if not RPC_OK:
        print("RPC NOT CONNECTED")
        pause()
        return

    while True:
        clear()
        print(" MONERO DASHBOARD ")
        print("==================")
        print(f"RPC STATUS: {'CONNECTED' if RPC_OK else 'OFFLINE'}\n")

        print("1) Balance")
        if role in ["pro", "root"]:
            print("2) History")
        if role == "root":
            print("3) Transfer")

        print("0) Back")
        c = input("> ")

        if c == "1":
            show_balance()
        elif c == "2" and role in ["pro", "root"]:
            show_history()
        elif c == "3" and role == "root":
            transfer_ui()
        elif c == "0":
            break

def show_balance():
    clear()
    print(" BALANCE ")
    print("=========")
    print("Total:", wallet.balance())
    print("Unlocked:", wallet.unlocked_balance())
    pause()

def show_history():
    clear()
    print(" HISTORY ")
    print("=========")
    for tx in wallet.incoming():
        print("+", tx.amount, tx.hash)
    for tx in wallet.outgoing():
        print("-", tx.amount, tx.hash)
    pause()

def transfer_ui():
    clear()
    print(" TRANSFER ")
    print("==========")
    addr = input("Address: ")
    amt = float(input("Amount: "))

    try:
        tx = wallet.transfer(addr, amt)
        print("TX HASH:", tx.hash)
    except Exception as e:
        print("ERROR:", e)
    pause()

# ===================== MAIN =====================
while True:
    user = login()
    if not user:
        print("Login failed")
        time.sleep(1)
        continue

    if user["role"] == "root":
        root_menu()
    else:
        monero_menu(user["role"])
