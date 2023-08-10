from __future__ import annotations

import logging
import os
from datetime import date
from pathlib import Path
from time import strftime

import flask as f

from app.utils import Example

logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)


#
# -------------------------------------------------------------------
# Settings
# -------------------------------------------------------------------
#


ENVIRONMENT = os.getenv('ENVIRONMENT', 'prod')
DEV = ENVIRONMENT == 'dev'
PROD = ENVIRONMENT == 'prod'

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'ui' / 'templates'
STATIC_DIR = BASE_DIR / 'ui' / 'static'

SITE_NAME = 'Feed Preview'
SITE_HOST = 'feed-preview.fly.dev'
SITE_TAGLINE = 'Generate XML feed previews with social embeds'
SITE_DESCRIPTION = "Generate XML feed previews effortlessly and enhance them with dynamic social embeds. Preview, share, and connect your data in a whole new way."
SITE_IMAGE_URL = '/static/img/social-feeds.webp'
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 450

SITE_TITLE = f'{SITE_NAME} - {SITE_TAGLINE}'
SITE_HOST = SITE_HOST if PROD else 'localhost:8000'
SITE_URL = f'https://{SITE_HOST}' if PROD else f'http://{SITE_HOST}'

CACHE_CONTROL = 3600 if PROD else None  # 1 hour


#
# -------------------------------------------------------------------
# Application
# -------------------------------------------------------------------
#


app = f.Flask(
    import_name='app',
    static_folder=STATIC_DIR,
    template_folder=TEMPLATE_DIR,
)
app.config.update(
    {
        'SECRET_KEY': 'XmGkfiGgRYntIzWO3lMEZtZHmAj0ovPxwY5ltBBj',
        'SEND_FILE_MAX_AGE_DEFAULT': CACHE_CONTROL,
        'SESSION_COOKIE_SAMESITE': 'Lax',
    }
)


@app.after_request
def log_request(response: f.Response):
    args = (
        strftime('[%Y-%b-%d %H:%M]'),
        f.request.remote_addr,
        f.request.method,
        f.request.full_path,
        response.status,
    )
    app.logger.info('%s %s %s %s %s', *args)
    return response


@app.after_request
def add_headers(response: f.Response):
    response.headers['Referrer-Policy'] = 'origin-when-cross-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'deny'
    response.headers['X-XSS-Protection'] = '0'
    response.headers['X-Built-By'] = 'ad9280c159074d9ec90899b584f520606e83d10e'
    return response


@app.context_processor
def add_metadata():
    return {
        'site_name': SITE_NAME,
        'site_url': SITE_URL,
        'page_url': SITE_URL,
        'title': SITE_TITLE,
        'heading': SITE_TAGLINE,
        'description': SITE_DESCRIPTION,
        'image': {
            'url': SITE_IMAGE_URL,
            'alt': SITE_TITLE,
            'width': IMAGE_WIDTH,
            'height': IMAGE_HEIGHT,
        },
        'copyright_year': f'{date.today().year}'
    }


@app.errorhandler(404)
def error_404(_):
    return f.render_template('error.html', '404'), 404


@app.errorhandler(500)
def error_500(_):
    return f.render_template('error.html', '500'), 500


#
# -------------------------------------------------------------------
# App Routes
# -------------------------------------------------------------------
#


@app.route('/', methods=['GET', 'POST'])
def index():
    ex = Example()

    if f.request.method == 'POST':
        url = f.request.form.get('embed_url')
        ex = Example(url)
        ex.process()

    return f.render_template('index.html', ec=ex)
