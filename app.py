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

# --- NOUVEAU : AFFICHAGE DU MESSAGE ADMIN ---
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

# 4. CLASSEMENT GÉNÉRAL (AVEC ÉVOLUTION)
st.subheader("🏆 CLASSEMENT GÉNÉRAL")
df_scores = load_data(SCORES_FILE)

if not df_scores.empty:
    # On s'assure que les colonnes nécessaires existent
    if "AncienRang" not in df_scores.columns:
        df_scores["AncienRang"] = 0
    
    # Calcul du Rang Actuel
    df_scores = df_scores.sort_values(by="Points", ascending=False).reset_index(drop=True)
    df_scores["RangActuel"] = df_scores.index + 1
    
    # Fonction pour définir l'icône d'évolution
    def get_evolution(row):
        if row["AncienRang"] == 0: return "🆕"
        if row["RangActuel"] < row["AncienRang"]: return "🔼"
        if row["RangActuel"] > row["AncienRang"]: return "🔽"
        return "〓"

    df_scores["Évo"] = df_scores.apply(get_evolution, axis=1)
    
    # Affichage propre
    classement_final = df_scores[["Évo", "Joueur", "Points"]].copy()
    st.table(classement_final)
else:
    st.info("Le classement sera mis à jour après la validation des matchs par l'admin.")

# 5. ESPACE ADMIN (ONGLETS SÉCURISÉS)
st.divider()
with st.expander("🛠️ ACCÈS ADMINISTRATEUR"):
    mdp = st.text_input("Code secret :", type="password")
    
    if mdp == "2003":
        tab1, tab2, tab3, tab4 = st.tabs(["✅ Valider Résultats", "👥 Suivi des Votes", "📢 Message Annonce", "⚠️ Danger"])

        with tab1:
            st.write("### Entrer les résultats réels")
            reels = {m: st.selectbox(f"Gagnant {m}", ["St-Nolff", "Adversaire"], key=f"adm_{m}") for m in matchs}
            
            if st.button("✅ CALCULER ET CLOTURER LA JOURNÉE"):
                df_v = load_data(VOTES_FILE)
                if df_v.empty:
                    st.error("Personne n'a encore voté !")
                else:
                    df_gen = load_data(SCORES_FILE)
                    if df_gen.empty:
                        df_gen = pd.DataFrame(columns=["Joueur", "Points", "AncienRang"])
                    else:
                        # Avant de calculer, on enregistre la position actuelle comme "AncienRang"
                        df_gen = df_gen.sort_values(by="Points", ascending=False).reset_index(drop=True)
                        df_gen["AncienRang"] = df_gen.index + 1

                    for index, row in df_v.iterrows():
                        joueur = row['Joueur']
                        bons = sum(1 for m in matchs if row[m] == reels[m])
                        pts_journee = bons + (3 if bons == 8 else 0)
                        
                        if joueur in df_gen['Joueur'].values:
                            df_gen.loc[df_gen['Joueur'] == joueur, 'Points'] += pts_journee
                        else:
                            new_row = pd.DataFrame([{"Joueur": joueur, "Points": pts_journee, "AncienRang": 0}])
                            df_gen = pd.concat([df_gen, new_row], ignore_index=True)
                    
                    save_data(df_gen, SCORES_FILE)
                    if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                    st.success("Classement mis à jour !")
                    st.rerun()

        with tab2:
            st.write("### Liste des joueurs ayant voté")
            df_v = load_data(VOTES_FILE)
            if not df_v.empty:
                st.dataframe(df_v[["Joueur"]], use_container_width=True)
            else:
                st.info("Aucun vote pour le moment.")

        with tab3:
            st.write("### Modifier l'annonce de la rencontre")
            current_msg = load_message()
            new_msg = st.text_area("Écris ton message ici (Lieu, Date, Adversaire...)", current_msg)
            if st.button("Enregistrer le message"):
                save_message(new_msg)
                st.success("Message mis à jour !")
                st.rerun()

        with tab4:
            st.write("### Réinitialisation complète")
            if st.button("🗑️ Effacer TOUT"):
                if os.path.exists(SCORES_FILE): os.remove(SCORES_FILE)
                if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                if os.path.exists(MSG_FILE): os.remove(MSG_FILE)
                st.rerun()
            
    elif mdp != "":
        st.error("Mot de passe incorrect.")
