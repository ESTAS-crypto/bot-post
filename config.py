# ================================================================
#  CONFIG.PY — Pengaturan Bot Auto Post
#  Edit file ini sesuai kebutuhan Anda.
# ================================================================

# ---------------------------------------------------------------
#  TOKEN AKUN DISCORD ANDA
# ---------------------------------------------------------------
TOKEN = "TOKEN DISCORD"


# ================================================================
#  [1] SERVER TUJUAN POST
#  ➤ Server orang lain yang mau Anda kirimi pesan otomatis
#
#  Cara ambil SERVER ID:
#    1. Aktifkan Developer Mode: Settings → Advanced → Developer Mode ON
#    2. Klik kanan nama SERVER (bukan channel) → "Copy Server ID"
#
#  Cara ambil CHANNEL ID:
#    1. Klik kanan nama CHANNEL di dalam server → "Copy Channel ID"
# ================================================================
TARGET_SERVER_NAME  = ""              # Nama server tujuan (bebas isi, hanya untuk info)
TARGET_SERVER_ID    =  0                    # ← Server ID server tujuan  (klik kanan nama SERVER)
TARGET_CHANNEL_ID   = 0# ← Channel ID di server tujuan (klik kanan nama CHANNEL)


# ================================================================
#  [2] SERVER KONTROL BOT (Server Milik Anda)
#  ➤ Server tempat Anda mengirim command untuk mengontrol bot
#  ➤ Contoh command: !setmsg, !setcd, !toggleauto, !status
#
#  Cara ambil SERVER ID & CHANNEL ID: sama seperti cara di atas
# ================================================================
CONTROL_SERVER_NAME = ""         # Nama server kontrol (bebas isi, hanya untuk info)
CONTROL_SERVER_ID   = 0                     # ← Server ID server Anda  (klik kanan nama SERVER)
CONTROL_CHANNEL_ID  =  0  # ← Channel ID di server Anda (klik kanan nama CHANNEL)


# ================================================================
#  [3] PENGATURAN PESAN & JEDA
# ================================================================

# Pesan yang otomatis dikirim ke channel tujuan
DEFAULT_MESSAGE = "🌊 Selamat datang di Nexora, para bangsawan!"

# Jeda MINIMUM antar kiriman (dalam detik) → 600 = 10 menit
CD_MIN = 600

# Jeda MAKSIMUM antar kiriman (dalam detik) → 900 = 15 menit
# Bot kirim pesan secara acak antara CD_MIN hingga CD_MAX detik
CD_MAX = 900
