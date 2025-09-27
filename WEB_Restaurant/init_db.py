from models import Base, User, Menu, Order, Reservation, SiteSettings
from settings import Session
from werkzeug.security import generate_password_hash


def init_db():
    base = Base()

    print("=" * 50)
    print("ІНІЦІАЛІЗАЦІЯ БАЗИ ДАНИХ Sushi Monsters")
    print("=" * 50)

    choice = input("Видалити всі дані та створити нову базу? (y/n): ").lower()

    if choice == "y":
        print("Видаляємо стару базу даних...")
        base.drop_db()
        print("Створюємо нову базу даних...")
        base.create_db()
        print("Базу даних створено!")
    else:
        print("Просто створюємо таблиці (якщо не існують)...")
        base.create_db()
        print("Базу даних перевірено!")

    session = Session()

    existing_admin = session.query(User).filter(User.username == "sushi_admin").first()
    if not existing_admin:

        admin_user = User(
            username="sushi_admin",
            email="admin@sushi-bar.ua",
            hash_password=generate_password_hash("SushiAdmin123!"),
            is_admin=True,
        )
        session.add(admin_user)
        print(" Адміністратора створено!")
        print("   Логін: sushi_admin")
        print("   Пароль: SushiAdmin123!")
        print("   Email: admin@sushi-bar.ua")
    else:
        print("  Адміністратор вже існує!")

    # Перевіряємо чи тестовий користувач вже існує
    existing_test_user = (
        session.query(User).filter(User.username == "test_user").first()
    )
    if not existing_test_user:
        # Створюємо тестового користувача
        test_user = User(
            username="test_user",
            email="test@user.ua",
            hash_password=generate_password_hash("TestUser123!"),
            is_admin=False,
        )
        session.add(test_user)
        print(" Тестового користувача створено!")
        print("   Логін: test_user")
        print("   Пароль: TestUser123!")
    else:
        print("  Тестовий користувач вже існує!")

    # Додавання налаштувань сайту (фонові зображення)
    existing_settings = session.query(SiteSettings).first()
    if not existing_settings:
        background_settings = [
            SiteSettings(
                setting_name="main_background_image",
                setting_value="https://media.discordapp.net/attachments/1417846956751061053/1420711858729385994/G_fon.png?ex=68d66486&is=68d51306&hm=e87798775fec547b3e4d135257e2b1ccc68518cc49ed11441c64030652c9bee6&=&quality=lossless",
                description="Головне фонове зображення сайту",
            ),
            SiteSettings(
                setting_name="menu_background_image",
                setting_value="https://media.discordapp.net/attachments/1417846956751061053/1420711860034076772/menu_fon.png?ex=68d66486&is=68d51306&hm=6cc45fe56373dc1d59cfb8aa22ce40cea11e8fa9d80a577a52f6faab8103f752&=&quality=lossless",
                description="Фонове зображення сторінки меню",
            ),
            SiteSettings(
                setting_name="admin_panel_background_image",
                setting_value="https://media.discordapp.net/attachments/1333041787111215125/1420733710487257108/admin_panel_fon.jpg?ex=68d678e0&is=68d52760&hm=e36c325140c045a20b29a08319a85643e1cbfad47905e2c24d6cb5dbe331ead4&=",
                description="Фонове зображення сторінки адміністратора",
            ),
            SiteSettings(
                setting_name="logo_image",
                setting_value="https://media.discordapp.net/attachments/1208013883202338868/1421143982196396092/logo_sushi_monsters.png?ex=68d7f6f8&is=68d6a578&hm=17d3df32c9a1cf3a54e19e186d7eac0cab36e0325e38f92e3b96b837736d0d2c&=&quality=lossless",
                description="Логотип сайту",
            ),
            SiteSettings(
                setting_name="mini_logo_image",
                setting_value="https://media.discordapp.net/attachments/1417846956751061053/1420471946776154345/logo_sushi_monsters.png?ex=68d77f57&is=68d62dd7&hm=9981d4237beb4f8ea066f7c2ee5779a3296624aea9c31aaf255f6532f1ca6e56&=&quality=lossless",
                description="Логотип сайту у навігації",
            ),
            SiteSettings(
                setting_name="cart_background_image",
                setting_value="https://media.discordapp.net/attachments/1333041787111215125/1420733710835388527/cart_fon.jpg?ex=68d678e0&is=68d52760&hm=1b8ab723177dc6cef954859e582720f4385413a795325a7af66a7f07b634662a&=",
                description="Фон для сторінки корзини",
            ),
            SiteSettings(
                setting_name="order_history_background_image",
                setting_value="https://media.discordapp.net/attachments/1333041787111215125/1420733710835388527/cart_fon.jpg?ex=68d678e0&is=68d52760&hm=1b8ab723177dc6cef954859e582720f4385413a795325a7af66a7f07b634662a&=",
                description="Фон для сторінки історії замовлень",
            ),
        ]

        for setting in background_settings:
            session.add(setting)
        print(f"✅ Додано {len(background_settings)} налаштувань сайту!")
    else:
        settings_count = session.query(SiteSettings).count()
        print(f"  Налаштування сайту вже існують! Кількість: {settings_count}")

    existing_menu = session.query(Menu).first()
    if not existing_menu:

        menu_items = [
            Menu(
                name="Філадельфія класична",
                price=320.00,
                rating=5,
                description="Лосось, вершковий сир, огірок, авокадо, норі",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420074980946743326/philadelphia_roll.jpg?ex=68d564e3&is=68d41363&hm=dec1f385253652b2621e90be1e70e429014ab2c536ae4574e745dfd8fbf11002&=",
                category="Роли",
                active=True,
            ),
            Menu(
                name="Каліфорнія з вугрем",
                price=280.00,
                rating=4,
                description="Вугор, вершковий сир, авокадо, ікра масаго",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420074979139125359/california_roll.jpg?ex=68d564e2&is=68d41362&hm=3b74c332bbc97ca5b0efa0077c0e10ca2dc19842b7d6431a3841f59ae6e60ffd&=",
                category="Роли",
                active=True,
            ),
            Menu(
                name="Сет 'Самурай'",
                price=650.00,
                rating=5,
                description="8 ролів: філадельфія, каліфорнія, з лососем та тунцем",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454306896674948/set_samurai.jpg?ex=68d574a9&is=68d42329&hm=e4556dbabdc6a0ad0e0eb3d9006048822e85b8120aa9526f6686ff8a21c37932&=",
                category="Сети",
                active=True,
            ),
            Menu(
                name="Місо суп",
                price=120.00,
                rating=4,
                description="Традиційний японський суп з пастою місо, тофу та водоростями",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454306548813835/miso_soup.jpg?ex=68d574a9&is=68d42329&hm=ad6a251517ce310c4dd994a6d02788cb5fa02adbba3670c0404294271a757b3b&=",
                category="Супи",
                active=True,
            ),
            Menu(
                name="Темпура з креветок",
                price=180.00,
                rating=4,
                description="Креветки в хрусткому тісті темпура з соусом",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454306196230236/shrimp_tempura.jpg?ex=68d574a9&is=68d42329&hm=c9ee92323fdf1e57040a4d66eeeaa2cf0363cd22aee16133e82d470e47c62f76&=",
                category="Гарячі страви",
                active=True,
            ),
            Menu(
                name="Запечений рол з лососем",
                price=220.00,
                rating=5,
                description="Лосось, вершковий сир, запечені під соусом унагі",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454305923858452/baked_salmon_roll.jpg?ex=68d574a9&is=68d42329&hm=b7f0a423c37e29ebf1e7cbe6689b06dc7174e1e66188e182f018b64db575a056&=",
                category="Запечені роли",
                active=True,
            ),
            Menu(
                name="Гункани з тунцем",
                price=150.00,
                rating=4,
                description="4 шт., тунець, ікра тобіко, майонез",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454305504432281/tuna_gunkans.jpg?ex=68d574a9&is=68d42329&hm=8fb91cf6be6beb69b1523aef3e3dd98370b0c801222b08ab304bbc4e54f81db2&=&",
                category="Гункани",
                active=True,
            ),
            Menu(
                name="Спайсі рол з креветкою",
                price=190.00,
                rating=4,
                description="Креветка, огірок, спайсі соус, ікра масаго",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454307760967834/spicy_shrimp_roll.jpg?ex=68d574a9&is=68d42329&hm=5448b08e5d1349abe1b167b9b7232459e1d62f2143ddd5528c5b38b4b0c1a99e&=",
                category="Спайсі роли",
                active=True,
            ),
            Menu(
                name="Вегетаріанський сет",
                price=380.00,
                rating=4,
                description="Роли з авокадо, огірком, перцем та морквою",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420454307194474597/vegetarian_set.jpg?ex=68d574a9&is=68d42329&hm=f8c0a6b5330ef983b0249bbc25c35d05f00b59b615babd171e4805e0ab190839&=",
                category="Сети",
                active=True,
            ),
            Menu(
                name="Чай зелений",
                price=50.00,
                rating=5,
                description="Якісний зелений чай на порцію",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420074979843768513/green_tea.jpg?ex=68d564e2&is=68d41362&hm=74f4fd2814aa3583011f51cc4a2ed4bf9a2f5f2d322156b9e8af0a37ef47a87f&=",
                category="Напої",
                active=True,
            ),
            Menu(
                name="Мочі",
                price=80.00,
                rating=4,
                description="Солодкі рисові кліцки з різними начинками",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420074980380643338/mochi.jpg?ex=68d564e3&is=68d41363&hm=054a6f83cc05575d6462bbb12475bd9e07c6cfa6bce8bc21087a1a02cd12ac93&=",
                category="Десерти",
                active=True,
            ),
            Menu(
                name="Сашимі з лосося",
                price=200.00,
                rating=5,
                description="Свіжий лосось, тонко нарізаний",
                image_path="https://media.discordapp.net/attachments/1417846956751061053/1420074981471158366/sashimi.jpg?ex=68d564e3&is=68d41363&hm=3fd064c8104547230c27dde8556d0fbd84f09e2a22372791be6ddbd7748c62b4&=",
                category="Сашимі",
                active=True,
            ),
        ]

        for item in menu_items:
            session.add(item)
        print(f"✅ Додано {len(menu_items)} страв меню!")
    else:
        menu_count = session.query(Menu).count()
        print(f"  Меню вже заповнене! Кількість страв: {menu_count}")

    try:
        session.commit()
        print("=" * 50)
        print(" БАЗУ ДАНИХ УСПІШНО ІНІЦІАЛІЗОВАНО!")
        print("=" * 50)

        users_count = session.query(User).count()
        menu_count = session.query(Menu).count()
        settings_count = session.query(SiteSettings).count()
        admins_count = session.query(User).filter(User.is_admin == True).count()

        print(f"Користувачів у системі: {users_count}")
        print(f"Адміністраторів: {admins_count}")
        print(f"Налаштувань сайту завантажено: {settings_count}")
        print(f"Страв у меню: {menu_count}")
        print("=" * 50)

    except Exception as e:
        session.rollback()
        print(f" Помилка при збереженні даних: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
