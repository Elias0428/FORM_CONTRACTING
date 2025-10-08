from flask import Flask, render_template, request, redirect, url_for
from db import db
from models import *
from dotenv import load_dotenv
from xhtml2pdf import pisa
from flask_mail import Mail, Message
from io import BytesIO
import base64
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración base de datos
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DB')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de correo
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
db.init_app(app)


# ---------------------------
# FUNCIÓN PARA GENERAR EL PDF
# ---------------------------
def render_pdf(nombre, email, phone, zipCode, licensed, npn, observation,
               allAca, allSupplementals, allMedicareAdvantage, allMedicareSupplement,
               allLifeInsurance, allFinalExpenses, allShortTermMedical, allContacted,
               documentos=[]):

    # Renderizamos el HTML con Jinja2 (Flask usa render_template)
    html = render_template("pdf_template.html", 
        name=nombre,
        email=email,
        phone=phone,
        zipCode=zipCode,
        licensed=licensed,
        npn=npn,
        observation=observation,
        allAca=allAca,
        allSupplementals=allSupplementals,
        allMedicareAdvantage=allMedicareAdvantage,
        allMedicareSupplement=allMedicareSupplement,
        allLifeInsurance=allLifeInsurance,
        allFinalExpenses=allFinalExpenses,
        allShortTermMedical=allShortTermMedical,
        allContacted=allContacted,
        documentos=documentos
    )

    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer


# ---------------------------
# RUTA PRINCIPAL
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        nombre = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        zipCode = request.form.get("zipCode")
        licensed = request.form.get("licensed")
        npn = request.form.get("npn")
        observation = request.form.get("observation")
        TC = request.form.get("TC")

        # ---- Procesar archivos sin guardarlos ----
        documentos = []
        for f in request.files.getlist("documents"):
            if f.mimetype.startswith("image/"):
                img_data = base64.b64encode(f.read()).decode("utf-8")
                documentos.append(f"data:{f.mimetype};base64,{img_data}")
            else:
                documentos.append(f.filename)

        # ---- Procesar los checkboxes ----
        aca = request.form.getlist("aca")
        allAca = ", ".join(aca)

        supplementals = request.form.getlist("supplementals")
        allSupplementals = ", ".join(supplementals)

        medicareAdvantage = request.form.getlist("medicareAdvantage")
        allMedicareAdvantage = ", ".join(medicareAdvantage)

        medicareSupplement = request.form.getlist("medicareSupplement")
        allMedicareSupplement = ", ".join(medicareSupplement)

        lifeInsurance = request.form.getlist("lifeInsurance")
        allLifeInsurance = ", ".join(lifeInsurance)

        finalExpenses = request.form.getlist("finalExpenses")
        allFinalExpenses = ", ".join(finalExpenses)

        shortTermMedical = request.form.getlist("shortTermMedical")
        allShortTermMedical = ", ".join(shortTermMedical)

        contacted = request.form.getlist("contacted")
        allContacted = ", ".join(contacted)

        # ---- Guardar en BD ----
        agent = Solicitud(nombre=nombre, email=email, phone=phone, zipCode=zipCode, licensed=licensed, npn=npn, observation=observation, TC=TC)
        db.session.add(agent)
        db.session.flush()

        db.session.add(Aca(aca=allAca, solicitud_id=agent.id))
        db.session.add(Supplementals(supplementals=allSupplementals, solicitud_id=agent.id))
        db.session.add(MedicareAdvantage(medicareAdvantage=allMedicareAdvantage, solicitud_id=agent.id))
        db.session.add(MedicareSupplement(medicareSupplement=allMedicareSupplement, solicitud_id=agent.id))
        db.session.add(LifeInsurance(lifeInsurance=allLifeInsurance, solicitud_id=agent.id))
        db.session.add(FinalExpenses(finalExpenses=allFinalExpenses, solicitud_id=agent.id))
        db.session.add(ShortTermMedical(sortTermMedical=allShortTermMedical, solicitud_id=agent.id))
        db.session.add(Contacted(contacted=allContacted, solicitud_id=agent.id))

        db.session.commit()

        # ---- Generar el PDF ----
        pdf = render_pdf(
            nombre, email, phone, zipCode, licensed, npn, observation,
            allAca, allSupplementals, allMedicareAdvantage, allMedicareSupplement,
            allLifeInsurance, allFinalExpenses, allShortTermMedical, allContacted,
            documentos=documentos
        )

        try:
            # Enviar correo con PDF adjunto
            msg = Message("New Contracting", recipients=[os.getenv("MAIL_RECIPIENT")])
            msg.body = "Adjunto encontrarás el PDF con los datos del formulario."
            msg.attach("contracting.pdf", "application/pdf", pdf.read())
            mail.send(msg)

            return redirect(url_for("form", success=1))
        except Exception as e:
            print("❌ Error al enviar correo:", e)
            return redirect(url_for("form", error=1))

    success = request.args.get("success")
    error = request.args.get("error")
    return render_template("form.html", success=success, error=error)


if __name__ == "__main__":
    app.run(debug=True)
