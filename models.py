from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="Trekker")
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    treks_managed = db.relationship("Trek", backref="manager", lazy=True)
    bookings = db.relationship("Booking", backref="trekker", lazy=True, cascade="all, delete-orphan")

    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False, cascade="all, delete-orphan")


class StaffProfile(db.Model):

    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    staff_status = db.Column(db.String(20), nullable=True)   # use it for trek staff to track if ther account is Pending, approved or rejected
    experience = db.Column(db.Integer, nullable=True)
    specialization = db.Column(db.String(100), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)


class Trek(db.Model):

    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Pending")   # will track Open / Closed / Completed
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_removed = db.Column(db.Boolean, nullable=False, default=False)

    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)      

    bookings = db.relationship("Booking", backref="trek", lazy=True)


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Booked")   #will track reservation if booked, cancelled or completed
    payment_status = db.Column(db.String(20), nullable=False, default="Unpaid")
    
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
