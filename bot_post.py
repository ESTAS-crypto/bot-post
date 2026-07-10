import discord
from discord.ext import commands
import asyncio
import random
import sys

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

# ================================================================
#  INISIALISASI BOT
# ================================================================
bot = commands.Bot(command_prefix="!", self_bot=True)

# ================================================================
#  LOOP AUTO POST
# ================================================================
async def auto_post_loop():
    global auto_enabled
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


    while not bot.is_closed():
        if not auto_enabled:
            await asyncio.sleep(5)
            continue

        delay = random.randint(cd_min, cd_max)
        print(f"⏳ Kirim berikutnya dalam {delay} detik ({delay//60} menit {delay%60} detik)...")
        await asyncio.sleep(delay)

        if not auto_enabled:
            continue

        try:
            await channel.send(current_message)
            print(f"✅ Pesan terkirim ke #{channel.name}: {current_message[:60]}")
        except Exception as e:
            print(f"❌ Gagal kirim pesan: {e}")

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


@bot.command(name="setcd")
async def set_cooldown(ctx, min_detik: int, max_detik: int = 0):
    """Ubah jeda antar kiriman pesan.
    Contoh: !setcd 300 600  → jeda acak antara 5–10 menit
    Contoh: !setcd 300      → jeda tetap 5 menit"""
    if not is_control_channel(ctx):
        return
    global cd_min, cd_max
    if max_detik == 0:
        max_detik = min_detik
    if min_detik < 10 or min_detik > max_detik:
        await ctx.send("❌ Tidak valid. Contoh: `!setcd 300 600`", delete_after=10)
        return
    cd_min = min_detik
    cd_max = max_detik
    await ctx.send(
        f"⏱️ Jeda diubah: {cd_min}–{cd_max} detik "
        f"({cd_min//60}–{cd_max//60} menit)",
        delete_after=10
    )
    print(f"⏱️ Cooldown diubah: {cd_min}–{cd_max} detik")


@bot.command(name="toggleauto")
async def toggle_auto(ctx):
    """Aktifkan atau matikan auto post.
    Contoh: !toggleauto"""
    if not is_control_channel(ctx):
        return
    global auto_enabled
    auto_enabled = not auto_enabled
    status = "🟢 AKTIF" if auto_enabled else "🔴 MATI"
    await ctx.send(f"⏯️ Auto post sekarang: {status}", delete_after=10)
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
    msg = (
        f"**📊 Status Bot**\n"
        f"Auto Post : {status_auto}\n"
        f"Server Tujuan : {TARGET_SERVER_NAME}\n"
        f"Channel Tujuan : <#{TARGET_CHANNEL_ID}>\n"
        f"Jeda : {cd_min}–{cd_max} detik\n"
        f"Pesan : {current_message[:80]}"
    )
    await ctx.send(msg, delete_after=30)


# ================================================================
#  JALANKAN BOT
# ================================================================
bot.run(TOKEN)