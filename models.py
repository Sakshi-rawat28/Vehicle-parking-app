from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Define the relationship with Vehicle
    vehicles = db.relationship('Vehicle', backref='user', lazy=True)
    # Define the relationship with Reservation
    reserve_user= db.relationship('Reservation', backref='user', lazy=True)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(25), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(20))


    # Define the relationship with Reservation
    reserved_vehicle = db.relationship('Reservation', backref='vehicle', lazy=True,cascade="all, delete-orphan")

class ParkingLot(db.Model):
    __tablename__ = 'parkinglot'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    # is_deleted= db.Column(db.Boolean , default=False)

    # Define the relationship with ParkingSpot
    spots= db.relationship('ParkingSpot', backref='parkinglot', lazy=True,cascade="all, delete-orphan" )
    lots= db.relationship('Reservation', backref='parkinglot', lazy=True,cascade="all, delete-orphan")

class ParkingSpot(db.Model):
    __tablename__ = 'parkingspot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    # is_deleted= db.Column(db.Boolean , default=False)

    # Define the relationship with Reservation
    reserved_spot = db.relationship('Reservation', backref='parkingspot', lazy=True ,cascade="all, delete-orphan")

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)


with app.app_context():
    db.create_all()  # Create the database tables if they don't exist
    print("Database tables created successfully.")

    #creating default admin user
    admin= User.query.filter_by(is_admin=True).first()
    if not admin:
        password_hash = generate_password_hash('admin123')
        admin = User(name='Admin', address='Admin Address', pincode='123456',
                     username='admin123@gmail.com', passhash=password_hash, is_admin=True)
        db.session.add(admin)
        db.session.commit()