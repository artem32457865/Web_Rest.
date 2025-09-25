from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from settings import Session
from models import Menu, Order, OrderStatus
from sqlalchemy.orm import joinedload

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            current_lang = session.get('language', 'uk')
            from app import t
            flash(t('Доступ заборонено. Потрібні права адміністратора'), "error")
            return redirect(url_for("index"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    current_lang = session.get('language', 'uk')
    from app import t
    
    with Session() as session_db:
        total_orders = session_db.query(Order).count()
        pending_orders = session_db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
        active_menu_items = session_db.query(Menu).filter(Menu.active == True).count()
    
    return render_template("admin/dashboard.html", 
                         total_orders=total_orders, 
                         pending_orders=pending_orders, 
                         active_menu_items=active_menu_items,
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

@bp.route("/menu")
@login_required
@admin_required
def menu_management():
    current_lang = session.get('language', 'uk')
    from app import t
    
    with Session() as session_db:
        menu_items = session_db.query(Menu).all()
    
    return render_template("admin/menu.html", 
                         menu_items=menu_items,
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

@bp.route("/menu/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_menu_item():
    current_lang = session.get('language', 'uk')
    from app import t
    
    if request.method == "POST":
        name = request.form.get("name")
        price = float(request.form.get("price"))
        description = request.form.get("description")
        category = request.form.get("category")
        image_path = request.form.get("image_path", "")
        
        new_item = Menu(
            name=name, price=price, description=description, 
            category=category, image_path=image_path
        )
        
        with Session() as session_db:
            session_db.add(new_item)
            session_db.commit()
            flash(t('Страву додано успішно'), "success")
            return redirect(url_for("admin.menu_management"))
    
    return render_template("admin/add_menu.html",
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

@bp.route("/menu/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_menu_item(item_id):
    current_lang = session.get('language', 'uk')
    from app import t
    
    with Session() as session_db:
        item = session_db.query(Menu).filter(Menu.id == item_id).first()
        if not item:
            flash(t('Страву не знайдено'), "error")
            return redirect(url_for("admin.menu_management"))
        
        if request.method == "POST":
            item.name = request.form.get("name")
            item.price = float(request.form.get("price"))
            item.description = request.form.get("description")
            item.category = request.form.get("category")
            item.image_path = request.form.get("image_path", "")
            item.active = bool(request.form.get("active"))
            session_db.commit()
            flash(t('Страву оновлено успішно'), "success")
            return redirect(url_for("admin.menu_management"))
    
    return render_template("admin/edit_menu.html", 
                         item=item,
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

@bp.route("/menu/delete/<int:item_id>")
@login_required
@admin_required
def delete_menu_item(item_id):
    current_lang = session.get('language', 'uk')
    from app import t
    
    with Session() as session_db:
        item = session_db.query(Menu).filter(Menu.id == item_id).first()
        if item:
            session_db.delete(item)
            session_db.commit()
            flash(t('Страву видалено успішно'), "success")
        else:
            flash(t('Страву не знайдено'), "error")
    return redirect(url_for("admin.menu_management"))

@bp.route("/orders")
@login_required
@admin_required
def orders_management():
    current_lang = session.get('language', 'uk')
    from app import t
    
    with Session() as session_db:
        # Используем eager loading для загрузки связанных данных
        orders = session_db.query(Order).options(
            joinedload(Order.user),
            joinedload(Order.menu_item)
        ).order_by(Order.created_at.desc()).all()
    
    return render_template("admin/orders.html", 
                         orders=orders, 
                         OrderStatus=OrderStatus,
                         t=lambda key: t(key, current_lang),
                         lang=current_lang)

@bp.route("/orders/update_status/<int:order_id>", methods=["POST"])
@login_required
@admin_required
def update_order_status(order_id):
    current_lang = session.get('language', 'uk')
    from app import t
    
    new_status = request.form.get("status")
    with Session() as session_db:
        order = session_db.query(Order).filter(Order.id == order_id).first()
        if order and new_status in [status.name for status in OrderStatus]:
            order.status = OrderStatus[new_status]
            session_db.commit()
            flash(t('Статус замовлення оновлено'), "success")
        else:
            flash(t('Помилка оновлення статусу'), "error")
    return redirect(url_for("admin.orders_management"))

@bp.route("/orders/cancel/<int:order_id>")
@login_required
@admin_required
def cancel_order(order_id):
    current_lang = session.get('language', 'uk')
    from app import t
    
    with Session() as session_db:
        order = session_db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.CANCELLED
            session_db.commit()
            flash(t('Замовлення скасовано адміном'), "success")
        else:
            flash(t('Замовлення не знайдено'), "error")
    return redirect(url_for("admin.orders_management"))