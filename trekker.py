from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User

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
    
    return render_template("trekker/dashboard.html")


