from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Auth Menu
auth_menu_markup = InlineKeyboardMarkup(row_width=1)
auth_menu_markup.add(
    InlineKeyboardButton("🔑 Войти", callback_data='log_in'),
    InlineKeyboardButton("👤 Регистрация", callback_data='sign_up')
)

# Back to Auth Menu
back_to_auth_markup = InlineKeyboardMarkup(row_width=1)
back_to_auth_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='back_to_auth')
)

# Admin Main Menu
admin_main_menu_markup = InlineKeyboardMarkup(row_width=1)
admin_main_menu_markup.add(
    InlineKeyboardButton("📊 Достижения", callback_data='admin_view_achievements_menu'),
    InlineKeyboardButton("🔍 Подтверждение достижений", callback_data='admin_approve_achievements_menu')
)

# Admin Back to Main Menu
admin_back_to_main_markup = InlineKeyboardMarkup(row_width=1)
admin_back_to_main_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='admin_back_to_main')
)

# Admin Back to Groups View
admin_back_to_groups_view_markup = InlineKeyboardMarkup(row_width=1)
admin_back_to_groups_view_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='admin_back_to_groups_view')
)

# Admin Back to Students View
admin_back_to_students_view_markup = InlineKeyboardMarkup(row_width=1)
admin_back_to_students_view_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='admin_back_to_students_view')
)

# Admin Achievement Details Menu
admin_achievement_details_markup = InlineKeyboardMarkup(row_width=1)
admin_achievement_details_markup.add(
    InlineKeyboardButton("❌ Удалить", callback_data='admin_delete_achievement'),
    InlineKeyboardButton("✏️ Редактировать описание", callback_data='admin_edit_description_achievement'),
    InlineKeyboardButton("📎 Редактировать файлы", callback_data='admin_edit_files_achievement'),
    InlineKeyboardButton("⬅️ Назад", callback_data='admin_back_to_achievements_view')
)

# Admin Back to Achievement Details Menu
admin_back_to_achievement_details_markup = InlineKeyboardMarkup(row_width=1)
admin_back_to_achievement_details_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='admin_back_to_achievement_details')
)

# Admin Approve Achievement Details Menu
admin_approve_achievement_details_markup = InlineKeyboardMarkup(row_width=1)
admin_approve_achievement_details_markup.add(
    InlineKeyboardButton("🟢 Подтвердить", callback_data='admin_approve_achievement'),
    InlineKeyboardButton("🔴 Отклонить", callback_data='admin_reject_achievement'),
    InlineKeyboardButton("⬅️ Назад", callback_data='admin_back_to_approve_achievements_view')
)

# Student Main Menu
student_main_menu_markup = InlineKeyboardMarkup(row_width=1)
student_main_menu_markup.add(
    InlineKeyboardButton("🥇🥈🥉 Мои достижения", callback_data='student_view_achievements'),
    InlineKeyboardButton("🏆 Загрузить достижение", callback_data='student_new_achievement')
)

# Student Back to Main Menu
student_back_to_main_markup = InlineKeyboardMarkup(row_width=1)
student_back_to_main_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='student_back_to_main')
)

# Student Waiting Files Menu
student_waiting_files_markup = InlineKeyboardMarkup(row_width=1)
student_waiting_files_markup.add(
    InlineKeyboardButton("✅ Готово", callback_data='student_files_loaded'),
    InlineKeyboardButton("⬅️ Назад", callback_data='student_back_to_main')
)

# Student Achievement Details Menu
student_achievement_details_markup = InlineKeyboardMarkup(row_width=1)
student_achievement_details_markup.add(
    InlineKeyboardButton("❌ Удалить", callback_data='student_delete_achievement'),
    InlineKeyboardButton("✏️ Редактировать описание", callback_data='student_edit_description_achievement'),
    InlineKeyboardButton("📎 Редактировать файлы", callback_data='student_edit_files_achievement'),
    InlineKeyboardButton("⬅️ Назад", callback_data='student_view_achievements')
)

# Student Back to Achievement Details Menu
student_back_to_achievement_details_markup = InlineKeyboardMarkup(row_width=1)
student_back_to_achievement_details_markup.add(
    InlineKeyboardButton("⬅️ Назад", callback_data='student_back_to_achievement_choice')
)

# Student Edit Files Loaded Menu
student_edit_waiting_files_markup = InlineKeyboardMarkup(row_width=1)
student_edit_waiting_files_markup.add(
    InlineKeyboardButton("✅ Готово", callback_data='student_edit_files_loaded'),
    InlineKeyboardButton("⬅️ Назад", callback_data='student_back_to_achievement_choice')
)
