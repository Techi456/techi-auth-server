from flask import Flask, request, jsonify, render_template_string
import uuid
import json
import time
import os

app = Flask(__name__)

TOKENS_FILE = "tokens.json"

def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------------------------
# GENERA LINK TEMPORANEO
# -------------------------
@app.route("/generate/<user_code>")
def generate(user_code):
    token = uuid.uuid4().hex[:6].upper()
    expires = time.time() + 600  # 10 minuti

    data = load_tokens()
    data[token] = {
        "user_code": user_code,
        "expires": expires,
        "confirmed": False,
        "trello_key": None,
        "trello_token": None
    }
    save_tokens(data)

    return jsonify({
        "login_url": f"https://{request.host}/auth/{token}",
        "token": token,
        "expires_in": 600
    })

# -------------------------
# PAGINA DI LOGIN
# -------------------------
PAGE = """
<html>
<head>
<title>Techi Login</title>
</head>
<body style="font-family:Arial; text-align:center; margin-top:50px;">
<h2>Autorizza Techi</h2>
<p>Token: {{token}}</p>

<form action="/confirm" method="POST">
    <input type="hidden" name="token" value="{{token}}">
    <button type="submit">Autorizza</button>
</form>

</body>
</html>
"""

@app.route("/auth/<token>")
def auth_page(token):
    return render_template_string(PAGE, token=token)

# -------------------------
# CONFERMA ACCESSO
# -------------------------
@app.route("/confirm", methods=["POST"])
def confirm():
    token = request.form.get("token")
    data = load_tokens()

    if token not in data:
        return "Token non valido", 400

    if time.time() > data[token]["expires"]:
        return "Token scaduto", 400

    data[token]["confirmed"] = True
    save_tokens(data)

    return "Accesso confermato! Puoi tornare su Telegram."

# -------------------------
# CONTROLLO TOKEN
# -------------------------
@app.route("/check/<token>")
def check(token):
    data = load_tokens()

    if token not in data:
        return jsonify({"valid": False})

    if time.time() > data[token]["expires"]:
        return jsonify({"valid": False})

    return jsonify(data[token])

# -------------------------
# SALVA CREDENZIALI TRELLO
# -------------------------
@app.route("/trello", methods=["POST"])
def trello():
    body = request.json
    token = body.get("token")
    key = body.get("trello_key")
    ttoken = body.get("trello_token")

    data = load_tokens()

    if token not in data:
        return jsonify({"error": "Token non valido"}), 400

    data[token]["trello_key"] = key
    data[token]["trello_token"] = ttoken
    save_tokens(data)

    return jsonify({"status": "ok"})
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
