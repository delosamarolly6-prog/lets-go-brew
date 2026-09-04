from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask import Flask, render_template, request, redirect, url_for, session
import os
from database import get_connection
from dotenv import load_dotenv

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import (
    save_customer_message,
    get_customer_messages,
    create_user,
    get_user,
    create_default_users,
    get_menu_items,
    create_order
)


# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv(
    "GOOGLE_MAPS_API_KEY"
)


print("================================")
print(
    "Google Maps API Key loaded:",
    bool(GOOGLE_MAPS_API_KEY)
)
print("================================")


# =========================
# FLASK APP
# =========================

app = Flask(__name__, template_folder="templates")

# New secret every time the Flask server starts.
# This clears old browser sessions during development.
app.secret_key = os.urandom(24)

# =========================
# CREATE DEFAULT USERS
# =========================

create_default_users()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "home.html"
    )


# =========================
# MENU
# =========================

@app.route("/menu")
def menu():

    if "user_id" not in session:
        return redirect(url_for("login"))

    menu_items = get_menu_items()

    return render_template(
        "menu.html",
        menu_items=menu_items
    )


# =========================
# ABOUT US
# =========================

@app.route("/about")
def about():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "about.html"
    )


# =========================
# CONTACT US
# =========================

@app.route(
    "/contact",
    methods=["GET", "POST"]
)
def contact():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        save_customer_message(
            name,
            email,
            message
        )

        print("\n==============================")
        print("       CUSTOMER MESSAGE")
        print("==============================")
        print("Name:", name)
        print("Email:", email)
        print("Message:", message)
        print("Status: Saved to Database")
        print("==============================\n")

        return "Message received!"


    return render_template(
        "contact.html",
        google_maps_api_key=GOOGLE_MAPS_API_KEY
    )


# =========================
# LOGIN
# =========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        # Find user
        user = get_user(
            username
        )


        # Check password
        if user and check_password_hash(
            user[3],
            password
        ):

            # Save session
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[4]


            print("\n==============================")
            print("             LOGIN")
            print("==============================")
            print(
                "Username:",
                user[1]
            )
            print(
                "Role:",
                user[4]
            )
            print("==============================\n")


            # =========================
            # ADMIN
            # =========================

            if user[4] == "Admin":

                return redirect(
                    url_for(
                        "admin_dashboard"
                    )
                )


            # =========================
            # STAFF
            # =========================

            elif user[4] == "Staff":

                return redirect(
                    url_for(
                        "staff_dashboard"
                    )
                )


            # =========================
            # CUSTOMER
            # =========================

            else:

                return redirect(
                    url_for("home")
                )


        # =========================
        # INVALID LOGIN
        # =========================

        return render_template(
            "login.html",
            error="Invalid username or password."
        )


    return render_template(
        "login.html"
    )


# =========================
# SIGNUP
# =========================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )


        # Password confirmation
        if password != confirm_password:

            return render_template(
                "signup.html",
                error="Passwords do not match."
            )


        # Check username
        existing_user = get_user(
            username
        )

        if existing_user:

            return render_template(
                "signup.html",
                error="Username already exists."
            )


        # Hash password
        password_hash = generate_password_hash(
            password
        )


        # Create CUSTOMER
        create_user(
            username,
            email,
            password_hash
        )


        print("\n==============================")
        print("          NEW ACCOUNT")
        print("==============================")
        print(
            "Username:",
            username
        )
        print(
            "Email:",
            email
        )
        print("Role: Customer")
        print("==============================\n")


        return redirect(
            url_for("login")
        )


    return render_template(
        "signup.html"
    )


# ==================================================
# ADMIN ACCESS CHECK
# ==================================================

def admin_required():

    if "user_id" not in session:

        return False

    if session.get("role") != "Admin":

        return False

    return True


# ==================================================
# STAFF ACCESS CHECK
# ==================================================

def staff_required():

    if "user_id" not in session:

        return False

    if session.get("role") not in [
        "Staff",
        "Admin"
    ]:

        return False

    return True


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin/dashboard")
def admin_dashboard():

    # =========================
    # ADMIN SECURITY
    # =========================

    if not admin_required():

        return redirect(
            url_for("login")
        )


    # =========================
    # DATABASE CONNECTION
    # =========================

    conn = get_connection()

    cursor = conn.cursor()


    try:

        # =========================
        # MENU ITEMS COUNT
        # =========================

        cursor.execute("""

            SELECT COUNT(*)
            FROM MenuItems

        """)

        menu_count = cursor.fetchone()[0]


        # =========================
        # TODAY'S ORDERS
        # =========================

        cursor.execute("""

            SELECT COUNT(*)
            FROM Orders
            WHERE CAST(order_date AS DATE) = CAST(GETDATE() AS DATE)

        """)

        today_orders = cursor.fetchone()[0]


        # =========================
        # TOTAL MESSAGES
        # =========================

        cursor.execute("""

            SELECT COUNT(*)
            FROM CustomerMessages

        """)

        message_count = cursor.fetchone()[0]


        # =========================
        # TODAY'S SALES
        # ONLY COMPLETED ORDERS
        # =========================

        cursor.execute("""

            SELECT
                ISNULL(SUM(total_amount), 0)
            FROM Orders
            WHERE
                CAST(order_date AS DATE) =
                CAST(GETDATE() AS DATE)

                AND status = 'Completed'

        """)

        today_sales = cursor.fetchone()[0]


        # =========================
        # RECENT ORDERS
        # =========================

        cursor.execute("""

            SELECT TOP 5

                order_id,

                user_id,

                total_amount,

                status,

                order_date

            FROM Orders

            ORDER BY order_date DESC

        """)


        recent_orders = cursor.fetchall()


    except Exception as e:

        print(
            "ADMIN DASHBOARD ERROR:",
            e
        )


        # DEFAULT VALUES

        menu_count = 0

        today_orders = 0

        message_count = 0

        today_sales = 0

        recent_orders = []


    finally:

        cursor.close()

        conn.close()


    # =========================
    # RENDER DASHBOARD
    # =========================

    return render_template(

        "admin/dashboard.html",

        menu_count=menu_count,

        today_orders=today_orders,

        message_count=message_count,

        today_sales=today_sales,

        recent_orders=recent_orders

    )

# =========================
# ADMIN HISTORY
# =========================
@app.route("/admin/history")
def admin_history():

    if not admin_required():

        return redirect(
            url_for("login")
        )

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            o.order_id,
            o.user_id,
            o.order_date,
            o.total_amount,
            o.status,
            u.username

        FROM Orders AS o

        LEFT JOIN Users AS u
            ON o.user_id = u.user_id

        ORDER BY o.order_date DESC
    """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "admin/history.html",
        history=history
    )


# =========================
# ADMIN MENU
# =========================

@app.route("/admin/menu")
def admin_menu():

    if not admin_required():

        return redirect(
            url_for("login")
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                menu_id,
                item_name,
                description,
                price,
                category,
                image,
                availability
            FROM MenuItems
            ORDER BY menu_id
        """)

        rows = cursor.fetchall()

        menu_items = []

        for row in rows:

            menu_items.append({

                "menu_id": row[0],

                "item_name": row[1],

                "description": row[2],

                "price": float(row[3]),

                "category": row[4],

                "image": row[5],

                "availability": row[6]

            })

    except Exception as e:

        print("ADMIN MENU ERROR:", e)

        menu_items = []

    finally:

        cursor.close()
        conn.close()

    return render_template(

        "admin/menu.html",

        menu_items=menu_items

    )



# =========================
# ADMIN ORDERS
# =========================

@app.route("/admin/orders")
def admin_orders():

    if not admin_required():
        return redirect(
            url_for("login")
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                o.order_id,
                o.user_id,
                o.order_date,
                o.total_amount,
                o.status,
                oi.item_name,
                oi.quantity,
                oi.price,
                oi.subtotal
            FROM Orders o
            LEFT JOIN OrderItems oi
                ON o.order_id = oi.order_id
            ORDER BY o.order_date DESC
        """)

        rows = cursor.fetchall()

        orders = {}

        for row in rows:

            order_id = row[0]

            if order_id not in orders:

                orders[order_id] = {
                    "order_id": row[0],
                    "user_id": row[1],
                    "order_date": row[2],
                    "total_amount": row[3],
                    "status": row[4],
                    "items": []
                }

            if row[5] is not None:

                orders[order_id]["items"].append({
                    "item_name": row[5],
                    "quantity": row[6],
                    "price": row[7],
                    "subtotal": row[8]
                })

        orders = list(orders.values())

        return render_template(
            "admin/orders.html",
            orders=orders
        )

    except Exception as e:

        print("ADMIN ORDERS ERROR:", e)

        return "Error loading orders.", 500

    finally:

        cursor.close()
        conn.close()


# =========================
# ADMIN MESSAGES
# =========================

@app.route("/admin/messages")
def admin_messages():

    if not admin_required():

        return redirect(
            url_for("login")
        )

    messages = get_customer_messages()
    
    return render_template(
        "admin/messages.html",
        messages=messages
    )


# =========================
# STAFF DASHBOARD
# =========================

@app.route("/staff/dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    return render_template(
        "staff/dashboard.html"
    )


# =========================
# STAFF ORDERS
# =========================

@app.route("/staff/orders")
def staff_orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only Staff can access
    if session.get("role") != "Staff":
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                o.order_id,
                o.user_id,
                o.order_date,
                o.total_amount,
                o.status,
                oi.item_name,
                oi.quantity,
                oi.price,
                oi.subtotal
            FROM Orders o
            LEFT JOIN OrderItems oi
                ON o.order_id = oi.order_id
            ORDER BY o.order_date DESC
        """)

        rows = cursor.fetchall()

        orders = {}

        for row in rows:

            order_id = row[0]

            if order_id not in orders:

                orders[order_id] = {
                    "order_id": row[0],
                    "user_id": row[1],
                    "order_date": row[2],
                    "total_amount": row[3],
                    "status": row[4],
                    "items": []
                }

            if row[5] is not None:

                orders[order_id]["items"].append({
                    "item_name": row[5],
                    "quantity": row[6],
                    "price": row[7],
                    "subtotal": row[8]
                })

        orders = list(orders.values())

        return render_template(
            "staff/orders.html",
            orders=orders
        )

    except Exception as e:

        print("STAFF ORDERS ERROR:", e)

        return "Error loading staff orders.", 500

    finally:

        cursor.close()
        conn.close()



# =========================
# STAFF UPDATE ORDER STATUS
# =========================

@app.route("/staff/orders/update", methods=["POST"])
def update_order_status():

    if not staff_required():
        return redirect(url_for("login"))

    order_id = request.form.get("order_id")
    status = request.form.get("status")

    allowed_statuses = [
        "Pending",
        "Preparing",
        "Ready",
        "Completed",
        "Cancelled"
    ]

    # Check if valid
    if not order_id or status not in allowed_statuses:
        print("INVALID ORDER STATUS UPDATE")

        return redirect(
            url_for("staff_orders")
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE Orders
            SET status = ?
            WHERE order_id = ?
        """, (
            status,
            order_id
        ))

        conn.commit()

        print(
            f"ORDER #{order_id} STATUS UPDATED TO: {status}"
        )

    except Exception as e:

        conn.rollback()

        print(
            "UPDATE ORDER STATUS ERROR:",
            e
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("staff_orders")
    )


# =========================
# STAFF DELETE ORDER
# =========================

@app.route("/staff/orders/delete", methods=["POST"])
def delete_staff_order():

    if not staff_required():
        return redirect(
            url_for("login")
        )

    order_id = request.form.get("order_id")

    if not order_id:
        return redirect(
            url_for("staff_orders")
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # DELETE ORDER ITEMS FIRST
        cursor.execute("""
            DELETE FROM OrderItems
            WHERE order_id = ?
        """, (
            order_id,
        ))

        # DELETE ORDER
        cursor.execute("""
            DELETE FROM Orders
            WHERE order_id = ?
        """, (
            order_id,
        ))

        conn.commit()

        print(
            f"ORDER #{order_id} DELETED"
        )

    except Exception as e:

        conn.rollback()

        print(
            "DELETE ORDER ERROR:",
            e
        )

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("staff_orders")
    )
# =========================
# STAFF MESSAGES
# =========================

@app.route("/staff/messages")
def staff_messages():

    if not staff_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "staff/messages.html"
    )



@app.route("/checkout", methods=["POST"])
def checkout():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    if not data or "items" not in data:
        return jsonify({
            "success": False,
            "message": "No items found."
        }), 400

    items = data["items"]

    if len(items) == 0:
        return jsonify({
            "success": False,
            "message": "Your cart is empty."
        }), 400

    user_id = session["user_id"]

    total_amount = 0

    for item in items:
        price = float(item["price"])
        quantity = int(item["quantity"])

        total_amount += price * quantity

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO Orders
            (user_id, total_amount, status)
            OUTPUT INSERTED.order_id
            VALUES (?, ?, ?)
        """, (
            user_id,
            total_amount,
            "Pending"
        ))

        order_id = cursor.fetchone()[0]

        for item in items:

            menu_id = int(item["id"])
            item_name = item["name"]
            quantity = int(item["quantity"])
            price = float(item["price"])

            subtotal = price * quantity

            cursor.execute("""
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
            """, (
                order_id,
                menu_id,
                item_name,
                quantity,
                price,
                subtotal
            ))

        conn.commit()

        return jsonify({
            "success": True,
            "order_id": order_id
        })

    except Exception as e:

        conn.rollback()

        print("CHECKOUT ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cursor.close()
        conn.close()
# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )