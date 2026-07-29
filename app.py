import os
from flask import Flask, render_template_string, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cyber_sec_super_secret_key_valentin_aboubacar_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyber_academy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_validated = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

TRANSLATIONS = {
    'fr': {
        'title': "Centre de Formation des Hackers Éthiques",
        'home': "Accueil",
        'register': "S'inscrire",
        'login': "Connexion",
        'dashboard': "Mon Espace",
        'logout': "Déconnexion",
        'hero_title': "Apprends le Hacking Éthique & La Cybersécurité",
        'hero_desc': "Rejoins le programme d'élite conçu par Valentin et son collaborateur Aboubacar.",
        'join_btn': "Rejoindre la Formation",
        'chat_title': "Discussion WhatsApp Style",
        'settings': "Paramètres",
        'type_msg': "Écrire un message...",
        'pay_info': "Paiement via Wave, MTN ou Orange Money au +225 05 65 92 21 05"
    },
    'en': {
        'title': "Ethical Hackers Training Center",
        'home': "Home",
        'register': "Register",
        'login': "Login",
        'dashboard': "My Account",
        'logout': "Logout",
        'hero_title': "Learn Ethical Hacking & Cybersecurity",
        'hero_desc': "Join the elite program created by Valentin and his collaborator Aboubacar.",
        'join_btn': "Join Training",
        'chat_title': "WhatsApp Style Chat",
        'settings': "Settings",
        'type_msg': "Type a message...",
        'pay_info': "Payment via Wave, MTN or Orange Money at +225 05 65 92 21 05"
    }
}

TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }} | Valentin & Aboubacar</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0b10;
            --bg-card: #121520;
            --neon-blue: #00d2ff;
            --neon-red: #ff2a5f;
            --neon-green: #00ff88;
            --text-main: #e0e6ed;
            --text-muted: #8a99ad;
            --whatsapp-bg: #075e54;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Rajdhani', sans-serif; }
        
        body {
            background-image:
            linear-gradient(
                rgba(10, 11, 16, 0.70),
                rgba(10, 11, 16, 0.85)
            ),
            url('/static/fond.jpg.jpg');

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;

            color: var(--text-main);
            overflow-x: hidden;
        }

        h1, h2, h3 { font-family: 'Orbitron', sans-serif; text-transform: uppercase; }
        header { background: rgba(10, 11, 16, 0.95); border-bottom: 2px solid var(--neon-blue); position: fixed; width: 100%; top: 0; z-index: 1000; }
        .nav-container { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; flex-wrap: wrap; }
        .logo-box { display: flex; align-items: center; gap: 10px; }
        .logo-img-container { width: 45px; height: 45px; border-radius: 50%; background: linear-gradient(135deg, #1d3557, #e63946); border: 2px solid var(--neon-blue); display: flex; justify-content: center; align-items: center; }
        .logo-text { font-size: 0.95rem; font-weight: 800; color: #fff; line-height: 1.1; }
        .nav-links { display: flex; gap: 15px; list-style: none; align-items: center; flex-wrap: wrap; }
        .nav-links a { color: var(--text-main); text-decoration: none; font-weight: 600; transition: 0.3s; }
        .nav-links a:hover { color: var(--neon-blue); }
        .lang-selector { background: #1a2238; color: #fff; border: 1px solid var(--neon-blue); padding: 5px; border-radius: 4px; }
        .hero { padding: 140px 20px 60px; text-align: center; max-width: 900px; margin: 0 auto; }
        .hero h1 { font-size: 2.2rem; margin-bottom: 15px; color: #fff; text-shadow: 0 0 15px rgba(0, 210, 255, 0.5); }
        .hero p { font-size: 1.1rem; color: var(--text-muted); margin-bottom: 25px; }
        .btn-cyber { background: linear-gradient(45deg, var(--neon-blue), #0055ff); color: #fff; padding: 10px 22px; border: none; border-radius: 4px; font-weight: 700; cursor: pointer; text-decoration: none; display: inline-block; transition: 0.3s; }
        .btn-red { background: linear-gradient(45deg, var(--neon-red), #b00020); }
        
        .container { 
            max-width: 1100px; 
            margin: 0 auto; 
            padding: 40px 20px; 
            background: transparent;
        }

        .panel { 
            background: rgba(18,21,32,0.75); 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 10px; 
            padding: 30px; 
            max-width: 550px; 
            margin: 0 auto; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5); 
        }

        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; }
        .form-control { width: 100%; padding: 10px; background: rgba(0, 0, 0, 0.5); border: 1px solid #2a3447; border-radius: 5px; color: #fff; }
        .whatsapp-container { max-width: 600px; margin: 90px auto 20px; background: #e5ddd5; border-radius: 12px; overflow: hidden; box-shadow: 0 5px 25px rgba(0,0,0,0.6); display: flex; flex-direction: column; height: 550px; }
        .wa-header { background: var(--whatsapp-bg); color: #fff; padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; }
        .wa-header-info { display: flex; align-items: center; gap: 10px; }
        .wa-avatar { width: 40px; height: 40px; background: #fff; color: var(--whatsapp-bg); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
        .wa-actions { display: flex; gap: 15px; font-size: 1.2rem; cursor: pointer; }
        .wa-body { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background-image: radial-gradient(#d1ccc0 1px, transparent 1px); background-size: 20px 20px; }
        .wa-message { max-width: 75%; padding: 8px 12px; border-radius: 7.5px; font-size: 0.95rem; color: #000; word-wrap: break-word; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13); }
        .wa-incoming { background: #fff; align-self: flex-start; }
        .wa-outgoing { background: #dcf8c6; align-self: flex-end; }
        .wa-footer { background: #f0f0f0; padding: 10px; display: flex; align-items: center; gap: 10px; }
        .wa-footer input { flex: 1; padding: 10px 15px; border-radius: 20px; border: 1px solid #ccc; outline: none; }
        .wa-send-btn { background: var(--whatsapp-bg); color: #fff; border: none; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 3000; justify-content: center; align-items: center; }
        .modal-content { background: var(--bg-card); padding: 25px; border-radius: 8px; width: 320px; border: 1px solid var(--neon-blue); text-align: center; }
        .alert { padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; font-weight: bold; }
        .alert-success { background: rgba(0, 255, 136, 0.2); color: var(--neon-green); }
        .alert-danger { background: rgba(255, 42, 95, 0.2); color: var(--neon-red); }
        footer { 
    background: rgba(5,6,8,0.85);
    backdrop-filter: blur(8px);
    padding: 20px; 
    text-align: center; 
    color: var(--text-muted); 
    font-size: 0.9rem; 
    margin-top: 200px;
    border-top: 1px solid var(--neon-blue);
}
    </style>
</head>
<body>

    <header>
        <div class="nav-container">
            <div class="logo-box">
                <div class="logo-img-container"><i class="fa-solid fa-user-ninja" style="color:#fff;"></i></div>
                <div class="logo-text">CYBER ACADEMY<br><span style="font-size: 0.7rem; color: var(--neon-blue);">Valentin & Aboubacar</span></div>
            </div>
            <ul class="nav-links">
                <li><a href="/?lang={{ lang }}">{{ t.home }}</a></li>
                {% if current_user.is_authenticated %}
                    <li><a href="/chat?lang={{ lang }}" style="color: var(--neon-green);"><i class="fa-brands fa-whatsapp"></i> Chat VIP</a></li>
                    <li><a href="/dashboard?lang={{ lang }}">{{ t.dashboard }}</a></li>
                    <li><a href="/logout?lang={{ lang }}" class="btn-cyber btn-red" style="padding: 4px 10px; font-size: 0.85rem;">{{ t.logout }}</a></li>
                {% else %}
                    <li><a href="/register?lang={{ lang }}" class="btn-cyber" style="padding: 5px 12px; font-size: 0.85rem;">{{ t.register }}</a></li>
                    <li><a href="/login?lang={{ lang }}" style="color: var(--neon-green);"><i class="fa-solid fa-lock"></i> {{ t.login }}</a></li>
                {% endif %}
                <li>
                    <select class="lang-selector" onchange="location.href='?lang='+this.value">
                        <option value="fr" {% if lang == 'fr' %}selected{% endif %}>FR</option>
                        <option value="en" {% if lang == 'en' %}selected{% endif %}>EN</option>
                    </select>
                </li>
            </ul>
        </div>
    </header>

    <main>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div style="max-width: 500px; margin: 90px auto 0; padding: 0 15px;">
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        {% if page == 'index' %}
        <section class="hero">
            <h1>{{ t.hero_title }}</h1>
            <p>{{ t.hero_desc }}</p>
            <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                <a href="/register?lang={{ lang }}" class="btn-cyber">{{ t.join_btn }}</a>
                <a href="/chat?lang={{ lang }}" class="btn-cyber btn-red"><i class="fa-brands fa-whatsapp"></i> Accéder au Chat</a>
            </div>
        </section>
        {% endif %}

        {% if page == 'register' %}
        <div class="container" style="margin-top: 70px;">
            <div class="panel">
                <h2 style="text-align: center; color: var(--neon-blue); margin-bottom: 15px;">{{ t.register }}</h2>
                <form method="POST">
                    <div class="form-group"><label>Nom Complet</label><input type="text" name="full_name" class="form-control" required></div>
                    <div class="form-group"><label>WhatsApp</label><input type="tel" name="phone" class="form-control" placeholder="+225..." required></div>
                    <div class="form-group"><label>Email</label><input type="email" name="email" class="form-control" required></div>
                    <div class="form-group"><label>Mot de passe</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn-cyber" style="width: 100%;">S'inscrire</button>
                </form>
            </div>
        </div>
        {% endif %}

        {% if page == 'login' %}
        <div class="container" style="margin-top: 70px;">
            <div class="panel">
                <h2 style="text-align: center; color: var(--neon-green); margin-bottom: 15px;">{{ t.login }}</h2>
                <form method="POST">
                    <div class="form-group"><label>Email</label><input type="email" name="email" class="form-control" required></div>
                    <div class="form-group"><label>Mot de passe</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn-cyber" style="width: 100%;">{{ t.login }}</button>
                </form>
            </div>
        </div>
        {% endif %}

        {% if page == 'chat' %}
        <div class="whatsapp-container">
            <div class="wa-header">
                <div class="wa-header-info">
                    <div class="wa-avatar">V</div>
                    <div>
                        <div style="font-weight: bold; font-size: 0.95rem;">Valentin (Formateur VIP)</div>
                        <div style="font-size: 0.75rem; color: #a0aec0;">En ligne - Support Cyber</div>
                    </div>
                </div>
                <div class="wa-actions">
                    <i class="fa-solid fa-gear" title="Paramètres" onclick="openSettings()" style="cursor: pointer;"></i>
                    <i class="fa-solid fa-phone"></i>
                </div>
            </div>
            
            <div class="wa-body" id="wa-chat-body">
                <div class="wa-message wa-incoming">Bonjour et bienvenue ! Posez vos questions sur la cybersécurité ici. {{ t.pay_info }}</div>
            </div>

            <div class="wa-footer">
                <input type="text" id="wa-input" placeholder="{{ t.type_msg }}" onkeypress="if(event.key==='Enter') sendWaMessage()">
                <button class="wa-send-btn" onclick="sendWaMessage()"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>

        <div class="modal" id="settings-modal">
            <div class="modal-content">
                <h3 style="color: var(--neon-blue); margin-bottom: 15px;"><i class="fa-solid fa-gear"></i> Paramètres du Chat</h3>
                <p style="margin-bottom: 15px; font-size: 0.9rem; color: var(--text-muted);">Options du compte et de notification.</p>
                <button class="btn-cyber btn-red" onclick="closeSettings()" style="width: 100%;">Fermer</button>
            </div>
        </div>
        {% endif %}

        {% if page == 'dashboard' %}
        <div class="container" style="margin-top: 70px;">
            <div class="panel" style="text-align: center;">
                <h2>Espace Membre</h2>
                <p style="margin: 15px 0;">Bienvenue, <strong>{{ current_user.full_name }}</strong></p>
                <p style="color: var(--neon-green);">Statut : Connecté et Prêt</p>
            </div>
        </div>
        {% endif %}
    </main>

    <footer>
        <p>© 2026 Centre de Formation des Hackers Éthiques - Valentin & Aboubacar</p>
    </footer>

    <script>
        function openSettings() { document.getElementById('settings-modal').style.display = 'flex'; }
        function closeSettings() { document.getElementById('settings-modal').style.display = 'none'; }
        function sendWaMessage() {
            const input = document.getElementById('wa-input');
            const txt = input.value.trim();
            if(!txt) return;
            const body = document.getElementById('wa-chat-body');
            body.innerHTML += `<div class="wa-message wa-outgoing">${txt}</div>`;
            input.value = '';
            body.scrollTop = body.scrollHeight;

            setTimeout(() => {
                let reply = "Message reçu ! Valentin vous répondra rapidement.";
                if(txt.toLowerCase().includes('paiement') || txt.toLowerCase().includes('wave')) {
                    reply = "Pour valider, effectuez le dépôt au +225 05 65 92 21 05.";
                }
                body.innerHTML += `<div class="wa-message wa-incoming">${reply}</div>`;
                body.scrollTop = body.scrollHeight;
            }, 600);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    lang = request.args.get('lang', 'fr')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    return render_template_string(TEMPLATE, page='index', lang=lang, t=t)

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = request.args.get('lang', 'fr')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Cet email existe déjà.', 'danger')
            return redirect(url_for('register', lang=lang))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(full_name=full_name, phone=phone, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('chat', lang=lang))

    return render_template_string(TEMPLATE, page='register', lang=lang, t=t)

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = request.args.get('lang', 'fr')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('chat', lang=lang))
        else:
            flash('Identifiants incorrects.', 'danger')
    return render_template_string(TEMPLATE, page='login', lang=lang, t=t)

@app.route('/chat')
@login_required
def chat():
    lang = request.args.get('lang', 'fr')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    return render_template_string(TEMPLATE, page='chat', lang=lang, t=t)

@app.route('/dashboard')
@login_required
def dashboard():
    lang = request.args.get('lang', 'fr')
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    return render_template_string(TEMPLATE, page='dashboard', lang=lang, t=t)

@app.route('/logout')
@login_required
def logout():
    lang = request.args.get('lang', 'fr')
    logout_user()
    return redirect(url_for('index', lang=lang))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)