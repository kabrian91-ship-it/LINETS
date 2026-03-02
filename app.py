from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# -------------------------
# LANGUAGE SYSTEM
# -------------------------
LANGUAGES = {
    "en": {
        "title": "LINETS MAMA E SHOP",
        "add_product": "Add Product",
        "products": "Products",
        "stock": "Stock",
        "price": "Price",
        "save": "Save",
        "chatbot": "Shop Assistant"
    },
    "sw": {
        "title": "DUKA LA LINETS MAMA E",
        "add_product": "Ongeza Bidhaa",
        "products": "Bidhaa",
        "stock": "Hisa",
        "price": "Bei",
        "save": "Hifadhi",
        "chatbot": "Msaidizi wa Duka"
    }
}

current_lang = "en"

# -------------------------
# DATABASE
# -------------------------
def init_db():
    conn = sqlite3.connect("linets_mama_e_shop.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        category TEXT,
        buying_price REAL,
        selling_price REAL,
        image TEXT,
        current_stock INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# HOME PAGE
# -------------------------
@app.route("/", methods=["GET"])
def home():
    global current_lang
    lang = LANGUAGES[current_lang]

    conn = sqlite3.connect("linets_mama_e_shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    return render_template_string("""
    <html>
    <head>
        <title>{{lang.title}}</title>
        <style>
            body {
                margin:0;
                font-family: Arial;
                background: url('https://images.unsplash.com/photo-1607082350899-7e105aa886ae') no-repeat center center fixed;
                background-size: cover;
            }
            .overlay {
                background: rgba(0,0,0,0.7);
                min-height: 100vh;
                padding: 40px;
                color: white;
            }
            h1 {
                text-align: center;
                letter-spacing: 2px;
            }
            .nav {
                text-align:center;
                margin-bottom: 20px;
            }
            .nav a {
                background:#00c6ff;
                padding:10px 20px;
                border-radius:25px;
                margin:5px;
                color:white;
                text-decoration:none;
                font-weight:bold;
                transition:0.3s;
            }
            .nav a:hover {
                background:#0072ff;
                transform:scale(1.1);
            }
            .products {
                display:flex;
                flex-wrap:wrap;
                gap:20px;
                justify-content:center;
            }
            .card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding:15px;
                border-radius:15px;
                width:220px;
                text-align:center;
                box-shadow:0 0 15px rgba(0,0,0,0.5);
                transition:0.3s;
            }
            .card:hover {
                transform: translateY(-10px);
            }
            .card img {
                width:100%;
                height:150px;
                object-fit:cover;
                border-radius:10px;
            }
            .price {
                color:#00ffcc;
                font-weight:bold;
                font-size:18px;
            }
            .stock {
                background:#ff9800;
                padding:3px 8px;
                border-radius:10px;
                font-size:12px;
            }
            .chatbox {
                margin-top:40px;
                background:rgba(255,255,255,0.1);
                padding:20px;
                border-radius:15px;
                text-align:center;
            }
            input {
                padding:8px;
                width:60%;
                border-radius:20px;
                border:none;
                outline:none;
            }
            button {
                padding:8px 15px;
                border-radius:20px;
                border:none;
                background:#00c6ff;
                color:white;
                cursor:pointer;
                font-weight:bold;
            }
            button:hover {
                background:#0072ff;
            }
        </style>
    </head>
    <body>
        <div class="overlay">
            <h1>{{lang.title}}</h1>

            <div class="nav">
                <a href="/add">{{lang.add_product}}</a>
                <a href="/switch/en">English</a>
                <a href="/switch/sw">Swahili</a>
            </div>

            <div class="products">
                {% for p in products %}
                <div class="card">
                    {% if p[5] %}
                        <img src="{{p[5]}}">
                    {% else %}
                        <img src="https://via.placeholder.com/200">
                    {% endif %}
                    <h3>{{p[1]}}</h3>
                    <div class="price">${{p[4]}}</div>
                    <span class="stock">Stock: {{p[6]}}</span>
                </div>
                {% endfor %}
            </div>

            <div class="chatbox">
                <h3>{{lang.chatbot}}</h3>
                <form method="post" action="/chat">
                    <input name="message" placeholder="Ask about stock, profit, products...">
                    <button type="submit">Send</button>
                </form>
                {% if response %}
                    <p><b>Bot:</b> {{response}}</p>
                {% endif %}
            </div>

        </div>
    </body>
    </html>
    """, products=products, lang=lang)

# -------------------------
# ADD PRODUCT
# -------------------------
@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        buying_price = request.form["buying_price"]
        selling_price = request.form["selling_price"]
        image = request.form["image"]

        conn = sqlite3.connect("linets_mama_e_shop.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (product_name, category, buying_price, selling_price, image, current_stock)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (name, category, buying_price, selling_price, image))
        conn.commit()
        conn.close()

        return redirect("/")

    return """
    <h2>Add Product</h2>
    <form method="post">
        Name:<br><input name="name"><br><br>
        Category:<br><input name="category"><br><br>
        Buying Price:<br><input name="buying_price"><br><br>
        Selling Price:<br><input name="selling_price"><br><br>
        Image URL:<br><input name="image"><br><br>
        <button type="submit">Save</button>
    </form>
    """

# -------------------------
# SMART CHATBOT
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    message = request.form["message"].lower()
    conn = sqlite3.connect("linets_mama_e_shop.db")
    cursor = conn.cursor()

    response = "I did not understand."

    if "stock" in message:
        cursor.execute("SELECT SUM(current_stock) FROM products")
        total = cursor.fetchone()[0]
        response = f"Total stock available is {total}"
    elif "products" in message:
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        response = f"You have {count} products in your shop."
    elif "profit" in message:
        response = "Profit = Selling Price minus Buying Price."
    elif "hello" in message:
        response = "Hello 👋 Welcome to Linets Mama E Shop!"

    conn.close()

    return render_template_string(
        "<script>alert('{}'); window.location.href='/'</script>".format(response)
    )

# -------------------------
# LANGUAGE SWITCH
# -------------------------
@app.route("/switch/<language>")
def switch(language):
    global current_lang
    if language in LANGUAGES:
        current_lang = language
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
