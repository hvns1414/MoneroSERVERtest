# Monero TCP Terminal Server

Terminal üzerinden (nc / telnet) bağlanılabilen,
AES şifreli kullanıcı veritabanı kullanan,
role-based (low / pro / root) yetkilendirmeye sahip
bir **Monero Wallet TCP Server**.

Bu proje **test / öğrenme / lab** amaçlıdır.

---

## 🚀 Özellikler

- TCP socket server
- nc / telnet / putty (raw) ile bağlantı
- AES (Fernet) ile şifrelenmiş kullanıcı veritabanı
- SHA256 parola hash
- Role-based yetkilendirme
- Monero Wallet RPC entegrasyonu
- Server-side wallet (client private key görmez)
- Menü tabanlı terminal arayüzü

---

## 👤 Roller

| Rol  | Yetkiler |
|-----|----------|
| low | Balance görüntüleme |
| pro | Balance + History |
| root | Tüm işlemler + kullanıcı oluşturma + transfer |

---

## 🔑 Varsayılan Root Hesabı

Username: root
Password: toor

yaml
Kodu kopyala

İlk çalıştırmada otomatik oluşturulur.

---

## 📁 Dosya Yapısı

servermain.py
users.enc # AES şifreli kullanıcı veritabanı
master.key # AES master key (SİLME!)

yaml
Kodu kopyala

⚠️ `master.key` silinirse kullanıcılar çözülemez.

---

## 🧰 Gereksinimler

- Python 3.10+
- Monero Wallet RPC (opsiyonel ama önerilir)

### Python kütüphaneleri
```bash
pip install monero cryptography
🪙 Monero Wallet RPC
Wallet RPC server tarafında çalışmalıdır.

Örnek:

bash
Kodu kopyala
monero-wallet-rpc.exe \
  --wallet-file mywallet \
  --rpc-bind-ip 127.0.0.1 \
  --rpc-bind-port 18082 \
  --disable-rpc-login
⚠️ Local node kullanırsan blockchain indirir
Önerilen: Remote node

▶️ Server Başlatma
bash
Kodu kopyala
python servermain.py
Varsayılan port:

yaml
Kodu kopyala
5555
🌐 Bağlanma (Client)
Netcat
bash
Kodu kopyala
nc 127.0.0.1 5555
Telnet
bash
Kodu kopyala
telnet 127.0.0.1 5555
🔐 Giriş Akışı
makefile
Kodu kopyala
=== MONERO TCP UI ===
Username:
Password:
Başarılı giriş sonrası role göre menü açılır.

🧭 Menü Örnekleri
Root Menü
sql
Kodu kopyala
1) Create User
2) Monero Dashboard
0) Logout
Monero Dashboard
scss
Kodu kopyala
1) Balance
2) History        (pro / root)
3) Transfer       (root)
0) Back
👥 Yeni Kullanıcı Oluşturma (Root)
yaml
Kodu kopyala
Username:
Password:
Role (low/pro/root):
Kullanıcılar AES ile şifrelenerek users.enc içine kaydedilir.

⚠️ Güvenlik Notları
TCP bağlantı şifreli değildir

Parolalar ağdan plaintext gider

TLS / SSL yok

Production için uygun değildir

Gerçek kullanım için eklenmesi gerekenler:
TLS (ssl.wrap_socket)

Rate limiting

IP allowlist

Audit logging

Transfer confirmation

🧪 Test Modu
Eğer Monero RPC çalışmıyorsa:

Login / user sistemi çalışır

Balance / transfer çalışmaz

📜 Lisans
Bu proje eğitim ve test amaçlıdır.
Herhangi bir finansal sorumluluk kabul edilmez.

✨ Gelecek Geliştirmeler (Opsiyonel)
JSON-based protocol

Textual GUI client

TLS destekli server

Web dashboard

2FA / OTP

yaml
Kodu kopyala

---

İstersen bir sonraki adımda:
- 📦 **ZIP proje yapısı**
- 🖥️ **Client.py (menülü)**
- 🔐 **TLS eklenmiş versiyon**
- 🧪 **Mock / demo wallet**

hazırlayabilirim.

Hangisine geçelim?
