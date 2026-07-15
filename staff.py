from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Trek, Booking
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
    assigned_treks = Trek.query.filter_by(staff_id=session['user_id'], is_removed=False).all()

    count_participants = Booking.query.join(Trek).filter(Trek.staff_id == session['user_id'],
                                Trek.is_removed == False, 
                                Booking.status == "Booked").count()

    count_open_treks = Trek.query.filter_by(staff_id=session['user_id'], status="Open", is_removed=False).count()

    return render_template("staff/dashboard.html",
                           count_assigned_treks=count_assigned_treks,
                           assigned_treks=assigned_treks,
                           count_participants=count_participants,
                           count_open_treks=count_open_treks)

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

@staff.route("/update_status/<int:trek_id>", methods=['POST'])
def update_status(trek_id):
    trek = Trek.query.get(trek_id)
    if trek.staff_id != session['user_id']:
        flash("You are not assigned to this trek.", "error")
        return redirect(url_for("staff.dashboard"))
    
    status = request.form.get('status')
    if status:
        trek.status = status
        if status == "Completed":
            active_bookings = Booking.query.filter_by(trek_id=trek_id, status="Booked").all()
            for booking in active_bookings:
                booking.status = "Completed"
        db.session.commit()
        flash(f"{trek.title} is {status}.", "success")

    return redirect(url_for("staff.dashboard"))

@staff.route("/update_slots/<int:trek_id>", methods=['POST'])
def update_slots(trek_id):
    trek = Trek.query.get(trek_id)
    if trek.staff_id != session['user_id']:
        flash("You are not assigned to this trek.", "error")
        return redirect(url_for("staff.dashboard"))
    
    available_slots = request.form.get('available_slots')
    if available_slots:
        slots = int(available_slots)
        if (slots > trek.total_slots) or (slots < 0):
            flash("Available slots must be within total slots.", "error")
            return redirect(url_for("staff.dashboard"))
        trek.available_slots = slots
    db.session.commit()
    flash(f"{trek.title}'s slots are updated", "success")

    return redirect(url_for("staff.dashboard"))
    
@staff.route("/registered_trekkers/<int:trek_id>", methods=['POST', 'GET'])   
def registered_trekkers(trek_id):
    trek = Trek.query.get(trek_id)
    if trek.staff_id != session['user_id']:
        flash("You are not assigned to this trek.", "error")
        return redirect(url_for("staff.dashboard"))
    
    all_participants = Booking.query.filter_by(trek_id=trek.id).all()

    count_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
    count_cancels = Booking.query.filter_by(trek_id=trek.id, status="Cancelled").count()

    return render_template("staff/registered_trekkers.html", all_participants=all_participants, trek=trek, count_bookings=count_bookings, count_cancels=count_cancels)

@staff.route("/cancel_booking/<int:booking_id>", methods=['POST'])
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    trek = Trek.query.get(booking.trek_id)
    if trek.staff_id != session['user_id']:
        flash("You are not assigned to this trek.", "error")
        return redirect(url_for("staff.dashboard"))

    if booking.status == "Booked":
        booking.status = "Cancelled"
        trek.available_slots += 1
        db.session.commit()
        flash("Booking cancelled and slot restored", "success")
    
    return redirect(url_for("staff.registered_trekkers", trek_id=trek.id))

@staff.route("/restore_booking/<int:booking_id>", methods=['POST'])
def restore_booking(booking_id):
    booking = Booking.query.get(booking_id)
    trek = Trek.query.get(booking.trek_id)
    if trek.staff_id != session['user_id']:
        flash("You are not assigned to this trek.", "error")
        return redirect(url_for("staff.dashboard"))

    if trek.available_slots <= 0:
        flash("There are no available slots to restore this booking.", "error")
        return redirect(url_for("staff.registered_trekkers", trek_id=trek.id))

    booking.status = "Booked"
    trek.available_slots -= 1
    db.session.commit()
    flash("Booking restored successfully.", "success")

    return redirect(url_for("staff.registered_trekkers", trek_id=trek.id))
