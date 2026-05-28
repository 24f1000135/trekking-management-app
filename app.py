from flask import Flask, render_template
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__, template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekkingapp.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trekkingmanagemntapp'

db.init_app(app)

@app.route('/')
def home():
    return render_template("home.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("DB creation successful!")

        admin = User.query.filter_by(role="Admin").first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@mail.com",
                password="admin123",
                role="Admin", 
                is_blacklisted=False)
            
            db.session.add(admin)
            db.session.commit()
            print("Admin created.")
            
    app.run(debug=True)

              
