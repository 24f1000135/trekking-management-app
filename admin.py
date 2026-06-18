from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User
from werkzeug.security import generate_password_hash

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.before_request
def check_admin():
    if not session.get('user_id'):
        flash("Please log in to continue.", "error")
        return redirect(url_for('auth.login'))
    
    if session.get('role') != "Admin":
        flash("Unauthorised access.", "warning")
        return redirect(url_for('auth.login'))

@admin.route("/dashboard")
def dashboard():

    return render_template("admin/dashboard.html")

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

