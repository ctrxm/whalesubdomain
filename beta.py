import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from CloudFlare import CloudFlare
import random
import string

# Ganti dengan token bot Telegram Anda
TELEGRAM_TOKEN = '6573899040:AAEKYvNAIyyVrv-2WVlUjAwuYPGJVYs85QU'

# Ganti dengan API Key Cloudflare Anda
CLOUDFLARE_API_KEY = '4c6c88b6cffbe2f738489f5cb1612700f17f3'
CLOUDFLARE_EMAIL = 'hendra1rangga@gmail.com'

# Dictionary untuk menyimpan alamat IP server pengguna
user_ips = {}

def start(update, context):
    user_id = update.message.from_user.id
    context.bot.send_message(chat_id=update.message.chat_id, text="Selamat Datang Di Whale Subdomain🐳!, ini adalah layanan subdomain gratis dan otomatis dengan menggunakan API Cloudflare!\n\nSilahkan gunakan layanan ini dengan baik,kami tidak mengizinkan subdomain untuk tindakan ilegal cth : phising/scam/web judi\n")

    # Pilihan domain
    reply_keyboard = [['🥇 XVA.LTD', '🥈 GAFOQE.COM', '🥉 GARUDASHIELD.COM'], ['❌ Cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=user_id, text="Pilih domain yang tersedia:", reply_markup=markup)



    # Mengatur state agar bot tahu kita sedang menunggu pemilihan domain
    return 'wait_domain'

def cancel(update, context):
    user_id = update.message.from_user.id
    context.bot.send_message(chat_id=user_id, text="Terimakasih Sudah Menggunakan Layanan Kami\n\nKeberuntungan Berpihak Pada Yang Berani\n", reply_markup=ReplyKeyboardRemove())
    # Hapus data pengguna dari kamus jika ada
    if user_id in user_ips:
        del user_ips[user_id]
    return ConversationHandler.END

def wait_domain(update, context):
    user_id = update.message.from_user.id
    selected_domain = update.message.text.lower()

    if selected_domain not in ['🥇 xva.ltd', '🥈 gafoqe.com', '🥉 garudashield.com', '❌ cancel']:
        context.bot.send_message(chat_id=user_id, text="Pilihan domain tidak valid. Silakan pilih domain yang benar.")
        return 'wait_domain'
    elif selected_domain == 'cancel':
        return cancel(update, context)

    user_ips[user_id] = {'domain': selected_domain}

    # Menggunakan keyboard khusus untuk memudahkan input IP
    reply_keyboard = [['Cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=user_id, text="Masukkan IP server Hosting/Bug/VPS Kamu:", reply_markup=markup)

    # Mengatur state agar bot tahu kita sedang menunggu IP
    return 'wait_ip'

def wait_ip(update, context):
    user_id = update.message.from_user.id
    user_data = user_ips[user_id]
    user_data['ip'] = update.message.text

    if 'domain' not in user_data:
        context.bot.send_message(chat_id=user_id, text="Terjadi kesalahan. Silakan coba lagi.")
        return cancel(update, context)

    # Membuat string acak untuk subdomain
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    subdomain = f"{random_string}"

    # Mengelola subdomain di Cloudflare
    cf = CloudFlare(email=CLOUDFLARE_EMAIL, token=CLOUDFLARE_API_KEY)

    # Menentukan zone id berdasarkan pilihan domain
    if user_data['domain'] == 'xva.ltd':
        zone_id = 'f48cc580bb94d2b12755c9ac3a975015'
    elif user_data['domain'] == 'gafoqe.com':
        zone_id = '45b2d3902a429f40c86fb435477de110'
    elif user_data['domain'] == 'garudashield.com':
        zone_id = 'dec253b052e3f2e7d40b91a2aabdd575'
    else:
        context.bot.send_message(chat_id=user_id, text="Terjadi kesalahan. Silakan coba lagi.")
        return cancel(update, context)

    record = {
        'type': 'A',
        'name': f"{subdomain}.{user_data['domain']}",
        'content': user_data['ip'],
    }

    try:
        cf.zones.dns_records.post(zone_id, data=record)
        # Mengirimkan pesan ke pengguna dengan subdomain yang dibuat
        message = f"Subdomain Berhasil dibuat.\n\nDOMAIN : {user_data['domain']}\nIP : {user_data['ip']}\n\nSubdomain Kamu :\n{subdomain}.{user_data['domain']}\n\nCreated BY : @ctrxzip.\nID Kamu : {user_id}\n"
        context.bot.send_message(chat_id=user_id, text=message)
    except Exception as e:
        print(f"Error creating DNS record: {e}")
        context.bot.send_message(chat_id=user_id, text="Terjadi kesalahan saat membuat rekaman DNS. Silakan coba lagi.")

    # Menghapus data pengguna dari kamus setelah digunakan
    del user_ips[user_id]

    return cancel(update, context)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'wait_domain': [MessageHandler(Filters.text & ~Filters.command, wait_domain)],
            'wait_ip': [MessageHandler(Filters.text & ~Filters.command, wait_ip)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    
    # Mulai bot
    updater.start_polling()

    # Jalankan bot sampai pengguna menekan Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
    
    
