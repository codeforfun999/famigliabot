import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# =============================
# 🔑 ТВОЙ ТОКЕН
# =============================
TOKEN = "7552581646:AAH5Wpxfeq9PH1_m2DY38OCS1sC54hLKPws"

# =============================
# ⚙️ ЛОГИ
# =============================
logging.basicConfig(level=logging.INFO)

# =============================
# 📌 ИНИЦИАЛИЗАЦИЯ
# =============================
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# =============================
# 📈 ГЛОБАЛЬНОЕ ХРАНИЛИЩЕ КУРСОВ
# =============================
courses = {
    "usd_mdl": {"rate": None, "change": "⏸"},
    "btc": {"rate": None, "change": "⏸"},
    "ltc": {"rate": None, "change": "⏸"},
    "trc20": {"rate": None, "change": "⏸"},
}

# =============================
# 💵 ФУНКЦИЯ ОБНОВЛЕНИЯ КУРСА
# =============================
async def fetch_rates():
    global courses
    async with aiohttp.ClientSession() as session:
        try:
            # USD-MDL (API БНМ)
            async with session.get("https://www.bnm.md/en/official_exchange_rates?get_xml=1") as resp:
                text = await resp.text()
                import re
                match = re.search(r"<CharCode>USD</CharCode>\s*<Value>([\d.]+)</Value>", text)
                if match:
                    new_rate = float(match.group(1))
                    old_rate = courses["usd_mdl"]["rate"]
                    if old_rate:
                        courses["usd_mdl"]["change"] = "📈" if new_rate > old_rate else "📉" if new_rate < old_rate else "⏸"
                    courses["usd_mdl"]["rate"] = new_rate

            # BTC (CoinDesk)
            async with session.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json") as resp:
                data = await resp.json()
                new_rate = float(data["bpi"]["USD"]["rate"].replace(",", ""))
                old_rate = courses["btc"]["rate"]
                if old_rate:
                    courses["btc"]["change"] = "📈" if new_rate > old_rate else "📉" if new_rate < old_rate else "⏸"
                courses["btc"]["rate"] = new_rate

            # LTC (CoinGecko)
            async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd") as resp:
                data = await resp.json()
                new_rate = float(data["litecoin"]["usd"])
                old_rate = courses["ltc"]["rate"]
                if old_rate:
                    courses["ltc"]["change"] = "📈" if new_rate > old_rate else "📉" if new_rate < old_rate else "⏸"
                courses["ltc"]["rate"] = new_rate

            # TRC20 (USDT = 1$)
            new_rate = 1.0
            old_rate = courses["trc20"]["rate"]
            if old_rate:
                courses["trc20"]["change"] = "📈" if new_rate > old_rate else "📉" if new_rate < old_rate else "⏸"
            courses["trc20"]["rate"] = new_rate

        except Exception as e:
            logging.error(f"Ошибка получения курса: {e}")

# =============================
# 🔄 ЦИКЛ ОБНОВЛЕНИЯ
# =============================
async def updater():
    while True:
        await fetch_rates()
        await asyncio.sleep(900)  # 15 минут

# =============================
# 📲 МЕНЮ
# =============================
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("💵 XCHANGE"),
    KeyboardButton("🏚 ЛАВКИ СЕМЬИ")
)
main_menu.add(
    KeyboardButton("🎩 OG's"),
    KeyboardButton("🕸 СВЯЗИ СЕМЬИ")
)
main_menu.add(
    KeyboardButton("📉 КУРС"),
    KeyboardButton("🗂 ПРОФИЛЬ")
)

back_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 Назад"))

# =============================
# 👋 START
# =============================
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    photo_url = "https://i.ibb.co/G47PnhHx/Leonardo-Phoenix-10-Crimeinspired-aesthetic-luxurious-atmosphe-2.jpg"
    caption = (
        "🎩 <b>Benvenuto, Amico...</b>\n\n"
        "Ты пересёк порог семьи <b>Famiglia</b>.\n"
        "Здесь у каждого своя роль:\n"
        "💵 кто-то меняет деньги,\n"
        "🏚 кто-то держит лавки,\n"
        "👁 кто-то просто наблюдает.\n\n"
        "💸 <b>Деньги крутятся.</b>\n"
        "🏚 <b>Дела решаются.</b>\n"
        "🎩 <b>Уважение зарабатывается.</b>\n\n"
        "Теперь ты один из нас... выбери свой <a href='https://t.me/OnlyOmerta_BOT'>путь</a>."
    )
    await bot.send_photo(message.chat.id, photo=photo_url, caption=caption, reply_markup=main_menu)

# =============================
# 📉 КУРС
# =============================
@dp.message_handler(lambda m: m.text == "📉 КУРС")
async def show_rates(message: types.Message):
    text = "📊 <b>Актуальные курсы:</b>\n\n"
    if courses["usd_mdl"]["rate"]:
        text += f"🇺🇸 USD → 🇲🇩 MDL: {courses['usd_mdl']['rate']} MDL {courses['usd_mdl']['change']}\n"
    if courses["btc"]["rate"]:
        text += f"₿ BTC: {courses['btc']['rate']}$ {courses['btc']['change']}\n"
    if courses["ltc"]["rate"]:
        text += f"Ł LTC: {courses['ltc']['rate']}$ {courses['ltc']['change']}\n"
    if courses["trc20"]["rate"]:
        text += f"💠 TRC20 (USDT): {courses['trc20']['rate']}$ {courses['trc20']['change']}\n"

    await message.answer(text, reply_markup=back_menu)

# =============================
# 🗂 ПРОФИЛЬ
# =============================
@dp.message_handler(lambda m: m.text == "🗂 ПРОФИЛЬ")
async def profile(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Безымянный"
    rank = "🤌 Associato"  # пока фиксированный ранг
    await message.answer(
        f"📂 <b>Досье</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"🧑‍💼 Ник: @{username}\n"
        f"🎩 Ранг: {rank}",
        reply_markup=back_menu
    )

# =============================
# 🎩 OG's
# =============================
@dp.message_handler(lambda m: m.text == "🎩 OG's")
async def ogs(message: types.Message):
    text = (
        "🎩 <b>Старшие в семье:</b>\n\n"
        "👑 Don — @CashEater7\n"
        "🦴 Consigliere — @teamfutut"
    )
    await message.answer(text, reply_markup=back_menu)

# =============================
# 🕸 СВЯЗИ СЕМЬИ
# =============================
@dp.message_handler(lambda m: m.text == "🕸 СВЯЗИ СЕМЬИ")
async def links(message: types.Message):
    btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🍷 Сходка", url="https://t.me/gogobitches")
    )
    await message.answer("🕸 Наши связи:", reply_markup=btn)

# =============================
# 🔙 НАЗАД
# =============================
@dp.message_handler(lambda m: m.text == "🔙 Назад")
async def back(message: types.Message):
    await message.answer("Возвращаемся в главное меню:", reply_markup=main_menu)

# =============================
# 🏃 ЗАПУСК
# =============================
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_rates())  # ✅ сразу обновляем курсы при старте
    loop.create_task(updater())
    executor.start_polling(dp, skip_updates=True)