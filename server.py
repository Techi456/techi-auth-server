from flask import Flask, request, jsonify, render_template_string
from tokens import (
    create_token,
    confirm_token,
    check_token,
    load_tokens,
    save_tokens
)
import urllib.parse

app = Flask(__name__)

# ============================================================
# 🔵 LOGIN BASE (per autorizzare il bot)
# ============================================================

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

@app.route("/generate/<user_code>")
def generate(user_code):
    token = create_token(user_code)
    login_url = f"https://{request.host}/auth/{token}"
    return jsonify({"token": token, "login_url": login_url})

@app.route("/auth/<token>")
def auth_page(token):
    return render_template_string(AUTH_PAGE, token=token)

@app.route("/confirm/<token>", methods=["POST"])
def confirm(token):
    ok = confirm_token(token)
    if ok:
        return "Accesso confermato! Ora puoi collegare Trello dal bot."
    return "Token non valido."

@app.route("/check/<token>")
def check(token):
    return jsonify(check_token(token))

# ============================================================
# 🔵 TRELLO OAUTH — LOGIN COME GOOGLE
# ============================================================

TRELLO_API_KEY = "140a60e799e18ca52c60afe6f1933d55"   # <--- INSERISCI QUI LA TUA API KEY

@app.route("/trello/start/<user_code>")
def trello_start(user_code):
    # Genera token temporaneo per associare l’utente
    token = create_token(user_code)

    # URL di callback
    callback_url = f"https://{request.host}/trello/callback"

    # URL ufficiale Trello OAuth
    trello_url = (
        "https://trello.com/1/authorize?"
        f"key={TRELLO_API_KEY}&"
        f"return_url={urllib.parse.quote(callback_url)}&"
        "scope=read,write&"
        "expiration=never&"
        "name=TechiBot"
    )

    return jsonify({"auth_url": trello_url, "token": token})

@app.route("/trello/callback")
def trello_callback():
    trello_token = request.args.get("token")

    if not trello_token:
        return "Errore: Trello non ha restituito un token."

    # Recupera l’ultimo token generato (utente corrente)
    data = load_tokens()
    last_token = list(data.keys())[-1]

    data[last_token]["trello_token"] = trello_token
    save_tokens(data)

    return "Trello collegato! Puoi tornare su Telegram."

# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

