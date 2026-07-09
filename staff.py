from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Trek
from werkzeug.security import generate_password_hash

staff = Blueprint("staff", __name__, url_prefix="/staff")

@staff.before_request
def check_staff():
    if not session.get('user_id'):
        flash("Please log in to continue.", "error")
        return redirect(url_for('auth.login'))
       
    if session.get('role') != "Staff":
        flash("Unauthorised access.", "warning")
        return redirect(url_for('auth.login'))

@staff.route("/dashboard")
def dashboard():
    count_assigned_treks = Trek.query.filter_by(staff_id=session['user_id'], is_removed=False).count()

    return render_template("staff/dashboard.html", count_assigned_treks=count_assigned_treks)

@staff.route("/edit_profile/<int:user_id>", methods=['POST', 'GET'])
def edit_profile(user_id):
    edit_staff = User.query.get(session['user_id'])

    if request.method == 'POST':
        edit_staff.name = request.form.get('name')
        edit_staff.email = request.form.get('email')
        edit_staff.contact = request.form.get('contact')
        new_password = request.form.get('password')
        if new_password:
            edit_staff.password = generate_password_hash(new_password)
        edit_staff.staff_profile.experience = int(request.form.get('experience'))
        edit_staff.staff_profile.specialization = request.form.get('specialization')

        db.session.commit()
        flash("Your profile is updated.", "success")
        return redirect(url_for("staff.dashboard",))
    
    return render_template("staff/edit_profile.html", edit_staff=edit_staff)

