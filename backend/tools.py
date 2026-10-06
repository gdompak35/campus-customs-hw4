from pathlib import Path
import sqlite3
try: from .models import ProductCard, ProductInfo, StockItem, StockLookup
except ImportError: from models import ProductCard, ProductInfo, StockItem, StockLookup

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'data' / 'campus_customs.db'

def _rows(query, params=()):
    with sqlite3.connect(DB) as db:
        db.row_factory = sqlite3.Row
        return [dict(row) for row in db.execute(query, params).fetchall()]

def search_products(search: str = '') -> list[ProductCard]:
    term = f'%{search.strip()}%'
    products = _rows('SELECT * FROM catalogue WHERE name LIKE ? OR garment_type LIKE ? OR description LIKE ? OR search_tags LIKE ? ORDER BY name LIMIT 12', (term, term, term, term))
    if not products:
        normalized = search.lower().replace(' v ', ' vs ').replace(' t shirt', ' t-shirt').strip()
        tokens = [token for token in normalized.split() if token not in {'what', 'kind', 'of', 'do', 'you', 'have', 'how', 'many', 'the', 'are', 'in', 'stock'}]
        if tokens:
            clauses = ' AND '.join(['(lower(name) LIKE ? OR lower(garment_type) LIKE ? OR lower(description) LIKE ? OR lower(search_tags) LIKE ?)' for _ in tokens])
            params = [value for token in tokens for value in (f'%{token}%', f'%{token}%', f'%{token}%', f'%{token}%')]
            products = _rows(f'SELECT * FROM catalogue WHERE {clauses} ORDER BY name LIMIT 12', params)
    stock = _rows('SELECT product_id, size, quantity FROM inventory ORDER BY product_id, size')
    sizes = {}
    for row in stock: sizes.setdefault(row['product_id'], []).append({'size': row['size'], 'quantity': row['quantity']})
    return [ProductCard(product_id=p['product_id'], name=p['name'], price=p['price'], description=p['description'], image_url='/media/'+p['image_file_path'], sizes=[StockItem(size=s['size'], quantity=s['quantity'], in_stock=s['quantity'] > 0) for s in sizes.get(p['product_id'], [])]) for p in products]

def _stock(product_id: str, size: str | None = None) -> list[StockItem]:
    query = 'SELECT size, quantity FROM inventory WHERE product_id = ?'
    params: list[str] = [product_id]
    if size:
        query += ' AND upper(size) = upper(?)'
        params.append(size.strip())
    query += ' ORDER BY size'
    return [StockItem(size=row['size'], quantity=row['quantity'], in_stock=row['quantity'] > 0) for row in _rows(query, params)]

def lookup_product(product: str) -> ProductInfo | None:
    """Look up database-backed catalogue facts and current size stock."""
    matches = _rows('SELECT * FROM catalogue WHERE product_id = ? OR lower(name) = lower(?) LIMIT 1', (product.strip(), product.strip()))
    if not matches:
        matches = _rows('SELECT * FROM catalogue WHERE name LIKE ? OR product_id LIKE ? ORDER BY name LIMIT 1', (f'%{product.strip()}%', f'%{product.strip()}%'))
    if not matches: return None
    item = matches[0]
    try: colors = __import__('json').loads(item['colors'])
    except Exception: colors = []
    return ProductInfo(product_id=item['product_id'], name=item['name'], garment_type=item['garment_type'], description=item['description'], price=item['price'], colors=colors, stock=_stock(item['product_id']))

def check_stock(product: str, size: str | None = None) -> StockLookup:
    """Check live inventory; zero quantity is explicitly out of stock."""
    info = lookup_product(product)
    if not info: return StockLookup(product_id=product, product_name=product, requested_size=size, results=[], found=False)
    return StockLookup(product_id=info.product_id, product_name=info.name, requested_size=size, results=_stock(info.product_id, size), found=True)
