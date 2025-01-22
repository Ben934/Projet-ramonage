import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.ticker import MaxNLocator

# Créer la connexion à SQLite
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

# Créer une session
Session = sessionmaker(bind=engine)
session = Session()

# Fonction pour charger les clients depuis la base de données
def load_data():
    return pd.read_sql(session.query(Client).statement, session.bind)

# Fonction pour ajouter un nouveau client
def add_client(client_data):
    new_client = Client(**client_data)
    session.add(new_client)
    session.commit()

# Fonction pour modifier un client existant
def update_client(client_id, client_data):
    client = session.query(Client).filter(Client.id == client_id).first()
    for key, value in client_data.items():
        setattr(client, key, value)
    session.commit()

# Fonction pour afficher les données sous forme de DataFrame
def show_clients():
    return pd.read_sql(session.query(Client).statement, session.bind)

# Interface Streamlit
st.title("Gestion des Ramonages avec SQLite")

# Menu principal
menu = st.sidebar.radio("Menu", ["Ajouter un client", "Afficher/Modifier les clients","Statistiques"])

if menu == "Ajouter un client":
    st.subheader("Ajouter un nouveau client")

    nom_client = st.text_input("Nom Client")
    numero_tel = st.text_input("Numéro de tel")
    adresse = st.text_input("Adresse")
    ville = st.text_input("Ville")
    code_postal = st.text_input("Code Postal")
    date_intervention = st.date_input("Date d'intervention")
    element_chauffe = st.selectbox("Élément de chauffe", ["Cheminée", "Insert", "Poêle à bois"])
    difficulte_ramonage = st.selectbox("Difficulté du ramonage", ["Facile", "Moyen", "Difficile"])
    difficulte_acces = st.selectbox("Difficulté d'accès", ["Facile", "Moyen", "Difficile"])
    commentaire = st.text_area("Commentaire")
    prix_intervention = st.number_input("Prix de l'intervention (€)", min_value=0.0, format="%.2f")

    if st.button("Ajouter client"):
        # Construire un dictionnaire avec les données du client
        client_data = {
            "nom_client": nom_client,
            "numero_tel": numero_tel,
            "adresse": adresse,
            "ville": ville,
            "code_postal": code_postal,
            "date_intervention": date_intervention,
            "element_chauffe": element_chauffe,
            "difficulte_ramonage": difficulte_ramonage,
            "difficulte_acces": difficulte_acces,
            "commentaire": commentaire,
            "prix_intervention": prix_intervention,
        }
        # Ajouter à la base de données
        add_client(client_data)
        st.success("Client ajouté avec succès !")

elif menu == "Afficher/Modifier les clients":
    st.subheader("Clients")
    clients = show_clients()
    st.dataframe(clients)

    client_id = st.number_input("Entrez l'ID du client à modifier", min_value=1, step=1)
    client_to_edit = session.query(Client).filter(Client.id == client_id).first()

    if client_to_edit:
        st.write(f"Modifications pour le client : {client_to_edit.nom_client}")

        new_nom_client = st.text_input("Nom Client", value=client_to_edit.nom_client)
        new_numero_tel = st.text_input("Numéro de tel", value=client_to_edit.numero_tel)
        new_adresse = st.text_input("Adresse", value=client_to_edit.adresse)
        new_ville = st.text_input("Ville", value=client_to_edit.ville)
        new_code_postal = st.text_input("Code Postal", value=client_to_edit.code_postal)
        new_date_intervention = st.date_input("Date d'intervention", value=client_to_edit.date_intervention)
        new_element_chauffe = st.selectbox("Élément de chauffe", ["Cheminée", "Insert", "Poêle à bois"], index=["Cheminée", "Insert", "Poêle à bois"].index(client_to_edit.element_chauffe))
        new_difficulte_ramonage = st.selectbox("Difficulté du ramonage", ["Facile", "Moyen", "Difficile"], index=["Facile", "Moyen", "Difficile"].index(client_to_edit.difficulte_ramonage))
        new_difficulte_acces = st.selectbox("Difficulté d'accès", ["Facile", "Moyen", "Difficile"], index=["Facile", "Moyen", "Difficile"].index(client_to_edit.difficulte_acces))
        new_commentaire = st.text_area("Commentaire", value=client_to_edit.commentaire)
        new_prix_intervention = st.number_input("Prix de l'intervention (€)", min_value=0.0, value=client_to_edit.prix_intervention)

        if st.button("Modifier client"):
            client_data = {
                "nom_client": new_nom_client,
                "numero_tel": new_numero_tel,
                "adresse": new_adresse,
                "ville": new_ville,
                "code_postal": new_code_postal,
                "date_intervention": new_date_intervention,
                "element_chauffe": new_element_chauffe,
                "difficulte_ramonage": new_difficulte_ramonage,
                "difficulte_acces": new_difficulte_acces,
                "commentaire": new_commentaire,
                "prix_intervention": new_prix_intervention,
            }
            update_client(client_id, client_data)
            st.success("Client modifié avec succès !")
    else:
        st.warning("Client non trouvé.")
    

# Partie Statistiques
elif menu == "Statistiques":
    st.subheader("Statistiques sur les clients")

    # Charger les données à partir de la base de données SQLite
    data = show_clients()

    if not data.empty:
        # --- Sélection de l'année ---
       # Assurez-vous que la colonne est au format datetime
        data['date_intervention'] = pd.to_datetime(data['date_intervention'], errors='coerce')

        # Extraire les années uniques
        unique_years = sorted(data['date_intervention'].dropna().dt.year.unique())  # Ignorer les dates non valides
        unique_years.insert(0, "Toutes les années")  # Ajouter une option pour toutes les années

        # Sélectionner une année ou toutes les années
        selected_year = st.selectbox("Sélectionner l'année", unique_years)

        # Filtrer les données
        if selected_year == "Toutes les années":
            data_filtered = data
        else:
            data_filtered = data[data['date_intervention'].dt.year == selected_year]

        # --- Section KPI ---
        col1, col2, col3 = st.columns(3)
        with col1:
            total_clients = len(data_filtered)
            st.metric("Nombre de clients", total_clients)

        with col2:
            total_revenue = data_filtered["prix_intervention"].sum()
            st.metric("Chiffre d'affaires total (€)", f"{total_revenue:,.2f}")

        with col3:
            avg_price = data_filtered["prix_intervention"].mean()
            st.metric("Prix moyen (€)", f"{avg_price:,.2f}")

        # --- Graphiques ---        
        # 1. Graphique - Nombre de clients par ville
        st.write("**Répartition des clients par ville :**")
        ville_counts = data_filtered["ville"].value_counts()
        # Convertir ville_counts en DataFrame
        ville_counts_df = pd.DataFrame({
            'Ville': ville_counts.index,
            'Nombre de clients': ville_counts.values
        })

        # Créer le graphique
        fig1 = px.bar(ville_counts_df, x='Ville', y='Nombre de clients', 
                    labels={'Ville': 'Ville', 'Nombre de clients': 'Nombre de clients'},
                    title="Nombre de clients par ville", 
                    color='Nombre de clients', color_continuous_scale="Viridis")

        st.plotly_chart(fig1, use_container_width=True)

        # 2. Graphique - Cumul du prix par mois
        st.write("**Cumul du prix des interventions par mois :**")
        data_filtered['mois_annee'] = data_filtered['date_intervention'].dt.to_period('M')

        # Convertir la période en chaîne de caractères
        data_filtered['mois_annee'] = data_filtered['mois_annee'].astype(str)

        # Maintenant, les périodes sont sous forme de chaînes de caractères, ce qui peut être utilisé dans Plotly.
        prix_par_mois = data_filtered.groupby('mois_annee')['prix_intervention'].sum().reset_index()

        fig2 = px.line(prix_par_mois, x='mois_annee', y='prix_intervention', 
                    title="Cumul des prix par mois", labels={'mois_annee': 'Mois', 'prix_intervention': 'Cumul du prix (€)'}, 
                    markers=True)
        fig2.update_xaxes(type='category')  # On utilise 'category' pour que les mois apparaissent correctement
        st.plotly_chart(fig2, use_container_width=True)


        # 3. Graphique - Répartition des difficultés de ramonage
        st.write("**Répartition des difficultés de ramonage :**")
        difficulte_counts = data_filtered['difficulte_ramonage'].value_counts()
        fig3 = px.pie(difficulte_counts, names=difficulte_counts.index, values=difficulte_counts.values, 
                      title="Répartition des difficultés de ramonage", hole=0.3)
        st.plotly_chart(fig3, use_container_width=True)

        # 4. Graphique - Répartition des clients par élément de chauffe
        st.write("**Répartition des clients par élément de chauffe :**")
        element_counts = data_filtered['element_chauffe'].value_counts()
        # Convertir element_counts en DataFrame
        element_counts_df = pd.DataFrame({
            'Élément de chauffe': element_counts.index,
            'Nombre de clients': element_counts.values
        })

        # Créer le graphique
        fig4 = px.bar(element_counts_df, x='Élément de chauffe', y='Nombre de clients',
                    title="Répartition des clients par élément de chauffe", 
                    color='Nombre de clients', color_continuous_scale="Plasma")

        st.plotly_chart(fig4, use_container_width=True)

    else:
        st.warning("Aucune donnée disponible pour générer des statistiques.")
