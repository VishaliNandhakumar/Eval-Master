import secrets
import PyPDF2
from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ngrok import run_with_ngrok # Required for ngrok to work


app = Flask(__name__)
run_with_ngrok(app)
  # Start ngrok when app is run
# app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = 'your_secret_key'
  # Some random string
  # Required for session management


# PostgreSQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To disable Flask-SQLAlchemy modification tracking
app.config['SECRET_KEY'] = secrets.token_hex(16)  # For session management -- generated random secret key
app.config['SESSION_TYPE'] = 'filesystem'  # To store session data


# 
db = SQLAlchemy(app)
requests.Session()

# Schema defnition
class UserDetails(db.Model):
    __tablename__ = 'user_details'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email_id = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<UserDetails {self.username}>'

# schema connection
with app.app_context():
    db.create_all()  # This creates the tables defined in your models

# home page
@app.route('/')
def home():
    """Render home page."""
    return render_template('home.html')


# login API
@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query the database for the user with the provided email
        user = UserDetails.query.filter_by(email_id=email).first()
        
        if user and check_password_hash(user.password, password):
            # If user exists and password is correct, set session data
            session['loggedin'] = True
            session['userid'] = user.id
            session['username'] = user.username
            session['email'] = user.email_id
            

            flash('Logged in successfully!', 'success')
             # Redirect to /index page
            return redirect(url_for('index'))

        else:
            flash('Invalid email or password!', 'danger')
    
    return render_template('login.html')

#Logout API
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

# Register API
@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("Inside post")
        username = request.form['name']
        print(username)
        email = request.form['email']
        print(email)
        password = request.form['password']
        print("password")
        
        # Check if the email or username already exists in the database
        existing_user = UserDetails.query.filter_by(email_id=email).first()
        if existing_user:
            flash('Email is already registered!', 'danger')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = generate_password_hash(password,method='pbkdf2:sha256')

        # Create a new user and add to the database
        new_user = UserDetails(username=username, email_id=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print("registration successful")

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirect to login page after successful registration
    
    return render_template('register.html')  # Render the registration form

# Index API
@app.route('/index')
def index():
    """Render the index page if the user is logged in."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Get username from database using session data
    user = UserDetails.query.filter_by(email_id=session.get('email')).first()
    if user:
        username = user.username
    else:
        username = "Guest"  # Fallback value
        
    return render_template('index.html', username=username)

# Colab URL (get the public URL from Colab, e.g., from ngrok or Google Colab's external exposure)
colab_url = "https://2585-34-87-94-123.ngrok-free.app/evaluate"  # Replace with the actual Colab URL


def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Handle cases where extract_text() may return None
    return text.strip()

# Evaluate API
from flask import Flask, request, jsonify
import requests


@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        expected_answer = None
        student_answer = None

        # 🟢 Case 1: PDF Upload (Multipart Form Data)
        if 'expected_file' in request.files and 'student_file' in request.files:
            expected_pdf = request.files['expected_file']
            student_pdf = request.files['student_file']

            if expected_pdf.filename == '' or student_pdf.filename == '':
                return jsonify({"error": "Both files must be provided"}), 400

            expected_answer = extract_text_from_pdf(expected_pdf)
            student_answer = extract_text_from_pdf(student_pdf)

        # 🟢 Case 2: JSON Input (Text-based API)
        elif request.is_json:
            data = request.get_json()
            expected_answer = data.get("expected_answer", "").strip()
            student_answer = data.get("student_answer", "").strip()

        # 🛑 Validation: Ensure both expected and student answers are present
        if not expected_answer or not student_answer:
            return jsonify({"error": "Both expected_answer and student_answer are required"}), 400

        # 🔄 Send data to Colab for evaluation
        response = requests.post(colab_url, json={
            "expected_answer": expected_answer,
            "student_answer": student_answer
        })

        # ✅ If Colab successfully processes it, store results in session
        if response.status_code == 200:
            result_data = response.json()
            session['evaluation_result'] = result_data  # Store in session
            return jsonify({"redirect": url_for('result_page')})  # Redirect to results page

        # 🛑 Error from Colab
        return jsonify({"error": "Error from Colab server"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500


@app.route('/get_results', methods=['GET'])
def get_results():
    """Fetches evaluation results from the session for frontend display."""
    result_data = session.get('evaluation_result')
    if not result_data:
        return jsonify({"error": "No results found"}), 404
    return jsonify(result_data)


@app.route('/results')
def result_page():
    """Renders the evaluation results page."""
    return render_template("evaluationresults.html")


# Run the Flask App
if __name__ == '__main__':
    app.run()

