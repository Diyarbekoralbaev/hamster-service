from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import database

API_TOKEN = '7376912095:AAHesY6_KUdm4hO4JPWrgUy8Xd7p1gDQmkQ'
CHANNEL_1 = "@Diyarbek_Blog"
CHANNEL_2 = "@AralTech_dev"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storege = MemoryStorage()
dp = Dispatcher(bot, storage=storege)
dp.middleware.setup(LoggingMiddleware())


class AddToken(StatesGroup):
    waiting_for_token = State()


main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("Add token"))
main_keyboard.add(KeyboardButton("Remove token"))
main_keyboard.add(KeyboardButton("Profile"))
main_keyboard.add(KeyboardButton("Help"))

cancel_button = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_button.add(KeyboardButton("Cancel"))

channel_button = InlineKeyboardMarkup()
channel_button.add(InlineKeyboardButton("Channel 1", url=f"https://t.me/{CHANNEL_1[1:]}"))
channel_button.add(InlineKeyboardButton("Channel 2", url=f"https://t.me/{CHANNEL_2[1:]}"))

async def check_user_joining(user_id):
    try:
        channel1 = await bot.get_chat_member(CHANNEL_1, user_id)
        channel2 = await bot.get_chat_member(CHANNEL_2, user_id)
        if not channel1.status in ("administrator", "creator", "member") or not channel2.status in ("administrator", "creator", "member"):
            return False
        return True
    except Exception as e:
        return False

@dp.message_handler(commands='start', state='*')
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    if database.get_user(message.from_user.id) is None:
        database.create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    if await check_user_joining(message.from_user.id):
        await message.reply("Welcome to the bot", reply_markup=main_keyboard)
    else:
        await message.reply("Please join the channels to use the bot", reply_markup=channel_button)


@dp.message_handler(state=AddToken.waiting_for_token)
async def process_token(message: types.Message, state: FSMContext):
    if await check_user_joining(message.from_user.id):
        if message.text == "Cancel":
            await state.finish()
            await message.reply("Cancelled", reply_markup=main_keyboard)
        else:
            if database.add_token(message.text, message.from_user.id):
                await message.reply("Token added successfully", reply_markup=main_keyboard)
            else:
                await message.reply("Token already exists", reply_markup=cancel_button)
            await state.finish()
    else:
        await message.reply("Please join the channels to use the bot", reply_markup=channel_button)


@dp.message_handler(lambda message: message.text == "Add token", state='*')
async def process_add_token(message: types.Message):
    if await check_user_joining(message.from_user.id):
        await message.reply("Send me your token", reply_markup=cancel_button)
        await AddToken.waiting_for_token.set()
    else:
        await message.reply("Please join the channels to use the bot", reply_markup=channel_button)


@dp.message_handler(lambda message: message.text == "Remove token", state='*')
async def process_remove_token(message: types.Message):
    if await check_user_joining(message.from_user.id):
        tokens = database.get_user_tokens(message.from_user.id)
        if tokens:
            keyboard = InlineKeyboardMarkup()
            for token in tokens:
                keyboard.add(InlineKeyboardButton(token, callback_data=f"remove_token_{token}"))
            await message.reply("Select a token to remove", reply_markup=keyboard)
        else:
            await message.reply("No tokens to remove", reply_markup=main_keyboard)
    else:
        await message.reply("Please join the channels to use the bot", reply_markup=channel_button)


@dp.callback_query_handler(lambda query: query.data.startswith("remove_token_"))
async def process_remove_token_callback(query: types.CallbackQuery):
    if await check_user_joining(query.from_user.id):
        token = query.data.split("_")[-1]
        database.delete_token(token)
        await query.message.reply("Token removed successfully", reply_markup=main_keyboard)
        await query.answer()
    else:
        await query.message.reply("Please join the channels to use the bot", reply_markup=channel_button)


@dp.message_handler(lambda message: message.text == "Profile", state='*')
async def process_profile(message: types.Message):
    try:
        if await check_user_joining(message.from_user.id):
            user = database.get_user(message.from_user.id)
            tokens = database.get_user_tokens(message.from_user.id)
            await message.reply(f"User ID: {user[0]}\nUsername: {user[1]}\nName: {user[2]}\nTokens: {', '.join(tokens)}", reply_markup=main_keyboard)
        else:
            database.delete_user(message.from_user.id)
            database.delete_users_tokens(message.from_user.id)
            await message.reply("Please join the channels to use the bot", reply_markup=channel_button)
    except Exception as e:
        await message.reply("Uhh, something went wrong, please restart the bot\n/start", reply_markup=main_keyboard)


@dp.message_handler(lambda message: message.text == "Help", state='*')
async def process_help(message: types.Message):
    if await check_user_joining(message.from_user.id):
        await message.reply("You can see a tutorial on how to use the bot here: https://bit.ly/hamster-run-always", reply_markup=main_keyboard)
    else:
        await message.reply("Please join the channels to use the bot", reply_markup=channel_button)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
