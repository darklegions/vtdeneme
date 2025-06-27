from flask import Flask, request, jsonify, session, redirect, send_file, render_template_string, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, json
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO

app = Flask(__name__)
app.secret_key = "kingo_super_secret"
CORS(app)

UPLOAD_FOLDER = "uploads"
DATA_FILE = "veriler.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Kullanıcı bilgileri
KULLANICILAR = {
    "emir": "1234",
    "arob": "1234",
    "cato": "1234"
}

KULLANICI_ISIMLERI = {
    "emir": {"ad": "Emir", "soyad": "Eröz"},
    "arob": {"ad": "Bora", "soyad": "Uğur"},
    "cato": {"ad": "Çağatay", "soyad": "Temiz"}
}

@app.route('/')
def anasayfa():
    return redirect("/giris")

@app.route('/giris', methods=['GET'])
def giris_formu():
    return """
    <h2>Giriş Yap</h2>
    <form method="POST" action="/giris">
        <input type="text" name="username" placeholder="Kullanıcı Adı" required><br>
        <input type="password" name="password" placeholder="Şifre" required><br>
        <button type="submit">Giriş</button>
    </form>
    """

@app.route('/giris', methods=['POST'])
def giris_yap():
    username = request.form.get("username")
    password = request.form.get("password")
    if username in KULLANICILAR and KULLANICILAR[username] == password:
        session["kullanici"] = username
        return redirect("/form")
    return "Hatalı giriş. <a href='/giris'>Geri dön</a>"

@app.route('/form', methods=['GET', 'POST'])
def form_sayfasi():
    if "kullanici" not in session:
        return redirect("/giris")

    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        kimlik_on = request.files["kimlik_on"]
        kimlik_arka = request.files["kimlik_arka"]

        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        kullanici_id = session["kullanici"]
        giris_yapan = KULLANICI_ISIMLERI.get(kullanici_id, {"ad": kullanici_id, "soyad": ""})

        on_path = os.path.join(UPLOAD_FOLDER, secure_filename(f"{name}_{surname}_on_{zaman}.jpg"))
        arka_path = os.path.join(UPLOAD_FOLDER, secure_filename(f"{name}_{surname}_arka_{zaman}.jpg"))

        kimlik_on.save(on_path)
        kimlik_arka.save(arka_path)

        veri = {
            "girisYapan": giris_yapan,
            "girilen": {
                "ad": name,
                "soyad": surname,
                "kimlik_on": on_path,
                "kimlik_arka": arka_path
            },
            "zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(veri, ensure_ascii=False) + "\n")

        return redirect("/form")

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Yeni Kayıt</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-4">
            <h4 class="mb-3">Yeni Kayıt Formu</h4>
            <form method="POST" action="/form" enctype="multipart/form-data" class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Ad</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Soyad</label>
                    <input type="text" name="surname" class="form-control" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Kimlik Ön Yüz</label>
                    <input type="file" name="kimlik_on" accept="image/*" class="form-control" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Kimlik Arka Yüz</label>
                    <input type="file" name="kimlik_arka" accept="image/*" class="form-control" required>
                </div>
                <div class="col-12 d-flex justify-content-between">
                    <button type="submit" class="btn btn-primary">Kaydet</button>
                    <a href="/veriler" class="btn btn-secondary">Kayıtları Gör</a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route('/kaydet', methods=['POST'])
def kaydet():
    if "kullanici" not in session:
        return redirect("/giris")

    name = request.form["name"]
    surname = request.form["surname"]
    kimlik_on = request.files["kimlik_on"]
    kimlik_arka = request.files["kimlik_arka"]

    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    kullanici_id = session["kullanici"]
    giris_yapan = KULLANICI_ISIMLERI.get(kullanici_id, {"ad": kullanici_id, "soyad": ""})

    on_path = os.path.join(UPLOAD_FOLDER, secure_filename(f"{name}_{surname}_on_{zaman}.jpg"))
    arka_path = os.path.join(UPLOAD_FOLDER, secure_filename(f"{name}_{surname}_arka_{zaman}.jpg"))

    kimlik_on.save(on_path)
    kimlik_arka.save(arka_path)

    veri = {
        "girisYapan": giris_yapan,
        "girilen": {
            "ad": name,
            "soyad": surname,
            "kimlik_on": on_path,
            "kimlik_arka": arka_path
        },
        "zaman": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(veri, ensure_ascii=False) + "\n")

    return redirect("/form")

@app.route('/veriler')
def admin_panel():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            veriler = [json.loads(s) for s in f if s.strip()]
    except:
        veriler = []

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Müşteri Paneli</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css" />
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    </head>
    <body>
    <h2>Müşteri Paneli</h2>
    <a href='/indir_excel'><button>Excel Olarak İndir</button></a>
    <br><br>
    <table id="veriTablosu" class="display" border='1' cellpadding='5'>
        <thead>
        <tr>
            <th>Giriş Yapan</th>
            <th>Girilen Ad</th>
            <th>Girilen Soyad</th>
            <th>Zaman</th>
            <th>Kimlik Ön</th>
            <th>Kimlik Arka</th>
            <th>Sil</th>
        </tr>
        </thead>
        <tbody>
        {% for v in veriler %}
        <tr>
            <td>{{ v['girisYapan']['ad'] }} {{ v['girisYapan']['soyad'] }}</td>
            <td>{{ v['girilen']['ad'] }}</td>
            <td>{{ v['girilen']['soyad'] }}</td>
            <td>{{ v['zaman'] }}</td>
            <td><a href='/{{ v["girilen"]["kimlik_on"] }}' target='_blank'>Gör</a></td>
            <td><a href='/{{ v["girilen"]["kimlik_arka"] }}' target='_blank'>Gör</a></td>
            <td>
                <form method='POST' action='/veri_sil/{{ loop.index0 }}'>
                    <button>Sil</button>
                </form>
            </td>
        </tr>
        {% endfor %}
        </tbody>
    </table>

    <script>
    $(document).ready(function() {
        $('#veriTablosu').DataTable({
            "pageLength": 10,
            "language": {
                "search": "Ara:",
                "lengthMenu": "Her sayfada _MENU_ kayıt göster",
                "zeroRecords": "Eşleşen kayıt bulunamadı",
                "info": "_TOTAL_ kayıttan _START_ - _END_ arası gösteriliyor",
                "infoEmpty": "Kayıt yok",
                "paginate": {
                    "first": "İlk",
                    "last": "Son",
                    "next": "Sonraki",
                    "previous": "Önceki"
                }
            }
        });
    });
    </script>

    </body>
    </html>
    """
    return render_template_string(html, veriler=veriler)

@app.route('/veri_sil/<int:index>', methods=["POST"])
def veri_sil(index):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            veriler = [json.loads(s) for s in f if s.strip()]
        if 0 <= index < len(veriler):
            del veriler[index]
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                for v in veriler:
                    f.write(json.dumps(v, ensure_ascii=False) + "\n")
    except:
        pass
    return redirect("/veriler")

@app.route('/indir_excel')
def indir_excel():
    try:
        wb = Workbook()
        ws = wb.active
        ws.append(["Yetkili", "Ad", "Soyad", "Zaman"])

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for s in f:
                v = json.loads(s)
                g = v["girisYapan"]
                girilen = v["girilen"]
                ws.append([f"{g['ad']} {g['soyad']}", girilen['ad'], girilen['soyad'], v["zaman"]])

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)
        return send_file(stream, as_attachment=True, download_name="veriler.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return str(e)

@app.route('/uploads/<path:filename>')
def yuklenen_dosya(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True)