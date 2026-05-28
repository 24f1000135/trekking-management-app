from flask import Flask, render_template
from models import db

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
    
    app.run(debug=True)

              
