import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, date
import os
import xlsxwriter

class RestaurantSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления рестораном")
        self.root.geometry("350x350")  # Увеличил размеры окна

        # Имя файла базы данных
        self.db_file = "restaurant_menu.db"

        # Создание базы данных, если файл не существует
        self.create_database()

        # Подключение к базе данных
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        # Включаем поддержку внешних ключей
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # Показать начальное окно
        self.login_window()

    # Создание базы данных
    def create_database(self):
        if not os.path.exists(self.db_file):
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Таблицы
            cursor.execute('''CREATE TABLE Категория (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Название TEXT NOT NULL UNIQUE
            )''')
            cursor.execute('''CREATE TABLE Ингредиент (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Название TEXT NOT NULL,
                Количество INTEGER NOT NULL,
                Единица_измерения TEXT NOT NULL
            )''')
            cursor.execute('''CREATE TABLE Пользователь (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Имя_фамилия TEXT NOT NULL,
                Роль TEXT NOT NULL,
                Пароль TEXT NOT NULL,
                Email TEXT NOT NULL UNIQUE,
                Дата_регистрации DATETIME NOT NULL
            )''')
            cursor.execute('''CREATE TABLE Блюдо (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Название TEXT NOT NULL,
                Цена REAL NOT NULL,
                Категория_id INTEGER NOT NULL,
                FOREIGN KEY (Категория_id) REFERENCES Категория(id)
            )''')
            cursor.execute('''CREATE TABLE Заказ (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Пользователь_id INTEGER NOT NULL,
                Дата_заказа DATE NOT NULL,
                Статус TEXT NOT NULL CHECK (Статус IN ('Новый', 'В процессе', 'Завершен', 'Отменен')),
                FOREIGN KEY (Пользователь_id) REFERENCES Пользователь(id) ON DELETE CASCADE
            )''')
            cursor.execute('''CREATE TABLE Блюдо_Ингредиент (
                Блюдо_id INTEGER,
                Ингредиент_id INTEGER,
                Количество DECIMAL(10, 2) NOT NULL CHECK (Количество >= 0),
                PRIMARY KEY (Блюдо_id, Ингредиент_id),
                FOREIGN KEY (Блюдо_id) REFERENCES Блюдо(id) ON DELETE CASCADE,
                FOREIGN KEY (Ингредиент_id) REFERENCES Ингредиент(id)
            )''')
            cursor.execute('''CREATE TABLE Блюдо_Заказ (
                Блюдо_id INTEGER,
                Заказ_id INTEGER,
                Количество INTEGER NOT NULL CHECK (Количество > 0),
                PRIMARY KEY (Блюдо_id, Заказ_id),
                FOREIGN KEY (Блюдо_id) REFERENCES Блюдо(id),
                FOREIGN KEY (Заказ_id) REFERENCES Заказ(id)
            )''')
            cursor.execute('''CREATE TABLE Отчет (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Дата_отчета DATETIME NOT NULL,
                Пользователь_id INTEGER,
                Общий_доход DECIMAL(10, 2) NOT NULL,
                Количество_заказов INTEGER NOT NULL,
                Популярные_блюда TEXT,
                FOREIGN KEY (Пользователь_id) REFERENCES Пользователь(id) ON DELETE CASCADE
            )''')
            # Заполнение таблиц
            cursor.executemany('INSERT INTO Категория (Название) VALUES (?)', [
                ('Салаты',),
                ('Закуски',),
                ('Десерты',),
                ('Напитки',),
                ('Основные блюда',),
                ('Супы',)
            ])
            cursor.executemany('INSERT INTO Ингредиент (Название, Количество, Единица_измерения) VALUES (?, ?, ?)', [
                ('Сахар', 10, 'кг'),
                ('Мука', 25, 'кг'),
                ('Молоко', 30, 'л'),
                ('Масло сливочное', 20, 'кг'),
                ('Яйца', 500, 'шт'),
                ('Соль', 15, 'кг')
            ])
            cursor.executemany(
                'INSERT INTO Пользователь (Имя_фамилия, Роль, Пароль, Email, Дата_регистрации) VALUES (?, ?, ?, ?, ?)',
                [
                    ('Иван Иванов', 'Администратор', 'admin123', 'admin@example.com', '2023-01-01'),
                    ('Петр Петров', 'Пользователь', 'user123', 'petr@example.com', '2023-02-01'),
                    ('Анна Смирнова', 'Пользователь', 'user456', 'anna@example.com', '2023-03-01'),
                    ('Мария Иванова', 'Пользователь', 'user789', 'maria@example.com', '2023-04-01'),
                    ('Олег Кузнецов', 'Пользователь', 'user147', 'oleg@example.com', '2023-05-01'),
                    ('Елена Сидорова', 'Пользователь', 'user258', 'elena@example.com', '2023-06-01')
                ])
            cursor.executemany('INSERT INTO Блюдо (Название, Цена, Категория_id) VALUES (?, ?, ?)', [
                ('Цезарь', 300.0, 1),
                ('Оливье', 250.0, 1),
                ('Чизкейк', 400.0, 3),
                ('Лимонад', 150.0, 4),
                ('Стейк', 1200.0, 5),
                ('Борщ', 350.0, 6)
            ])
            cursor.executemany('INSERT INTO Заказ (Пользователь_id, Дата_заказа, Статус) VALUES (?, ?, ?)', [
                (2, '2023-06-10', 'Завершен'),
                (3, '2023-06-11', 'Новый'),
                (4, '2023-06-12', 'В процессе'),
                (5, '2023-06-13', 'Отменен'),
                (6, '2023-06-14', 'Завершен'),
                (2, '2023-06-15', 'Завершен')
            ])
            cursor.executemany('INSERT INTO Блюдо_Ингредиент (Блюдо_id, Ингредиент_id, Количество) VALUES (?, ?, ?)', [
                (1, 1, 0.2),  # Салат "Цезарь" и сахар
                (1, 2, 0.1),  # Салат "Цезарь" и мука
                (3, 5, 3.0),  # Чизкейк и яйца
                (3, 4, 0.2),  # Чизкейк и масло сливочное
                (5, 6, 0.05),  # Стейк и соль
                (6, 1, 0.5)  # Борщ и сахар
            ])
            cursor.executemany('INSERT INTO Блюдо_Заказ (Блюдо_id, Заказ_id, Количество) VALUES (?, ?, ?)', [
                (1, 1, 2),  # "Цезарь" в заказе 1
                (2, 1, 1),  # "Оливье" в заказе 1
                (3, 2, 1),  # "Чизкейк" в заказе 2
                (4, 3, 3),  # "Лимонад" в заказе 3
                (5, 4, 2),  # "Стейк" в заказе 4
                (6, 5, 1)  # "Борщ" в заказе 5
            ])
            cursor.executemany(
                'INSERT INTO Отчет (Дата_отчета, Пользователь_id, Общий_доход, Количество_заказов, Популярные_блюда) VALUES (?, ?, ?, ?, ?)',
                [
                    ('2023-06-15', 1, 3000.0, 3, 'Цезарь, Оливье'),
                    ('2023-06-14', 1, 1500.0, 2, 'Чизкейк, Лимонад'),
                    ('2023-06-13', 1, 500.0, 1, 'Стейк'),
                    ('2023-06-12', 1, 250.0, 1, 'Оливье'),
                    ('2023-06-11', 1, 0.0, 1, 'Нет данных'),
                    ('2023-06-10', 1, 400.0, 1, 'Борщ')
                ])

            conn.commit()
            conn.close()

    # Очистка текущего окна
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Универсальная функция создания поля ввода
    def create_input_field(self, label_text, row, show=None):
        tk.Label(self.root, text=label_text).grid(row=row, column=0, pady=5, sticky="e")
        entry = tk.Entry(self.root, show=show)
        entry.grid(row=row, column=1, pady=5, sticky="w")
        return entry

    # Универсальная функция создания кнопки
    def create_button(self, text, command, row, column=1):
        tk.Button(self.root, text=text, command=command).grid(row=row, column=column, pady=5, sticky="ew")

    # Окно входа
    def login_window(self):
        self.clear_window()

        tk.Label(self.root, text="Вход").grid(row=0, column=0, columnspan=2, pady=10)

        self.email_entry = self.create_input_field("Email", 1)
        self.password_entry = self.create_input_field("Пароль", 2, show="*")

        self.create_button("Войти", self.login, 3)
        self.create_button("Регистрация", self.register_window, 4)

    # Окно регистрации
    def register_window(self):
        self.clear_window()

        tk.Label(self.root, text="Регистрация").grid(row=0, column=0, columnspan=2, pady=10)

        self.name_entry = self.create_input_field("Имя и фамилия", 1)
        self.reg_email_entry = self.create_input_field("Email", 2)
        self.reg_password_entry = self.create_input_field("Пароль", 3, show="*")

        self.create_button("Зарегистрироваться", self.register_user, 4)
        self.create_button("Назад", self.login_window, 5)

    # Проверка на пустые поля
    def validate_fields(self, *fields):
        if any(not field for field in fields):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return False
        return True

    # Обработка входа
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not self.validate_fields(email, password):
            return

        self.cursor.execute("SELECT id, Имя_фамилия, Роль FROM Пользователь WHERE Email=? AND Пароль=?", (email, password))
        user = self.cursor.fetchone()

        if user:
            self.user_id, self.user_name, self.role = user
            if self.role == "Администратор":
                self.admin_menu_window()
            else:
                self.user_menu_window()
        else:
            messagebox.showerror("Ошибка", "Неверный Email или пароль!")

    # Обработка регистрации
    def register_user(self):
        name = self.name_entry.get()
        email = self.reg_email_entry.get()
        password = self.reg_password_entry.get()

        if not self.validate_fields(name, email, password):
            return

        try:
            self.cursor.execute("""INSERT INTO Пользователь 
                (Имя_фамилия, Роль, Пароль, Email, Дата_регистрации) 
                VALUES (?, ?, ?, ?, ?)""",
                                (name, "Пользователь", password, email, datetime.now()))
            self.conn.commit()
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.login_window()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким Email уже существует!")

    # Меню администратора
    def admin_menu_window(self):
        self.clear_window()

        tk.Label(self.root, text=f"Добро пожаловать, {self.user_name}!").grid(row=0, column=0, columnspan=2, pady=10)

        options = [("Просмотреть меню", self.view_menu),
                   ("Добавить блюдо", self.add_dish),
                   ("Удалить блюдо", self.delete_dish),
                   ("Редактировать блюдо", self.edit_dish),
                   ("Удалить пользователя", self.delete_user),
                   ("Просмотреть отчеты", self.view_reports),
                   ("Экспорт меню в Excel", self.export_menu_to_excel),
                   ("Выход", self.exit_program)]

        for i, (text, command) in enumerate(options, start=1):
            self.create_button(text, command, i)

    # Меню пользователя
    def user_menu_window(self):
        self.clear_window()

        tk.Label(self.root, text=f"Добро пожаловать, {self.user_name}!").grid(row=0, column=0, columnspan=2, pady=10)

        options = [("Просмотреть меню", self.view_menu),
                   ("Мои заказы", self.view_orders),
                   ("Создать заказ", self.create_order),
                   ("Выход", self.exit_program)]

        for i, (text, command) in enumerate(options, start=1):
            self.create_button(text, command, i)

    def edit_ingredients(self):
        self.clear_window()
        tk.Label(self.root, text="Редактирование ингредиентов").grid(row=0, column=0, columnspan=2, pady=10)

        # Получение списка блюд
        self.cursor.execute("SELECT id, Название FROM Блюдо")
        dishes = self.cursor.fetchall()

        if not dishes:
            tk.Label(self.root, text="Нет доступных блюд").grid(row=1, column=0, columnspan=2)
            self.create_button("Назад", self.admin_menu_window, 2)
            return

        # Отображение списка блюд
        for i, (dish_id, dish_name) in enumerate(dishes, start=1):
            tk.Label(self.root, text=dish_name).grid(row=i, column=0, sticky="w")
            self.create_button("Редактировать", lambda id=dish_id: self.open_ingredient_editor(id), i, column=1)

        # Кнопка назад
        self.create_button("Назад", self.admin_menu_window, len(dishes) + 1)

    def open_ingredient_editor(self, dish_id):
        self.clear_window()

        # Получаем ингредиенты блюда
        self.cursor.execute("""
            SELECT i.id, i.Название, bi.Количество
            FROM Блюдо_Ингредиент bi
            JOIN Ингредиент i ON bi.Ингредиент_id = i.id
            WHERE bi.Блюдо_id = ?
        """, (dish_id,))
        ingredients = self.cursor.fetchall()

        if not ingredients:
            tk.Label(self.root, text="У блюда нет ингредиентов").grid(row=1, column=0, columnspan=2)

        ingredient_entries = {}
        for i, (ing_id, ing_name, quantity) in enumerate(ingredients, start=1):
            tk.Label(self.root, text=f"{ing_name}").grid(row=i, column=0)
            entry = tk.Entry(self.root)
            entry.insert(0, quantity)
            entry.grid(row=i, column=1)
            ingredient_entries[ing_id] = entry

        def save_ingredients():
            for ing_id, entry in ingredient_entries.items():
                new_quantity = entry.get()
                if not new_quantity.isdigit() or float(new_quantity) <= 0:
                    messagebox.showerror("Ошибка", "Введите корректное количество")
                    return

                self.cursor.execute("""
                    UPDATE Блюдо_Ингредиент SET Количество = ?
                    WHERE Блюдо_id = ? AND Ингредиент_id = ?
                """, (float(new_quantity), dish_id, ing_id))

            self.conn.commit()
            messagebox.showinfo("Успех", "Ингредиенты обновлены!")
            self.admin_menu_window()

        self.create_button("Сохранить", save_ingredients, len(ingredients) + 1)
        self.create_button("Назад", self.edit_ingredients, len(ingredients) + 2)

    # Добавление блюда
    def add_dish(self):
        self.clear_window()

        tk.Label(self.root, text="Добавить блюдо").grid(row=0, column=0, columnspan=2, pady=10)

        # Получаем список категорий
        self.cursor.execute("SELECT id, Название FROM Категория")
        categories = self.cursor.fetchall()

        if not categories:
            messagebox.showerror("Ошибка", "Нет доступных категорий для добавления блюда.")
            self.admin_menu_window()  # Возвращаем в меню администратора
            return

        # Создаем список названий категорий и словарь для соответствия
        category_names = [cat[1] for cat in categories]
        category_id_map = {cat[1]: cat[0] for cat in categories}

        # Поля для ввода данных о блюде
        name_entry = self.create_input_field("Название блюда:", 1)
        price_entry = self.create_input_field("Цена блюда:", 2)

        # Выпадающий список для выбора категории
        category_var = tk.StringVar(self.root)
        category_var.set(category_names[0])  # Значение по умолчанию

        tk.Label(self.root, text="Категория блюда:").grid(row=3, column=0, pady=5, sticky="e")
        category_menu = tk.OptionMenu(self.root, category_var, *category_names)
        category_menu.grid(row=3, column=1, pady=5, sticky="w")

        # Функция для добавления блюда в базу данных
        def submit_dish():
            name = name_entry.get()
            price = price_entry.get()
            category_name = category_var.get()

            # Проверка на пустые поля
            if not self.validate_fields(name, price, category_name):
                return

            # Получаем ID категории
            category_id = category_id_map.get(category_name)
            if not category_id:
                messagebox.showerror("Ошибка", "Категория не найдена!")
                return

            try:
                # Добавление блюда в базу данных
                self.cursor.execute("INSERT INTO Блюдо (Название, Цена, Категория_id) VALUES (?, ?, ?)",
                                    (name, float(price), category_id))
                self.conn.commit()
                messagebox.showinfo("Успех", "Блюдо успешно добавлено!")
                self.admin_menu_window()  # Возвращаем в меню администратора после добавления блюда

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении блюда: {e}")

        # Кнопка для добавления блюда
        self.create_button("Добавить", submit_dish, 4)

        # Кнопка "Назад" для возврата в меню администратора
        self.create_button("Назад", self.admin_menu_window, 5)

    # Удаление блюда
    def delete_dish(self):
        self.clear_window()

        tk.Label(self.root, text="Удаление блюда").grid(row=0, column=0, columnspan=2, pady=10)

        # Получаем список всех блюд
        self.cursor.execute("SELECT id, Название, Цена FROM Блюдо")
        dishes = self.cursor.fetchall()

        if not dishes:
            tk.Label(self.root, text="Нет доступных блюд для удаления").grid(row=1, column=0, columnspan=2)
            self.create_button("Назад", self.admin_menu_window, 2)
            return

        # Отображаем список блюд
        for i, (dish_id, dish_name, dish_price) in enumerate(dishes, start=1):
            tk.Label(self.root, text=f"{dish_name} - {dish_price:.2f} руб.").grid(row=i, column=0, sticky="w")
            self.create_button("Удалить", lambda id=dish_id: self.confirm_delete_dish(id), i, column=1)

        # Кнопка назад
        self.create_button("Назад", self.admin_menu_window, len(dishes) + 1)

    def confirm_delete_dish(self, dish_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это блюдо?"):
            try:
                # Удаляем все связанные записи
                self.cursor.execute("DELETE FROM Блюдо_Ингредиент WHERE Блюдо_id = ?", (dish_id,))
                self.cursor.execute("DELETE FROM Блюдо_Заказ WHERE Блюдо_id = ?", (dish_id,))

                # Удаляем блюдо
                self.cursor.execute("DELETE FROM Блюдо WHERE id = ?", (dish_id,))
                self.conn.commit()

                messagebox.showinfo("Успех", "Блюдо успешно удалено!")
                self.delete_dish()  # Обновляем список после удаления
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении блюда: {e}")

    # Редактирование блюда
    def edit_dish(self):
        self.clear_window()

        tk.Label(self.root, text="Редактирование блюда").grid(row=0, column=0, columnspan=2, pady=10)

        # Получаем список всех блюд из базы данных
        self.cursor.execute("SELECT id, Название, Цена FROM Блюдо")
        dishes = self.cursor.fetchall()

        if not dishes:
            tk.Label(self.root, text="Нет доступных блюд для редактирования").grid(row=1, column=0, columnspan=2)
            self.create_button("Назад", self.admin_menu_window, 2)
            return

        # Отображаем список блюд
        for i, (dish_id, dish_name, dish_price) in enumerate(dishes, start=1):
            tk.Label(self.root, text=f"{dish_name} - {dish_price:.2f} руб.").grid(row=i, column=0, sticky="w")
            self.create_button("Редактировать", lambda id=dish_id: self.open_edit_dish_window(id), i, column=1)

        # Кнопка назад
        self.create_button("Назад", self.admin_menu_window, len(dishes) + 1)

    def open_edit_dish_window(self, dish_id):
        self.clear_window()

        # Получаем данные о блюде
        self.cursor.execute("SELECT Название, Цена, Категория_id FROM Блюдо WHERE id=?", (dish_id,))
        dish_data = self.cursor.fetchone()

        if not dish_data:
            messagebox.showerror("Ошибка", "Блюдо не найдено!")
            self.edit_dish()
            return

        dish_name, dish_price, dish_category_id = dish_data

        # Получаем список категорий
        self.cursor.execute("SELECT id, Название FROM Категория")
        categories = self.cursor.fetchall()

        if not categories:
            messagebox.showerror("Ошибка", "Нет доступных категорий для редактирования блюда.")
            self.edit_dish()
            return

        category_names = [cat[1] for cat in categories]
        category_id_map = {cat[0]: cat[1] for cat in categories}

        # Проверяем, существует ли категория для текущего блюда
        if dish_category_id not in category_id_map:
            current_category = "Неизвестно"
        else:
            current_category = category_id_map[dish_category_id]

        tk.Label(self.root, text="Редактирование блюда").grid(row=0, column=0, columnspan=2, pady=10)

        # Поля для редактирования
        name_entry = self.create_input_field("Название блюда:", 1)
        name_entry.insert(0, dish_name)

        price_entry = self.create_input_field("Цена блюда:", 2)
        price_entry.insert(0, str(dish_price))

        # Выпадающий список для выбора категории
        category_var = tk.StringVar(self.root)
        category_var.set(current_category if current_category != "Неизвестно" else category_names[0])

        tk.Label(self.root, text="Категория блюда:").grid(row=3, column=0, pady=5, sticky="e")
        category_menu = tk.OptionMenu(self.root, category_var, *category_names)
        category_menu.grid(row=3, column=1, pady=5, sticky="w")

        # Функция для сохранения изменений
        def save_changes():
            name = name_entry.get()
            price = price_entry.get()
            category_name = category_var.get()

            # Проверка на пустые поля
            if not self.validate_fields(name, price, category_name):
                return

            # Получаем ID категории
            category_id = next((id for id, name in category_id_map.items() if name == category_name), None)
            if not category_id:
                messagebox.showerror("Ошибка", "Категория не найдена!")
                return

            try:
                # Обновление данных блюда в базе данных
                self.cursor.execute("""
                    UPDATE Блюдо 
                    SET Название = ?, Цена = ?, Категория_id = ? 
                    WHERE id = ?
                """, (name, float(price), category_id, dish_id))
                self.conn.commit()
                messagebox.showinfo("Успех", "Данные блюда успешно обновлены!")
                self.edit_dish()

            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении данных блюда: {e}")

        # Кнопка для сохранения изменений
        self.create_button("Сохранить изменения", save_changes, 4)

        # Кнопка "Назад"
        self.create_button("Назад", self.edit_dish, 5)

    def save_dish_changes(self, dish_id, new_name, new_price, new_category, category_id_map):
        # Проверка на пустые поля
        if not self.validate_fields(new_name, new_price, new_category):
            return

        # Получаем ID категории
        category_id = category_id_map.get(new_category)
        if not category_id:
            messagebox.showerror("Ошибка", "Категория не найдена!")
            return

        try:
            # Обновление данных в базе
            self.cursor.execute("""
                UPDATE Блюдо 
                SET Название = ?, Цена = ?, Категория_id = ?
                WHERE id = ?
            """, (new_name, float(new_price), category_id, dish_id))
            self.conn.commit()
            messagebox.showinfo("Успех", "Данные блюда успешно обновлены!")
            self.edit_dish()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных блюда: {e}")

    # Удаление пользователя
    def delete_user(self):
        self.clear_window()

        tk.Label(self.root, text="Удаление пользователя").grid(row=0, column=0, columnspan=2, pady=10)

        # Получаем список всех пользователей, кроме текущего администратора
        self.cursor.execute("SELECT id, Имя_фамилия, Email FROM Пользователь WHERE id != ?", (self.user_id,))
        users = self.cursor.fetchall()

        if not users:
            tk.Label(self.root, text="Нет пользователей для удаления").grid(row=1, column=0, columnspan=2)
            self.create_button("Назад", self.admin_menu_window, 2)
            return

        # Отображаем список пользователей
        for i, (user_id, user_name, user_email) in enumerate(users, start=1):
            tk.Label(self.root, text=f"{user_name} ({user_email})").grid(row=i, column=0, sticky="w")
            self.create_button("Удалить", lambda id=user_id: self.confirm_delete_user(id), i, column=1)

        # Кнопка назад
        self.create_button("Назад", self.admin_menu_window, len(users) + 1)

    def confirm_delete_user(self, user_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого пользователя?"):
            try:
                # Проверка связанных данных
                self.cursor.execute("SELECT id FROM Заказ WHERE Пользователь_id = ?", (user_id,))
                related_orders = self.cursor.fetchall()

                if related_orders:
                    # Удаляем все связанные заказы и их записи
                    for order_id in related_orders:
                        self.cursor.execute("DELETE FROM Блюдо_Заказ WHERE Заказ_id = ?", (order_id[0],))
                    self.cursor.execute("DELETE FROM Заказ WHERE Пользователь_id = ?", (user_id,))

                # Удаление отчета, связанного с пользователем
                self.cursor.execute("DELETE FROM Отчет WHERE Пользователь_id = ?", (user_id,))

                # Удаление пользователя
                self.cursor.execute("DELETE FROM Пользователь WHERE id = ?", (user_id,))
                self.conn.commit()

                messagebox.showinfo("Успех", "Пользователь успешно удален!")
                self.delete_user()  # Обновляем список пользователей
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении пользователя: {e}")

    # Просмотр отчетов
    def view_reports(self):
        self.clear_window()

        tk.Label(self.root, text="Отчеты о продажах").grid(row=0, column=0, columnspan=2, pady=10)

        try:
            # Запрос для получения общего дохода и количества заказов
            self.cursor.execute('''
                SELECT 
                    IFNULL(SUM(bz.Количество * b.Цена), 0) AS Общий_доход,
                    COUNT(DISTINCT z.id) AS Количество_заказов
                FROM Заказ z
                LEFT JOIN Блюдо_Заказ bz ON z.id = bz.Заказ_id
                LEFT JOIN Блюдо b ON bz.Блюдо_id = b.id
                WHERE z.Статус = 'Завершен'
            ''')
            report_data = self.cursor.fetchone()
            общий_доход, количество_заказов = report_data or (0, 0)

            # Запрос для получения популярных блюд
            self.cursor.execute('''
                SELECT 
                    b.Название, SUM(bz.Количество) AS Количество
                FROM Блюдо b
                JOIN Блюдо_Заказ bz ON b.id = bz.Блюдо_id
                JOIN Заказ z ON z.id = bz.Заказ_id
                WHERE z.Статус = 'Завершен'
                GROUP BY b.id
                ORDER BY Количество DESC
                LIMIT 5
            ''')
            popular_dishes = self.cursor.fetchall()
            популярные_блюда = ", ".join(
                [f"{name} ({quantity} шт.)" for name, quantity in popular_dishes]) or "Нет данных"

            # Отображение отчета
            tk.Label(self.root, text=f"Общий доход: {общий_доход:.2f} руб.").grid(row=1, column=0, columnspan=2,
                                                                                  sticky="w")
            tk.Label(self.root, text=f"Количество заказов: {количество_заказов}").grid(row=2, column=0, columnspan=2,
                                                                                       sticky="w")
            tk.Label(self.root, text=f"Популярные блюда: {популярные_блюда}").grid(row=3, column=0, columnspan=2,
                                                                                   sticky="w")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при генерации отчета: {e}")

        # Кнопка назад
        self.create_button("Назад", self.admin_menu_window, 4)

    # Просмотр заказов
    def view_orders(self):
        self.clear_window()
        tk.Label(self.root, text="Мои заказы").grid(row=0, column=0, columnspan=2, pady=10)

        try:
            # Получаем заказы
            self.cursor.execute("""
                SELECT z.id, z.Дата_заказа, z.Статус, SUM(bz.Количество * b.Цена) AS Стоимость
                FROM Заказ z
                LEFT JOIN Блюдо_Заказ bz ON z.id = bz.Заказ_id
                LEFT JOIN Блюдо b ON bz.Блюдо_id = b.id
                WHERE z.Пользователь_id = ?
                GROUP BY z.id
            """, (self.user_id,))
            orders = self.cursor.fetchall()

            if not orders:
                tk.Label(self.root, text="У вас нет заказов").grid(row=1, column=0, columnspan=2)
                return

            for i, (order_id, order_date, status, total_price) in enumerate(orders, start=1):
                tk.Label(self.root, text=f"Заказ {order_id}: {status}, {total_price:.2f} руб.").grid(row=i, column=0,
                                                                                                     columnspan=2)
                self.create_button("Состав", lambda id=order_id: self.view_order_details(id), i + 1, column=0)

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке заказов: {e}")

        self.create_button("Назад", self.user_menu_window, len(orders) + 2)

    def view_order_details(self, order_id):
        self.clear_window()
        tk.Label(self.root, text=f"Состав заказа {order_id}").grid(row=0, column=0, columnspan=2, pady=10)

        self.cursor.execute("""
            SELECT b.Название, bz.Количество, b.Цена
            FROM Блюдо_Заказ bz
            JOIN Блюдо b ON bz.Блюдо_id = b.id
            WHERE bz.Заказ_id = ?
        """, (order_id,))
        dishes = self.cursor.fetchall()

        for i, (dish_name, quantity, price) in enumerate(dishes, start=1):
            tk.Label(self.root, text=f"{dish_name}: {quantity} шт., {price:.2f} руб.").grid(row=i, column=0)

        self.create_button("Назад", self.view_orders, len(dishes) + 2)

    # Создание заказа
    def create_order(self):
        self.clear_window()

        tk.Label(self.root, text="Создание заказа").grid(row=0, column=0, columnspan=2, pady=10)

        # Получение списка блюд из базы данных
        self.cursor.execute("SELECT id, Название, Цена FROM Блюдо")
        dishes = self.cursor.fetchall()

        if not dishes:
            tk.Label(self.root, text="Меню пустое. Нет доступных блюд для заказа.").grid(row=1, column=0, columnspan=2)
            self.create_button("Назад", self.user_menu_window, 2)
            return

        # Отображение списка блюд
        self.order_items = {}
        for i, (dish_id, dish_name, dish_price) in enumerate(dishes, start=1):
            tk.Label(self.root, text=f"{dish_name} - {dish_price:.2f} руб.").grid(row=i, column=0, sticky="w")
            quantity_entry = tk.Entry(self.root, width=5)
            quantity_entry.grid(row=i, column=1)
            self.order_items[dish_id] = quantity_entry

        # Кнопка для подтверждения заказа
        self.create_button("Оформить заказ", self.submit_order, len(dishes) + 1)
        self.create_button("Назад", self.user_menu_window, len(dishes) + 2)

    def submit_order(self):
        order_data = []

        # Проверяем введенные количества блюд
        for dish_id, entry in self.order_items.items():
            quantity = entry.get()
            if quantity.isdigit() and int(quantity) > 0:
                order_data.append((dish_id, int(quantity)))

        if not order_data:
            messagebox.showerror("Ошибка", "Выберите хотя бы одно блюдо и укажите количество!")
            return

        try:
            # Для отладки
            print(f"Создание заказа с пользователем {self.user_id}, датой {date.today()}, статусом 'Новый'")

            # Создаем новый заказ со статусом "Новый"
            self.cursor.execute("INSERT INTO Заказ (Пользователь_id, Дата_заказа, Статус) VALUES (?, ?, ?)",
                                (self.user_id, date.today(), 'Новый'))
            order_id = self.cursor.lastrowid

            # Добавляем блюда в заказ
            for dish_id, quantity in order_data:
                self.cursor.execute("INSERT INTO Блюдо_Заказ (Блюдо_id, Заказ_id, Количество) VALUES (?, ?, ?)",
                                    (dish_id, order_id, quantity))

            self.conn.commit()
            messagebox.showinfo("Успех", "Заказ успешно создан!")
            self.user_menu_window()

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании заказа: {e}")

    # Просмотр меню
    def view_menu(self):
        global dishes
        self.clear_window()

        tk.Label(self.root, text="Меню ресторана").grid(row=0, column=0, columnspan=2, pady=10)

        # Получение списка блюд из базы данных
        try:
            self.cursor.execute("""
                    SELECT b.Название, b.Цена, c.Название 
                    FROM Блюдо b
                    JOIN Категория c ON b.Категория_id = c.id
                """)
            dishes = self.cursor.fetchall()

            if not dishes:
                tk.Label(self.root, text="Меню пустое.").grid(row=1, column=0, columnspan=2)
            else:
                for i, (dish_name, dish_price, category_name) in enumerate(dishes, start=1):
                    tk.Label(self.root, text=f"{dish_name} - {dish_price:.2f} руб. ({category_name})").grid(row=i,
                                                                                                            column=0,
                                                                                                            columnspan=2,
                                                                                                            sticky="w")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке меню: {e}")

        # Кнопка назад возвращает в соответствующее меню
        back_function = self.admin_menu_window if self.role == "Администратор" else self.user_menu_window
        self.create_button("Назад", back_function, len(dishes) + 2)

    def export_menu_to_excel(self):
        file_path = "menu.xlsx"
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet()

        # Заголовки
        headers = ["Название", "Цена", "Категория"]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Получение данных из базы
        self.cursor.execute("""
            SELECT b.Название, b.Цена, c.Название
            FROM Блюдо b
            JOIN Категория c ON b.Категория_id = c.id
        """)
        menu_items = self.cursor.fetchall()

        for row, (name, price, category) in enumerate(menu_items, start=1):
            worksheet.write(row, 0, name)
            worksheet.write(row, 1, price)
            worksheet.write(row, 2, category)

        workbook.close()
        messagebox.showinfo("Успех", f"Меню экспортировано в файл {file_path}")

    # Выход из приложения
    def exit_program(self):
        self.conn.close()
        self.root.quit()

# Запуск приложения
root = tk.Tk()
app = RestaurantSystem(root)
root.mainloop()