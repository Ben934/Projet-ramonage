from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date

# Configuration de la base de données
DATABASE_URL = "sqlite:///clients.db"
engine = create_engine(DATABASE_URL, echo=True)

# Définir le modèle pour la base de données
Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True)
    nom_client = Column(String, nullable=False)
    numero_tel = Column(String, nullable=False)
    adresse = Column(String)
    ville = Column(String)
    code_postal = Column(String)
    date_intervention = Column(Date)
    element_chauffe = Column(String)
    difficulte_ramonage = Column(String)
    difficulte_acces = Column(String)
    commentaire = Column(String)
    prix_intervention = Column(Float)

# Créer la table si elle n'existe pas
Base.metadata.create_all(engine)
print("Base de données initialisée avec succès !")
