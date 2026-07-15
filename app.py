from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash
from auth import auth
from admin import admin
from staff import staff
from trekker import trekker

app = Flask(__name__, template_folder="templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekkingapp.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trekkingmanagemntapp'

db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(staff)
app.register_blueprint(trekker)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("DB creation successful!")

        admin_user = User.query.filter_by(role="Admin").first()
        if not admin_user:
            admin_user = User(
                name="Admin",
                email="admin@mail.com",
                password=generate_password_hash("admin123"),
                role="Admin", 
                is_blacklisted=False)
            
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)

              
