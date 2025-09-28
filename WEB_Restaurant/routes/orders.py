from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from settings import Session
from models import Menu, Order, OrderStatus
from sqlalchemy.orm import joinedload
import sqlite3
import os

bp = Blueprint("orders", __name__)


@bp.route("/menu")
def menu():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        menu_items = db_session.query(Menu).filter(Menu.active == True).all()
        categories = sorted(
            list(set(item.category for item in menu_items if item.category))
        )
    return render_template(
        "menu.html",
        menu_items=menu_items,
        categories=categories,
        t=lambda key: t(key, current_lang),
        lang=current_lang,
    )


@bp.route("/add_to_cart/<int:item_id>", methods=["POST"])
@login_required
def add_to_cart(item_id):
    quantity = int(request.form.get("quantity", 1))

    with Session() as db_session:
        menu_item = db_session.query(Menu).filter(Menu.id == item_id).first()
        if not menu_item:
            flash("dish_not_found", "error")
            return redirect(url_for("orders.menu"))

        existing_order = (
            db_session.query(Order)
            .filter(
                Order.user_id == current_user.id,
                Order.menu_id == item_id,
                Order.status == OrderStatus.PENDING,
            )
            .first()
        )

        if existing_order:
            existing_order.quantity += quantity
            existing_order.total_price = (
                existing_order.menu_item.price * existing_order.quantity
            )
        else:
            new_order = Order(
                user_id=current_user.id,
                menu_id=item_id,
                quantity=quantity,
                total_price=menu_item.price * quantity,
            )
            db_session.add(new_order)

        db_session.commit()
        flash("added_to_cart", "success")
        return redirect(url_for("orders.menu"))


@bp.route("/cart")
@login_required
def cart():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        cart_items = (
            db_session.query(Order)
            .options(joinedload(Order.menu_item))
            .filter(
                Order.user_id == current_user.id, Order.status == OrderStatus.PENDING
            )
            .all()
        )

        total = sum(item.total_price for item in cart_items)

        from app import get_background_settings

        images = get_background_settings()

        return render_template(
            "cart.html",
            cart_items=cart_items,
            total=total,
            background_image=images.get("cart_background_image"),
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/update_cart/<int:order_id>", methods=["POST"])
@login_required
def update_cart(order_id):
    quantity = int(request.form.get("quantity", 1))
    with Session() as db_session:
        order = (
            db_session.query(Order)
            .filter(Order.id == order_id, Order.user_id == current_user.id)
            .first()
        )
        if order and quantity > 0:
            order.quantity = quantity
            order.total_price = order.menu_item.price * quantity
            db_session.commit()
            flash("quantity_updated", "success")
        elif order and quantity == 0:
            db_session.delete(order)
            db_session.commit()
            flash("item_removed_from_cart", "success")
        return redirect(url_for("orders.cart"))


@bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    with Session() as db_session:
        pending_orders = (
            db_session.query(Order)
            .filter(
                Order.user_id == current_user.id, Order.status == OrderStatus.PENDING
            )
            .all()
        )
        for order in pending_orders:
            order.status = OrderStatus.CONFIRMED
        db_session.commit()
        flash("order_placed", "success")
        return redirect(url_for("orders.menu"))


@bp.route("/order_history")
@login_required
def order_history():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        orders_list = (
            db_session.query(Order)
            .options(joinedload(Order.menu_item))
            .filter(Order.user_id == current_user.id)
            .order_by(Order.created_at.desc())
            .all()
        )

        from app import get_background_settings

        images = get_background_settings()

        return render_template(
            "order_history.html",
            orders=orders_list,
            background_image=images.get("order_history_background_image"),
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/cancel_order/<int:order_id>")
@login_required
def cancel_order(order_id):
    with Session() as db_session:
        order = (
            db_session.query(Order)
            .filter(
                Order.id == order_id,
                Order.user_id == current_user.id,
                Order.status == OrderStatus.PENDING,
            )
            .first()
        )

        if order:
            db_session.delete(order)
            db_session.commit()
            flash("order_cancelled", "success")
        else:
            flash("order_cancel_error", "error")

    return redirect(url_for("orders.cart"))


@bp.route("/menu")
def show_menu():
    db_path = os.path.join(os.path.dirname(__file__), "..", "restaurant_db.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu WHERE active = 1")
    menu_items = cursor.fetchall()
    conn.close()
    return render_template("menu.html", menu_items=menu_items)
