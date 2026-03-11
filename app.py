import streamlit as st
import pandas as pd
import os

# 1. CONFIGURATION
st.set_page_config(page_title="Pronos St-Nolff", page_icon="🏸", layout="centered")

# Fichiers de sauvegarde
VOTES_FILE = "tous_les_votes.csv"
SCORES_FILE = "classement_general.csv"
MSG_FILE = "message_admin.txt"

# Fonctions de sauvegarde et chargement
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_message(text):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        f.write(text)

def load_message():
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "Aucune info pour le moment."

# 2. STYLE CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .header-box { 
        background-color: #004a99; 
        color: white !important; 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        border-bottom: 4px solid #ffcc00; 
    }
    .header-box h1 { color: white !important; margin-bottom: 5px; font-size: 1.8rem !important; }
    .header-box p { color: white !important; font-size: 0.9rem !important; margin: 0; }
    .admin-msg {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeeba;
        text-align: center;
        margin: 20px 0;
        font-weight: bold;
    }
    .match-card { background: #f1f3f5; padding: 10px; border-radius: 8px; border-left: 5px solid #004a99; margin-top: 10px; font-weight: bold; color: #004a99 !important; }
    </style>
    """, unsafe_allow_html=True)

# Présentation
st.markdown("""
    <div class="header-box">
        <h1>🏸 Le MPP de l'AOBD</h1>
        <p>Pronostique les 8 matchs : 1pt par bonne réponse + 3pts bonus si 8/8.</p>
    </div>
    """, unsafe_allow_html=True)

# AFFICHAGE DU MESSAGE ADMIN
msg_admin = load_message()
st.markdown(f'<div class="admin-msg">📢 {msg_admin}</div>', unsafe_allow_html=True)

# 3. INTERFACE JOUEUR (VOTE)
st.subheader("1️⃣ Fais ton prono !")
nom = st.text_input("Ton Prénom & Nom :", placeholder="Ex: Lucas B").strip()

matchs = ["Simple Homme 1", "Simple Homme 2", "Simple Dame 1", "Simple Dame 2", 
          "Double Homme", "Double Dame", "Mixte 1", "Mixte 2"]

if nom:
    pronos = {}
    for m in matchs:
        st.markdown(f'<div class="match-card">{m}</div>', unsafe_allow_html=True)
        pronos[m] = st.radio(f"Vainqueur {m}", ["St-Nolff", "Adversaire"], key=f"p_{m}", horizontal=True, label_visibility="collapsed")
    
    if st.button("🚀 ENREGISTRER MON VOTE"):
        df_v = load_data(VOTES_FILE)
        nouveau_vote = {"Joueur": nom}
        nouveau_vote.update(pronos)
        df_v = pd.concat([df_v, pd.DataFrame([nouveau_vote])], ignore_index=True)
        save_data(df_v, VOTES_FILE)
        st.success("C'est enregistré !")
        st.balloons()

st.divider()

# 4. CLASSEMENT GÉNÉRAL (AVEC ÉVOLUTION CHIFFRÉE)
st.subheader("🏆 CLASSEMENT GÉNÉRAL")
df_scores = load_data(SCORES_FILE)

if not df_scores.empty:
    if "AncienRang" not in df_scores.columns:
        df_scores["AncienRang"] = 0
    
    # On trie par points
    df_scores = df_scores.sort_values(by="Points", ascending=False).reset_index(drop=True)
    # On définit le rang (1, 2, 3...)
    df_scores["Rang"] = df_scores.index + 1
    
    # Fonction pour calculer l'évolution (+2, -1, etc.)
    def get_evolution_label(row):
        if row["AncienRang"] == 0: 
            return "🆕"
        diff = int(row["AncienRang"]) - int(row["Rang"])
        if diff > 0: 
            return f"🟢 +{diff}"
        elif diff < 0: 
            return f"🔴 {diff}"
        else: 
            return "〓"

    df_scores["Évolution"] = df_scores.apply(get_evolution_label, axis=1)
    
    # --- SUPPRESSION DE LA COLONNE D'INDEX ET PRÉPARATION DE L'AFFICHAGE ---
    # On sélectionne les colonnes dans l'ordre voulu
    classement_final = df_scores[["Rang", "Évolution", "Joueur", "Points"]]
    
    # On affiche le tableau sans la colonne d'index de gauche
    st.table(classement_final.set_index("Rang"))
else:
    st.info("Le classement sera mis à jour après la validation des matchs par l'admin.")

# 5. ESPACE ADMIN
st.divider()
with st.expander("🛠️ ACCÈS ADMINISTRATEUR"):
    mdp = st.text_input("Code secret :", type="password")
    
    if mdp == "2003":
        tab1, tab2, tab3, tab4 = st.tabs(["✅ Valider Résultats", "👥 Suivi des Votes", "📢 Message Annonce", "⚠️ Danger"])

        with tab1:
            st.write("### Entrer les résultats réels")
            reels = {m: st.selectbox(f"Gagnant {m}", ["St-Nolff", "Adversaire"],
