from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User

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
    
    return render_template("staff/dashboard.html")

