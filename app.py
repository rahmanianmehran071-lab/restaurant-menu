"""
شب‌نشین — منوی دیجیتال رستوران سنتی
نسخه ۳ — پنل مشتری و ادمین کاملاً جدا

اجرا: python app.py
  منو مشتری  → http://localhost:5000
  پنل ادمین  → http://localhost:5000/admin
"""

from flask import Flask, request, jsonify, send_from_directory, Response
import json, os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
DATA_FILE     = os.path.join(os.path.dirname(__file__), 'data.json')
ALLOWED_EXT   = {'png', 'jpg', 'jpeg', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Default data ──────────────────────────────────────────────────────────────
DEFAULT = {
    "categories": [
        {"id":"appetizer","name":"پیش‌غذا و سوپ","icon":"🥣"},
        {"id":"main",     "name":"غذای اصلی",     "icon":"🍲"},
        {"id":"rice",     "name":"پلوها",          "icon":"🍚"},
        {"id":"kebab",    "name":"کباب و گریل",    "icon":"🔥"},
        {"id":"drink",    "name":"نوشیدنی",        "icon":"☕"},
        {"id":"dessert",  "name":"دسر",            "icon":"🍮"},
    ],
    "items": [
        {"id":1, "name":"آش رشته",      "cat":"appetizer","desc":"آش سنتی با حبوبات و سبزیجات تازه",     "price":85000, "badge":"hot","active":True, "img":"🥣"},
        {"id":2, "name":"سوپ جو",       "cat":"appetizer","desc":"سوپ گرم با جو مروارید و سبزیجات",       "price":75000, "badge":"",  "active":True, "img":"🍲"},
        {"id":3, "name":"میرزاقاسمی",   "cat":"appetizer","desc":"کباب بادمجان با تخم‌مرغ و گوجه‌فرنگی", "price":95000, "badge":"new","active":True, "img":"🍆"},
        {"id":4, "name":"خورشت فسنجان", "cat":"main",     "desc":"خورشت گردو و انار با مرغ محلی",         "price":185000,"badge":"hot","active":True, "img":"🍗"},
        {"id":5, "name":"قرمه‌سبزی",    "cat":"main",     "desc":"خورشت معروف با سبزی تازه و لوبیا",     "price":175000,"badge":"",  "active":True, "img":"🌿"},
        {"id":6, "name":"قیمه",         "cat":"main",     "desc":"خورشت لپه با گوشت و لیمو عمانی",       "price":165000,"badge":"",  "active":True, "img":"🍖"},
        {"id":7, "name":"کوفته تبریزی", "cat":"main",     "desc":"کوفته بزرگ با آلو و گردو",             "price":195000,"badge":"new","active":True, "img":"🥩"},
        {"id":8, "name":"دلمه",         "cat":"main",     "desc":"دلمه برگ مو با برنج و گوشت",           "price":155000,"badge":"",  "active":False,"img":"🫑"},
        {"id":9, "name":"چلو",          "cat":"rice",     "desc":"برنج ایرانی با کره و زعفران",           "price":55000, "badge":"",  "active":True, "img":"🍚"},
        {"id":10,"name":"باقالی‌پلو",   "cat":"rice",     "desc":"پلو با باقالی و شوید تازه",             "price":75000, "badge":"",  "active":True, "img":"🫘"},
        {"id":11,"name":"کلم‌پلو",      "cat":"rice",     "desc":"پلو با کلم و گوشت سنتی",               "price":145000,"badge":"",  "active":True, "img":"🥗"},
        {"id":12,"name":"کباب کوبیده",  "cat":"kebab",    "desc":"کباب گوشت چرخ‌کرده با ادویه مخصوص",   "price":245000,"badge":"hot","active":True, "img":"🍢"},
        {"id":13,"name":"جوجه‌کباب",    "cat":"kebab",    "desc":"مرغ مزه‌دار شده با زعفران",             "price":225000,"badge":"",  "active":True, "img":"🍗"},
        {"id":14,"name":"برگ",          "cat":"kebab",    "desc":"کباب برگ گوشت تازه",                    "price":285000,"badge":"off","active":True, "img":"🥩"},
        {"id":15,"name":"دوغ سنتی",     "cat":"drink",    "desc":"دوغ محلی با نعنا",                      "price":35000, "badge":"",  "active":True, "img":"🥛"},
        {"id":16,"name":"چای سنتی",     "cat":"drink",    "desc":"چای ایرانی با زعفران",                  "price":25000, "badge":"",  "active":True, "img":"☕"},
        {"id":17,"name":"شربت آلبالو",  "cat":"drink",    "desc":"شربت سنتی با آلبالوی تازه",             "price":45000, "badge":"new","active":True, "img":"🍒"},
        {"id":18,"name":"زولبیا بامیه", "cat":"dessert",  "desc":"شیرینی سنتی ماه رمضان",                "price":55000, "badge":"off","active":False,"img":"🍩"},
        {"id":19,"name":"بستنی سنتی",   "cat":"dessert",  "desc":"بستنی زعفرانی با گلاب",                 "price":65000, "badge":"",  "active":True, "img":"🍨"},
        {"id":20,"name":"حلوا",         "cat":"dessert",  "desc":"حلوا ارده با کنجد",                     "price":45000, "badge":"",  "active":True, "img":"🟤"},
    ]
}

# ── DB helpers ────────────────────────────────────────────────────────────────
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,'r',encoding='utf-8') as f:
            return json.load(f)
    return json.loads(json.dumps(DEFAULT))

def save(data):
    with open(DATA_FILE,'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def allowed(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route('/')
def customer():
    with open(os.path.join(os.path.dirname(__file__), 'menu.html'), encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')

@app.route('/admin')
def admin():
    with open(os.path.join(os.path.dirname(__file__), 'admin.html'), encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html')

# ── Uploads ───────────────────────────────────────────────────────────────────

@app.route('/uploads/<fname>')
def serve_upload(fname):
    return send_from_directory(UPLOAD_FOLDER, fname)

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error':'فایلی ارسال نشد'}), 400
    f = request.files['file']
    if not f.filename or not allowed(f.filename):
        return jsonify({'error':'فرمت غیرمجاز'}), 400
    ext  = f.filename.rsplit('.',1)[1].lower()
    name = f'{uuid.uuid4().hex}.{ext}'
    f.save(os.path.join(UPLOAD_FOLDER, name))
    return jsonify({'url': f'/uploads/{name}'})

# ── API: categories ───────────────────────────────────────────────────────────

@app.route('/api/categories', methods=['GET'])
def get_cats():
    return jsonify(load()['categories'])

@app.route('/api/categories', methods=['POST'])
def add_cat():
    d = load(); b = request.json
    name = (b.get('name') or '').strip()
    if not name:
        return jsonify({'error':'نام الزامی است'}), 400
    cat = {'id': f'cat_{uuid.uuid4().hex[:8]}', 'name': name, 'icon': b.get('icon','🍽')}
    d['categories'].append(cat); save(d)
    return jsonify(cat), 201

@app.route('/api/categories/<cid>', methods=['DELETE'])
def del_cat(cid):
    d = load()
    d['categories'] = [c for c in d['categories'] if c['id'] != cid]
    save(d)
    return jsonify({'ok': True})

# ── API: items ────────────────────────────────────────────────────────────────

@app.route('/api/items', methods=['GET'])
def get_items():
    d = load(); items = d['items']
    if request.args.get('cat'):
        items = [i for i in items if i['cat'] == request.args['cat']]
    act = request.args.get('active')
    if act == 'true':  items = [i for i in items if i['active']]
    if act == 'false': items = [i for i in items if not i['active']]
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def add_item():
    d = load(); b = request.json
    if not b.get('name') or not b.get('price'):
        return jsonify({'error':'نام و قیمت الزامی است'}), 400
    nid = max((i['id'] for i in d['items']), default=0) + 1
    item = {
        'id': nid, 'name': b['name'].strip(),
        'cat': b.get('cat',''), 'desc': (b.get('desc') or '').strip(),
        'price': int(b['price']), 'badge': b.get('badge',''),
        'active': b.get('active', True), 'img': b.get('img','🍽')
    }
    d['items'].append(item); save(d)
    return jsonify(item), 201

@app.route('/api/items/<int:iid>', methods=['PUT'])
def update_item(iid):
    d = load(); b = request.json
    item = next((i for i in d['items'] if i['id'] == iid), None)
    if not item: return jsonify({'error':'یافت نشد'}), 404
    for k in ['name','cat','desc','badge','active','img']:
        if k in b: item[k] = b[k]
    if 'price' in b: item['price'] = int(b['price'])
    save(d); return jsonify(item)

@app.route('/api/items/<int:iid>', methods=['DELETE'])
def delete_item(iid):
    d = load()
    d['items'] = [i for i in d['items'] if i['id'] != iid]
    save(d); return jsonify({'ok': True})

@app.route('/api/items/<int:iid>/toggle', methods=['POST'])
def toggle_item(iid):
    d = load()
    item = next((i for i in d['items'] if i['id'] == iid), None)
    if not item: return jsonify({'error':'یافت نشد'}), 404
    item['active'] = not item['active']
    save(d); return jsonify(item)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\n🕯️  شب‌نشین — منوی دیجیتال')
    print('━'*38)
    print('  منوی مشتری  →  http://localhost:5000')
    print('  پنل ادمین   →  http://localhost:5000/admin')
    print('━'*38 + '\n')
    app.run(debug=True, port=5000)
