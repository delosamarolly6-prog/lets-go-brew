import pyodbc
from werkzeug.security import generate_password_hash


# =========================
# DATABASE CONNECTION
# =========================

def get_connection():

    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-FT0GAS8D\\SQLEXPRESS;"
        "DATABASE=breww;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


# =========================
# SAVE CUSTOMER MESSAGE
# =========================

def save_customer_message(name, email, message):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO CustomerMessages
        (customer_name, email, message, date_sent, status)
        VALUES (?, ?, ?, GETDATE(), 'Unread')
    """

    cursor.execute(
        query,
        (name, email, message)
    )

    connection.commit()

    cursor.close()
    connection.close()


# =========================
# GET CUSTOMER MESSAGES
# =========================

def get_customer_messages():

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            message_id,
            customer_name,
            email,
            message,
            date_sent,
            status
        FROM CustomerMessages
        ORDER BY date_sent DESC
    """

    cursor.execute(query)

    messages = cursor.fetchall()

    cursor.close()
    connection.close()

    return messages


# =========================
# CREATE USER
# =========================

def create_user(username, email, password_hash):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO Users
        (username, email, password_hash, role)
        VALUES (?, ?, ?, 'Customer')
    """

    cursor.execute(
        query,
        (username, email, password_hash)
    )

    connection.commit()

    cursor.close()
    connection.close()


# =========================
# GET USER
# =========================

def get_user(username):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            user_id,
            username,
            email,
            password_hash,
            role
        FROM Users
        WHERE username = ?
    """

    cursor.execute(
        query,
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


# =========================
# CREATE DEFAULT ADMIN
# AND STAFF USERS
# =========================

def create_default_users():

    connection = get_connection()
    cursor = connection.cursor()

    # =========================
    # ADMIN
    # =========================

    cursor.execute(
        """
        SELECT user_id
        FROM Users
        WHERE username = ?
        """,
        ("admin",)
    )

    admin_exists = cursor.fetchone()

    if not admin_exists:

        admin_password = generate_password_hash(
            "admin123"
        )

        cursor.execute(
            """
            INSERT INTO Users
            (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                "admin",
                "admin@lets-go-brew.com",
                admin_password,
                "Admin"
            )
        )

        print("Default Admin account created.")


    # =========================
    # STAFF
    # =========================

    cursor.execute(
        """
        SELECT user_id
        FROM Users
        WHERE username = ?
        """,
        ("staff",)
    )

    staff_exists = cursor.fetchone()

    if not staff_exists:

        staff_password = generate_password_hash(
            "staff123"
        )

        cursor.execute(
            """
            INSERT INTO Users
            (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                "staff",
                "staff@lets-go-brew.com",
                staff_password,
                "Staff"
            )
        )

        print("Default Staff account created.")


    connection.commit()

    cursor.close()
    connection.close()

    print("==============================")
    print("DEFAULT USERS CHECKED")
    print("==============================")
    # =========================
# GET MENU ITEMS
# =========================

def get_menu_items():

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            menu_id,
            item_name,
            description,
            price,
            category,
            image,
            availability
        FROM MenuItems
        WHERE availability = 'Available'
        ORDER BY menu_id
    """

    cursor.execute(query)

    menu_items = cursor.fetchall()

    cursor.close()
    connection.close()

    return menu_items
# =========================
# CREATE ORDER
# =========================

def create_order(user_id, cart_items):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # =========================
        # COMPUTE TOTAL
        # =========================

        total_amount = 0

        for item in cart_items:

            price = float(item["price"])
            quantity = int(item["quantity"])

            total_amount += price * quantity


        # =========================
        # CREATE ORDER
        # =========================

        cursor.execute(
            """
            INSERT INTO Orders
            (
                user_id,
                total_amount,
                status
            )
            OUTPUT INSERTED.order_id
            VALUES (?, ?, 'Pending')
            """,
            (
                user_id,
                total_amount
            )
        )

        order_id = cursor.fetchone()[0]


        # =========================
        # CREATE ORDER ITEMS
        # =========================

        for item in cart_items:

            price = float(item["price"])
            quantity = int(item["quantity"])

            subtotal = price * quantity

            cursor.execute(
                """
                INSERT INTO OrderItems
                (
                    order_id,
                    menu_id,
                    item_name,
                    quantity,
                    price,
                    subtotal
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    int(item["id"]),
                    item["name"],
                    quantity,
                    price,
                    subtotal
                )
            )


        # =========================
        # SAVE
        # =========================

        connection.commit()

        print("==============================")
        print("ORDER CREATED")
        print("==============================")
        print("Order ID:", order_id)
        print("User ID:", user_id)
        print("Total:", total_amount)
        print("==============================")


        return order_id


    except Exception as e:

        connection.rollback()

        print("ORDER ERROR:", e)

        return None


    finally:

        cursor.close()
        connection.close()