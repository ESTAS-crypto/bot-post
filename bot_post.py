import discord
from discord.ext import commands
import asyncio
import random
import sys
import time

# Import semua pengaturan dari config.py
from config import (
    TOKEN,
    TARGET_SERVER_NAME, TARGET_SERVER_ID, TARGET_CHANNEL_ID,
    CONTROL_SERVER_NAME, CONTROL_SERVER_ID, CONTROL_CHANNEL_ID,
    DEFAULT_MESSAGE, CD_MIN, CD_MAX
)

# Atur encoding terminal agar mendukung emoji di Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ================================================================
#  VARIABEL STATE (bisa diubah lewat command)
# ================================================================
current_message = DEFAULT_MESSAGE
auto_enabled    = True
cd_min          = CD_MIN
cd_max          = CD_MAX

# Waktu kapan post berikutnya akan dikirim (unix timestamp)
# 0 = belum diset, akan diset saat loop pertama jalan
next_post_time  = 0

# ================================================================
#  INISIALISASI BOT
# ================================================================
bot = commands.Bot(command_prefix="!", self_bot=True)

# ================================================================
#  LOOP AUTO POST
# ================================================================
async def auto_post_loop():
    global auto_enabled, next_post_time
    await bot.wait_until_ready()

    # Ambil channel tujuan post
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        try:
            channel = await bot.fetch_channel(TARGET_CHANNEL_ID)
        except Exception as e:
            print(f"❌ Gagal mendapatkan channel tujuan: {e}")
            print(f"   Pastikan akun Anda sudah JOIN di server '{TARGET_SERVER_NAME}'")
            return

    print(f"✅ Auto post siap!")
    print(f"   Server Tujuan  : {channel.guild.name}  (Server ID : {channel.guild.id})")
    print(f"   Channel Tujuan : #{channel.name}  (Channel ID: {channel.id})")

    # Set waktu post pertama
    delay = random.randint(cd_min, cd_max)
    next_post_time = time.time() + delay
    print(f"⏳ Kirim pertama dalam {delay} detik ({delay//60} menit {delay%60} detik)...")

    # Loop cek setiap 1 detik — responsif terhadap perubahan CD & toggle
    while not bot.is_closed():
        await asyncio.sleep(1)

        if not auto_enabled:
            continue

        now = time.time()
        if now >= next_post_time:
            try:
                await channel.send(current_message)
                print(f"✅ Pesan terkirim ke #{channel.name}: {current_message[:60]}")
            except Exception as e:
                print(f"❌ Gagal kirim pesan: {e}")

            # Set waktu post berikutnya
            delay = random.randint(cd_min, cd_max)
            next_post_time = time.time() + delay
            print(f"⏳ Kirim berikutnya dalam {delay} detik ({delay//60} menit {delay%60} detik)...")

# ================================================================
#  HELPER: Cek apakah command berasal dari channel kontrol
# ================================================================
def is_control_channel(ctx):
    """Validasi: command hanya diterima dari server + channel kontrol yang benar."""
    correct_channel = ctx.channel.id == CONTROL_CHANNEL_ID
    correct_server  = (CONTROL_SERVER_ID == 0) or (ctx.guild and ctx.guild.id == CONTROL_SERVER_ID)
    return correct_channel and correct_server

# ================================================================
#  EVENTS
# ================================================================
@bot.event
async def on_ready():
    print("=" * 50)
    print(f"👑 Akun     : {bot.user.name} (ID: {bot.user.id})")
    print(f"🎯 Post ke  : Server '{TARGET_SERVER_NAME}' (ID: {TARGET_SERVER_ID}) | Channel ID {TARGET_CHANNEL_ID}")
    print(f"🎮 Kontrol  : Server '{CONTROL_SERVER_NAME}' (ID: {CONTROL_SERVER_ID}) | Channel ID {CONTROL_CHANNEL_ID}")
    print(f"⏱️  Jeda     : {cd_min}–{cd_max} detik")
    print(f"📢 Pesan    : {current_message}")
    print("=" * 50)
    bot.loop.create_task(auto_post_loop())

# ================================================================
#  COMMANDS — Ketik di channel kontrol (server Anda sendiri)
# ================================================================

@bot.command(name="setmsg")
async def set_message(ctx, *, new_msg: str):
    """Ubah isi pesan auto post.
    Contoh: !setmsg Halo semua, ayo gabung!"""
    if not is_control_channel(ctx):
        return
    global current_message
    current_message = new_msg
    await ctx.send(f"✅ Pesan diubah:\n> {new_msg}", delete_after=10)
    print(f"📝 Pesan diubah: {new_msg}")


@bot.command(name="getmsg")
async def get_message(ctx):
    """Lihat pesan auto post yang aktif saat ini.
    Contoh: !getmsg"""
    if not is_control_channel(ctx):
        return
    await ctx.send(
        f"📢 **Pesan auto post saat ini:**\n{current_message}",
        delete_after=30
    )


@bot.command(name="setcd")
async def set_cooldown(ctx, min_detik: int = None, max_detik: int = None):
    """Ubah atau lihat jeda antar kiriman pesan.
    !setcd             → tampilkan CD saat ini
    !setcd 300         → set jeda tetap 5 menit
    !setcd 300 600     → set jeda acak 5–10 menit"""
    if not is_control_channel(ctx):
        return
    global cd_min, cd_max, next_post_time

    # Kalau tidak ada argumen → tampilkan CD saat ini
    if min_detik is None:
        sisa = max(0, int(next_post_time - time.time()))
        await ctx.send(
            f"⏱️ **Cooldown saat ini:** {cd_min}–{cd_max} detik "
            f"({cd_min//60} mnt {cd_min%60} dtk – {cd_max//60} mnt {cd_max%60} dtk)\n"
            f"⏳ Sisa waktu post berikutnya: **{sisa} detik** ({sisa//60} mnt {sisa%60} dtk)\n"
            f"Untuk ubah: `!setcd <min> <max>` — Contoh: `!setcd 300 600`",
            delete_after=20
        )
        return

    # Kalau hanya 1 angka → jeda tetap
    if max_detik is None:
        max_detik = min_detik

    if min_detik < 10 or min_detik > max_detik:
        await ctx.send(
            "❌ Input tidak valid!\n"
            "Pastikan min ≤ max dan minimal 10 detik.\n"
            "Contoh: `!setcd 300 600`",
            delete_after=10
        )
        return

    cd_min = min_detik
    cd_max = max_detik

    # Reset timer agar langsung pakai CD baru
    new_delay = random.randint(cd_min, cd_max)
    next_post_time = time.time() + new_delay

    await ctx.send(
        f"✅ Cooldown diubah!\n"
        f"⏱️ Jeda baru: {cd_min}–{cd_max} detik ({cd_min//60} mnt – {cd_max//60} mnt)\n"
        f"⏳ Post berikutnya dalam: **{new_delay} detik**",
        delete_after=15
    )
    print(f"⏱️ Cooldown diubah: {cd_min}–{cd_max} detik | Post berikutnya dalam {new_delay} detik")


@bot.command(name="postnow")
async def post_now(ctx):
    """Paksa kirim pesan sekarang tanpa menunggu CD.
    Contoh: !postnow"""
    if not is_control_channel(ctx):
        return
    global next_post_time
    next_post_time = time.time()  # trigger post di iterasi berikutnya
    await ctx.send("🚀 Pesan akan dikirim sekarang!", delete_after=5)
    print("🚀 Force post dipicu!")


@bot.command(name="toggleauto")
async def toggle_auto(ctx):
    """Aktifkan atau matikan auto post.
    Contoh: !toggleauto"""
    if not is_control_channel(ctx):
        return
    global auto_enabled, next_post_time
    auto_enabled = not auto_enabled
    status = "🟢 AKTIF" if auto_enabled else "🔴 MATI"
    if auto_enabled:
        # Reset timer saat diaktifkan kembali
        delay = random.randint(cd_min, cd_max)
        next_post_time = time.time() + delay
        await ctx.send(f"⏯️ Auto post: {status}\n⏳ Post berikutnya dalam {delay} detik", delete_after=10)
    else:
        await ctx.send(f"⏯️ Auto post: {status}", delete_after=10)
    print(f"⚡ Auto post: {status}")


@bot.command(name="edit")
async def edit_last_message(ctx, *, new_content: str):
    """Edit pesan terakhir bot di channel TUJUAN.
    Contoh: !edit Pesan yang sudah diedit"""
    if not is_control_channel(ctx):
        return
    target = bot.get_channel(TARGET_CHANNEL_ID)
    if not target:
        try:
            target = await bot.fetch_channel(TARGET_CHANNEL_ID)
        except Exception as e:
            await ctx.send(f"❌ Channel tujuan tidak ditemukan: {e}", delete_after=10)
            return
    async for msg in target.history(limit=30):
        if msg.author.id == bot.user.id:
            await msg.edit(content=new_content)
            await ctx.send(f"✏️ Pesan berhasil diedit:\n> {new_content}", delete_after=10)
            return
    await ctx.send("❌ Tidak ada pesan dari akun ini di channel tujuan.", delete_after=10)


@bot.command(name="status")
async def show_status(ctx):
    """Lihat status bot saat ini.
    Contoh: !status"""
    if not is_control_channel(ctx):
        return
    status_auto = "🟢 AKTIF" if auto_enabled else "🔴 MATI"
    sisa = max(0, int(next_post_time - time.time()))
    msg = (
        f"**📊 Status Bot**\n"
        f"Auto Post     : {status_auto}\n"
        f"Server Tujuan : {TARGET_SERVER_NAME}\n"
        f"Channel Tujuan: <#{TARGET_CHANNEL_ID}>\n"
        f"Cooldown      : {cd_min}–{cd_max} detik\n"
        f"Post berikutnya: **{sisa} detik lagi** ({sisa//60} mnt {sisa%60} dtk)\n"
        f"Pesan         : {current_message[:80]}"
    )
    await ctx.send(msg, delete_after=30)


# ================================================================
#  JALANKAN BOT
# ================================================================
bot.run(TOKEN)