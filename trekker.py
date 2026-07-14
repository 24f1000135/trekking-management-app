from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import db, User, Trek, Booking
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
    search   = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    location   = request.args.get('location', '')
    query = Trek.query.filter_by(status="Open", is_removed=False)

    if search:
        query = query.filter(Trek.title.ilike(f"%{search}%"))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    available_treks = query.all()
    booked_treks = Booking.query.filter_by(user_id=session['user_id'], status="Booked").all()
    trekking_history = Booking.query.join(Trek).filter(Booking.user_id==session['user_id'], 
                                        Booking.status.in_(['Completed', 'Cancelled'])).all()

    return render_template("trekker/dashboard.html", available_treks=available_treks,
                            booked_treks=booked_treks, 
                            search=search, 
                            difficulty=difficulty, 
                            location=location,
                            trekking_history=trekking_history)

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

@trekker.route("/book_trek/<int:trek_id>", methods=['POST'])
def book_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if trek.available_slots <= 0:
        flash("No slots are available for this trek.", "error")
        return redirect(url_for('trekker.dashboard'))

    existing_booking = Booking.query.filter_by(trek_id=trek_id, user_id=session['user_id'], status="Booked").first()
    if existing_booking:
        flash("You have booked this trek already.", "error")
        return redirect(url_for('trekker.dashboard'))

    book_trek = Booking(trek_id=trek_id, user_id=session['user_id'], status="Booked", payment_status="Unpaid" )
    trek.available_slots -= 1

    db.session.add(book_trek)
    db.session.commit()
    flash(f"Trek for {trek.title} is booked successfully", "success")

    return redirect(url_for("trekker.dashboard"))
    
@trekker.route("/booking_detail/<int:booking_id>", methods=['GET'])
def booking_detail(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != session['user_id']:
        flash("You are not authorised to view this booking.", "error")
        return redirect(url_for('trekker.dashboard'))
    return render_template("trekker/booking_detail.html", booking=booking)

@trekker.route("/cancel_booking/<int:booking_id>", methods=['POST'])
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)

    if booking.user_id != session['user_id']:
        flash("Unauthorised.", "error")
        return redirect(url_for("trekker.dashboard"))
    if booking.status != "Booked":
        flash("This booking cannot be cancelled.", "error")
        return redirect(url_for("trekker.dashboard"))

    booking.status = "Cancelled"
    booking.trek.available_slots += 1
    db.session.commit()
    flash("Booking cancelled successfully.", "success")

    return redirect(url_for("trekker.dashboard"))

@trekker.route("/pay_booking/<int:booking_id>", methods=['POST'])
def pay_booking(booking_id):
    booking = Booking.query.get(booking_id)

    if booking.user_id != session['user_id']:
        flash("Unauthorised.", "error")
        return redirect(url_for("trekker.dashboard"))
    if booking.payment_status == "Paid":
        flash("This booking is already paid.", "warning")
        return redirect(url_for("trekker.booking_detail", booking_id=booking.id))
    if booking.status != "Booked":
        flash("Cannot pay for a cancelled or completed booking.", "error")
        return redirect(url_for("trekker.booking_detail", booking_id=booking.id))

    booking.payment_status = "Paid"
    db.session.commit()
    flash("Payment successful.", "success")

    return redirect(url_for("trekker.booking_detail", booking_id=booking.id))
