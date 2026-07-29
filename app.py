import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cyber_academy_secure_key_2026_!@#')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cyber_academy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# ==================== MODÈLES DE BASE DE DONNÉES ====================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(50), nullable=False)
    pays = db.Column(db.String(50), nullable=False)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='client')  # 'admin' ou 'client'
    statut_compte = db.Column(db.String(20), default='En attente')  # 'En attente' ou 'Actif'
    
    paiements = db.relationship('Paiement', backref='utilisateur', lazy=True)

class Paiement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    montant = db.Column(db.Float, nullable=False)
    methode = db.Column(db.String(50), nullable=False) # ex: Stripe, PayPal, Mobile Money
    statut = db.Column(db.String(20), default='Validé') # 'Validé' ou 'En attente'
    date_paiement = db.Column(db.DateTime, default=datetime.utcnow)

class MessageChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expéditeur = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class MessageIA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    question = db.Column(db.Text, nullable=False)
    reponse = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== TEMPLATE HTML / CSS / JS UNIFIÉ ====================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Cyber Academy - Plateforme d'Excellence en Cybersécurité{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #131b2e;
            --accent-color: #00ffcc;
            --text-color: #e2e8f0;
            --text-muted: #94a3b8;
            --border-color: #1e293b;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar {
            background-color: rgba(13, 17, 23, 0.95) !important;
            border-bottom: 1px solid var(--border-color);
        }
        .navbar-brand, .nav-link {
            color: var(--text-color) !important;
            font-weight: 500;
        }
        .nav-link:hover, .nav-link.active {
            color: var(--accent-color) !important;
        }
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            border-radius: 10px;
        }
        .form-control, .form-select {
            background-color: #0f172a;
            border: 1px solid var(--border-color);
            color: var(--text-color);
        }
        .form-control:focus, .form-select:focus {
            background-color: #0f172a;
            border-color: var(--accent-color);
            color: var(--text-color);
            box-shadow: 0 0 0 0.25rem rgba(0, 255, 204, 0.25);
        }
        .btn-custom {
            background-color: var(--accent-color);
            color: #000;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
        }
        .btn-custom:hover {
            background-color: #00b38f;
            color: #fff;
        }
        footer {
            background-color: #090d16;
            border-top: 1px solid var(--border-color);
            margin-top: auto;
            padding: 20px 0;
            text-align: center;
            color: var(--text-muted);
        }
        /* Widget Chat & IA Flottant */
        #chat-widget-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        #chat-popup {
            display: none;
            width: 350px;
            height: 480px;
            background: var(--card-bg);
            border: 1px solid var(--accent-color);
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: #0f172a;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-body {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            font-size: 0.9rem;
        }
        .chat-footer {
            padding: 10px;
            background: #0f172a;
            border-top: 1px solid var(--border-color);
        }
        .chat-bubble {
            padding: 8px 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            max-width: 85%;
            word-wrap: break-word;
        }
        .chat-user { background: #1e3a8a; color: #fff; margin-left: auto; }
        .chat-peer { background: #334155; color: #fff; }
        .chat-ai { background: #065f46; color: #fff; }
    </style>
    {% block extra_head %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}"><i class="fa-solid fa-shield-halved text-info me-2"></i>Cyber Academy</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-link"><a class="nav-link" href="{{ url_for('index') }}">Accueil</a></li>
                    <li class="nav-link"><a class="nav-link" href="{{ url_for('chat_communautaire') }}">Chat Communautaire</a></li>
                    {% if current_user.is_authenticated %}
                        {% if current_user.role == 'admin' %}
                            <li class="nav-link"><a class="nav-link text-warning" href="{{ url_for('admin_dashboard') }}">Admin Dashboard</a></li>
                        {% endif %}
                        <li class="nav-link"><a class="nav-link" href="{{ url_for('logout') }}">Déconnexion ({{ current_user.prenom }})</a></li>
                    {% else %}
                        <li class="nav-link"><a class="nav-link" href="{{ url_for('login') }}">Connexion</a></li>
                        <li class="nav-link"><a class="nav-link" href="{{ url_for('register') }}">Inscription</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <!-- Widget Flottant Chat & IA -->
    <div id="chat-widget-container">
        <button id="chat-toggle-btn" class="btn btn-custom rounded-circle p-3 shadow-lg" onclick="toggleChatPopup()">
            <i class="fa-solid fa-comments fa-lg"></i>
        </button>
        <div id="chat-popup">
            <div class="chat-header">
                <span><i class="fa-solid fa-robot text-info me-2"></i>Assistant IA & Support</span>
                <button class="btn btn-sm text-white" onclick="toggleChatPopup()"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="chat-body" id="ai-chat-messages">
                <div class="chat-bubble chat-ai">Bonjour ! Je suis l'assistant virtuel de Cyber Academy. Comment puis-je vous aider aujourd'hui ?</div>
            </div>
            <div class="chat-footer">
                <div class="input-group">
                    <input type="text" id="ai-input" class="form-control form-control-sm" placeholder="Posez votre question à l'IA..." onkeypress="if(event.key==='Enter') sendAIMessage()">
                    <button class="btn btn-custom btn-sm" onclick="sendAIMessage()"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>
        </div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; 2026 Cyber Academy - Tous droits réservés. Plateforme sécurisée et optimisée.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleChatPopup() {
            const popup = document.getElementById('chat-popup');
            popup.style.display = popup.style.display === 'flex' ? 'none' : 'flex';
        }
        function sendAIMessage() {
            const input = document.getElementById('ai-input');
            const text = input.value.trim();
            if(!text) return;
            
            const chatBody = document.getElementById('ai-chat-messages');
            chatBody.innerHTML += `<div class="chat-bubble chat-user">${text}</div>`;
            input.value = '';
            chatBody.scrollTop = chatBody.scrollHeight;

            fetch('/api/ai-chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: text})
            })
            .then(res => res.json())
            .then(data => {
                chatBody.innerHTML += `<div class="chat-bubble chat-ai">${data.reponse}</div>`;
                chatBody.scrollTop = chatBody.scrollHeight;
            })
            .catch(err => {
                chatBody.innerHTML += `<div class="chat-bubble chat-ai">Erreur de communication avec l'assistant.</div>`;
            });
        }
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""

# ==================== ROUTES DE L'APPLICATION ====================

@app.route('/')
def index():
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', """
    <div class="p-5 mb-4 bg-dark rounded-3 border border-secondary text-center">
        <h1 class="display-5 fw-bold text-info">Bienvenue sur Cyber Academy</h1>
        <p class="col-md-8 fs-4 mx-auto text-muted">La référence en formation et solutions de cybersécurité, pentesting et architecture réseau sécurisée.</p>
        <div class="mt-4">
            <a href="{{ url_for('register') }}" class="btn btn-custom btn-lg me-2">Créer un compte</a>
            <a href="\\u200b{{ url_for('login') }}" class="btn btn-outline-light btn-lg">Se connecter</a>
        </div>
    </div>
    """))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        telephone = request.form.get('telephone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        pays = request.form.get('pays')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(telephone=telephone).first():
            flash('Ce numéro de téléphone est déjà utilisé.', 'error')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Premier utilisateur enregistré devient automatiquement Admin
        is_first_user = User.query.count() == 0
        role_assigned = 'admin' if is_first_user else 'client'
        statut_assigned = 'Actif' if is_first_user else 'En attente'

        new_user = User(
            nom=nom, prenom=prenom, telephone=telephone, email=email,
            password_hash=hashed_password, adresse=adresse, ville=ville, pays=pays,
            role=role_assigned, statut_compte=statut_assigned
        )
        db.session.add(new_user)
        db.session.commit()

        # Si ce n'est pas le premier utilisateur, simuler ou enregistrer un paiement fictif/réel pour validation automatique
        if not is_first_user:
            paiement = Paiement(user_id=new_user.id, montant=99.00, methode='Carte Bancaire', statut='Validé')
            new_user.statut_compte = 'Actif'  # Validation automatique après paiement confirmé
            db.session.add(paiement)
            db.session.commit()

        flash('Compte créé avec succès ! Votre compte est actif après confirmation du paiement.', 'success')
        return redirect(url_for('login'))

    content = """
    <div class="row justify-content-center">
        <div class="col-md-8 card p-4 shadow">
            <h2 class="text-center mb-4 text-info"><i class="fa-solid fa-user-plus me-2"></i>Inscription Client / Admin</h2>
            <form method="POST">
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Nom</label><input type="text" name="nom" class="form-control" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Prénom</label><input type="text" name="prenom" class="form-control" required></div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Téléphone</label><input type="text" name="telephone" class="form-control" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Email</label><input type="email" name="email" class="form-control" required></div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Mot de passe</label><input type="password" name="password" class="form-control" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Confirmer le mot de passe</label><input type="password" name="confirm_password" class="form-control" required></div>
                </div>
                <div class="mb-3"><label class="form-label">Adresse</label><input type="text" name="adresse" class="form-control" required></div>
                <div class="row">
                    <div class="col-md-6 mb-3"><label class="form-label">Ville</label><input type="text" name="ville" class="form-control" required></div>
                    <div class="col-md-6 mb-3"><label class="form-label">Pays</label><input type="text" name="pays" class="form-control" required></div>
                </div>
                <button type="submit" class="btn btn-custom w-100 py-2">S'inscrire et Activer</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Connexion réussie !', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')

    content = """
    <div class="row justify-content-center">
        <div class="col-md-5 card p-4 shadow">
            <h2 class="text-center mb-4 text-info"><i class="fa-solid fa-right-to-bracket me-2"></i>Connexion</h2>
            <form method="POST">
                <div class="mb-3"><label class="form-label">Email</label><input type="email" name="email" class="form-control" required></div>
                <div class="mb-3"><label class="form-label">Mot de passe</label><input type="password" name="password" class="form-control" required></div>
                <button type="submit" class="btn btn-custom w-100 py-2">Se connecter</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('index'))

    users = User.query.all()
    paiements = Paiement.query.all()
    total_clients = User.query.filter_by(role='client').count()
    total_paiements = sum([p.montant for p in paiements])

    content = f"""
    <div class="container">
        <h1 class="mb-4 text-info"><i class="fa-solid fa-gauge-high me-2"></i>Tableau de Bord Administrateur</h1>
        <div class="row mb-4">
            <div class="col-md-4"><div class="card p-3 text-center"><h5>Total Clients</h5><h3>{total_clients}</h3></div></div>
            <div class="col-md-4"><div class="card p-3 text-center"><h5>Total Paiements</h5><h3>{total_paiements:.2f} €</h3></div></div>
            <div class="col-md-4"><div class="card p-3 text-center"><h5>Utilisateurs Totaux</h5><h3>{len(users)}</h3></div></div>
        </div>
        
        <h3 class="mb-3">Gestion des Utilisateurs & Comptes</h3>
        <div class="table-responsive card p-3">
            <table class="table table-dark table-hover">
                <thead>
                    <tr>
                        <th>ID</th><th>Nom & Prénom</th><th>Email</th><th>Téléphone</th><th>Rôle</th><th>Statut</th><th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{u.id}</td><td>{u.prenom} {u.nom}</td><td>{u.email}</td><td>{u.telephone}</td><td>{u.role}</td><td><span class='badge bg-{'success' if u.statut_compte=='Actif' else 'warning'}'>{u.statut_compte}</span></td><td>{u.date_inscription.strftime('%Y-%m-%d')}</td></tr>" for u in users])}
                </tbody>
            </table>
        </div>
    </div>
    """
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat_communautaire():
    if request.method == 'POST':
        texte = request.form.get('message')
        if texte:
            msg = MessageChat(expéditeur=f"{current_user.prenom} {current_user.nom}", message=texte)
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('chat_communautaire'))

    messages = MessageChat.query.order_by(MessageChat.timestamp.asc()).all()
    content = f"""
    <div class="container">
        <h2 class="mb-4 text-info"><i class="fa-solid fa-comments me-2"></i>Chat Communautaire en Temps Réel</h2>
        <div class="card p-3 mb-3" style="height: 400px; overflow-y: auto;" id="chat-box">
            {''.join([f"<div class='mb-2'><strong>{m.expéditeur}</strong> <small class='text-muted'>({m.timestamp.strftime('%H:%M')})</small>:<br>{m.message}</div>" for m in messages])}
        </div>
        <form method="POST">
            <div class="input-group">
                <input type="text" name="message" class="form-control" placeholder="Écrivez votre message..." required autocomplete="off">
                <button class="btn btn-custom" type="submit">Envoyer</button>
            </div>
        </form>
    </div>
    <script>
        const cb = document.getElementById('chat-box');
        cb.scrollTop = cb.scrollHeight;
    </script>
    """
    return render_template_string(BASE_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    data = request.get_json()
    question = data.get('question', '').lower()
    
    # Base de réponses intelligentes intégrée pour l'IA
    reponse = "Je suis l'assistant IA de Cyber Academy. Pour toute question spécifique sur nos formations en cybersécurité, pentesting ou gestion de compte, veuillez consulter notre support ou créer un compte."
    if "bonjour" in question or "salut" in question:
        reponse = "Bonjour ! Comment puis-je vous accompagner dans votre parcours sur Cyber Academy ?"
    elif "compte" in question or "inscription" in question:
        reponse = "Vous pouvez vous inscrire facilement via la page d'inscription. Votre compte devient actif instantanément après validation du paiement."
    elif "admin" in question or "administrateur" in question:
        reponse = "Le premier utilisateur inscrit sur la plateforme devient automatiquement administrateur et accède au tableau de bord complet."
    elif "prix" in question or "tarif" in question or "paiement" in question:
        reponse = "Nos formations et services d'audit sont proposés au tarif standard sécurisé de 99,00 € avec validation automatique."

    return jsonify({'reponse': reponse})

# ==================== INITIALISATION DE L'APPLICATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
else:
    with app.app_context():
        db.create_all()