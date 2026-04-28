from flask import Flask, request, jsonify, render_template_string
from token import (
    create_token,
    confirm_token,
    check_token,
    save_trello_credentials,
)
import time

app = Flask(__name__)

# -----------------------------
# Pagina HTML per confermare accesso
# -----------------------------
AUTH_PAGE = """
<html>
<head>
<title>Autorizzazione</title>
</head>
<body style="font-family:Arial; text-align:center; margin-top:50px;">
<h2>Autorizza l'accesso</h2>
<p>Stai autorizzando il tuo bot Techi ad accedere al tuo account.</p>

<form action="/confirm/{{token}}" method="POST">
    <button type="submit" style="padding:10px 20px;">Confermo</button>
</form>

</body>
</html>
"""

# -----------------------------
# Pagina HTML per Trello
# -----------------------------
TRELLO_PAGE = """
<html>
<head>
<title>Collega Trello</title>
</head>
<body style="font-family:Arial; text-align:center; margin-top:50px;">
<h2>Collega Trello</h2>
<p>Inserisci la tua API Key e il tuo Token Trello</p>

<form action="/save_trello" method="POST">
    <input type="hidden" name="token" value="{{token}}">
    <p><input type="text" name="trello_key" placeholder="API Key" style="width:300px;"></p>
    <p><input type="text" name="trello_token" placeholder="Token Trello" style="width:300px;"></p>
    <button type="submit" style="padding:10px 20px;">Salva</button>
</form>

</body>
</html>
"""

# -----------------------------
# GENERA TOKEN
# -----------------------------
@app.route("/generate/<user_code>")
def generate(user_code):
    token = create_token(user_code)
    login_url = f"https://{request.host}/auth/{token}"
    return jsonify({"token": token, "login_url": login_url})

# -----------------------------
# MOSTRA PAGINA DI AUTORIZZAZIONE
# -----------------------------
@app.route("/auth/<token>")
def auth_page(token):
    return render_template_string(AUTH_PAGE, token=token)

# -----------------------------
# CONFERMA ACCESSO
# -----------------------------
@app.route("/confirm/<token>", methods=["POST"])
def confirm(token):
    ok = confirm_token(token)
    if ok:
        return "Accesso confermato! Puoi tornare su Telegram."
    return "Token non valido."

# -----------------------------
# CHECK TOKEN (usato dal bot)
# -----------------------------
@app.route("/check/<token>")
def check(token):
    return jsonify(check_token(token))

# -----------------------------
# PAGINA PER INSERIRE CREDENZIALI TRELLO
# -----------------------------
@app.route("/trello/<token>")
def trello_page(token):
    return render_template_string(TRELLO_PAGE, token=token)

# -----------------------------
# SALVA CREDENZIALI TRELLO
# -----------------------------
@app.route("/save_trello", methods=["POST"])
def save_trello():
    token = request.form.get("token")
    key = request.form.get("trello_key")
    ttoken = request.form.get("trello_token")

    ok = save_trello_credentials(token, key, ttoken)

    if not ok:
        return "Token non valido", 400

    return "Credenziali Trello salvate! Puoi tornare su Telegram."

# -----------------------------
# AVVIO SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

