from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from settings import Session
from models import Menu, Order, OrderStatus, SiteSettings, User, Reservation

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash("access_denied", "error")
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:

        total_orders = db_session.query(Order).count()
        pending_orders = (
            db_session.query(Order).filter(Order.status == OrderStatus.PENDING).count()
        )
        active_menu_items = db_session.query(Menu).filter(Menu.active == True).count()

        return render_template(
            "admin/dashboard.html",
            total_orders=total_orders,
            pending_orders=pending_orders,
            active_menu_items=active_menu_items,
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/menu")
@login_required
@admin_required
def menu_management():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        menu_items = db_session.query(Menu).all()
        return render_template(
            "admin/menu.html",
            menu_items=menu_items,
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/menu/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_menu_item():
    current_lang = session.get("language", "uk")
    from app import t

    if request.method == "POST":
        name = request.form.get("name")
        price = float(request.form.get("price"))
        description = request.form.get("description")
        category = request.form.get("category")
        image_path = request.form.get("image_path", "")

        new_item = Menu(
            name=name,
            price=price,
            description=description,
            category=category,
            image_path=image_path,
        )

        with Session() as db_session:
            db_session.add(new_item)
            db_session.commit()

        flash("dish_added", "success")
        return redirect(url_for("admin.menu_management"))

    return render_template(
        "admin/add_menu.html", t=lambda key: t(key, current_lang), lang=current_lang
    )


@bp.route("/menu/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_menu_item(item_id):
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        item = db_session.query(Menu).filter(Menu.id == item_id).first()

        if not item:
            flash("dish_not_found", "error")
            return redirect(url_for("admin.menu_management"))

        if request.method == "POST":
            item.name = request.form.get("name")
            item.price = float(request.form.get("price"))
            item.description = request.form.get("description")
            item.category = request.form.get("category")
            item.image_path = request.form.get("image_path", "")
            item.active = bool(request.form.get("active"))

            db_session.commit()
            flash("dish_updated", "success")
            return redirect(url_for("admin.menu_management"))

        return render_template(
            "admin/edit_menu.html",
            item=item,
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/menu/delete/<int:item_id>")
@login_required
@admin_required
def delete_menu_item(item_id):
    with Session() as db_session:
        item = db_session.query(Menu).filter(Menu.id == item_id).first()

        if item:
            db_session.delete(item)
            db_session.commit()
            flash("dish_deleted", "success")
        else:
            flash("dish_not_found", "error")
    return redirect(url_for("admin.menu_management"))


@bp.route("/orders")
@login_required
@admin_required
def orders_management():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        orders = db_session.query(Order).order_by(Order.created_at.desc()).all()
        return render_template(
            "admin/orders.html",
            orders=orders,
            OrderStatus=OrderStatus,
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/orders/update_status/<int:order_id>", methods=["POST"])
@login_required
@admin_required
def update_order_status(order_id):
    new_status = request.form.get("status")
    with Session() as db_session:
        order = db_session.query(Order).filter(Order.id == order_id).first()

        if order and new_status in [status.name for status in OrderStatus]:
            order.status = OrderStatus[new_status]
            db_session.commit()
            flash("order_status_updated", "success")
        else:
            flash("status_update_error", "error")

    return redirect(url_for("admin.orders_management"))


@bp.route("/orders/cancel/<int:order_id>")
@login_required
@admin_required
def cancel_order(order_id):
    with Session() as db_session:
        order = db_session.query(Order).filter(Order.id == order_id).first()

        if order:
            order.status = OrderStatus.CANCELLED
            db_session.commit()
            flash("order_cancelled", "success")
        else:
            flash("order_not_found", "error")

    return redirect(url_for("admin.orders_management"))


@bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def site_settings():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        if request.method == "POST":
            settings_data = {
                "main_background_image": request.form.get("main_background_image"),
                "menu_background_image": request.form.get("menu_background_image"),
                "admin_panel_background_image": request.form.get(
                    "admin_panel_background_image"
                ),
                "cart_background_image": request.form.get("cart_background_image"),
                "order_history_background_image": request.form.get(
                    "order_history_background_image"
                ),
                "logo_image": request.form.get("logo_image"),
                "mini_logo_image": request.form.get("mini_logo_image"),
            }

            for setting_name, setting_value in settings_data.items():
                setting = (
                    db_session.query(SiteSettings)
                    .filter(SiteSettings.setting_name == setting_name)
                    .first()
                )

                if setting:
                    setting.setting_value = setting_value
                else:
                    new_setting = SiteSettings(
                        setting_name=setting_name,
                        setting_value=setting_value,
                        description=f"Налаштування {setting_name}",
                    )
                    db_session.add(new_setting)

            db_session.commit()
            flash("settings_saved", "success")
            return redirect(url_for("admin.site_settings"))

        settings = (
            db_session.query(SiteSettings)
            .filter(
                SiteSettings.setting_name.in_(
                    [
                        "main_background_image",
                        "menu_background_image",
                        "admin_panel_background_image",
                        "cart_background_image",
                        "order_history_background_image",
                        "logo_image",
                        "mini_logo_image",
                    ]
                )
            )
            .all()
        )

        settings_dict = {
            setting.setting_name: setting.setting_value for setting in settings
        }

        return render_template(
            "admin/settings.html",
            settings=settings_dict,
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/users")
@login_required
@admin_required
def users_management():
    current_lang = session.get("language", "uk")
    from app import t

    with Session() as db_session:
        users = db_session.query(User).all()
        return render_template(
            "admin/users.html",
            users=users,
            t=lambda key: t(key, current_lang),
            lang=current_lang,
        )


@bp.route("/users/toggle_admin/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_admin_status(user_id):
    if user_id == current_user.id:
        flash("cannot_revoke_self", "error")
        return redirect(url_for("admin.users_management"))

    is_admin = request.form.get("is_admin") == "true"

    with Session() as db_session:
        user = db_session.query(User).filter(User.id == user_id).first()

        if user:
            user.is_admin = is_admin
            db_session.commit()
            if is_admin:
                flash("admin_granted", "success")
            else:
                flash("admin_revoked", "success")
        else:
            flash("user_not_found", "error")

    return redirect(url_for("admin.users_management"))


@bp.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("cannot_delete_self", "error")
        return redirect(url_for("admin.users_management"))

    with Session() as db_session:
        user = db_session.query(User).filter(User.id == user_id).first()

        if user:
            db_session.query(Order).filter(Order.user_id == user_id).delete()
            db_session.query(Reservation).filter(
                Reservation.user_id == user_id
            ).delete()
            db_session.delete(user)
            db_session.commit()
            flash("user_deleted", "success")
        else:
            flash("user_not_found", "error")

    return redirect(url_for("admin.users_management"))
