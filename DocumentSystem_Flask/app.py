import os
import json
import logging
import traceback
import socket
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, send_file, abort, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps

from config import Config
from models import db, Document
from forms import ProtocolForm, ResolutionForm
from document_generator import document_generator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создание приложения Flask
app = Flask(__name__)
app.config.from_object(Config)

# Добавляем поддержку прокси (для продакшена)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


# Функция для получения внешнего IP
def get_external_ip():
    try:
        # Пробуем получить внешний IP через запрос к внешнему сервису
        import requests
        response = requests.get('https://api.ipify.org', timeout=3)
        return response.text.strip()
    except:
        try:
            # Альтернативный метод - через сокет
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "Невозможно определить IP"


# Декоратор для базовой аутентификации (опционально)
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == app.config.get('ADMIN_USER', 'admin') and
                            auth.password == app.config.get('ADMIN_PASS', 'admin123')):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def authenticate():
    """Отправка требования аутентификации"""
    from flask import Response
    return Response(
        'Необходима аутентификация для доступа', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


# Проверка и создание необходимых папок
def ensure_directories():
    """Проверка и создание всех необходимых папок"""
    directories = [
        app.config.get('instance_path', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')),
        app.config['OUTPUT_DIR'],
        app.config['PROTOCOLS_DIR'],
        app.config['RESOLUTIONS_DIR'],
        os.path.join(app.config['OUTPUT_DIR'], 'backup'),  # Папка для бэкапов
        os.path.join(app.config['OUTPUT_DIR'], 'temp')  # Временная папка
    ]

    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Папка создана/проверена: {directory}")

            # Проверяем права на запись
            test_file = os.path.join(directory, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"   ✓ Права на запись есть")

        except Exception as e:
            logger.error(f"❌ Ошибка при создании/проверке папки {directory}: {e}")
            return False

    return True


# Проверяем папки перед инициализацией
if not ensure_directories():
    logger.error("❌ Критическая ошибка: не удалось создать необходимые папки")
    exit(1)

# Инициализация базы данных
db.init_app(app)

# Инициализация генератора документов
document_generator.init_app(app)

# Создание таблиц базы данных
with app.app_context():
    try:
        db.create_all()
        logger.info("✅ База данных успешно инициализирована")

        # Проверяем подключение к БД
        test_query = Document.query.first()
        logger.info("   ✓ Подключение к БД работает")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка при инициализации базы данных: {e}")
        exit(1)


# Главная страница
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    """Главная страница с информацией о системе"""
    try:
        # Получаем статистику
        protocols_count = Document.query.filter_by(document_type='protocol').count()
        resolutions_count = Document.query.filter_by(document_type='resolution').count()
        total_count = Document.query.count()

        # Последние 10 документов
        recent_documents = Document.query.order_by(Document.created_at.desc()).limit(10).all()

        # Получаем IP для отображения
        external_ip = get_external_ip()

        return render_template('index.html',
                               protocols_count=protocols_count,
                               resolutions_count=resolutions_count,
                               total_count=total_count,
                               recent_documents=[doc.to_dict() for doc in recent_documents],
                               external_ip=external_ip,
                               port=app.config.get('PORT', 5000))
    except Exception as e:
        logger.error(f"Ошибка на главной странице: {e}")
        return render_template('500.html'), 500


# API для получения списка документов (JSON)
@app.route('/api/documents')
def api_documents():
    """API endpoint для получения списка документов в JSON формате"""
    try:
        documents = Document.query.order_by(Document.created_at.desc()).all()
        return jsonify({
            'success': True,
            'documents': [doc.to_dict() for doc in documents]
        })
    except Exception as e:
        logger.error(f"Ошибка в API документов: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# API для получения одного документа (JSON)
@app.route('/api/document/<int:doc_id>')
def api_document(doc_id):
    """API endpoint для получения документа по ID"""
    try:
        document = Document.query.get_or_404(doc_id)
        return jsonify({
            'success': True,
            'document': document.to_dict()
        })
    except Exception as e:
        logger.error(f"Ошибка в API документа {doc_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404


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
                'secretary': form.secretary.data,
                'created_at': datetime.now().isoformat(),
                'client_ip': request.remote_addr
            }

            logger.info(f"📄 Начало генерации протокола №{form.number.data}")

            # Генерируем документ в Word
            filepath = document_generator.generate_protocol(data)

            logger.info(f"   ✅ Word файл создан: {os.path.basename(filepath)}")

            # Сохраняем в базу данных
            document = Document(
                document_type='protocol',
                document_number=str(form.number.data),
                document_date=form.date.data,
                title=f"Протокол №{form.number.data} от {form.date.data.strftime('%d.%m.%Y')}",
                content=json.dumps(data, ensure_ascii=False, default=str),
                file_path=filepath,
                author=f"IP: {request.remote_addr}",
                status='final'
            )

            db.session.add(document)
            db.session.commit()

            flash(f'✅ Протокол успешно создан! ID: {document.id}', 'success')
            logger.info(f"   ✅ Протокол сохранен в БД, ID: {document.id}")
            return redirect(url_for('view_document', doc_id=document.id))

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"❌ Ошибка при создании протокола: {error_msg}")
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
                'members': form.members.data,
                'created_at': datetime.now().isoformat(),
                'client_ip': request.remote_addr
            }

            logger.info(f"📄 Начало генерации постановления №{form.number.data}")

            # Генерируем документ в Word
            filepath = document_generator.generate_resolution(data)

            logger.info(f"   ✅ Word файл создан: {os.path.basename(filepath)}")

            # Сохраняем в базу данных
            document = Document(
                document_type='resolution',
                document_number=str(form.number.data),
                document_date=form.date.data,
                title=f"Постановление №{form.number.data} от {form.date.data.strftime('%d.%m.%Y')}",
                content=json.dumps(data, ensure_ascii=False, default=str),
                file_path=filepath,
                author=f"IP: {request.remote_addr}",
                status='final'
            )

            db.session.add(document)
            db.session.commit()

            flash(f'✅ Постановление успешно создано! ID: {document.id}', 'success')
            logger.info(f"   ✅ Постановление сохранено в БД, ID: {document.id}")
            return redirect(url_for('view_document', doc_id=document.id))

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            logger.error(f"❌ Ошибка при создании постановления: {error_msg}")
            logger.error(traceback.format_exc())
            flash(f'❌ Ошибка при создании постановления: {error_msg}', 'danger')

    return render_template('create_resolution.html', form=form)


# Список документов
@app.route('/documents')
@app.route('/documents/page/<int:page>')
def documents_list(page=1):
    """Список всех документов с возможностью фильтрации"""
    try:
        per_page = app.config.get('DOCUMENTS_PER_PAGE', 15)
        doc_type = request.args.get('type', '')
        search_query = request.args.get('q', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')

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

        # Фильтр по дате
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Document.document_date >= date_from_obj)
            except:
                pass

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Document.document_date <= date_to_obj)
            except:
                pass

        # Пагинация
        pagination = query.order_by(Document.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        documents = [doc.to_dict() for doc in pagination.items]

        return render_template('documents_list.html',
                               documents=documents,
                               pagination=pagination,
                               current_type=doc_type,
                               search_query=search_query,
                               date_from=date_from,
                               date_to=date_to)
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке списка документов: {e}")
        logger.error(traceback.format_exc())
        flash(f'Ошибка при загрузке списка документов: {str(e)}', 'danger')
        return render_template('documents_list.html', documents=[], pagination=None)


# Просмотр информации о документе
@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    """Просмотр информации о документе"""
    try:
        document = Document.query.get_or_404(doc_id)

        # Парсим содержимое JSON
        try:
            content = json.loads(document.content) if document.content else {}
        except:
            content = {'raw': document.content}

        return render_template('view_document.html',
                               document=document.to_dict(),
                               content=content)
    except Exception as e:
        logger.error(f"❌ Ошибка при просмотре документа {doc_id}: {e}")
        flash(f'Ошибка при просмотре документа: {str(e)}', 'danger')
        return redirect(url_for('documents_list'))


# Скачивание документа
@app.route('/download/<int:doc_id>')
@app.route('/download/<int:doc_id>/<format>')
def download_document(doc_id, format='docx'):
    """Скачивание файла документа"""
    try:
        document = Document.query.get_or_404(doc_id)

        if not os.path.exists(document.file_path):
            # Пробуем найти файл по альтернативному пути
            alt_path = os.path.join(app.config['OUTPUT_DIR'], os.path.basename(document.file_path))
            if os.path.exists(alt_path):
                document.file_path = alt_path
                db.session.commit()
            else:
                flash('❌ Файл документа не найден на сервере', 'danger')
                return redirect(url_for('view_document', doc_id=doc_id))

        # Определяем MIME тип для Word
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        # Логируем скачивание
        logger.info(f"📥 Скачивание документа {doc_id} с IP: {request.remote_addr}")

        return send_file(
            document.file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(document.file_path)
        )
    except Exception as e:
        logger.error(f"❌ Ошибка при скачивании документа {doc_id}: {e}")
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
            # Создаем бэкап перед удалением
            backup_dir = os.path.join(app.config['OUTPUT_DIR'], 'backup')
            os.makedirs(backup_dir, exist_ok=True)

            backup_file = os.path.join(backup_dir, f"BACKUP_{os.path.basename(doc_file)}")
            import shutil
            shutil.copy2(doc_file, backup_file)
            logger.info(f"   ✓ Создан бэкап: {backup_file}")

            # Удаляем оригинал
            os.remove(doc_file)
            logger.info(f"   ✓ Удален файл: {doc_file}")

        # Удаляем запись из БД
        db.session.delete(document)
        db.session.commit()

        flash(f'✅ Документ "{doc_title}" успешно удален', 'success')
        logger.info(f"✅ Удален документ ID: {doc_id}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Ошибка при удалении документа {doc_id}: {e}")
        flash(f'❌ Ошибка при удалении документа: {str(e)}', 'danger')

    return redirect(url_for('documents_list'))


# Здоровье сервиса (для мониторинга)
@app.route('/health')
def health_check():
    """Endpoint для проверки работоспособности"""
    try:
        # Проверяем БД
        db.session.execute('SELECT 1').fetchall()

        # Проверяем папки
        dirs_ok = all(os.path.exists(d) for d in [
            app.config['OUTPUT_DIR'],
            app.config['PROTOCOLS_DIR'],
            app.config['RESOLUTIONS_DIR']
        ])

        return jsonify({
            'status': 'healthy' if dirs_ok else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'directories': 'ok' if dirs_ok else 'some missing',
            'version': app.config.get('VERSION', '1.0.0')
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Статистика
@app.route('/stats')
def statistics():
    """Статистика использования системы"""
    try:
        # Общая статистика
        total_docs = Document.query.count()
        protocols = Document.query.filter_by(document_type='protocol').count()
        resolutions = Document.query.filter_by(document_type='resolution').count()

        # Статистика по дням (последние 7 дней)
        last_week = datetime.now() - timedelta(days=7)
        daily_stats = db.session.query(
            db.func.date(Document.created_at).label('date'),
            db.func.count().label('count')
        ).filter(Document.created_at >= last_week).group_by('date').all()

        return jsonify({
            'total_documents': total_docs,
            'protocols': protocols,
            'resolutions': resolutions,
            'daily_stats': [{'date': str(stat[0]), 'count': stat[1]} for stat in daily_stats]
        })
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return jsonify({'error': str(e)}), 500


# Обработчик ошибок 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


# Обработчик ошибок 403 (доступ запрещен)
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403


# Обработчик ошибок 500
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Запуск приложения
if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 СИСТЕМА ДОКУМЕНТООБОРОТА ЗАПУЩЕНА")
    print("=" * 70)
    print(f"\n📁 Рабочая директория: {os.path.abspath(os.path.dirname(__file__))}")
    print(f"📁 Папка output: {app.config['OUTPUT_DIR']}")

    # Получаем IP адреса
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"

    print(f"\n🌐 ЛОКАЛЬНЫЙ ДОСТУП (в вашей сети):")
    print(f"   ▶ http://{local_ip}:5000")
    print(f"   ▶ http://localhost:5000")
    print(f"   ▶ http://127.0.0.1:5000")

    print(f"\n📊 Статистика использования:")
    with app.app_context():
        try:
            total = Document.query.count()
            print(f"   • Всего документов в БД: {total}")
        except:
            print(f"   • База данных готова к работе")

    print(f"\n💡 УПРАВЛЕНИЕ:")
    print(f"   • Чтобы остановить сервер: Ctrl+C")
    print(f"   • Логи сохраняются в: app.log")
    print("=" * 70 + "\n")

    # Запускаем с настройками для внешнего доступа
    app.run(
        debug=True,
        host='0.0.0.0',
        port=app.config.get('PORT', 5000),
        threaded=True
    )