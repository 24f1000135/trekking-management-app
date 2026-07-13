from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Trek, Booking, StaffProfile
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

@admin.route("/dashboard", methods=['GET'])
def dashboard():

    count_trekkers = User.query.filter_by(role="Trekker").count()
    count_trek_staffs = User.query.filter_by(role="Staff").count()
    count_treks = Trek.query.count()
    count_bookings = Booking.query.count()
        
    treks = Trek.query.all()

    all_bookings = Booking.query.join(Trek).join(User, Booking.user_id == User.id).all()

    trekking_history = Trek.query.all()

    return render_template("admin/dashboard.html", count_trekkers=count_trekkers,
                           count_trek_staffs=count_trek_staffs,
                           count_treks=count_treks,
                           count_bookings=count_bookings, treks=treks,
                           all_bookings=all_bookings,
                           trekking_history=trekking_history)

@admin.route("/new_trek", methods=['POST', 'GET'])
def new_trek():
    if request.method == 'POST':
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
                        total_slots=int(total_slots),
                        available_slots=int(total_slots),
                        start_date=datetime.strptime(start_date, "%Y-%m-%d"),
                        end_date=datetime.strptime(end_date, "%Y-%m-%d"),
                        status=status)
        
        db.session.add(new_trek)
        db.session.commit()
        flash("New trek is added.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/new_trek.html")

@admin.route("/edit_trek/<int:trek_id>", methods=['POST', 'GET'])
def edit_trek(trek_id):
    edit_trek = Trek.query.get(trek_id)

    if request.method == 'POST':
        edit_trek.title = request.form.get('title')
        edit_trek.location = request.form.get('location')
        edit_trek.difficulty = request.form.get('difficulty')
        edit_trek.duration = int(request.form.get('duration'))
        edit_trek.total_slots = int(request.form.get('total_slots'))
        edit_trek.start_date = datetime.strptime(request.form.get('start_date'), "%Y-%m-%d")
        edit_trek.end_date = datetime.strptime(request.form.get('end_date'), "%Y-%m-%d")
        edit_trek.status = request.form.get('status')

        db.session.commit()
        flash("Updated the trek details.", "success")
        return redirect(url_for("admin.view_treks"))
    
    return render_template("admin/edit_trek.html", trek=edit_trek)

@admin.route("/view_treks", methods=['GET'])
def view_treks():
    search = request.args.get('search', "")
    query = Trek.query.filter_by(is_removed=False)

    if search:
        if search.isdigit():
            query = query.filter(Trek.id == int(search))
        else:
            query = query.filter(Trek.title.ilike(f"%{search}%"))

    all_treks = query.all() 

    return render_template("admin/view_treks.html", all_treks=all_treks, search=search)

@admin.route("/remove_trek/<int:trek_id>/delete", methods=['POST', 'GET'])
def remove_trek(trek_id):
    trek = Trek.query.get(trek_id)
    trek.is_removed = True
    db.session.commit()
    flash("The trek is removed.", "success")

    return redirect(url_for("admin.view_treks"))

@admin.route("/view_staffs", methods=['GET'])
def view_staffs():
    search = request.args.get('search', "")
    query = User.query.filter_by(role="Staff")

    if search:
        if search.isdigit():
            query = query.filter(User.id == int(search))
        else:
            query = query.filter(User.name.ilike(f"%{search}%"))

    all_staffs = query.all() 

    return render_template("admin/view_staffs.html", all_staffs=all_staffs, search=search)

@admin.route("/approve_staff/<int:staff_id>", methods=['POST'])
def approve_staff(staff_id):
    staff = User.query.get(staff_id)
    staff.staff_profile.staff_status = "Approved"
    db.session.commit()
    flash(f"{staff.name}'s form has been approved.", "success")
    return redirect(url_for("admin.view_staffs"))

@admin.route("/reject_staff/<int:staff_id>", methods=['POST'])
def reject_staff(staff_id):
    staff = User.query.get(staff_id)
    staff.staff_profile.staff_status = "Rejected"
    db.session.commit()
    flash(f"{staff.name}'s form has been rejected.", "success")
    return redirect(url_for("admin.view_staffs"))

@admin.route("/remove_staff/<int:staff_id>", methods=['POST'])
def remove_staff(staff_id):
    staff = User.query.get(staff_id)
    staff.staff_profile.staff_status = "Removed"
    db.session.commit()
    flash(f"{staff.name} has been removed.", "success")
    return redirect(url_for("admin.view_staffs"))

@admin.route("/view_trekkers", methods=['POST', 'GET'])
def view_trekkers():
    search = request.args.get('search', "")
    query = User.query.filter_by(role="Trekker")

    if search:
        if search.isdigit():
            query = query.filter(User.id == int(search))
        else:
            query = query.filter(User.name.ilike(f"%{search}%"))

    all_trekkers = query.all() 

    return render_template("admin/view_trekkers.html", all_trekkers=all_trekkers, search=search)

@admin.route("/blacklist_user/<int:user_id>", methods=['POST'])
def blacklist_user(user_id):
    user = User.query.get(user_id)
    user.is_blacklisted = True
    db.session.commit()
    flash(f"{user.name}'s account is blacklisted.", "success")
    return redirect(request.referrer)

@admin.route("/unblacklist_user/<int:user_id>", methods=['POST'])
def unblacklist_user(user_id):
    user = User.query.get(user_id)
    user.is_blacklisted = False
    db.session.commit()
    flash(f"{user.name}'s account is unblacklisted.", "success")
    return redirect(request.referrer)

@admin.route("/assign_staff/<int:trek_id>", methods=['POST', 'GET'])
def assign_staff(trek_id):
    trek = Trek.query.get(trek_id)
    approved_staff = User.query.join(StaffProfile).filter(User.role == "Staff", StaffProfile.staff_status == "Approved").all()

    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        staff = User.query.get(int(staff_id))
        trek.staff_id = int(staff_id) if staff_id else None
        db.session.commit()
        flash(f"{staff.name} is assigned to {trek.title}.", "success")
        return redirect(url_for("admin.view_treks"))
    
    return render_template("admin/assign_staff.html", trek=trek, approved_staff=approved_staff)




