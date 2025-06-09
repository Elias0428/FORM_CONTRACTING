from flask import Flask, render_template, request, redirect, url_for
from db import db
from models import *
from dotenv import load_dotenv
from xhtml2pdf import pisa
from flask_mail import Mail, Message
from io import BytesIO
from flask_migrate import Migrate
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
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
db.init_app(app)
migrate = Migrate(app, db) 


def render_pdf(nombre, email, phone, zipCode, licensed, npn, observation, allAca, allMedicareAdvantage, allMedicareSupplement, allLifeInsurance, allFinalExpenses):
    # Renderizar la plantilla con variables individuales
    html = render_template("pdf_template.html", name=nombre, email=email, phone=phone, zipCode=zipCode, licensed=licensed, npn=npn, observation=observation, allAca=allAca, allMedicareAdvantage=allMedicareAdvantage, allMedicareSupplement=allMedicareSupplement, allLifeInsurance=allLifeInsurance, allFinalExpenses=allFinalExpenses )
    pdf_stream = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_stream)
    if pisa_status.err:
        return None
    pdf_stream.seek(0)  # importante para leer desde el inicio luego
    return pdf_stream


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
        

        # Guardar en base de datos
        agent = Solicitud(nombre=nombre, email=email, phone=phone, zipCode=zipCode, licensed=licensed, npn=npn, observation=observation)
        db.session.add(agent)
        db.session.flush()  
        
        aca = request.form.getlist("aca")
        allAca = ", ".join(aca)
        planAca = Aca(aca=allAca, solicitud_id=agent.id)
        db.session.add(planAca)

        medicareAdvantage = request.form.getlist("medicareAdvantage")
        allMedicareAdvantage = ", ".join(medicareAdvantage)
        planMedicareAdvantage  = MedicareAdvantage(medicareAdvantage=allMedicareAdvantage, solicitud_id=agent.id)
        db.session.add(planMedicareAdvantage)

        medicareSupplement = request.form.getlist("medicareSupplement")
        allMedicareSupplement = ", ".join(medicareSupplement)
        planMedicareSupplement = MedicareSupplement(medicareSupplement=allMedicareSupplement, solicitud_id=agent.id)
        db.session.add(planMedicareSupplement)

        lifeInsurance = request.form.getlist("lifeInsurance")
        allLifeInsurance = ", ".join(lifeInsurance)
        planLifeInsurance = LifeInsurance(lifeInsurance=allLifeInsurance, solicitud_id=agent.id)
        db.session.add(planLifeInsurance)

        finalExpenses = request.form.getlist("finalExpenses")
        allFinalExpenses = ", ".join(finalExpenses)
        planFinalExpenses = FinalExpenses(finalExpenses=allFinalExpenses, solicitud_id=agent.id)
        db.session.add(planFinalExpenses)

        db.session.commit()

        # Generar PDF con los datos
        pdf = render_pdf(nombre, email, phone, zipCode, licensed, npn, observation, allAca, allMedicareAdvantage, allMedicareSupplement, allLifeInsurance, allFinalExpenses)

        try: 
            # Enviar correo con PDF adjunto
            if pdf:
                msg = Message("New Contracting", recipients=[os.getenv("MAIL_RECIPIENT")])
                msg.body = "Adjunto encontrarás el PDF con los datos del formulario."
                msg.attach("contracting.pdf", "application/pdf", pdf.read())
                mail.send(msg)

            # Si todo va bien, redirigimos con success
            return redirect(url_for("form", success=1))

        except Exception as e:
            print("Error al enviar correo:", e)
            # Si falla el correo, redirigimos con error
            return redirect(url_for("form", error=1))


    success = request.args.get("success")
    error = request.args.get("error")
    return render_template("form.html", success=success, error=error)


if __name__ == "__main__":
    app.run(debug=True)
