from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Trek
from werkzeug.security import generate_password_hash

trekker = Blueprint("trekker", __name__, url_prefix="/trekker")

@trekker.before_request
def check_trekker():
    if not session.get('user_id'):
        flash("Please log in to continue.", "error")
        return redirect(url_for('auth.login'))
    
    if session.get('role') != "Trekker":
        flash("Unauthorised access.", "warning")
        return redirect(url_for('auth.login'))

@trekker.route("/dashboard")
def dashboard():
    available_treks = Trek.query.filter_by(status="Open", is_removed=False).all()

    return render_template("trekker/dashboard.html", available_treks=available_treks)

@trekker.route("/edit_profile/<int:user_id>", methods=['POST', 'GET'])
def edit_profile(user_id):
    edit_trekker = User.query.get(session['user_id'])

    if request.method == "POST":
        edit_trekker.name = request.form.get('name')
        edit_trekker.email = request.form.get('email')
        edit_trekker.contact = request.form.get('contact')
        new_password = request.form.get('password')
        if new_password:
            edit_trekker.password = generate_password_hash(new_password)

        db.session.commit()
        flash("Your profile is updated.", "success")
        return redirect(url_for("trekker.dashboard"))
    
    return render_template("trekker/edit_profile.html", edit_trekker=edit_trekker)


    

