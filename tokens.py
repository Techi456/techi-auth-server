import json
import os
import time

TOKENS_FILE = "tokens.json"

def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    try:
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_tokens(data):
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_token(user_code):
    token = str(int(time.time()))[-6:]
    data = load_tokens()

    data[token] = {
        "user_code": user_code,
        "confirmed": False,
        "expires_at": time.time() + 600,
        "trello_key": None,
        "trello_token": None
    }

    save_tokens(data)
    return token

def confirm_token(token):
    data = load_tokens()
    if token not in data:
        return False

    data[token]["confirmed"] = True
    save_tokens(data)
    return True

def check_token(token):
    data = load_tokens()

    if token not in data:
        return {"valid": False}

    entry = data[token]

    if time.time() > entry["expires_at"]:
        return {"valid": False, "expired": True}

    return {
        "valid": True,
        "confirmed": entry["confirmed"],
        "trello_key": entry.get("trello_key"),
        "trello_token": entry.get("trello_token")
    }

def save_trello_credentials(token, key, ttoken):
    data = load_tokens()

    if token not in data:
        return False

    data[token]["trello_key"] = key
    data[token]["trello_token"] = ttoken

    save_tokens(data)
    return True

def get_trello_credentials(token):
    data = load_tokens()

    if token not in data:
        return None

    return {
        "key": data[token].get("trello_key"),
        "token": data[token].get("trello_token")
    }
