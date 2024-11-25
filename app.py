'''from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

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

# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('search', '').lower()  # Search query for filtering files
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

if __name__ == '__main__':
    app.run(debug=True)
'''
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
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

if __name__ == '__main__':
    app.run(debug=True)

