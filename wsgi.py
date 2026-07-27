from app import app, initialiser_admin

# Initialise l'administrateur au démarrage sur le serveur
initialiser_admin()

if __name__ == "__main__":
    app.run()