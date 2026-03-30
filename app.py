import os, math, shutil, io
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from PIL import Image

app = Flask(__name__)

ALL_ASPECTS = [(1,1),(1,1.25),(1,1.5),(1,1.75),(1,2),(1,2.5),(1,3),(1,3.5),(1,4)]
IMG_EXTS = {'.jpg','.jpeg','.png','.webp','.bmp','.tiff','.tif','.gif'}

def qz(v, q):
    return round(v / q) * q

def get_buckets(T, q):
    seen, res = set(), []
    for h, w in ALL_ASPECTS:
        sq = math.sqrt(h * w)
        for bh, bw in [(h/sq*T, w/sq*T), (w/sq*T, h/sq*T)]:
            key = (qz(bh,q), qz(bw,q))
            if key not in seen:
                seen.add(key)
                res.append(key)
    return sorted(res, key=lambda b: b[0]/b[1])

def make_out_path(filepath, bucket, T):
    stem = Path(filepath).stem
    bH, bW = bucket
    sub = os.path.join(os.path.dirname(filepath), str(T))
    os.makedirs(sub, exist_ok=True)
    return os.path.join(sub, f"{stem}-{bW}x{bH}-{T}.png")

def copy_txt(src_img_path, dest_img_path):
    src_txt = Path(src_img_path).with_suffix('.txt')
    if src_txt.exists():
        shutil.copy2(str(src_txt), str(Path(dest_img_path).with_suffix('.txt')))

def prep_image(fp, fill_rgb):
    img = Image.open(fp)
    if img.mode == 'P':
        img = img.convert('RGBA')
    if img.mode == 'RGBA':
        return img, tuple(fill_rgb) + (255,)
    return img.convert('RGB'), tuple(fill_rgb)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan():
    folder = (request.json or {}).get('folder', '').strip()
    if not folder or not os.path.isdir(folder):
        return jsonify(error=f'Folder not found: {folder}'), 400
    imgs = []
    for f in sorted(os.listdir(folder)):
        if Path(f).suffix.lower() in IMG_EXTS:
            fp = os.path.join(folder, f)
            try:
                with Image.open(fp) as img:
                    W, H = img.size
                imgs.append({'name': f, 'path': fp, 'W': W, 'H': H})
            except Exception:
                pass
    return jsonify(images=imgs)

@app.route('/api/thumb')
def thumb():
    path = request.args.get('p', '')
    try:
        img = Image.open(path).convert('RGB')
        img.thumbnail((200, 200), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=85)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')
    except Exception as e:
        return str(e), 400

@app.route('/api/pad', methods=['POST'])
def do_pad():
    d = request.json or {}
    fp, nH, nW = d['path'], int(d['nH']), int(d['nW'])
    bucket, T = tuple(d['bucket']), d['T']
    fill_rgb = d.get('fill', [0,0,0])
    try:
        img, fill = prep_image(fp, fill_rgb)
        sW, sH = img.size
        canvas = Image.new(img.mode, (nW, nH), fill)
        canvas.paste(img, ((nW-sW)//2, (nH-sH)//2))
        op = make_out_path(fp, bucket, T)
        canvas.save(op, 'PNG', compress_level=0)
        copy_txt(fp, op)
        return jsonify(ok=True, out=op)
    except Exception as e:
        return jsonify(ok=False, error=str(e))

@app.route('/api/scalpad', methods=['POST'])
def do_scalpad():
    d = request.json or {}
    fp, nH, nW = d['path'], int(d['nH']), int(d['nW'])
    bucket, T = tuple(d['bucket']), d['T']
    fill_rgb = d.get('fill', [0,0,0])
    try:
        img, fill = prep_image(fp, fill_rgb)
        sW, sH = img.size
        scale = min(nW/sW, nH/sH)
        scW, scH = round(sW*scale), round(sH*scale)
        scaled = img.resize((scW, scH), Image.LANCZOS)
        canvas = Image.new(scaled.mode, (nW, nH), fill)
        canvas.paste(scaled, ((nW-scW)//2, (nH-scH)//2))
        op = make_out_path(fp, bucket, T)
        canvas.save(op, 'PNG', compress_level=0)
        copy_txt(fp, op)
        return jsonify(ok=True, out=op)
    except Exception as e:
        return jsonify(ok=False, error=str(e))

@app.route('/api/sortfolders', methods=['POST'])
def sort_folders():
    """Copy each image (and its .txt) into a subfolder named after its rec T, keeping originals in place."""
    d = request.json or {}
    items = d.get('items', [])
    moved = 0
    for item in items:
        src = item.get('path', '')
        T = item.get('T')
        if not src or not T or not os.path.isfile(src):
            continue
        sub = os.path.join(os.path.dirname(src), str(T))
        os.makedirs(sub, exist_ok=True)
        try:
            shutil.copy2(src, os.path.join(sub, Path(src).name))
            moved += 1
        except Exception:
            pass
        txt = Path(src).with_suffix('.txt')
        if txt.exists():
            try:
                shutil.copy2(str(txt), os.path.join(sub, txt.name))
            except Exception:
                pass
    return jsonify(moved=moved)

@app.route('/api/move', methods=['POST'])
def move_originals():
    d = request.json or {}
    paths, folder = d.get('paths', []), d.get('folder', '')
    orig_dir = os.path.join(folder, 'originals')
    os.makedirs(orig_dir, exist_ok=True)
    moved = []
    for p in paths:
        try:
            shutil.move(p, os.path.join(orig_dir, Path(p).name))
            moved.append(p)
        except Exception:
            pass
        txt = Path(p).with_suffix('.txt')
        if txt.exists():
            try:
                shutil.move(str(txt), os.path.join(orig_dir, txt.name))
            except Exception:
                pass
    return jsonify(moved=moved, dest=orig_dir)

if __name__ == '__main__':
    import webbrowser, threading
    threading.Timer(0.8, lambda: webbrowser.open('http://127.0.0.1:5137')).start()
    print("\n  Aspect Bucketing Tool  →  http://127.0.0.1:5137\n")
    app.run(port=5137, debug=False)
