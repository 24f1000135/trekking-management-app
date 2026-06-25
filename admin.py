from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Trek, Booking
from werkzeug.security import generate_password_hash
from datetime import datetime

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.before_request
def check_admin():
    if not session.get('user_id'):
        flash("Please log in to continue.", "error")
        return redirect(url_for('auth.login'))
    
    if session.get('role') != "Admin":
        flash("Unauthorised access.", "warning")
        return redirect(url_for('auth.login'))

@admin.route("/dashboard", methods=['POST', 'GET'])
def dashboard():

    count_trekkers = User.query.filter_by(role="Trekker").count()
    count_trek_staffs = User.query.filter_by(role="Staff").count()
    count_treks = Trek.query.count()
    count_bookings = Booking.query.count()
        
    return render_template("admin/dashboard.html", count_trekkers=count_trekkers,
                           count_trek_staffs=count_trek_staffs,
                           count_treks=count_treks,
                           count_bookings=count_bookings)

@admin.route("/register_staff", methods=['POST', 'GET'])
def register_staff():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for("admin.register_staff"))

        hashed_pass = generate_password_hash(password)
        new_staff = User(name=name,
                           email=email,
                           contact=contact,
                           role='Staff',
                           password=hashed_pass,
                           is_blacklisted=False
                           )
        
        db.session.add(new_staff)
        db.session.commit()
        flash(f"{name} is registered as a new staff member successfully", "success")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/register_staff.html")

@admin.route("/new_trek", methods=['POST', 'GET'])
def new_trek():
    if request.method == 'POST':
        # staffs = User.query.filter_by(role="Staff").all()

        title = request.form.get('title')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        total_slots = request.form.get('total_slots')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        status = request.form.get('status')

        new_trek = Trek(title=title,
                        location=location,
                        difficulty=difficulty,
                        duration=int(duration),
                        total_slots=total_slots,
                        available_slots=total_slots,
                        start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                        end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                        status=status)
        
        db.session.add(new_trek)
        db.session.commit()
        flash("New trek is added.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/new_trek.html")