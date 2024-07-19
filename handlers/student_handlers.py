from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import get_achievements_by_user, add_achievement, delete_achievement, update_achievement_status, update_achievement_files, update_achievement_description
from keyboards import (
    student_main_menu_markup, student_back_to_main_markup,
    student_waiting_files_markup, student_achievement_details_markup,
    student_back_to_achievement_details_markup, student_edit_waiting_files_markup
)

class StudentState(StatesGroup):
    main_menu = State()
    waiting_for_achievement_choice = State()
    viewing_achievement_details = State()
    waiting_for_description = State()
    waiting_for_files = State()
    edit_waiting_for_description = State()
    edit_waiting_for_files = State()

async def student_view_achievements(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)
    user_data = await state.get_data()
    full_name = user_data.get('full_name')
    achievements = get_achievements_by_user(full_name)
    if not achievements:
        await callback_query.message.answer("У вас пока нет достижений.", reply_markup=student_main_menu_markup)
        return

    response = "Ваши достижения:\n\n"
    for idx, achievement in enumerate(achievements, start=1):
        status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
        response += f"{idx}. {status_emoji} {achievement.description[:50]}...\n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер достижения для подробного просмотра:", reply_markup=student_back_to_main_markup)
    await StudentState.waiting_for_achievement_choice.set()

async def student_choose_achievement(message_or_callback: types.Message or types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    full_name = user_data.get('full_name')
    achievements = get_achievements_by_user(full_name)

    if isinstance(message_or_callback, types.Message):
        message = message_or_callback

        try:
            achievement_idx = int(message.text) - 1
            if achievement_idx < 0 or achievement_idx >= len(achievements):
                raise ValueError("Invalid index")

            achievement = achievements[achievement_idx]
            await state.update_data(current_achievement=achievement.to_dict())
            await StudentState.viewing_achievement_details.set()

            # Отправка файлов
            for file_type, file_id in achievement.files:
                if file_type == 'photo':
                    await message.answer_photo(file_id)
                elif file_type == 'document':
                    await message.answer_document(file_id)

            status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
            response = f"{achievement.description}\n{achievement.status} {status_emoji}\n"
            await message.answer(response, reply_markup=student_achievement_details_markup)

        except (ValueError, IndexError):
            await message.answer("Неверный номер достижения. Пожалуйста, попробуйте снова.")
            await display_achievements_list(message, state, achievements)

    elif isinstance(message_or_callback, types.CallbackQuery):
        callback_query = message_or_callback

        if not achievements:
            await callback_query.message.answer("У вас пока нет достижений.", reply_markup=student_main_menu_markup)
            return

        await display_achievements_list(callback_query.message, state, achievements)
        await StudentState.waiting_for_achievement_choice.set()

async def display_achievements_list(message: types.Message, state: FSMContext, achievements):
    response = "Ваши достижения:\n\n"
    for idx, achievement in enumerate(achievements, start=1):
        status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
        response += f"{idx}. {status_emoji} {achievement.description[:50]}...\n"

    await message.answer(response)
    await message.answer("Введите номер достижения для подробного просмотра:", reply_markup=student_back_to_main_markup)


async def student_add_achievement(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(files=[])  # Очистить список файлов
    await callback_query.message.answer("Пожалуйста, введите описание достижения:", reply_markup=student_back_to_main_markup)
    await StudentState.waiting_for_description.set()

async def student_save_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await StudentState.waiting_for_files.set()
    await message.answer("Теперь отправьте файлы, которые необходимо прикрепить к достижению. Когда закончите, нажмите 'Готово'.", reply_markup=student_waiting_files_markup)

async def student_upload_files(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)

    user_data = await state.get_data()
    files = user_data.get('files', [])

    # Проверка на количество файлов
    if len(files) >= 10:
        await message.answer("Вы не можете загрузить больше 10 файлов.")
        return

    # Проверка типа контента
    if not message.photo and not message.document:
        await message.answer("Пожалуйста, отправьте фото или документ.")
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        files.append(('photo', file_id))
    elif message.document:
        file_id = message.document.file_id
        files.append(('document', file_id))

    await state.update_data(files=files)

async def student_files_loaded(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)

    user_data = await state.get_data()
    description = user_data.get('description')
    files = user_data.get('files', [])
    full_name = user_data.get('full_name')
    group_number = user_data.get('group_number')

    add_achievement(description, files, group_number, full_name)
    await StudentState.main_menu.set()
    await callback_query.message.answer("Достижение успешно добавлено!", reply_markup=student_main_menu_markup)

async def student_back_to_main(callback_query: types.CallbackQuery, state: FSMContext):
    await StudentState.main_menu.set()
    await callback_query.message.answer("Выберите действие:", reply_markup=student_main_menu_markup)


async def student_back_to_achievement_choice(callback_query: types.CallbackQuery, state: FSMContext):
    await StudentState.viewing_achievement_details.set()
    await student_choose_achievement(callback_query, state)

async def student_edit_description(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите новое описание достижения:", reply_markup=student_back_to_achievement_details_markup)
    await StudentState.edit_waiting_for_description.set()

async def student_save_edited_description(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']
    new_description = message.text

    update_achievement_description(achievement_id, new_description)
    await message.answer("Описание успешно обновлено.")

    # Вернуться к выбору достижения
    full_name = user_data.get('full_name')
    achievements = get_achievements_by_user(full_name)
    if not achievements:
        await message.answer("У вас пока нет достижений.", reply_markup=student_main_menu_markup)
        return

    response = "Ваши достижения:\n\n"
    for idx, achievement in enumerate(achievements, start=1):
        status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
        response += f"{idx}. {status_emoji} {achievement.description[:50]}...\n"

    await message.answer(response)
    await message.answer("Введите номер достижения для подробного просмотра:", reply_markup=student_back_to_main_markup)

    await StudentState.waiting_for_achievement_choice.set()

async def student_edit_files(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(files=[])  # Очистить список файлов
    await callback_query.message.answer("Отправьте новые файлы для достижения. Когда закончите, нажмите 'Готово'.", reply_markup=student_edit_waiting_files_markup)
    await StudentState.edit_waiting_for_files.set()

async def student_save_edited_files(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']
    files = user_data.get('files', [])

    update_achievement_files(achievement_id, files)
    await callback_query.message.answer("Файлы успешно обновлены.")
    await student_view_achievements(callback_query, state)


async def student_delete_achievement(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']

    delete_achievement(achievement_id)
    await callback_query.message.answer("Достижение успешно удалено.")
    await student_view_achievements(callback_query, state)


def register_student_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(student_view_achievements, text='student_view_achievements',
                                       state=StudentState.main_menu)
    dp.register_callback_query_handler(student_view_achievements, text='student_view_achievements',
                                       state=StudentState.viewing_achievement_details)

    dp.register_message_handler(student_choose_achievement, state=StudentState.waiting_for_achievement_choice)
    dp.register_callback_query_handler(student_add_achievement, text='student_new_achievement', state=StudentState.main_menu)
    dp.register_message_handler(student_save_description, state=StudentState.waiting_for_description)
    dp.register_message_handler(student_upload_files, content_types=['photo', 'document'], state=StudentState.waiting_for_files)
    dp.register_callback_query_handler(student_files_loaded, text='student_files_loaded', state=StudentState.waiting_for_files)
    dp.register_message_handler(student_upload_files, content_types=['photo', 'document'], state=StudentState.edit_waiting_for_files)
    dp.register_callback_query_handler(student_save_edited_files, text='student_edit_files_loaded', state=StudentState.edit_waiting_for_files)

    dp.register_callback_query_handler(student_back_to_main, text='student_back_to_main', state=StudentState.waiting_for_achievement_choice)
    dp.register_callback_query_handler(student_back_to_main, text='student_back_to_main', state=StudentState.waiting_for_description)
    dp.register_callback_query_handler(student_back_to_main, text='student_back_to_main', state=StudentState.waiting_for_files)

    dp.register_callback_query_handler(student_back_to_achievement_choice, text='student_back_to_achievement_choice',
                                       state=StudentState.viewing_achievement_details)
    dp.register_callback_query_handler(student_back_to_achievement_choice, text='student_back_to_achievement_choice',
                                       state=StudentState.edit_waiting_for_description)
    dp.register_callback_query_handler(student_back_to_achievement_choice, text='student_back_to_achievement_choice',
                                       state=StudentState.edit_waiting_for_files)

    dp.register_callback_query_handler(student_edit_description, text='student_edit_description_achievement', state=StudentState.viewing_achievement_details)
    dp.register_message_handler(student_save_edited_description, state=StudentState.edit_waiting_for_description)
    dp.register_callback_query_handler(student_edit_files, text='student_edit_files_achievement', state=StudentState.viewing_achievement_details)
    dp.register_callback_query_handler(student_delete_achievement, text='student_delete_achievement', state=StudentState.viewing_achievement_details)
    dp.register_message_handler(student_upload_files, content_types=['photo', 'document'], state=StudentState.edit_waiting_for_files)
    dp.register_callback_query_handler(student_save_edited_files, text='student_edit_files_loaded', state=StudentState.edit_waiting_for_files)
