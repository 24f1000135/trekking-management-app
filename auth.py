from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, StaffProfile
from werkzeug.security import generate_password_hash, check_password_hash

auth= Blueprint("auth", __name__)

@auth.route("/", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not registered.", "error")
            return redirect(url_for("auth.login"))
        
        if user.is_blacklisted == True:
            flash("Your account has been suspended.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Incorrect Password", "error")
            return redirect(url_for("auth.login"))

        if user.role == "Staff":
            if user.staff_profile.staff_status == 'Pending':
                flash("Waiting for admin aprroval.", "error")
                return redirect(url_for("auth.login"))
            elif user.staff_profile.staff_status == "Rejected":
                flash("Registration was not be approved!", "error")
                return redirect(url_for("auth.login"))
            elif user.staff_profile.staff_status == "Removed":
                flash("Your account has been removed by admin.", "error")
                return redirect(url_for("auth.login"))

        session['user_id'] = user.id
        session['name'] = user.name
        session['role'] = user.role
        flash(f"Welcome, {user.name}!", "success")
        
        if user.role == "Admin":
            return redirect(url_for("admin.dashboard"))
        elif user.role == "Staff":
            return redirect(url_for("staff.dashboard"))
        else:
            return redirect(url_for("trekker.dashboard"))
        
    return render_template('auth/login.html')

@auth.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect(url_for("auth.register"))

        hashed_pass = generate_password_hash(password)
        new_trekker = User(name=name,
                           email=email,
                           contact=contact,
                           role='Trekker',
                           password=hashed_pass,
                           is_blacklisted=False
                           )
        
        db.session.add(new_trekker)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template('auth/register.html')

@auth.route("/staff_register", methods=['POST', 'GET'])
def staff_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        contact = request.form.get('contact')
        password = request.form.get('password')
        experience = request.form.get('experience')
        specialization = request.form.get('specialization')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect(url_for("auth.staff_register"))
    
        hashed_pass = generate_password_hash(password)
        new_staff = User(name=name,
                         email=email,
                         contact=contact,
                         role='Staff',
                         password=hashed_pass,
                         is_blacklisted=False)

        db.session.add(new_staff)
        db.session.commit()

        new_staff_profile = StaffProfile(user_id=new_staff.id,
                                         staff_status='Pending',
                                         experience=int(experience),
                                         specialization=specialization)
        
        db.session.add(new_staff_profile)
        db.session.commit()
        flash("Registration form submitted. Waiting for admin approval.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register_staff.html")

@auth.route("/dashboard")
def dashboard():
    if session.get('role') == 'Admin':
        return redirect(url_for('admin.dashboard'))
    elif session.get('role') == 'Staff':
        return redirect(url_for('staff.dashboard'))
    else:
        return redirect(url_for('trekker.dashboard'))

@auth.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))

