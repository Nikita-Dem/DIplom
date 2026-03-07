import os
import json
import logging
import traceback
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, abort, jsonify

from config import Config
from models import db, Document
from forms import ProtocolForm, ResolutionForm
from document_generator import document_generator

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Создание приложения Flask
app = Flask(__name__)
app.config.from_object(Config)


# Проверка и создание необходимых папок
def ensure_directories():
    """Проверка и создание всех необходимых папок"""
    directories = [
        app.config.get('instance_path', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')),
        app.config['OUTPUT_DIR'],
        app.config['PROTOCOLS_DIR'],
        app.config['RESOLUTIONS_DIR']
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Папка создана/проверена: {directory}")

            # Проверяем права на запись
            test_file = os.path.join(directory, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"Права на запись в {directory} есть")

        except Exception as e:
            logger.error(f"Ошибка при создании/проверке папки {directory}: {e}")
            return False

    return True


# Проверяем папки перед инициализацией
if not ensure_directories():
    logger.error("Критическая ошибка: не удалось создать необходимые папки")
    exit(1)

# Инициализация базы данных
db.init_app(app)

# Инициализация генератора документов
document_generator.init_app(app)

# Создание таблиц базы данных
with app.app_context():
    try:
        db.create_all()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Критическая ошибка при инициализации базы данных: {e}")
        exit(1)


# Главная страница
@app.route('/')
@app.route('/index')
def index():
    """Главная страница с информацией о системе"""
    try:
        # Получаем статистику
        protocols_count = Document.query.filter_by(document_type='protocol').count()
        resolutions_count = Document.query.filter_by(document_type='resolution').count()
        total_count = Document.query.count()

        # Последние 5 документов
        recent_documents = Document.query.order_by(Document.created_at.desc()).limit(5).all()

        return render_template('index.html',
                               protocols_count=protocols_count,
                               resolutions_count=resolutions_count,
                               total_count=total_count,
                               recent_documents=[doc.to_dict() for doc in recent_documents])
    except Exception as e:
        logger.error(f"Ошибка на главной странице: {e}")
        return render_template('500.html'), 500


# Создание протокола
@app.route('/create/protocol', methods=['GET', 'POST'])
def create_protocol():
    """Создание нового протокола"""
    form = ProtocolForm()

    if form.validate_on_submit():
        try:
            # Собираем данные из формы
            data = {
                'number': form.number.data,
                'date': form.date.data.strftime('%d.%m.%Y'),
                'topic': form.topic.data,
                'location': form.location.data,
                'datetime': form.datetime.data,
                'participants': form.participants.data,
                'agenda': form.agenda.data,
                'decisions': form.decisions.data,
                'chairman': form.chairman.data,
                'secretary': form.secretary.data
            }

            logger.info(f"Начало генерации протокола")

            # Генерируем документ в Word
            filepath = document_generator.generate_protocol(data)

            logger.info(f"Word файл создан: {filepath}")

            # Сохраняем в базу данных
            document = Document(
                document_type='protocol',
                document_number=str(form.number.data),
                document_date=form.date.data,
                title=f"Протокол №{form.number.data} от {form.date.data.strftime('%d.%m.%Y')}",
                content=json.dumps(data, ensure_ascii=False, default=str),
                file_path=filepath,
                author='Пользователь',
                status='final'
            )

            db.session.add(document)
            db.session.commit()

            flash(f'✅ Протокол успешно создан! ID: {document.id}', 'success')
            logger.info(f"Создан протокол ID: {document.id}")
            return redirect(url_for('view_document', doc_id=document.id))

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"Ошибка при создании протокола: {error_msg}")
            logger.error(traceback.format_exc())
            flash(f'❌ Ошибка при создании протокола: {error_msg}', 'danger')

    return render_template('create_protocol.html', form=form)


# Создание постановления
@app.route('/create/resolution', methods=['GET', 'POST'])
def create_resolution():
    """Создание нового постановления"""
    form = ResolutionForm()

    if form.validate_on_submit():
        try:
            # Собираем данные из формы
            data = {
                'number': form.number.data,
                'date': form.date.data.strftime('%d.%m.%Y'),
                'topic': form.topic.data,
                'basis': form.basis.data,
                'text': form.text.data,
                'chairman': form.chairman.data,
                'members': form.members.data
            }

            logger.info(f"Начало генерации постановления")

            # Генерируем документ в Word
            filepath = document_generator.generate_resolution(data)

            logger.info(f"Word файл создан: {filepath}")

            # Сохраняем в базу данных
            document = Document(
                document_type='resolution',
                document_number=str(form.number.data),
                document_date=form.date.data,
                title=f"Постановление №{form.number.data} от {form.date.data.strftime('%d.%m.%Y')}",
                content=json.dumps(data, ensure_ascii=False, default=str),
                file_path=filepath,
                author='Пользователь',
                status='final'
            )

            db.session.add(document)
            db.session.commit()

            flash(f'✅ Постановление успешно создано! ID: {document.id}', 'success')
            logger.info(f"Создано постановление ID: {document.id}")
            return redirect(url_for('view_document', doc_id=document.id))

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"Ошибка при создании постановления: {error_msg}")
            logger.error(traceback.format_exc())
            flash(f'❌ Ошибка при создании постановления: {error_msg}', 'danger')

    return render_template('create_resolution.html', form=form)


# Список документов
@app.route('/documents')
def documents_list():
    """Список всех документов с возможностью фильтрации"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = app.config.get('DOCUMENTS_PER_PAGE', 10)
        doc_type = request.args.get('type', '')
        search_query = request.args.get('q', '')

        # Базовый запрос
        query = Document.query

        # Фильтр по типу
        if doc_type and doc_type != 'all':
            query = query.filter_by(document_type=doc_type)

        # Поиск по номеру или названию
        if search_query:
            query = query.filter(
                (Document.document_number.contains(search_query)) |
                (Document.title.contains(search_query))
            )

        # Пагинация
        pagination = query.order_by(Document.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        documents = [doc.to_dict() for doc in pagination.items]

        return render_template('documents_list.html',
                               documents=documents,
                               pagination=pagination,
                               current_type=doc_type,
                               search_query=search_query)
    except Exception as e:
        logger.error(f"Ошибка при загрузке списка документов: {e}")
        logger.error(traceback.format_exc())
        flash(f'Ошибка при загрузке списка документов: {str(e)}', 'danger')
        return render_template('documents_list.html', documents=[], pagination=None)


# Просмотр информации о документе
@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    """Просмотр информации о документе"""
    try:
        document = Document.query.get_or_404(doc_id)

        return render_template('view_document.html',
                               document=document.to_dict())
    except Exception as e:
        logger.error(f"Ошибка при просмотре документа {doc_id}: {e}")
        flash(f'Ошибка при просмотре документа: {str(e)}', 'danger')
        return redirect(url_for('documents_list'))


# Скачивание документа
@app.route('/download/<int:doc_id>')
def download_document(doc_id):
    """Скачивание файла документа"""
    try:
        document = Document.query.get_or_404(doc_id)

        if not os.path.exists(document.file_path):
            flash('Файл документа не найден на сервере', 'danger')
            return redirect(url_for('view_document', doc_id=doc_id))

        # Определяем MIME тип для Word
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        return send_file(
            document.file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(document.file_path)
        )
    except Exception as e:
        logger.error(f"Ошибка при скачивании документа {doc_id}: {e}")
        flash(f'Ошибка при скачивании документа: {str(e)}', 'danger')
        return redirect(url_for('documents_list'))


# Удаление документа
@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    """Удаление документа"""
    try:
        document = Document.query.get_or_404(doc_id)

        # Сохраняем информацию для лога
        doc_title = document.title
        doc_file = document.file_path

        # Удаляем файл, если он существует
        if os.path.exists(doc_file):
            os.remove(doc_file)
            logger.info(f"Удален файл: {doc_file}")

        # Удаляем запись из БД
        db.session.delete(document)
        db.session.commit()

        flash(f'✅ Документ "{doc_title}" успешно удален', 'success')
        logger.info(f"Удален документ ID: {doc_id}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении документа {doc_id}: {e}")
        flash(f'❌ Ошибка при удалении документа: {str(e)}', 'danger')

    return redirect(url_for('documents_list'))


# Обработчик ошибок 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# Обработчик ошибок 500
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Запуск приложения
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 СИСТЕМА ДОКУМЕНТООБОРОТА ЗАПУЩЕНА")
    print("=" * 60)
    print(f"\n📁 Рабочая директория: {os.path.abspath(os.path.dirname(__file__))}")
    print(f"📁 Папка output: {app.config['OUTPUT_DIR']}")
    print(f"\n📱 Локальный доступ:")
    print(f"   http://localhost:5000")
    print(f"   http://127.0.0.1:5000")
    print("\n💡 Чтобы остановить сервер, нажмите Ctrl+C")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)