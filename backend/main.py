from pathlib import Path
import json
import sqlite3
import hashlib
import hmac
import secrets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
try:
    from .models import ChatReply, ChatRequest
    from .agent import run_agent
except ImportError:
    from models import ChatReply, ChatRequest
    from agent import run_agent

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'data' / 'campus_customs.db'
app = FastAPI(title='Campus Customs API')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])
app.mount('/media', StaticFiles(directory=ROOT / 'data'), name='media')

with sqlite3.connect(DB) as db:
    user_columns = {row[1] for row in db.execute('PRAGMA table_info(users)')}
    if 'phone' not in user_columns:
        db.execute('ALTER TABLE users ADD COLUMN phone TEXT')

HASH_ITERATIONS = 120_000

class AccountRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

def redact_sensitive(message: str) -> tuple[str, bool]:
    redacted = message
    found = False
    card_pattern = r'(?<!\d)(?:\d[ -]?){13,19}(?!\d)'
    redacted, card_count = __import__('re').subn(card_pattern, '[REDACTED CARD NUMBER]', redacted)
    password_pattern = r'(?i)(\b(?:my\s+)?password\s*(?:is|=|:)\s*)[^\s,.;!?]+'
    redacted, password_count = __import__('re').subn(password_pattern, r'\1[REDACTED PASSWORD]', redacted)
    return redacted, bool(card_count or password_count)

def save_chat(user_id: int, role: str, content: str, products=None):
    with sqlite3.connect(DB) as db:
        db.execute('INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)', (user_id, role, content, json.dumps(products or [])))

def chat_history(user_id: int):
    return rows('SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 10', (user_id,))[::-1]

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), HASH_ITERATIONS)
    return f'pbkdf2_sha256${HASH_ITERATIONS}${salt}${digest.hex()}'

def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored.split('$')
        if algorithm != 'pbkdf2_sha256': return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations)).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def rows(query, params=()):
    with sqlite3.connect(DB) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(query, params).fetchall()]

@app.post('/api/auth/register')
def register(account: AccountRequest):
    if len(account.password) < 6 or not any(c.islower() for c in account.password) or not any(c.isupper() for c in account.password) or not any(c.isdigit() for c in account.password):
        raise HTTPException(status_code=400, detail='Password must be at least 6 characters and include lowercase, uppercase, and a number.')
    name = f'{account.first_name.strip()} {account.last_name.strip()}'.strip()
    try:
        with sqlite3.connect(DB) as db:
            db.execute('INSERT INTO users (name, email, password_hash, first_name, last_name, phone) VALUES (?, ?, ?, ?, ?, ?)', (name, account.email.lower().strip(), hash_password(account.password), account.first_name.strip(), account.last_name.strip(), account.phone.strip() if account.phone else None))
            user_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail='An account with that email already exists.')
    return {'id': user_id, 'name': name, 'email': account.email.lower().strip()}

@app.post('/api/auth/login')
def login(credentials: LoginRequest):
    found = rows('SELECT id, name, email, password_hash, first_name, last_name FROM users WHERE lower(email) = lower(?)', (credentials.email.strip(),))
    if not found or not verify_password(credentials.password, found[0]['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid email or password.')
    user = found[0]
    user.pop('password_hash', None)
    return user

@app.get('/api/products')
def products():
    data = rows('SELECT * FROM catalogue ORDER BY name')
    stock = rows('SELECT product_id, size, quantity FROM inventory ORDER BY product_id, size')
    by_product = {}
    for item in stock: by_product.setdefault(item['product_id'], []).append({'size': item['size'], 'quantity': item['quantity']})
    for item in data:
        for field in ('colors', 'search_tags'):
            try: item[field] = json.loads(item[field])
            except (TypeError, json.JSONDecodeError): pass
        item['sizes'] = by_product.get(item['product_id'], [])
        item['image_url'] = '/media/' + item['image_file_path']
    return data

@app.get('/api/products/{product_id}')
def product(product_id: str):
    result = products()
    match = next((item for item in result if item['product_id'] == product_id), None)
    if not match: raise HTTPException(status_code=404, detail='Product not found')
    return match

@app.get('/api/health')
def health(): return {'status': 'ok'}

@app.get('/api/chat/history/{user_id}')
def get_chat_history(user_id: int):
    return chat_history(user_id)

@app.post('/api/chat', response_model=ChatReply)
async def chat(request: ChatRequest):
    safe_message, sensitive_found = redact_sensitive(request.message)
    customer = None
    stored_history = []
    if request.user_id:
        found = rows('SELECT id, first_name, last_name, email FROM users WHERE id = ?', (request.user_id,))
        if found:
            customer = found[0]
            stored_history = [item['content'] for item in chat_history(request.user_id) if item['role'] == 'user'][-5:]
    history = [redact_sensitive(item)[0] for item in (stored_history or request.history[-5:])]
    response = await run_agent(safe_message, history, customer, request.page_context)
    if sensitive_found:
        response.reply = 'For your security, please do not share payment card numbers or passwords in chat. ' + response.reply
    if customer:
        save_chat(customer['id'], 'user', safe_message)
        save_chat(customer['id'], 'assistant', response.reply, [item.model_dump() for item in response.products])
    return response
