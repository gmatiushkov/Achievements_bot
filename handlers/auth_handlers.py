from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import add_user, get_user, user_exists
from keyboards import auth_menu_markup, back_to_auth_markup, student_main_menu_markup, admin_main_menu_markup
from config import ADMINS_FULLNAMES

class AuthState(StatesGroup):
    not_authorized = State()

class Register(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_group_number = State()
    waiting_for_password = State()

class Login(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_password = State()

async def start_command(message: types.Message):
    await AuthState.not_authorized.set()
    await message.answer("Добро пожаловать! Пожалуйста, авторизуйтесь или зарегистрируйтесь.", reply_markup=auth_menu_markup)

async def auth_menu(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'log_in':
        await Login.waiting_for_full_name.set()
        await callback_query.message.answer("Пожалуйста, введите ваше ФИО:", reply_markup=back_to_auth_markup)
    elif callback_query.data == 'sign_up':
        await Register.waiting_for_full_name.set()
        await callback_query.message.answer("Пожалуйста, введите ваше ФИО:", reply_markup=back_to_auth_markup)

async def login_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await Login.waiting_for_password.set()
    await message.answer("Пожалуйста, введите ваш пароль:", reply_markup=back_to_auth_markup)

async def login_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    full_name = user_data.get('full_name')
    password = message.text

    user = get_user(full_name, password)
    if user:
        await state.finish()
        if full_name in ADMINS_FULLNAMES:
            await message.answer("Добро пожаловать, администратор!", reply_markup=admin_main_menu_markup)
        else:
            await message.answer("Добро пожаловать!", reply_markup=student_main_menu_markup)
    else:
        await AuthState.not_authorized.set()
        await message.answer("Неверное ФИО или пароль. Пожалуйста, попробуйте снова.", reply_markup=auth_menu_markup)

async def register_full_name(message: types.Message, state: FSMContext):
    if user_exists(message.text):
        await message.answer("Пользователь с таким ФИО уже существует. Если вы забыли пароль, обратитесь к администратору.", reply_markup=back_to_auth_markup)
        return
    await state.update_data(full_name=message.text)
    await Register.waiting_for_group_number.set()
    await message.answer("Пожалуйста, введите номер вашей группы:", reply_markup=back_to_auth_markup)

async def register_group_number(message: types.Message, state: FSMContext):
    await state.update_data(group_number=message.text)
    await Register.waiting_for_password.set()
    await message.answer("Пожалуйста, придумайте пароль:", reply_markup=back_to_auth_markup)

async def register_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    full_name = user_data.get('full_name')
    group_number = user_data.get('group_number')
    password = message.text

    add_user(full_name, group_number, password)
    await AuthState.not_authorized.set()
    await message.answer("Регистрация успешна! Пожалуйста, авторизуйтесь.", reply_markup=auth_menu_markup)

async def back_to_auth(callback_query: types.CallbackQuery, state: FSMContext):
    await AuthState.not_authorized.set()
    await callback_query.message.answer("Вы вернулись в главное меню аутентификации.", reply_markup=auth_menu_markup)

def register_auth_handlers(dp: Dispatcher, bot: Bot):
    dp.register_message_handler(start_command, commands="start", state="*")
    dp.register_callback_query_handler(auth_menu, state=AuthState.not_authorized)
    dp.register_message_handler(login_full_name, state=Login.waiting_for_full_name)
    dp.register_message_handler(login_password, state=Login.waiting_for_password)
    dp.register_message_handler(register_full_name, state=Register.waiting_for_full_name)
    dp.register_message_handler(register_group_number, state=Register.waiting_for_group_number)
    dp.register_message_handler(register_password, state=Register.waiting_for_password)
    dp.register_callback_query_handler(back_to_auth, text='back_to_auth', state="*")
