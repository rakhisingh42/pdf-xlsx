'''from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Paths to store files
PDF_FOLDER = os.path.join('static', 'pdfs')
EXCEL_FOLDER = os.path.join('static', 'excels')
app.config['PDF_FOLDER'] = PDF_FOLDER
app.config['EXCEL_FOLDER'] = EXCEL_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}

# Ensure folders exist
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)

# Check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy user store (replace with a database in production)
users = {}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Create some test users
users['admin'] = User('admin', 'admin', 'password123')

# Load a user
@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Routes for login and signup
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        
        if user and user.password == password:  # In production, use hashed passwords!
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            user = User(username, username, password)  # Store user (hashed password is recommended)
            users[username] = user
            flash('User created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose another one.', 'danger')
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Home route (with file upload)
@app.route('/', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def index():
    # Search query for filtering files
    search_query = request.args.get('search', '').lower()
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if search_query in f.lower()]
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if search_query in f.lower()]
    
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            # Save the file to the correct folder
            if filename.endswith('.pdf'):
                file.save(os.path.join(PDF_FOLDER, filename))
            elif filename.endswith(('.xlsx', '.xls')):
                file.save(os.path.join(EXCEL_FOLDER, filename))
            flash(f'{filename} uploaded successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Only PDFs and Excel files are allowed.', 'danger')

    return render_template('index.html', pdf_files=pdf_files, excel_files=excel_files)

# Routes to serve files
@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory(app.config['PDF_FOLDER'], filename)

@app.route('/excel/<filename>')
def serve_excel(filename):
    return send_from_directory(app.config['EXCEL_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))'''

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

# Initialize db outside of app to avoid circular import
db = SQLAlchemy()

# Setup Flask-Login
login_manager = LoginManager()

# Paths to store files
PDF_FOLDER = os.path.join('static', 'pdfs')
EXCEL_FOLDER = os.path.join('static', 'excels')
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}

# Ensure folders exist
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create application factory function
def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # For flash messages

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Change this to another DB URI if needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db with the app
    db.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # User Model
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(150), unique=True, nullable=False)
        password = db.Column(db.String(150), nullable=False)

    # Load a user for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Routes for login, signup, etc.
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials. Please try again.', 'danger')
                return redirect(url_for('login'))
        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose another one.', 'danger')
                return redirect(url_for('signup'))
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    # Home route (with file upload)
    @app.route('/', methods=['GET', 'POST'])
    @login_required  # Ensure the user is logged in
    def index():
        search_query = request.args.get('search', '').lower()
        pdf_files = [f for f in os.listdir(PDF_FOLDER) if search_query in f.lower()]
        excel_files = [f for f in os.listdir(EXCEL_FOLDER) if search_query in f.lower()]
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = file.filename
                if filename.endswith('.pdf'):
                    file.save(os.path.join(PDF_FOLDER, filename))
                elif filename.endswith(('.xlsx', '.xls')):
                    file.save(os.path.join(EXCEL_FOLDER, filename))
                flash(f'{filename} uploaded successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid file type. Only PDFs and Excel files are allowed.', 'danger')
        return render_template('index.html', pdf_files=pdf_files, excel_files=excel_files)

    # Routes to serve files
    @app.route('/pdf/<filename>')
    def serve_pdf(filename):
        return send_from_directory(PDF_FOLDER, filename)

    @app.route('/excel/<filename>')
    def serve_excel(filename):
        return send_from_directory(EXCEL_FOLDER, filename)

    # Route to delete a PDF file
    @app.route('/delete/pdf/<filename>', methods=['POST'])
    @login_required
    def delete_pdf(filename):
        file_path = os.path.join(PDF_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'{filename} has been deleted!', 'success')
        else:
            flash(f'{filename} does not exist!', 'danger')
        return redirect(url_for('index'))

    # Route to delete an Excel file
    @app.route('/delete/excel/<filename>', methods=['POST'])
    @login_required
    def delete_excel(filename):
        file_path = os.path.join(EXCEL_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'{filename} has been deleted!', 'success')
        else:
            flash(f'{filename} does not exist!', 'danger')
        return redirect(url_for('index'))

    return app

# This block is for running the application directly (optional)
if __name__ == "__main__":
    app = create_app()  # Initialize app here
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
