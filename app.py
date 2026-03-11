import streamlit as st
import pandas as pd
import os

# 1. CONFIGURATION
st.set_page_config(page_title="MPP AOBD", page_icon="🏸", layout="centered")

# Fichiers de sauvegarde
VOTES_FILE = "tous_les_votes.csv"
SCORES_FILE = "classement_general.csv"
MSG_FILE = "message_admin.txt"

# Fonctions de gestion
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
    return "Préparez vos pronos pour la prochaine rencontre !"

# 2. DESIGN PERSONNALISÉ (CSS)
st.markdown("""
    <style>
    /* Fond général */
    .stApp { background-color: #f8f9fa; }
    
    /* Header principal */
    .header-box { 
        background: linear-gradient(135deg, #004a99 0%, #003366 100%);
        color: white !important; 
        padding: 25px; 
        border-radius: 0px 0px 20px 20px; 
        text-align: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: -60px -20px 20px -20px;
    }
    .header-box h1 { color: white !important; font-size: 2rem !important; font-weight: 800; margin-bottom: 8px; }
    .header-box p { color: #ffcc00 !important; font-size: 0.9rem !important; font-weight: 500; }
    
    /* Message Admin (Annonce) */
    .admin-msg {
        background-color: #ffffff;
        color: #004a99;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #ffcc00;
        text-align: center;
        font-weight: 600;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* Cartes de matchs */
    .match-card { 
        background: white; 
        padding: 12px; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0;
        margin-top: 15px; 
        font-weight: 700; 
        color: #333 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* Boutons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffcc00;
        color: #004a99;
    }

    /* Images */
    .stImage > img {
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="header-box">
        <h1>Le MPP de l'AOBD</h1>
        <p>1pt par bon prono • +3pts bonus si 8/8</p>
    </div>
    """, unsafe_allow_html=True)

# --- PHOTO EQUIPE ---
try:
    st.image("image_c4425f.jpg.jpeg", use_container_width=True)
except:
    pass

# --- MESSAGE ANNONCE ---
st.markdown(f'<div class="admin-msg">📢 {load_message()}</div>', unsafe_allow_html=True)

# 3. ESPACE VOTE
with st.container():
    st.subheader("🎯 Fais tes pronos")
    nom = st.text_input("Ton Prénom & Nom", placeholder="Ex: Lucas B").strip()

    matchs = ["Simple Homme 1", "Simple Homme 2", "Simple Dame 1", "Simple Dame 2", 
              "Double Homme", "Double Dame", "Mixte 1", "Mixte 2"]

    if nom:
        pronos = {}
        for m in matchs:
            st.markdown(f'<div class="match-card">🏸 {m}</div>', unsafe_allow_html=True)
            pronos[m] = st.radio(f"Vainqueur {m}", ["St-Nolff", "Adversaire"], key=f"p_{m}", horizontal=True, label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 VALIDER MES PRONOS"):
            df_v = load_data(VOTES_FILE)
            # Vérification si le nom a déjà voté cette session
            if not df_v.empty and nom.lower() in df_v["Joueur"].str.lower().values:
                st.error("Tu as déjà voté pour cette rencontre !")
            else:
                nouveau_vote = {"Joueur": nom}
                nouveau_vote.update(pronos)
                df_v = pd.concat([df_v, pd.DataFrame([nouveau_vote])], ignore_index=True)
                save_data(df_v, VOTES_FILE)
                st.success("Pronos enregistrés ! Bonne chance.")
                st.balloons()

st.divider()

# 4. CLASSEMENT
st.subheader("🏆 Classement Général")
df_scores = load_data(SCORES_FILE)

if not df_scores.empty:
    if "AncienRang" not in df_scores.columns:
        df_scores["AncienRang"] = 0
    df_scores = df_scores.sort_values(by="Points", ascending=False).reset_index(drop=True)
    df_scores["Rang"] = df_scores.index + 1
    
    def get_evolution_label(row):
        if row["AncienRang"] == 0: return "🆕"
        diff = int(row["AncienRang"]) - int(row["Rang"])
        if diff > 0: return f"🟢 +{diff}"
        elif diff < 0: return f"🔴 {diff}"
        return "〓"

    df_scores["Évo"] = df_scores.apply(get_evolution_label, axis=1)
    
    # Affichage simplifié pour mobile
    st.table(df_scores[["Rang", "Évo", "Joueur", "Points"]].set_index("Rang"))
else:
    st.info("Le classement sera affiché après la première journée.")

# --- PHOTO SUPPORTERS ---
try:
    st.image("image_c4423b.jpg.jpeg", use_container_width=True)
except:
    pass

# 5. ADMIN
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Espace Administrateur"):
    mdp = st.text_input("Code secret", type="password")
    if mdp == "2003":
        t1, t2, t3, t4 = st.tabs(["Résultats", "Votes", "Message", "Reset"])
        
        with t1:
            reels = {m: st.selectbox(f"{m}", ["St-Nolff", "Adversaire"], key=f"adm_{m}") for m in matchs}
            if st.button("Calculer la journée"):
                df_v = load_data(VOTES_FILE)
                if not df_v.empty:
                    df_gen = load_data(SCORES_FILE)
                    if not df_gen.empty:
                        df_gen = df_gen.sort_values(by="Points", ascending=False).reset_index(drop=True)
                        df_gen["AncienRang"] = df_gen.index + 1
                    else:
                        df_gen = pd.DataFrame(columns=["Joueur", "Points", "AncienRang"])

                    for _, row in df_v.iterrows():
                        j, b = row['Joueur'], sum(1 for m in matchs if row[m] == reels[m])
                        pts = b + (3 if b == 8 else 0)
                        if j in df_gen['Joueur'].values:
                            df_gen.loc[df_gen['Joueur'] == j, 'Points'] += pts
                        else:
                            df_gen = pd.concat([df_gen, pd.DataFrame([{"Joueur": j, "Points": pts, "AncienRang": 0}])], ignore_index=True)
                    save_data(df_gen, SCORES_FILE)
                    if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                    st.rerun()

        with t2:
            df_v = load_data(VOTES_FILE)
            st.write(df_v[["Joueur"]] if not df_v.empty else "Aucun vote")

        with t3:
            msg = st.text_area("Annonce :", load_message())
            if st.button("Enregistrer"):
                save_message(msg)
                st.rerun()

        with t4:
            if st.button("⚠️ RESET TOTAL"):
                if os.path.exists(SCORES_FILE): os.remove(SCORES_FILE)
                st.rerun()
