from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import (
    get_all_group_numbers, get_students_by_group, get_achievements_by_student,
    get_pending_achievements, delete_achievement, update_achievement_description,
    update_achievement_files, update_achievement_status
)
from keyboards import (
    admin_main_menu_markup, admin_back_to_main_markup, admin_back_to_groups_view_markup,
    admin_back_to_students_view_markup, admin_achievement_details_markup, admin_back_to_achievement_details_markup,
    admin_approve_achievement_details_markup
)

class AdminState(StatesGroup):
    main_menu = State()
    waiting_for_group_choice = State()
    waiting_for_student_choice = State()
    waiting_for_achievement_choice = State()
    viewing_achievement_details = State()
    edit_waiting_for_description = State()
    edit_waiting_for_files = State()
    approve_waiting_for_number = State()
    approve_waiting_for_approvement_choice = State()

async def admin_view_achievements_menu(callback_query: types.CallbackQuery, state: FSMContext):
    groups = get_all_group_numbers()
    if not groups:
        await callback_query.message.answer("Нет доступных групп.", reply_markup=admin_main_menu_markup)
        return

    response = "Группы:\n\n"
    for idx, group in enumerate(groups, start=1):
        response += f"{idx}. {group} \n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер группы:", reply_markup=admin_back_to_main_markup)
    await AdminState.waiting_for_group_choice.set()

async def admin_choose_group(message: types.Message, state: FSMContext):
    groups = get_all_group_numbers()

    try:
        group_idx = int(message.text) - 1
        if group_idx < 0 or group_idx >= len(groups):
            raise ValueError("Invalid index")

        group = groups[group_idx]
        await state.update_data(group=group)
        await AdminState.waiting_for_student_choice.set()

        students = get_students_by_group(group)
        if not students:
            await message.answer("Нет студентов в этой группе.", reply_markup=admin_back_to_groups_view_markup)
            return

        response = f"Студенты группы {group}:\n\n"
        for idx, student in enumerate(students, start=1):
            response += f"{idx}. {student} ( {len(get_achievements_by_student(student))}🏅)\n"

        await message.answer(response)
        await message.answer("Введите номер студента:", reply_markup=admin_back_to_groups_view_markup)

    except (ValueError, IndexError):
        await message.answer("❗️Неверный номер группы. Пожалуйста, попробуйте снова.")
        await display_groups_list(message, state)

async def display_groups_list(message: types.Message, state: FSMContext):
    groups = get_all_group_numbers()
    response = "Группы:\n\n"
    for idx, group in enumerate(groups, start=1):
        response += f"{idx}. {group}\n"

    await message.answer(response)
    await message.answer("Введите номер группы:", reply_markup=admin_back_to_main_markup)
    await AdminState.waiting_for_group_choice.set()

async def admin_choose_student(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    group = user_data.get('group')

    students = get_students_by_group(group)

    try:
        student_idx = int(message.text) - 1
        if student_idx < 0 or student_idx >= len(students):
            raise ValueError("Invalid index")

        student = students[student_idx]
        await state.update_data(student=student)
        await AdminState.waiting_for_achievement_choice.set()

        student_achievements = get_achievements_by_student(student)
        if not student_achievements:
            await message.answer("У студента нет достижений.", reply_markup=admin_back_to_students_view_markup)
            return

        response = f"Достижения студента {student}:\n\n"
        for idx, achievement in enumerate(student_achievements, start=1):
            status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
            description = achievement.description.strip().replace('\n', ' ')
            if len(description) > 27:
                description = description[:27] + '...'
            response += f"{idx}. {status_emoji} {description}\n"

        await message.answer(response)
        await message.answer("Введите номер достижения:", reply_markup=admin_back_to_students_view_markup)

    except (ValueError, IndexError):
        await message.answer("❗️Неверный номер студента. Пожалуйста, попробуйте снова.")
        students = get_students_by_group(group)
        response = f"Студенты группы {group}:\n\n"
        for idx, student in enumerate(students, start=1):
            response += f"{idx}. {student} ( {len(get_achievements_by_student(student))}🏅)\n"
        await message.answer(response)
        await message.answer("Введите номер студента:", reply_markup=admin_back_to_groups_view_markup)
        await AdminState.waiting_for_student_choice.set()

async def display_achievements_list(message: types.Message, state: FSMContext, achievements):
    response = f"Достижения студента {student}:\n\n"
    for idx, achievement in enumerate(student_achievements, start=1):
        status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
        description = achievement.description.strip().replace('\n', ' ')
        if len(description) > 27:
            description = description[:27] + '...'
        response += f"{idx}. {status_emoji} {description}\n"

    await message.answer(response)
    await message.answer("Введите номер достижения для подробного просмотра:", reply_markup=admin_back_to_students_view_markup)

async def admin_choose_achievement(message_or_callback: types.Message or types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    student = user_data.get('student')
    achievements = get_achievements_by_student(student)

    if isinstance(message_or_callback, types.Message):
        message = message_or_callback

        try:
            achievement_idx = int(message.text) - 1
            if achievement_idx < 0 or achievement_idx >= len(achievements):
                raise ValueError("Invalid index")

            achievement = achievements[achievement_idx]
            await state.update_data(current_achievement=achievement.to_dict())
            await AdminState.viewing_achievement_details.set()

            # Отправка файлов
            for file_type, file_id in achievement.files:
                if file_type == 'photo':
                    await message.answer_photo(file_id)
                elif file_type == 'document':
                    await message.answer_document(file_id)

            status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
            response = f"{achievement.description}\n\n{achievement.status} {status_emoji}\n"
            await message.answer(response, reply_markup=admin_achievement_details_markup)

        except (ValueError, IndexError):
            await message.answer("❗️Неверный номер достижения. Пожалуйста, попробуйте снова.")
            await display_achievements_list(message, state, achievements)

    elif isinstance(message_or_callback, types.CallbackQuery):
        callback_query = message_or_callback

        if not achievements:
            await callback_query.message.answer("У студента пока нет достижений.", reply_markup=admin_back_to_students_view_markup)
            return

        await display_achievements_list(callback_query.message, state, achievements)
        await AdminState.waiting_for_achievement_choice.set()

async def admin_back_to_main(callback_query: types.CallbackQuery, state: FSMContext):
    await AdminState.main_menu.set()
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=admin_main_menu_markup)

async def admin_back_to_groups_view(callback_query: types.CallbackQuery, state: FSMContext):
    await display_groups_list(callback_query.message, state)

async def admin_back_to_students_view(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    group = user_data.get('group')
    students = get_students_by_group(group)

    response = f"Студенты группы {group}:\n\n"
    for idx, student in enumerate(students, start=1):
        response += f"{idx}. {student} ( {len(get_achievements_by_student(student))}🏅)\n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер студента:", reply_markup=admin_back_to_groups_view_markup)
    await AdminState.waiting_for_student_choice.set()

async def admin_back_to_achievements_view(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    student = user_data.get('student')
    student_achievements = get_achievements_by_student(student)

    response = f"Достижения студента {student}:\n\n"
    for idx, achievement in enumerate(student_achievements, start=1):
        status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
        description = achievement.description.strip().replace('\n', ' ')
        if len(description) > 27:
            description = description[:27] + '...'
        response += f"{idx}. {status_emoji} {description}\n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер достижения:", reply_markup=admin_back_to_students_view_markup)
    await AdminState.waiting_for_achievement_choice.set()

async def admin_back_to_approve_achievements_view(callback_query: types.CallbackQuery, state: FSMContext):
    pending_achievements = get_pending_achievements()
    if not pending_achievements:
        await callback_query.message.answer("Нет достижений на рассмотрении.", reply_markup=admin_main_menu_markup)
        return

    response = "Достижения на рассмотрении:\n\n"
    for idx, ach in enumerate(pending_achievements, start=1):
        description = ach.description.strip().replace('\n', ' ')
        if len(description) > 27:
            description = description[:27] + '...'
        response += f"{idx}. {description}\n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер достижения для подробного просмотра:", reply_markup=admin_back_to_main_markup)
    await AdminState.approve_waiting_for_number.set()

async def admin_edit_description(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите новое описание достижения:", reply_markup=admin_back_to_achievement_details_markup)
    await AdminState.edit_waiting_for_description.set()

async def admin_save_edited_description(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']
    new_description = message.text

    update_achievement_description(achievement_id, new_description)
    await message.answer("Описание успешно обновлено.")

    await admin_choose_achievement(message, state)

async def admin_edit_files(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(files=[])  # Очистить список файлов
    await callback_query.message.answer("Отправьте новые файлы для достижения. Когда закончите, нажмите 'Готово'.", reply_markup=admin_back_to_achievement_details_markup)
    await AdminState.edit_waiting_for_files.set()

async def admin_upload_files(message: types.Message, state: FSMContext):
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

async def admin_save_edited_files(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']
    files = user_data.get('files', [])

    update_achievement_files(achievement_id, files)
    await callback_query.message.answer("Файлы успешно обновлены.")
    await admin_choose_achievement(callback_query.message, state)


async def admin_delete_achievement(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']

    # Удалить достижение
    delete_achievement(achievement_id)
    await callback_query.message.answer("Достижение успешно удалено.")

    # Обновить список достижений студента
    student = user_data.get('student')
    student_achievements = get_achievements_by_student(student)

    # Проверить, если у студента остались достижения
    if not student_achievements:
        await callback_query.message.answer("У студента нет достижений.",
                                            reply_markup=admin_back_to_students_view_markup)
        await AdminState.waiting_for_achievement_choice.set()
        return

    # Отобразить обновленный список достижений
    response = f"Достижения студента {student}:\n\n"
    for idx, achievement in enumerate(student_achievements, start=1):
        status_emoji = '🟢' if achievement.status == 'Подтверждено' else '🟡' if achievement.status == 'На рассмотрении' else '🔴'
        description = achievement.description.strip().replace('\n', ' ')
        if len(description) > 27:
            description = description[:27] + '...'
        response += f"{idx}. {status_emoji} {description}\n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер достижения для подробного просмотра:",
                                        reply_markup=admin_back_to_students_view_markup)
    await AdminState.waiting_for_achievement_choice.set()


async def admin_approve_achievements_menu(callback_query: types.CallbackQuery, state: FSMContext):
    pending_achievements = get_pending_achievements()
    if not pending_achievements:
        await callback_query.message.answer("Нет достижений на рассмотрении.", reply_markup=admin_main_menu_markup)
        return

    response = "Достижения на рассмотрении:\n\n"
    for idx, ach in enumerate(pending_achievements, start=1):
        description = ach.description.strip().replace('\n', ' ')
        if len(description) > 27:
            description = description[:27] + '...'
        response += f"{idx}. {description}\n"

    await callback_query.message.answer(response)
    await callback_query.message.answer("Введите номер достижения для подробного просмотра:", reply_markup=admin_back_to_main_markup)
    await AdminState.approve_waiting_for_number.set()

async def admin_choose_pending_achievement(message: types.Message, state: FSMContext):
    pending_achievements = get_pending_achievements()

    try:
        achievement_idx = int(message.text) - 1
        if achievement_idx >= len(pending_achievements):
            raise ValueError("Invalid index")

        achievement = pending_achievements[achievement_idx]
        await state.update_data(current_achievement=achievement.to_dict())
        await AdminState.approve_waiting_for_approvement_choice.set()

        # Отправка файлов
        for file_type, file_id in achievement.files:
            if file_type == 'photo':
                await message.answer_photo(file_id)
            elif file_type == 'document':
                await message.answer_document(file_id)

        response = f"Группа: {achievement.student_group}\n\n{achievement.student_name}\n\n{achievement.description}\n"
        await message.answer(response, reply_markup=admin_approve_achievement_details_markup)

    except (ValueError, IndexError):
        await message.answer("❗️Неверный номер достижения. Пожалуйста, попробуйте снова.")
        await display_pending_achievements_list(message)


async def display_pending_achievements_list(message: types.Message):
    pending_achievements = get_pending_achievements()
    response = "Достижения на рассмотрении:\n\n"
    for idx, ach in enumerate(pending_achievements, start=1):
        description = ach.description.strip().replace('\n', ' ')
        if len(description) > 27:
            description = description[:27] + '...'
        response += f"{idx}. {description}\n"

    await message.answer(response)
    await message.answer("Введите номер достижения для подробного просмотра:", reply_markup=admin_back_to_main_markup)
    await AdminState.approve_waiting_for_number.set()


async def admin_approve_achievement(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']

    update_achievement_status(achievement_id, 'Подтверждено')
    await callback_query.message.answer("Достижение подтверждено.")
    await display_pending_achievements_list(callback_query.message)

async def admin_reject_achievement(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    achievement_id = user_data.get('current_achievement')['id']

    update_achievement_status(achievement_id, 'Отклонено')
    await callback_query.message.answer("Достижение отклонено.")
    await display_pending_achievements_list(callback_query.message)


def register_admin_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(admin_view_achievements_menu, text='admin_view_achievements_menu', state=AdminState.main_menu)
    dp.register_callback_query_handler(admin_approve_achievements_menu, text='admin_approve_achievements_menu', state=AdminState.main_menu)

    dp.register_message_handler(admin_choose_group, state=AdminState.waiting_for_group_choice)
    dp.register_message_handler(admin_choose_student, state=AdminState.waiting_for_student_choice)
    dp.register_message_handler(admin_choose_achievement, state=AdminState.waiting_for_achievement_choice)
    dp.register_message_handler(admin_choose_pending_achievement, state=AdminState.approve_waiting_for_number)

    dp.register_callback_query_handler(admin_edit_description, text='admin_edit_description_achievement', state=AdminState.viewing_achievement_details)
    dp.register_message_handler(admin_save_edited_description, state=AdminState.edit_waiting_for_description)

    dp.register_callback_query_handler(admin_edit_files, text='admin_edit_files_achievement', state=AdminState.viewing_achievement_details)
    dp.register_message_handler(admin_upload_files, content_types=['photo', 'document'], state=AdminState.edit_waiting_for_files)
    dp.register_callback_query_handler(admin_save_edited_files, text='admin_save_edited_files', state=AdminState.edit_waiting_for_files)

    dp.register_callback_query_handler(admin_delete_achievement, text='admin_delete_achievement', state=AdminState.viewing_achievement_details)

    dp.register_callback_query_handler(admin_approve_achievement, text='admin_approve_achievement', state=AdminState.approve_waiting_for_approvement_choice)
    dp.register_callback_query_handler(admin_reject_achievement, text='admin_reject_achievement', state=AdminState.approve_waiting_for_approvement_choice)
    dp.register_callback_query_handler(admin_back_to_main, text='admin_back_to_main', state='*')
    dp.register_callback_query_handler(display_groups_list, text='admin_back_to_main', state=AdminState.waiting_for_group_choice)
    dp.register_callback_query_handler(admin_back_to_groups_view, text='admin_back_to_groups_view',
                                       state=AdminState.waiting_for_student_choice)
    dp.register_callback_query_handler(admin_back_to_students_view, text='admin_back_to_students_view',
                                       state=AdminState.waiting_for_achievement_choice)
    dp.register_callback_query_handler(admin_back_to_achievements_view, text='admin_back_to_achievements_view',
                                       state=AdminState.viewing_achievement_details)
    dp.register_callback_query_handler(admin_back_to_students_view, text='admin_back_to_students_view',
                                       state=AdminState.waiting_for_achievement_choice)
    dp.register_callback_query_handler(admin_back_to_approve_achievements_view,
                                       text='admin_back_to_approve_achievements_view',
                                       state=AdminState.approve_waiting_for_approvement_choice)