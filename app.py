from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

# BASE DE DATOS SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarjetas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# TABLA DE PERFILES NFC
class PerfilNFC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    instagram = db.Column(db.String(50))
    facebook = db.Column(db.String(50))
    banco = db.Column(db.String(100))
    tipo_cuenta = db.Column(db.String(50))
    numero_cuenta = db.Column(db.String(50))
    rut_pago = db.Column(db.String(20))
    link_mercadopago = db.Column(db.String(255))

# CREAR LA BASE DE DATOS AUTOMÁTICAMENTE
with app.app_context():
    db.create_all()

@app.route('/')
def inicio():
    return 'Sistema NFC funcionando. Entra a /admin'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nuevo = PerfilNFC(
            slug=request.form['slug'],
            nombre=request.form['nombre'],
            cargo=request.form.get('cargo'),
            whatsapp=request.form.get('whatsapp'),
            instagram=request.form.get('instagram'),
            facebook=request.form.get('facebook'),
            banco=request.form.get('banco'),
            tipo_cuenta=request.form.get('tipo_cuenta'),
            numero_cuenta=request.form.get('numero_cuenta'),
            rut_pago=request.form.get('rut_pago'),
            link_mercadopago=request.form.get('link_mercadopago')
        )

        db.session.add(nuevo)
        db.session.commit()

        return f"""
        <h2>Perfil creado correctamente</h2>
        <p>Enlace:</p>
        <a href="/u/{nuevo.slug}">Ver perfil</a>
        """

    return render_template('admin.html')

@app.route('/u/<slug>')
def ver_perfil(slug):
    usuario = PerfilNFC.query.filter_by(slug=slug).first_or_404()

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(request.url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    return render_template('perfil.html', user=usuario, qr_code=qr_base64)

@app.route('/u/<slug>/vcard')
def descargar_vcard(slug):
    usuario = PerfilNFC.query.filter_by(slug=slug).first_or_404()

    vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{usuario.nombre}
TITLE:{usuario.cargo}
TEL;TYPE=CELL:{usuario.whatsapp}
END:VCARD
"""

    output = BytesIO()
    output.write(vcard.encode('utf-8'))
    output.seek(0)

    return send_file(
        output,
        mimetype="text/vcard",
        as_attachment=True,
        download_name=f"{slug}.vcf"
    )

if __name__ == '__main__':
    app.run(debug=True)