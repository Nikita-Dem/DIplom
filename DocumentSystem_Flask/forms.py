from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date

class ProtocolForm(FlaskForm):
    """Форма для создания протокола"""
    number = IntegerField('Номер протокола',
                         validators=[DataRequired(message='Обязательное поле'),
                                   NumberRange(min=1, message='Номер должен быть положительным')])
    date = DateField('Дата',
                    validators=[DataRequired(message='Обязательное поле')],
                    default=date.today)
    topic = StringField('Тема',
                       validators=[DataRequired(message='Обязательное поле'),
                                 Length(max=255, message='Максимум 255 символов')])
    location = StringField('Место проведения',
                          validators=[DataRequired(message='Обязательное поле'),
                                    Length(max=255, message='Максимум 255 символов')])
    datetime = StringField('Дата и время заседания',
                          validators=[DataRequired(message='Обязательное поле')])
    participants = TextAreaField('Участники (каждый с новой строки)',
                                validators=[DataRequired(message='Обязательное поле')])
    agenda = TextAreaField('Повестка дня (каждый пункт с новой строки)',
                          validators=[DataRequired(message='Обязательное поле')])
    decisions = TextAreaField('Решения (каждое с новой строки)',
                             validators=[DataRequired(message='Обязательное поле')])
    chairman = StringField('Председатель',
                          validators=[DataRequired(message='Обязательное поле'),
                                    Length(max=255, message='Максимум 255 символов')])
    secretary = StringField('Секретарь',
                           validators=[DataRequired(message='Обязательное поле'),
                                     Length(max=255, message='Максимум 255 символов')])

class ResolutionForm(FlaskForm):
    """Форма для создания постановления"""
    number = IntegerField('Номер постановления',
                         validators=[DataRequired(message='Обязательное поле'),
                                   NumberRange(min=1, message='Номер должен быть положительным')])
    date = DateField('Дата',
                    validators=[DataRequired(message='Обязательное поле')],
                    default=date.today)
    topic = StringField('Тема',
                       validators=[DataRequired(message='Обязательное поле'),
                                 Length(max=255, message='Максимум 255 символов')])
    basis = TextAreaField('Основание (со ссылками на нормативные акты)',
                         validators=[DataRequired(message='Обязательное поле')])
    text = TextAreaField('Текст постановления (каждый пункт с новой строки)',
                        validators=[DataRequired(message='Обязательное поле')])
    chairman = StringField('Председатель',
                          validators=[DataRequired(message='Обязательное поле'),
                                    Length(max=255, message='Максимум 255 символов')])
    members = TextAreaField('Члены комиссии (каждый с новой строки)',
                           validators=[Optional()])