from flask import Flask, render_template, request, session, redirect, url_for, flash
from sqlalchemy import select
from unicodedata import category
from settings import DatabaseConfig, Session
from flask_login import LoginManager
from models import User, Menu, SiteSettings, Order
from routes import auth, admin, orders
from flask_wtf.csrf import CSRFProtect
from translations import translations
import os

app = Flask(__name__)
app.config.from_object(DatabaseConfig)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-for-development')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['REMEMBER_COOKIE_DURATION'] = 3600

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.remember_cookie_duration = 3600

csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    return user

@login_manager.user_loader
def load_user_from_session(user_id):
    try:
        return User.get(int(user_id))
    except:
        return None

# Функция для получения перевода
def t(key, lang='uk'):
    return translations.get(lang, {}).get(key, key)

# Маршрут для смены языка
@app.route("/set_language/<language>")
def set_language(language):
    if language in ['uk', 'en']:
        session['language'] = language
        current_lang = session.get('language', 'uk')
        flash(f"{t('Мову змінено на', current_lang)} {language.upper()}", 'success')
    return redirect(request.referrer or url_for('index'))

@app.route("/")
def index():
    images = get_background_settings()
    current_lang = session.get('language', 'uk')
    return render_template("index.html", 
                         background_image=images.get('main_background_image'),
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

@app.route("/admin/dashboard")
def dashboard():
    images = get_background_settings()
    current_lang = session.get('language', 'uk')
    with Session() as session_db:
        total_orders = session_db.query(Order).count()
        pending_orders = session_db.query(Order).filter(Order.status == 'PENDING').count()
        active_menu_items = session_db.query(Menu).filter_by(active=True).count()
    
    return render_template("admin/dashboard.html", 
                         background_image=images.get('admin_panel_background_image'),
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         active_menu_items=active_menu_items,
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

# Отримання фонових зображень
def get_background_settings():
    """Отримує налаштування фонових зображень з бази даних"""
    backgrounds = {}
    with Session() as session_db:
        settings = session_db.query(SiteSettings).filter(
            SiteSettings.setting_name.in_([
                'main_background_image',
                'menu_background_image', 
                'admin_panel_background_image',
                'cart_background_image',
                'order_history_background_image'
            ])
        ).all()
        for setting in settings:
            backgrounds[setting.setting_name] = setting.setting_value
    return backgrounds

app.register_blueprint(auth.bp, url_prefix="/auth")
app.register_blueprint(admin.bp)
app.register_blueprint(orders.bp)

# Обробники помилок
@app.errorhandler(404)
def not_found_error(error):
    current_lang = session.get('language', 'uk')
    return render_template('errors/404.html', 
                         t=lambda key: t(key, current_lang),
                         lang=current_lang), 404

@app.errorhandler(403)
def forbidden_error(error):
    current_lang = session.get('language', 'uk')
    return render_template('errors/403.html', 
                         t=lambda key: t(key, current_lang),
                         lang=current_lang), 403

@app.errorhandler(401)
def unauthorized_error(error):
    current_lang = session.get('language', 'uk')
    return render_template('errors/401.html', 
                         t=lambda key: t(key, current_lang),
                         lang=current_lang), 401

@app.errorhandler(500)
def internal_error(error):
    current_lang = session.get('language', 'uk')
    return render_template('errors/500.html', 
                         t=lambda key: t(key, current_lang),
                         lang=current_lang), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)