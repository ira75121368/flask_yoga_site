import openai
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
from db import add_client_account, get_client_by_phone, check_phone_exists, update_password, get_employees, \
    add_employee, del_employee, get_clients, get_client_attendance, \
    add_client, change_client, del_client, get_price_list, add_price_list, update_ticket_price, get_all_ticket_types, \
    get_schedule, add_schedule, update_free_spots, book_schedule_spot, get_filtered_schedule, client_exists
from forms import ClientRegisterForm, EmployeeForm, EmployeeFormChanges, ClientForm, ClientFormChanges, ScheduleForm, \
    LoginForm, PriceForm
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '7f1b9a9e43b0df63d3a77e96b0297d3d4f55a2ea36e9f2bfae4e4db0e0b81e2c'

ADMIN_CREDENTIALS = {
    'admin': "admin_password"
}


# 🌟 Регистрация для клиента
@app.route('/register_client', methods=['GET', 'POST'])
def register_client_route():
    form = ClientRegisterForm()

    if form.validate_on_submit():
        full_name = form.full_name.data
        phone = form.phone.data
        password = form.password.data

        # Вызываем функцию из модуля работы с БД
        add_client_account(full_name, phone, password)

        flash("Регистрация прошла успешно!", "success")
        return redirect(url_for('login'))  # или куда хочешь отправить после

    return render_template('register_client.html', form=form)


# Функция проверки авторизации
def is_authenticated():
    return session.get('logged_in') == True


# Контекстный процессор для передачи is_authenticated в шаблоны
@app.context_processor
def inject_is_authenticated():
    return dict(is_authenticated=is_authenticated)


# 🌟 Маршрут для главной страницы
@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))

    emploees = get_employees()
    price_list = get_price_list()
    schedule = get_schedule()
    return render_template('index.html', emploees=emploees, price_list=price_list, schedule=schedule)


# 🌟 Восстановление пароля
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        phone = request.form.get('phone')
        # Тут можно просто показать сообщение
        flash('Отправьте ваш номер нашему боту для восстановления пароля!', 'info')
        return redirect(url_for('login'))
    return render_template('password_new.html')


# 🌟 Вход в учетную запись
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Админ
        if username in ADMIN_CREDENTIALS:
            if password == ADMIN_CREDENTIALS[username]:
                session['logged_in'] = True
                session['is_admin'] = True
                flash("Вход выполнен как администратор!", "success")
                return redirect(url_for('index'))
            else:
                flash("Неверный пароль администратора", "danger")

        # Клиент
        user = get_client_by_phone(username)
        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['user_type'] = 'client'
            session['client_id'] = user[0]
            session['client_name'] = user[1]
            flash("Вы вошли как клиент!", "success")
            return redirect(url_for('client_dashboard'))

        flash("Неверный логин или пароль", "danger")

    return render_template('login.html', form=form)


# 🌟 Главная для админа
@app.route('/admin')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')


# 🌟 Главная для клиентов
@app.route('/studia')
def client_dashboard():
    if session.get('user_type') != 'client':
        return redirect(url_for('login'))

    client_id = session.get('client_id')

    attended_classes = get_client_attendance(client_id)

    return render_template(
        'client_dashboard.html',
        name=session.get('client_name'),
        attended_classes=attended_classes
    )


# 🌟 О студии
@app.route('/studio')
def studio_about():
    return render_template('studio_about.html')


# 🌟 Тренеры для клиентов
@app.route('/client_trainers')
def client_trainers():
    if session.get('user_type') != 'client':
        return redirect(url_for('login'))

    employees = get_employees()
    return render_template('client_trainers.html', employees=employees)


# 🌟 Расписание для клиентов
@app.route('/client_schedule', methods=['GET', 'POST'])
def client_schedule():
    if session.get('user_type') != 'client':
        return redirect(url_for('login'))

    if request.method == 'POST':
        schedule_id = request.form.get('schedule_id')

        if schedule_id:
            success = book_schedule_spot(schedule_id)
            if success:
                flash("Вы успешно записались на занятие!", "success")
            else:
                flash("К сожалению, свободных мест больше нет.", "danger")
        return redirect(url_for('client_schedule'))

    schedule = get_schedule()
    return render_template('client_schedule.html', schedule=schedule)


def client_schedule():
    day_filter = request.args.get('day')  # получаем день недели из формы
    schedule = get_filtered_schedule(day_filter)
    return render_template('client_schedule.html', schedule=schedule, selected_day=day_filter)


# 🌟 Выход из учетной записи
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('login'))


# 🌟 Раздел тренеров
@app.route('/emploees')
def emploees():
    if not is_authenticated():
        return redirect(url_for('login'))

    employees = get_employees()
    return render_template('emploees.html', employees=employees)


# 🌟 Раздел клиентов
@app.route('/clients')
def clients():
    if not is_authenticated():
        return redirect(url_for('login'))

    clients = get_clients()
    return render_template('clients.html', clients=clients)


# 🌟 Раздел цен
@app.route('/prices')
def prices():
    if not is_authenticated():
        return redirect(url_for('login'))

    price_list = get_price_list()
    return render_template('prices.html', price_list=price_list)


# 🌟 Раздел расписания
@app.route('/schedule')
def schedule():
    if not is_authenticated():
        return redirect(url_for('login'))

    schedule = get_schedule()
    return render_template('schedule.html', schedule=schedule)


# 🌟 Добавление тренера
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = EmployeeForm()
    if form.validate_on_submit():
        full_name = form.full_name.data
        if client_exists(full_name):
            flash("Ошибка: тренер уже занесён в базу!", "danger")
            return redirect(url_for('add_employee_route'))
        add_employee(form.full_name.data, form.phone.data, form.specialization.data, form.passport.data,
                     form.birthday.data)
        flash("Тренер добавлен!", "success")
        return redirect(url_for('emploees'))
    return render_template('add_employee.html', form=form)


# 🌟 Удаление тренера
@app.route('/del_employee', methods=['GET', 'POST'])
def del_employee_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = EmployeeFormChanges()
    if form.validate_on_submit():
        phone = form.phone.data
        specialization = form.specialization.data
        passport = form.passport.data
        birthday = form.birthday.data
        del_employee(form.full_name.data, phone, specialization, passport, birthday)
        flash("Тренер удален!", "success")
        return redirect(url_for('emploees'))

    return render_template('del_employee.html', form=form)


# 🌟 Поиск тренера
@app.route('/search_employees')
def search_employees():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    employees = get_employees()
    filtered_employees = [
        {
            "full_name": employee[1],
            "phone": employee[2],
            "specialization": employee[3],
            "passport": employee[4],
            "birthday": employee[5]
        }
        for employee in employees if query in employee[1].lower()
    ]

    return jsonify(filtered_employees)


# 🌟 Добавление данных в прайс-лист
@app.route('/add_price_list', methods=['GET', 'POST'])
def add_price_list_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = PriceForm()
    if form.validate_on_submit():
        add_price_list(form.membership_type.data, form.price.data)
        flash("Новый абонемент добавлен!", "success")
        return redirect(url_for('prices'))

    return render_template('add_prices.html', form=form)


@app.route('/update_price_list', methods=['GET', 'POST'])
def update_price_list_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = PriceForm()

    # Получение всех существующих типов абонементов для выбора
    ticket_types = get_all_ticket_types()
    form.membership_type.choices = [(t, t) for t in ticket_types]

    if form.validate_on_submit():
        update_ticket_price(form.membership_type.data, form.price.data)
        flash("Цена абонемента обновлена!", "success")
        return redirect(url_for('prices'))

    return render_template('change_prices.html', form=form)


# 🌟 Добавление клиента
@app.route('/add_client', methods=['GET', 'POST'])
def add_client_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = ClientForm()
    if form.validate_on_submit():
        phone = form.phone.data
        if client_exists(phone):
            flash("Ошибка: номер уже зарегистрирован!", "danger")
            return redirect(url_for('add_client_route'))

        add_client(form.full_name.data, phone)
        flash("Клиент добавлен!", "success")
        return redirect(url_for('clients'))

    return render_template('add_client.html', form=form)


# 🌟 Удаление клиента
@app.route('/del_client', methods=['GET', 'POST'])
def del_client_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = ClientFormChanges()
    if form.validate_on_submit():
        phone = form.phone.data
        del_client(form.full_name.data, phone)
        flash("Клиент удален!", "success")
        return redirect(url_for('clients'))

    return render_template('del_client.html', form=form)


# 🌟 Изменение данных клиента
@app.route('/del_client', methods=['GET', 'POST'])
def chande_client_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = ClientFormChanges()
    if form.validate_on_submit():
        phone = form.phone.data
        change_client(form.full_name.data, phone)
        flash("Данные о клиенте изменены!", "success")
        return redirect(url_for('clients'))

    return render_template('change_client.html', form=form)


# 🌟 Поиск клиента
@app.route('/search_clients')
def search_clients():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    clients = get_clients()  # [(id, full_name, phone), (id, full_name, phone), ...]
    filtered_clients = [
        {"full_name": client[1], "phone": client[2]}
        for client in clients if query in client[1].lower()
    ]

    return jsonify(filtered_clients)


# 🌟 Добавление занятия
@app.route('/add_schedule', methods=['GET', 'POST'])
def add_schedule_route():
    if not is_authenticated():
        return redirect(url_for('login'))

    form = ScheduleForm()
    if form.validate_on_submit():
        add_schedule(
            form.day_of_week.data, form.start_time.data, form.duration.data,
            form.specialization.data, form.instructor_name.data, form.free_spots.data
        )
        flash("Занятие добавлено!", "success")
        return redirect(url_for('schedule'))
    return render_template('add_schedule.html', form=form)


# 🌟 Обновление свободных мест
@app.route('/update_free_spots/<int:schedule_id>', methods=['POST'])
def update_free_spots_route(schedule_id):
    if not is_authenticated():
        return redirect(url_for('login'))

    new_free_spots = int(request.form['free_spots'])
    update_free_spots(schedule_id, new_free_spots)
    flash("Свободные места обновлены!", "success")
    return redirect(url_for('schedule'))


if __name__ == '__main__':
    app.run(debug=True)
