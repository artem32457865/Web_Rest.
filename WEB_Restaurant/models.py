from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, select, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from settings import Session
from flask_login import UserMixin
from settings import Base
import enum


class OrderStatus(enum.Enum):
    PENDING = "очікує"
    CONFIRMED = "підтверджено"
    PREPARING = "готується"
    READY = "готово"
    DELIVERING = "доставляється"
    COMPLETED = "виконано"
    CANCELLED = "скасовано"


class User(UserMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(String(200), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"User: {self.id}, {self.username}"

    @staticmethod
    def get(user_id: int):
        try:
            with Session() as session:
                user = session.get(User, user_id)
                return user
        except:
            return None

    @classmethod
    def get_by_username(cls, username: str):
        with Session() as session:
            user = session.scalar(select(cls).filter(cls.username == username))
            return user


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    setting_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    setting_value: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"SiteSettings: {self.setting_name} = {self.setting_value}"

    @classmethod
    def get_setting(cls, setting_name):
        """Отримати значення налаштування за назвою"""
        with Session() as session:
            stmt = select(cls).where(cls.setting_name == setting_name)
            result = session.execute(stmt)
            setting = result.scalar_one_or_none()
            return setting.setting_value if setting else None

    @classmethod
    def get_all_backgrounds(cls):
        """Отримати всі налаштування фонових зображень"""
        with Session() as session:
            stmt = select(cls).where(cls.setting_name.like("%background%"))
            result = session.execute(stmt)
            settings = result.scalars().all()
            return {setting.setting_name: setting.setting_value for setting in settings}


class Menu(Base):
    __tablename__ = "menu"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    rating: Mapped[int] = mapped_column(nullable=True, default=5)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(default=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="menu_item")

    def __repr__(self) -> str:
        return f"Menu: {self.id}, {self.name}"


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    total_price: Mapped[float] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    menu_item: Mapped["Menu"] = relationship("Menu", back_populates="orders")

    def __repr__(self) -> str:
        return f"Order: {self.id}, User ID: {self.user_id}, Status: {self.status.value}"


class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    guests: Mapped[int] = mapped_column(default=2)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    user: Mapped["User"] = relationship("User", back_populates="reservations")

    def __repr__(self) -> str:
        return (
            f"Reservation: {self.id}, User ID: {self.user_id}, Time: {self.time_start}"
        )
