from db import db

class Solicitud(db.Model):
    __tablename__ = 'solicitud'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(100))
    zipCode = db.Column(db.Integer)
    address = db.Column(db.String(255))
    licensed = db.Column(db.String(10))
    npn = db.Column(db.String(20))
    TC = db.Column(db.String(45))
    observation = db.Column(db.Text)
    
class Aca(db.Model):
    __tablename__ = 'aca'

    id = db.Column(db.Integer, primary_key=True)
    aca = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class Supplementals(db.Model):
    __tablename__ = 'supplementals'

    id = db.Column(db.Integer, primary_key=True)
    supplementals = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class MedicareAdvantage(db.Model):
    __tablename__ = 'medicareAdvantage'

    id = db.Column(db.Integer, primary_key=True)
    medicareAdvantage = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class MedicareSupplement(db.Model):
    __tablename__ = 'medicareSupplement'

    id = db.Column(db.Integer, primary_key=True)
    medicareSupplement = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class LifeInsurance(db.Model):
    __tablename__ = 'lifeInsurance'

    id = db.Column(db.Integer, primary_key=True)
    lifeInsurance = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class FinalExpenses(db.Model):
    __tablename__ = 'finalExpenses'

    id = db.Column(db.Integer, primary_key=True)
    finalExpenses = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class ShortTermMedical(db.Model):
    __tablename__ = 'sortTermMedical'

    id = db.Column(db.Integer, primary_key=True)
    sortTermMedical = db.Column(db.String(100))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class Contacted(db.Model):
    __tablename__ = 'contacted'

    id = db.Column(db.Integer, primary_key=True)
    contacted = db.Column(db.String(200))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)

class StateCoverage(db.Model):
    __tablename__ = 'stateCoverage'

    id = db.Column(db.Integer, primary_key=True)
    states = db.Column(db.String(200))
    solicitud_id = db.Column(db.Integer, db.ForeignKey('solicitud.id'), nullable=False)


