from page_analyzer.parser import check_page
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)

import os
import requests
from dotenv import load_dotenv

from page_analyzer.url_validator import is_valid_url, normalize_url
from .database import (
    check_url_existence,
    add_urls,
    get_one_url,
    get_all_urls,
    create_check_entry,
    get_checks_for_url,
)


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.post('/urls')
def add_url():
    """Добавление нового URL"""
    url_name = request.form.get('url', '')

    if not is_valid_url(url_name):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized_url_name = normalize_url(url_name)
    existing_url_id = check_url_existence(app, normalized_url_name)

    if existing_url_id:
        flash('Страница уже существует', 'info')
        return redirect(url_for('show_url_by_id', url_id=existing_url_id))

    new_url_id = add_urls(app, normalized_url_name)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url_by_id', url_id=new_url_id))


@app.get('/urls')
def get_urls():
    """Список всех URL"""
    urls = get_all_urls(app)
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:url_id>')
def show_url_by_id(url_id):
    """Страница конкретного URL"""
    url_obj = get_one_url(app, url_id)

    if not url_obj:
        flash('URL не найден', 'danger')
        return redirect(url_for('get_urls'))

    url_checks = get_checks_for_url(app, url_id)
    return render_template('url.html', url=url_obj, url_checks=url_checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def create_check(id):
    """Запуск проверки URL"""
    url_obj = get_one_url(app, id)

    if not url_obj:
        flash('URL не найден', 'danger')
        return redirect(url_for('get_urls'))

    try:
        response = requests.get(url_obj['name'], timeout=15)
        response.raise_for_status()

        parsed_data = check_page(response.text)
        create_check_entry(
            app,
            url_obj['id'],
            response.status_code,
            parsed_data.get('h1'),
            parsed_data.get('title'),
            parsed_data.get('description'),
        )
        flash('Страница успешно проверена', 'success')

    except requests.exceptions.HTTPError:
        flash('Произошла ошибка при проверке', 'danger')
    except requests.exceptions.Timeout:
        flash('Произошла ошибка при проверке', 'danger')
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('show_url_by_id', url_id=id))
