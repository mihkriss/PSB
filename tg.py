import os
import telebot
import threading
import time

# Настройки
TELEGRAM_TOKEN = "7986759367:AAEHDRrIIhWUB_G9nyahdyEvH0vHADrBr4c"  # Замените на ваш токен Telegram

bot = telebot.TeleBot(TELEGRAM_TOKEN)

authorized_chats = set()  # Множество для хранения ID авторизованных чатов

# Функция для отправки сообщений в Telegram
def send_telegram_message(topic, feedback):
    try:
        message = f"⚠️ Важный отзыв!\n\nТема: {topic}\nОтзыв: {feedback}"
        for chat_id in authorized_chats:
            bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")

# Обработчик команды /start для добавления чатов
def handle_start(message):
    chat_id = message.chat.id
    if chat_id not in authorized_chats:
        authorized_chats.add(chat_id)
        bot.reply_to(message, "Вы успешно подписаны на уведомления.")
    else:
        bot.reply_to(message, "Вы уже подписаны на уведомления.")

# Тестовая функция для отправки рандомных сообщений
def send_test_messages():
    topics = ["Оплата", "Доставка", "Качество продукта", "Поддержка"]
    feedbacks = [
        "Оплата прошла с ошибкой.",
        "Доставка задерживается.",
        "Продукт оказался повреждён.",
        "Служба поддержки не отвечает."
    ]
    while True:
        if authorized_chats:
            import random
            topic = random.choice(topics)
            feedback = random.choice(feedbacks)
            send_telegram_message(topic, feedback)
        time.sleep(600)  # Отправлять тестовые сообщения каждые 10 секунд

if __name__ == "__main__":
    bot.add_message_handler({"function": handle_start, "filters": {"commands": ["start"]}})

    # Запуск тестовой функции в отдельном потоке
    test_thread = threading.Thread(target=send_test_messages, daemon=True)
    test_thread.start()

    print("[+] Бот запущен и ожидает команды.")
    bot.polling(none_stop=True)
