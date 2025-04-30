import logging
import random
import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
import threading

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("Не задан TELEGRAM_BOT_TOKEN в переменных окружения!")
    exit(1)

RP_ACTIONS = {
    # Физические действия (12)
    "ударить": ["👊 <b>{user}</b> наносит удар по <b>{target}</b>", "🤜 <b>{user}</b> бьёт <b>{target}</b> в живот"],
    "толкнуть": ["🫳 <b>{user}</b> толкает <b>{target}</b>", "💨 <b>{user}</b> резко толкает <b>{target}</b>"],
    "пнуть": ["👟 <b>{user}</b> пинает <b>{target}</b>", "🦵 <b>{user}</b> наносит удар ногой по <b>{target}</b>"],
    "укусить": ["🦷 <b>{user}</b> кусает <b>{target}</b>", "😬 <b>{user}</b> впивается зубами в <b>{target}</b>"],
    "пощечина": ["👋 <b>{user}</b> даёт пощёчину <b>{target}</b>", "🤚 <b>{user}</b> отвешивает оплеуху <b>{target}</b>"],
    "ущипнуть": ["✂️ <b>{user}</b> щиплет <b>{target}</b>", "🤏 <b>{user}</b> защипывает <b>{target}</b>"],
    "шлепнуть": ["👋 <b>{user}</b> шлёпает <b>{target}</b>", "🍑 <b>{user}</b> наказывает <b>{target}</b>"],
    "царапать": ["🐾 <b>{user}</b> царапает <b>{target}</b>", "✋ <b>{user}</b> оставляет следы на <b>{target}</b>"],
    "душить": ["👹 <b>{user}</b> душит <b>{target}</b>", "💀 <b>{user}</b> перекрывает кислород <b>{target}</b>"],
    "пинать": ["👢 <b>{user}</b> пинает лежачего <b>{target}</b>", "🥾 <b>{user}</b> бьёт ногами <b>{target}</b>"],
    "ткнуть": ["👉 <b>{user}</b> тычет в <b>{target}</b>", "👈 <b>{user}</b> тыкает пальцем в <b>{target}</b>"],
    "уколоть": ["💉 <b>{user}</b> колет <b>{target}</b>", "🪡 <b>{user}</b> делает больно <b>{target}</b>"],

    # Дружеские взаимодействия (12)
    "обнять": ["🤗 <b>{user}</b> обнимает <b>{target}</b>", "🫂 <b>{user}</b> крепко обхватывает <b>{target}</b>"],
    "погладить": ["🐾 <b>{user}</b> гладит <b>{target}</b>", "💞 <b>{user}</b> нежно поглаживает <b>{target}</b>"],
    "поцеловать": ["💋 <b>{user}</b> целует <b>{target}</b>", "😘 <b>{user}</b> нежно прикасается губами к <b>{target}</b>"],
    "похлопать": ["👏 <b>{user}</b> хлопает <b>{target}</b> по плечу", "🤝 <b>{user}</b> одобрительно похлопывает <b>{target}</b>"],
    "прижать": ["💕 <b>{user}</b> прижимает к себе <b>{target}</b>", "🫂 <b>{user}</b> крепко сжимает в объятиях <b>{target}</b>"],
    "потрепать": ["✋ <b>{user}</b> треплет по голове <b>{target}</b>", "👋 <b>{user}</b> игриво трогает <b>{target}</b>"],
    "почесать": ["🐶 <b>{user}</b> чешет за ушком <b>{target}</b>", "✋ <b>{user}</b> массирует спину <b>{target}</b>"],
    "пожмякать": ["🤝 <b>{user}</b> пожимает руку <b>{target}</b>", "🫱 <b>{user}</b> крепко жмёт ладонь <b>{target}</b>"],
    "потискать": ["🐻 <b>{user}</b> тискает <b>{target}</b>", "🤗 <b>{user}</b> сжимает в объятиях <b>{target}</b>"],
    "пощекотать": ["😂 <b>{user}</b> щекочет <b>{target}</b>", "🪶 <b>{user}</b> дразнит <b>{target}</b>"],
    "покормить": ["🍎 <b>{user}</b> кормит <b>{target}</b>", "🍕 <b>{user}</b> угощает <b>{target}</b>"],
    "напоить": ["🍵 <b>{user}</b> поит <b>{target}</b> чаем", "🍷 <b>{user}</b> наливает напиток <b>{target}</b>"],

    # Эмоциональные действия (12)
    "похвалить": ["🌟 <b>{user}</b> хвалит <b>{target}</b>", "👑 <b>{user}</b> восхищается <b>{target}</b>"],
    "поругать": ["👎 <b>{user}</b> ругает <b>{target}</b>", "😠 <b>{user}</b> отчитывает <b>{target}</b>"],
    "смеяться": ["😂 <b>{user}</b> смеётся над <b>{target}</b>", "🤣 <b>{user}</b> ржёт с <b>{target}</b>"],
    "плакать": ["😭 <b>{user}</b> плачет из-за <b>{target}</b>", "😢 <b>{user}</b> рыдает на плече у <b>{target}</b>"],
    "засмеять": ["😆 <b>{user}</b> закатывается от смеха над <b>{target}</b>", "🤣 <b>{user}</b> потешается над <b>{target}</b>"],
    "заплакать": ["😭 <b>{user}</b> начинает рыдать из-за <b>{target}</b>", "😢 <b>{user}</b> распускает нюни из-за <b>{target}</b>"],
    "обидеть": ["😞 <b>{user}</b> обижает <b>{target}</b>", "💔 <b>{user}</b> ранит чувства <b>{target}</b>"],
    "поддержать": ["💪 <b>{user}</b> поддерживает <b>{target}</b>", "🤝 <b>{user}</b> оказывает моральную помощь <b>{target}</b>"],
    "утешить": ["🤗 <b>{user}</b> утешает <b>{target}</b>", "🫂 <b>{user}</b> успокаивает <b>{target}</b>"],
    "разозлить": ["😡 <b>{user}</b> злит <b>{target}</b>", "👿 <b>{user}</b> выводит из себя <b>{target}</b>"],
    "испугать": ["👻 <b>{user}</b> пугает <b>{target}</b>", "💀 <b>{user}</b> вселяет ужас в <b>{target}</b>"],
    "успокоить": ["🧘 <b>{user}</b> успокаивает <b>{target}</b>", "🕊️ <b>{user}</b> дарит покой <b>{target}</b>"],

    # Романтические действия (8)
    "признаться": ["💌 <b>{user}</b> признаётся в любви <b>{target}</b>", "💘 <b>{user}</b> открывает свои чувства <b>{target}</b>"],
    "флиртовать": ["😏 <b>{user}</b> флиртует с <b>{target}</b>", "😉 <b>{user}</b> игриво подмигивает <b>{target}</b>"],
    "пригласить": ["📩 <b>{user}</b> приглашает на свидание <b>{target}</b>", "💐 <b>{user}</b> предлагает встретиться <b>{target}</b>"],
    "обожать": ["🥰 <b>{user}</b> обожает <b>{target}</b>", "😍 <b>{user}</b> боготворит <b>{target}</b>"],
    "заигрывать": ["😘 <b>{user}</b> заигрывает с <b>{target}</b>", "😏 <b>{user}</b> кокетничает с <b>{target}</b>"],
    "соблазнить": ["💋 <b>{user}</b> соблазняет <b>{target}</b>", "👄 <b>{user}</b> привлекает внимание <b>{target}</b>"],
    "покорить": ["👑 <b>{user}</b> покоряет сердце <b>{target}</b>", "💝 <b>{user}</b> завоёвывает любовь <b>{target}</b>"],
    "ревновать": ["💔 <b>{user}</b> ревнует <b>{target}</b>", "👀 <b>{user}</b> следит за каждым шагом <b>{target}</b>"],

    # Боевые действия (8)
    "атаковать": ["⚔️ <b>{user}</b> атакует <b>{target}</b>", "🔫 <b>{user}</b> нападает на <b>{target}</b>"],
    "защитить": ["🛡️ <b>{user}</b> защищает <b>{target}</b>", "🏰 <b>{user}</b> прикрывает собой <b>{target}</b>"],
    "блокировать": ["✋ <b>{user}</b> блокирует удар <b>{target}</b>", "🖐️ <b>{user}</b> парирует атаку <b>{target}</b>"],
    "победить": ["🏆 <b>{user}</b> побеждает <b>{target}</b>", "🎖️ <b>{user}</b> одерживает верх над <b>{target}</b>"],
    "ранить": ["💢 <b>{user}</b> ранит <b>{target}</b>", "🩸 <b>{user}</b> наносит ранение <b>{target}</b>"],
    "контролировать": ["🧠 <b>{user}</b> контролирует <b>{target}</b>", "👁️ <b>{user}</b> подчиняет своей воле <b>{target}</b>"],
    "обезвредить": ["🛑 <b>{user}</b> обезвреживает <b>{target}</b>", "🚫 <b>{user}</b> нейтрализует угрозу от <b>{target}</b>"],
    "разоружить": ["🔫 <b>{user}</b> разоружает <b>{target}</b>", "⚔️ <b>{user}</b> лишает оружия <b>{target}</b>"],

    # Магические действия (8)
    "заколдовать": ["✨ <b>{user}</b> колдует над <b>{target}</b>", "🔮 <b>{user}</b> накладывает заклинание на <b>{target}</b>"],
    "исцелить": ["💚 <b>{user}</b> исцеляет <b>{target}</b>", "🩹 <b>{user}</b> лечит раны <b>{target}</b>"],
    "оживить": ["💖 <b>{user}</b> возвращает к жизни <b>{target}</b>", "⚡ <b>{user}</b> воскрешает <b>{target}</b>"],
    "превратить": ["🐸 <b>{user}</b> превращает <b>{target}</b> в лягушку", "🦋 <b>{user}</b> обращает <b>{target}</b> в бабочку"],
    "телепортировать": ["🌀 <b>{user}</b> телепортирует <b>{target}</b>", "⚡ <b>{user}</b> перемещает в пространстве <b>{target}</b>"],
    "клонировать": ["👥 <b>{user}</b> создаёт клон <b>{target}</b>", "🧬 <b>{user}</b> копирует <b>{target}</b>"],
    "заморозить": ["❄️ <b>{user}</b> замораживает <b>{target}</b>", "⛄ <b>{user}</b> превращает в лёд <b>{target}</b>"],
    "поджечь": ["🔥 <b>{user}</b> поджигает <b>{target}</b>", "🧯 <b>{user}</b> устраивает пожар для <b>{target}</b>"],

    # Преступные действия (8)
    "украсть": ["🦹 <b>{user}</b> крадёт у <b>{target}</b>", "👛 <b>{user}</b> ворует кошелёк у <b>{target}</b>"],
    "ограбить": ["💰 <b>{user}</b> грабит <b>{target}</b>", "💎 <b>{user}</b> отбирает драгоценности у <b>{target}</b>"],
    "похитить": ["🚔 <b>{user}</b> похищает <b>{target}</b>", "👣 <b>{user}</b> уводит с собой <b>{target}</b>"],
    "обмануть": ["🃏 <b>{user}</b> обманывает <b>{target}</b>", "🎭 <b>{user}</b> вводит в заблуждение <b>{target}</b>"],
    "шантажировать": ["💼 <b>{user}</b> шантажирует <b>{target}</b>", "📜 <b>{user}</b> вымогает у <b>{target}</b>"],
    "подставить": ["🎭 <b>{user}</b> подставляет <b>{target}</b>", "🕵️ <b>{user}</b> обвиняет невиновного <b>{target}</b>"],
    "взломать": ["💻 <b>{user}</b> взламывает <b>{target}</b>", "🔓 <b>{user}</b> получает доступ к данным <b>{target}</b>"],
    "запереть": ["🔒 <b>{user}</b> запирает <b>{target}</b>", "🚪 <b>{user}</b> заточает в комнате <b>{target}</b>"],

    # Повседневные действия (8)
    "уложить": ["🛌 <b>{user}</b> укладывает спать <b>{target}</b>", "🌙 <b>{user}</b> желает спокойной ночи <b>{target}</b>"],
    "разбудить": ["⏰ <b>{user}</b> будит <b>{target}</b>", "🔔 <b>{user}</b> нежно поднимает с постели <b>{target}</b>"],
    "позвать": ["📢 <b>{user}</b> зовёт <b>{target}</b>", "👋 <b>{user}</b> манит к себе <b>{target}</b>"],
    "выгнать": ["🚪 <b>{user}</b> выгоняет <b>{target}</b>", "👢 <b>{user}</b> выставляет за дверь <b>{target}</b>"],
    "простить": ["☮️ <b>{user}</b> прощает <b>{target}</b>", "🕊️ <b>{user}</b> мирится с <b>{target}</b>"],
    "научить": ["📚 <b>{user}</b> обучает <b>{target}</b>", "🎓 <b>{user}</b> передаёт знания <b>{target}</b>"],
    "учить": ["🧠 <b>{user}</b> учит <b>{target}</b>", "📖 <b>{user}</b> объясняет материал <b>{target}</b>"],
    "воспитывать": ["👨‍🏫 <b>{user}</b> воспитывает <b>{target}</b>", "🌱 <b>{user}</b> прививает манеры <b>{target}</b>"],

    # Творческие действия (4)
    "нарисовать": ["🎨 <b>{user}</b> рисует портрет <b>{target}</b>", "🖌️ <b>{user}</b> изображает <b>{target}</b> на холсте"],
    "спеть": ["🎤 <b>{user}</b> поёт песню для <b>{target}</b>", "🎶 <b>{user}</b> исполняет серенаду <b>{target}</b>"],
    "станцевать": ["💃 <b>{user}</b> танцует с <b>{target}</b>", "🕺 <b>{user}</b> приглашает на танец <b>{target}</b>"],
    "похлопать": ["👏 <b>{user}</b> аплодирует <b>{target}</b>", "🙌 <b>{user}</b> рукоплещет таланту <b>{target}</b>"]
}

class RPBot:
    def __init__(self):
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self._register_handlers()

    def _register_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self._start))
        self.dispatcher.add_handler(CommandHandler("help", self._help))
        self.dispatcher.add_handler(CommandHandler("actions", self._list_actions))
        self.dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self._handle_rp)
        )

    def _start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "🤖 <b>Привет! Я RP-бот с 80+ командами!</b>\n\n"
            "🔹 Используй <code>!команда @юзер</code>\n"
            "🔹 Или ответь на сообщение с <code>!командой</code>\n"
            "🔹 Поддерживаются пробелы после <code>!</code>\n\n"
            "📋 Полный список: /actions\n"
            "❓ Помощь: /help",
            parse_mode=ParseMode.HTML
        )

    def _help(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "ℹ️ <b>Помощь по RP-боту:</b>\n\n"
            "1. <b>Обычная команда:</b>\n"
            "   <code>!обнять @username</code>\n"
            "   <code>! обнять @username</code> (с пробелом)\n\n"
            "2. <b>Ответ на сообщение:</b>\n"
            "   Ответь на сообщение с текстом <code>!обнять</code>\n\n"
            "3. <b>Форматирование:</b>\n"
            "   Все имена выделяются <b>жирным</b>\n"
            "   Добавлены тематические эмодзи\n\n"
            "🎭 Доступно 80+ разных действий! /actions",
            parse_mode=ParseMode.HTML
        )

    def _list_actions(self, update: Update, context: CallbackContext):
        categories = {
            "💥 Физические (12)": ["ударить", "толкнуть", "пнуть", "укусить", "пощечина", "ущипнуть", 
                                  "шлепнуть", "царапать", "душить", "пинать", "ткнуть", "уколоть"],
            "🤗 Дружеские (12)": ["обнять", "погладить", "поцеловать", "похлопать", "прижать", "потрепать",
                                 "почесать", "пожмякать", "потискать", "пощекотать", "покормить", "напоить"],
            "🎭 Эмоции (12)": ["похвалить", "поругать", "смеяться", "плакать", "засмеять", "заплакать",
                              "обидеть", "поддержать", "утешить", "разозлить", "испугать", "успокоить"],
            "💘 Романтика (8)": ["признаться", "флиртовать", "пригласить", "обожать", 
                                "заигрывать", "соблазнить", "покорить", "ревновать"],
            "⚔️ Боевые (8)": ["атаковать", "защитить", "блокировать", "победить", 
                             "ранить", "контролировать", "обезвредить", "разоружить"],
            "✨ Магия (8)": ["заколдовать", "исцелить", "оживить", "превратить",
                           "телепортировать", "клонировать", "заморозить", "поджечь"],
            "🦹 Криминал (8)": ["украсть", "ограбить", "похитить", "обмануть",
                               "шантажировать", "подставить", "взломать", "запереть"],
            "🏠 Повседневные (8)": ["уложить", "разбудить", "позвать", "выгнать",
                                  "простить", "научить", "учить", "воспитывать"],
            "🎨 Творчество (4)": ["нарисовать", "спеть", "станцевать", "похлопать"]
        }

        response = "🎭 <b>Доступные RP-действия (80+):</b>\n\n"
        for category, actions in categories.items():
            response += f"{category}:\n"
            response += ", ".join([f"<code>!{a}</code>" for a in actions]) + "\n\n"

        response += (
            "📌 <b>Примеры:</b>\n"
            "<code>!обнять @юзер</code>\n"
            "<code>! обнять @юзер</code> (с пробелом)\n"
            "Ответь на сообщение с <code>!обнять</code>"
        )

        update.message.reply_text(response, parse_mode=ParseMode.HTML)

    def _handle_rp(self, update: Update, context: CallbackContext):
        try:
            message = update.message
            if not message or not message.text:
                return

            # Нормализация команды (удаляем лишние пробелы)
            text = message.text.replace('! ', '!', 1).strip()
            if not text.startswith('!'):
                return

            # Удаление сообщения
            try:
                message.delete()
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")

            # Извлечение команды (с поддержкой пробела после !)
            cmd_part = text[1:].strip()
            if not cmd_part:
                return

            cmd = cmd_part.split()[0].lower()
            if cmd not in RP_ACTIONS:
                return

            # Получение информации об участниках
            user = message.from_user
            user_name = f"@{user.username}" if user.username else user.first_name
            
            # Определение цели
            target = None
            if message.reply_to_message:
                target_user = message.reply_to_message.from_user
                target = f"@{target_user.username}" if target_user.username else target_user.first_name
            else:
                # Ищем упоминание в тексте команды
                parts = cmd_part.split()
                if len(parts) > 1:
                    target = parts[1]

            if not target:
                self._send_message(message.chat_id, f"<b>{user_name}</b>, укажите цель через @username или ответьте на сообщение")
                return

            # Отправка ответа с жирными именами
            response = random.choice(RP_ACTIONS[cmd]).format(
                user=user_name,
                target=target
            )
            self._send_message(message.chat_id, response)

        except Exception as e:
            logger.error(f"Ошибка обработки RP-команды: {e}")

    def _send_message(self, chat_id, text):
        """Безопасная отправка сообщения"""
        try:
            self.updater.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")

    def run(self):
        logger.info("Запуск RP-бота...")
        self.updater.start_polling()
        logger.info("RP-бот успешно запущен")
        self.updater.idle()

# Создаем Flask приложение для поддержания активности
app = Flask(__name__)

@app.route('/')
def home():
    return "RP Bot is running!", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем бота
    bot = RPBot()
    bot.run()
