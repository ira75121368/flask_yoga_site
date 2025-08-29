from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, EqualTo
from site_yoga.db import get_connection


class ClientRegisterForm(FlaskForm):
    full_name = StringField("ФИО", validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField("Телефон", validators=[
        DataRequired(), Length(min=10, max=15),
        Regexp(r'^\+?\d{10,15}$', message="Введите корректный номер")
    ])
    password = PasswordField("Пароль", validators=[
        DataRequired(), Length(min=6, max=100)
    ])
    confirm_password = PasswordField("Повторите пароль", validators=[
        DataRequired(), EqualTo('password', message="Пароли не совпадают")
    ])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    username = StringField('Номер телефона', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

class EmployeeForm(FlaskForm):
    full_name = StringField('Фамилия Имя Отчество тренера', validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])
    specialization = StringField('Специализация', validators=[DataRequired(), Length(min=3, max=50)])
    passport = StringField('Паспорт', validators=[DataRequired(), Length(min=10, max=15)])
    birthday = StringField('День рождения', validators=[DataRequired(), Length(min=3, max=50)])

class EmployeeFormChanges(FlaskForm):
    full_name = SelectField('Фамилия Имя Отчество тренера', validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])
    specialization = StringField('Специализация', validators=[DataRequired(), Length(min=3, max=50)])
    passport = StringField('Паспорт', validators=[DataRequired(), Length(min=10, max=15)])
    birthday = StringField('День рождения', validators=[DataRequired(), Length(min=3, max=50)])

    def __init__(self, *args, **kwargs):
        super(EmployeeFormChanges, self).__init__(*args, **kwargs)
        self.full_name.choices = self.get_employees()

    def get_employees(self):
        """Получаем список тренеров из базы данных"""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT full_name FROM kurs_2.employees ORDER BY full_name ASC;")
                employees = cursor.fetchall()  # [(Имя1,), (Имя2,)]
                return [(employee[0], employee[0], employee[0], employee[0], employee[0]) for employee in employees] if employees else [('', 'Нет тренеров')]


class PriceForm(FlaskForm):
    membership_type = SelectField("Тип абонемента", choices=[], validators=[DataRequired()])
    price = IntegerField("Цена", validators=[DataRequired(), NumberRange(min=1)])

class ClientForm(FlaskForm):
    full_name = StringField('Фамилия Имя Отчество клиента', validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])

class ClientFormChanges(FlaskForm):
    full_name = SelectField('Фамилия Имя Отчество клиента', validators=[DataRequired(), Length(min=3, max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=15)])

    def __init__(self, *args, **kwargs):
        super(ClientFormChanges, self).__init__(*args, **kwargs)
        self.full_name.choices = self.get_clients()

    def get_clients(self):
        """Получаем список клиентов из базы данных"""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT full_name FROM kurs_2.clients ORDER BY full_name ASC;")
                clients = cursor.fetchall()  # [(Имя1,), (Имя2,)]
                return [(client[0], client[0]) for client in clients] if clients else [('', 'Нет клиентов')]

class ScheduleForm(FlaskForm):
    day_of_week = SelectField('День недели', choices=[
        ('Пн', 'Понедельник'),
        ('Вт', 'Вторник'),
        ('Ср', 'Среда'),
        ('Чт', 'Четверг'),
        ('Пт', 'Пятница'),
        ('Сб', 'Суббота'),
        ('Вс', 'Воскресенье')
    ], validators=[DataRequired()])

    start_time = StringField('Время начала', validators=[DataRequired()])
    duration = SelectField('Продолжительность', choices=[
        (60, '60 минут'),
        (90, '90 минут')
    ], validators=[DataRequired()])

    specialization = SelectField('Специализация', choices=[
        ('Хатха-йога', 'Хатха-йога'),
        ('Кундалини йога', 'Кундалини йога'),
        ('йога для детей', 'Йога для детей'),
        ('йога для пожилых людей', 'Йога для пожилых людей')
    ], validators=[DataRequired()])


    instructor_name = SelectField('Имя тренера', validators=[DataRequired()], choices=[])

    free_spots = SelectField('Свободные места', choices=[
        (15, '15 мест'),
        (10, '10 мест')
    ], coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.instructor_name.choices = self.get_instructors()

    def get_instructors(self):
        """Получаем список тренеров из базы данных"""
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT full_name FROM kurs_2.employees ORDER BY full_name ASC;")
                instructors = cursor.fetchall()  # [(Имя1,), (Имя2,)]
                return [(instr[0], instr[0]) for instr in instructors] if instructors else [('', 'Нет тренеров')]

