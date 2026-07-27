import os
from flask import Flask, render_template_string, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyber_sec_super_secret_key_valentin_aboubacar_2026'
# Base de données SQLite locale (créée automatiquement au premier lancement)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyber_academy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODÈLE DE BASE DE DONNÉES ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_validated = db.Column(db.Boolean, default=False)  # Validé ou non par Valentin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DESIGN & HTML UNIQUE (FRONT-END + BACK-END INTÉGRÉ) ---
TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Centre de Formation des Hackers Éthiques | Valentin & Aboubacar</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0b10;
            --bg-card: #121520;
            --neon-blue: #00d2ff;
            --neon-red: #ff2a5f;
            --neon-green: #00ff88;
            --text-main: #e0e6ed;
            --text-muted: #8a99ad;
            --gold: #ffb703;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Rajdhani', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); overflow-x: hidden; }
        h1, h2, h3, .cyber-font { font-family: 'Orbitron', sans-serif; text-transform: uppercase; letter-spacing: 1.5px; }
        header { background: rgba(10, 11, 16, 0.95); border-bottom: 2px solid var(--neon-blue); position: fixed; width: 100%; top: 0; z-index: 1000; backdrop-filter: blur(10px); }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; }
        .logo-box { display: flex; align-items: center; gap: 15px; }
        .logo-img-container { width: 55px; height: 55px; border-radius: 50%; background: linear-gradient(135deg, #1d3557, #e63946); border: 2px solid var(--neon-blue); display: flex; justify-content: center; align-items: center; box-shadow: 0 0 15px rgba(0, 210, 255, 0.5); }
        .logo-img-container i { font-size: 28px; color: #fff; }
        .logo-text { font-size: 1.1rem; font-weight: 800; background: linear-gradient(90deg, var(--neon-blue), #ffffff, var(--neon-red)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; }
        .nav-links { display: flex; gap: 20px; list-style: none; align-items: center; }
        .nav-links a { color: var(--text-main); text-decoration: none; font-weight: 600; font-size: 1.1rem; transition: 0.3s; }
        .nav-links a:hover { color: var(--neon-blue); text-shadow: 0 0 10px var(--neon-blue); }
        .hero { padding: 160px 20px 80px; text-align: center; max-width: 1000px; margin: 0 auto; }
        .hero h1 { font-size: 2.8rem; margin-bottom: 20px; color: #fff; text-shadow: 0 0 20px rgba(0, 210, 255, 0.6); }
        .hero p { font-size: 1.3rem; color: var(--text-muted); margin-bottom: 30px; }
        .badge-certif { display: inline-block; background: rgba(0, 255, 136, 0.1); border: 1px solid var(--neon-green); color: var(--neon-green); padding: 8px 16px; border-radius: 20px; font-weight: bold; margin-bottom: 20px; }
        .btn-cyber { background: linear-gradient(45deg, var(--neon-blue), #0055ff); color: #fff; padding: 12px 28px; border: none; border-radius: 4px; font-size: 1.1rem; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-block; box-shadow: 0 0 20px rgba(0, 210, 255, 0.4); transition: 0.3s; text-align: center;}
        .btn-cyber:hover { transform: translateY(-3px); box-shadow: 0 0 30px rgba(0, 210, 255, 0.8); }
        .btn-red { background: linear-gradient(45deg, var(--neon-red), #b00020); box-shadow: 0 0 20px rgba(255, 42, 95, 0.4); }
        .container { max-width: 1200px; margin: 0 auto; padding: 60px 20px; }
        .section-title { text-align: center; font-size: 2.2rem; margin-bottom: 40px; position: relative; }
        .section-title::after { content: ''; display: block; width: 80px; height: 4px; background: var(--neon-blue); margin: 10px auto 0; box-shadow: 0 0 10px var(--neon-blue); }
        .team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; margin-top: 30px; }
        .team-card { background: var(--bg-card); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 12px; padding: 30px; text-align: center; }
        .avatar-box { width: 90px; height: 90px; border-radius: 50%; margin: 0 auto 20px; background: #1e2538; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: var(--neon-blue); border: 2px solid var(--neon-blue); }
        .panel { background: var(--bg-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 40px; max-width: 600px; margin: 0 auto; box-shadow: 0 0 30px rgba(0,0,0,0.5); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; }
        .form-control { width: 100%; padding: 12px 15px; background: rgba(0, 0, 0, 0.5); border: 1px solid #2a3447; border-radius: 6px; color: #fff; font-size: 1rem; }
        .form-control:focus { outline: none; border-color: var(--neon-blue); box-shadow: 0 0 10px rgba(0, 210, 255, 0.3); }
        .payment-box { background: rgba(0, 255, 136, 0.05); border: 1px solid var(--neon-green); border-radius: 8px; padding: 20px; margin-top: 20px; }
        .pay-number { font-size: 1.5rem; font-weight: bold; color: var(--gold); font-family: 'Share Tech Mono', monospace; text-align: center; margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.4); border-radius: 6px; }
        .schedule-table { width: 100%; border-collapse: collapse; margin-top: 20px; background: var(--bg-card); border-radius: 8px; overflow: hidden; }
        .schedule-table th, .schedule-table td { padding: 15px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .schedule-table th { background: rgba(0, 210, 255, 0.1); color: var(--neon-blue); font-family: 'Orbitron', sans-serif; }
        .alert { padding: 12px; border-radius: 6px; margin-bottom: 20px; text-align: center; font-weight: bold; }
        .alert-success { background: rgba(0, 255, 136, 0.15); border: 1px solid var(--neon-green); color: var(--neon-green); }
        .alert-danger { background: rgba(255, 42, 95, 0.15); border: 1px solid var(--neon-red); color: var(--neon-red); }
        /* AI Widget */
        .ai-chat-widget { position: fixed; bottom: 20px; right: 20px; width: 350px; height: 480px; background: var(--bg-card); border: 2px solid var(--neon-blue); border-radius: 12px; display: flex; flex-direction: column; box-shadow: 0 0 30px rgba(0, 0, 0, 0.8); z-index: 2000; transition: 0.3s; }
        .ai-chat-widget.collapsed { height: 50px; }
        .chat-header { background: rgba(0, 210, 255, 0.15); padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; border-bottom: 1px solid rgba(0, 210, 255, 0.3); }
        .chat-body { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; font-size: 0.95rem; }
        .msg { padding: 10px 14px; border-radius: 8px; max-width: 85%; line-height: 1.4; }
        .msg-ia { background: rgba(0, 210, 255, 0.1); border-left: 3px solid var(--neon-blue); align-self: flex-start; }
        .msg-user { background: rgba(255, 42, 95, 0.15); border-right: 3px solid var(--neon-red); align-self: flex-end; }
        .chat-input-box { display: flex; padding: 10px; background: rgba(0,0,0,0.5); border-top: 1px solid rgba(255,255,255,0.1); }
        .chat-input-box input { flex: 1; padding: 8px 12px; background: transparent; border: 1px solid #2a3447; color: #fff; border-radius: 4px; }
        .chat-input-box button { background: var(--neon-blue); border: none; color: #000; padding: 8px 15px; margin-left: 8px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        footer { background: #050608; padding: 30px 20px; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); color: var(--text-muted); margin-top: 80px; }
    </style>
</head>
<body>

    <header>
        <div class="nav-container">
            <div class="logo-box">
                <div class="logo-img-container"><i class="fa-solid fa-user-ninja"></i></div>
                <div class="logo-text">CENTRE DE FORMATION<br><span style="font-size: 0.8rem; color: #fff;">DES HACKERS ÉTHIQUES</span></div>
            </div>
            <ul class="nav-links">
                <li><a href="/">Accueil</a></li>
                <li><a href="#equipe">Fondateurs</a></li>
                <li><a href="#planning">Planning</a></li>
                {% if current_user.is_authenticated %}
                    <li><a href="/dashboard" style="color: var(--neon-green);">Mon Espace</a></li>
                    <li><a href="/logout" class="btn-cyber btn-red" style="padding: 5px 15px; font-size: 0.9rem;">Déconnexion</a></li>
                {% else %}
                    <li><a href="/register" class="btn-cyber" style="padding: 6px 16px; font-size: 0.9rem;">S'inscrire</a></li>
                    <li><a href="/login" style="color: var(--neon-green);"><i class="fa-solid fa-lock"></i> Connexion</a></li>
                {% endif %}
            </ul>
        </div>
    </header>

    <main>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div style="max-width: 600px; margin: 100px auto 0; padding: 0 20px;">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        {% if page == 'index' %}
        <section class="hero">
            <span class="badge-certif"><i class="fa-solid fa-certificate"></i> Formation Certifiante & Professionnelle</span>
            <h1>Apprends le Hacking Éthique & La Cybersécurité</h1>
            <p>Rejoins le programme d'élite conçu par <strong>Valentin</strong> et son collaborateur <strong>Aboubacar</strong>.</p>
            <div style="display: flex; gap: 15px; justify-content: center;">
                <a href="/register" class="btn-cyber">Rejoindre la Formation</a>
                <a href="#planning" class="btn-cyber btn-red">Voir l'emploi du temps</a>
            </div>
        </section>

        <section id="equipe" class="container">
            <h2 class="section-title">Les Fondateurs & Mentors</h2>
            <div class="team-grid">
                <div class="team-card">
                    <div class="avatar-box"><i class="fa-solid fa-user-shield"></i></div>
                    <h3>Valentin</h3>
                    <p style="color: var(--neon-blue); font-weight: bold; margin-bottom: 10px;">Fondateur & Expert Certifié</p>
                    <p style="font-size: 0.95rem; color: var(--text-muted);">Titulaire d'un certificat d'expertise internationale en Cybersécurité et Hacking Éthique. Valide les comptes après paiement.</p>
                    <p style="margin-top: 15px; color: var(--neon-green);"><i class="fa-brands fa-whatsapp"></i> +225 05 65 92 21 05</p>
                </div>
                <div class="team-card">
                    <div class="avatar-box" style="border-color: var(--neon-red); color: var(--neon-red);"><i class="fa-solid fa-laptop-code"></i></div>
                    <h3>Aboubacar</h3>
                    <p style="color: var(--neon-red); font-weight: bold; margin-bottom: 10px;">Collaborateur Technique</p>
                    <p style="font-size: 0.95rem; color: var(--text-muted);">Co-administrateur de la plateforme web, gestionnaire de la structure et du support des étudiants.</p>
                </div>
            </div>
        </section>

        <section id="planning" class="container">
            <h2 class="section-title">Emploi du Temps & Programme</h2>
            <table class="schedule-table">
                <thead><tr><th>Jour / Module</th><th>Horaire</th><th>Sujet Étudié</th><th>Format</th></tr></thead>
                <tbody>
                    <tr><td><strong>Lundi - Module 1</strong></td><td>19h00 - 21h00</td><td>Bases de la Cybersécurité & Réseaux</td><td><span style="color: var(--neon-green);">Direct</span></td></tr>
                    <tr><td><strong>Mercredi - Module 2</strong></td><td>19h00 - 21h00</td><td>Test d'intrusion & Vulnérabilités Web</td><td><span style="color: var(--neon-green);">Atelier</span></td></tr>
                    <tr><td><strong>Vendredi - Module 3</strong></td><td>19h00 - 21h00</td><td>Ingénierie Sociale & Sécurité</td><td><span style="color: var(--neon-green);">Pratique</span></td></tr>
                    <tr><td><strong>Samedi - CTF</strong></td><td>15h00 - 18h00</td><td>Challenges & Q&A en direct</td><td><span style="color: var(--gold);">VIP</span></td></tr>
                </tbody>
            </table>
        </section>
        {% endif %}

        {% if page == 'register' %}
        <div class="container" style="margin-top: 80px;">
            <div class="panel">
                <h2 style="text-align: center; color: var(--neon-blue); margin-bottom: 20px;">Inscription Sécurisée</h2>
                <form method="POST">
                    <div class="form-group"><label>Nom Complet</label><input type="text" name="full_name" class="form-control" required></div>
                    <div class="form-group"><label>Numéro de Téléphone (WhatsApp)</label><input type="tel" name="phone" class="form-control" placeholder="+225..." required></div>
                    <div class="form-group"><label>Adresse Email</label><input type="email" name="email" class="form-control" required></div>
                    <div class="form-group"><label>Mot de passe</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn-cyber" style="width: 100%;">Valider l'inscription & Instructions de Paiement</button>
                </form>
            </div>
        </div>
        {% endif %}

        {% if page == 'payment' %}
        <div class="container" style="margin-top: 80px;">
            <div class="panel" style="text-align: center;">
                <h2 style="color: var(--neon-green); margin-bottom: 15px;"><i class="fa-solid fa-circle-check"></i> Compte Pré-enregistré !</h2>
                <p style="color: var(--text-muted);">Effectuez votre paiement via <strong>Wave, MTN Money ou Orange Money</strong> pour activer votre accès.</p>
                <div class="payment-box">
                    <p>Numéro officiel du propriétaire (Valentin) :</p>
                    <div class="pay-number">+225 05 65 92 21 05</div>
                </div>
                <p style="margin: 20px 0;">Après paiement, envoyez votre reçu à Valentin sur WhatsApp pour validation immédiate :</p>
                <a href="https://wa.me/2250565922105?text=Bonjour%20Valentin,%20je%20viens%20de%20payer%20pour%20la%20formation%20cybersec.%20Voici%20ma%20preuve." target="_blank" class="btn-cyber btn-red" style="width: 100%;">
                    <i class="fa-brands fa-whatsapp"></i> Envoyer le reçu à Valentin
                </a>
                <div style="margin-top: 20px;"><a href="/login" style="color: var(--neon-blue);">Aller à la connexion une fois validé</a></div>
            </div>
        </div>
        {% endif %}

        {% if page == 'login' %}
        <div class="container" style="margin-top: 80px;">
            <div class="panel">
                <h2 style="text-align: center; color: var(--neon-green); margin-bottom: 20px;">Connexion Espace Membre</h2>
                <form method="POST">
                    <div class="form-group"><label>Email</label><input type="email" name="email" class="form-control" required></div>
                    <div class="form-group"><label>Mot de passe</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn-cyber" style="width: 100%;">Se Connecter</button>
                </form>
            </div>
        </div>
        {% endif %}

        {% if page == 'dashboard' %}
        <div class="container" style="margin-top: 80px;">
            <div class="panel" style="text-align: center;">
                <h2>Espace Membre : {{ user.full_name }}</h2>
                <p style="margin: 15px 0; color: var(--text-muted);">Statut actuel dans la base de données :</p>
                {% if user.is_validated %}
                    <div class="payment-box" style="border-color: var(--neon-green);">
                        <p style="color: var(--neon-green); font-weight: bold; font-size: 1.2rem;">COMPTE VALIDÉ PAR VALENTIN ✅</p>
                        <p style="margin: 15px 0;">Félicitations ! Vous avez accès au groupe officiel de formation.</p>
                        <a href="https://chat.whatsapp.com/ExempleGroupeVIP" target="_blank" class="btn-cyber">Rejoindre le Groupe VIP WhatsApp</a>
                    </div>
                {% else %}
                    <div class="payment-box" style="border-color: var(--gold); background: rgba(255,183,3,0.05);">
                        <p style="color: var(--gold); font-weight: bold; font-size: 1.1rem;">EN ATTENTE DE VALIDATION ⏳</p>
                        <p style="margin-top: 10px;">Valentin n'a pas encore validé votre paiement sur le <strong>+225 0565922105</strong>.</p>
                    </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </main>

    <!-- Assistant IA Chatbot Dynamique -->
    <div class="ai-chat-widget collapsed" id="ai-widget">
        <div class="chat-header" onclick="toggleChat()">
            <div><i class="fa-solid fa-robot" style="color: var(--neon-blue);"></i><span style="font-weight: bold; margin-left: 8px;">Assistant Cyber IA</span></div>
            <i class="fa-solid fa-chevron-up" id="chat-icon"></i>
        </div>
        <div class="chat-body" id="chat-body">
            <div class="msg msg-ia">Bonjour ! Je connais les emplois du temps et les modalités de paiement au +225 0565922105 (Valentin). Posez vos questions !</div>
        </div>
        <div class="chat-input-box">
            <input type="text" id="chat-input" placeholder="Posez une question..." onkeypress="handleKeyPress(event)">
            <button onclick="sendChatMessage()"><i class="fa-solid fa-paper-plane"></i></button>
        </div>
    </div>

    <footer>
        <p>© 2026 Centre de Formation des Hackers Éthiques.</p>
        <p style="font-size: 0.85rem; margin-top: 5px;">Fondateur : <strong>Valentin</strong> | Collaborateur : <strong>Aboubacar</strong></p>
        <p style="font-size: 0.8rem; color: var(--neon-blue); margin-top: 5px;">Paiements / Infos : +225 05 65 92 21 05</p>
    </footer>

    <script>
        function toggleChat() {
            const widget = document.getElementById('ai-widget');
            const icon = document.getElementById('chat-icon');
            widget.classList.toggle('collapsed');
            icon.className = widget.classList.contains('collapsed') ? "fa-solid fa-chevron-up" : "fa-solid fa-chevron-down";
        }
        function handleKeyPress(e) { if(e.key === 'Enter') sendChatMessage(); }
        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const text = input.value.trim();
            if(!text) return;
            const body = document.getElementById('chat-body');
            body.innerHTML += `<div class="msg msg-user">${text}</div>`;
            input.value = '';
            body.scrollTop = body.scrollHeight;

            setTimeout(() => {
                let resp = "Je suis l'IA de la formation. Pour toute urgence, contactez Valentin au +225 0565922105.";
                const q = text.toLowerCase();
                if(q.includes('heure') || q.includes('cours') || q.includes('planning')) {
                    resp = "Les cours ont lieu Lundi, Mercredi et Vendredi de 19h00 à 21h00, et le Samedi à 15h00.";
                } else if(q.includes('paye') || q.includes('paiement') || q.includes('wave') || q.includes('mtn')) {
                    resp = "Le paiement s'effectue par Wave, Orange ou MTN Money au +225 0565922105 (Valentin).";
                } else if(q.includes('valentin') || q.includes('aboubacar')) {
                    resp = "Valentin est le fondateur certifié et Aboubacar est le collaborateur technique de la plateforme !";
                }
                body.innerHTML += `<div class="msg msg-ia">${resp}</div>`;
                body.scrollTop = body.scrollHeight;
            }, 500);
        }
    </script>
</body>
</html>
"""

# --- ROUTES BACKEND (PYTHON / FLASK) ---
@app.route('/')
def index():
    return render_template_string(TEMPLATE, page='index')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(full_name=full_name, phone=phone, email=email, password=hashed_pw, is_validated=False)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return render_template_string(TEMPLATE, page='payment')

    return render_template_string(TEMPLATE, page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects.', 'danger')
    return render_template_string(TEMPLATE, page='login')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(TEMPLATE, page='dashboard', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Route d'administration pour que Valentin puisse valider un utilisateur rapidement
@app.route('/admin/valider/<int:user_id>')
def admin_valider(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_validated = True
        db.session.commit()
        return f"Compte de {user.full_name} validé avec succès par Valentin !"
    return "Utilisateur introuvable."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)