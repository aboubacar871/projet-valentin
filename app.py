from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèle Utilisateur
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes principales
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password, is_admin=False, is_approved=False)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Inscription réussie ! Veuillez effectuer le paiement au +225 05 65 92 21 05 en attendant la validation.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            elif not user.is_approved:
                return redirect(url_for('pending_approval'))
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_approved and not current_user.is_admin:
        return redirect(url_for('pending_approval'))
    return render_template('dashboard.html')

@app.route('/en-attente-validation')
@login_required
def pending_approval():
    if current_user.is_approved or current_user.is_admin:
        return redirect(url_for('dashboard'))
    return render_template('pending.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Routes d'administration pour Valentin
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return "Accès refusé. Réservé à l'administrateur.", 403
    
    pending_users = User.query.filter_by(is_approved=False, is_admin=False).all()
    return render_template('admin.html', users=pending_users)

@app.route('/admin/approve/<int:user_id>')
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return "Accès refusé", 403
        
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)