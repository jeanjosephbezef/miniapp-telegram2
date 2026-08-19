import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import Config


db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # S'assure que le dossier de la base de données existe
    os.makedirs(
        os.path.join(Config.BASE_DIR, "database"),
        exist_ok=True
    )

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        _migrer_colonnes_manquantes()

    return app


def _migrer_colonnes_manquantes():
    """Ajoute à chaud les colonnes créées après le premier déploiement
    (db.create_all() ne modifie jamais une table déjà existante).
    Sans Alembic, on vérifie et on ALTER TABLE si besoin — sans danger
    à rejouer, puisqu'on ne touche que les colonnes manquantes."""

    from sqlalchemy import inspect, text

    inspecteur = inspect(db.engine)

    if "parametre" not in inspecteur.get_table_names():
        return

    colonnes = [c["name"] for c in inspecteur.get_columns("parametre")]

    with db.engine.begin() as connexion:
        if "fond_ecran" not in colonnes:
            connexion.execute(
                text("ALTER TABLE parametre ADD COLUMN fond_ecran VARCHAR(255)")
            )
        if "dock_categories_actif" not in colonnes:
            connexion.execute(
                text(
                    "ALTER TABLE parametre ADD COLUMN dock_categories_actif "
                    "BOOLEAN DEFAULT 1"
                )
            )
        nouvelles_colonnes = {
            "nom_boutique": "VARCHAR(100)",
            "slogan": "VARCHAR(255)",
            "titre_accueil": "VARCHAR(100)",
            "titre_categories": "VARCHAR(100)",
            "titre_nouveautes": "VARCHAR(100)",
            "texte_bouton": "VARCHAR(100)",
            "couleur_primaire": "VARCHAR(7)",
            "couleur_texte": "VARCHAR(7)",
            "couleur_fond": "VARCHAR(7)",
            "message_bienvenue": "TEXT",
            "css_personnalise": "TEXT",
        }
        for nom, definition in nouvelles_colonnes.items():
            if nom not in colonnes:
                connexion.execute(text(f"ALTER TABLE parametre ADD COLUMN {nom} {definition}"))
