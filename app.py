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

# 2. DESIGN PERSONNALISÉ (GRIS PALE & ROUGE)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* Header principal */
    .header-box { 
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        color: white !important; 
        padding: 25px; 
        border-radius: 0px 0px 20px 20px; 
        text-align: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: -60px -20px 20px -20px;
    }
    .header-box h1 { color: white !important; font-size: 1.8rem !important; font-weight: 800; margin-bottom: 8px; }
    .header-box p { color: #ffeb3b !important; font-size: 0.9rem !important; font-weight: 500; }
    
    /* Message Admin */
    .admin-msg {
        background-color: #f0f2f6; /* Gris pale Streamlit */
        color: #31333F;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin: 15px 0;
    }

    /* Bloc de match unifié */
    .match-container {
        border: 1px solid #f0f2f6;
        border-radius: 12px;
        margin-bottom: 5px;
        overflow: hidden;
    }

    .match-header { 
        background-color: #f0f2f6; /* Gris pale identique au input */
        padding: 10px 15px; 
        font-weight: 700; 
        color: #000000;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Boutons de validation en Gris Pale */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #f0f2f6;
        color: #31333F;
        font-weight: bold;
        border: 1px solid #d1d5db;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #e0e4eb;
        border-color: #b71c1c;
        color: #b71c1c;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-box"><h1>Le MPP de l\'AOBD</h1><p>1pt par bon prono • +3pts bonus si 8/8</p></div>', unsafe_allow_html=True)

# --- PHOTO EQUIPE ---
try:
    st.image("image_c4425f.jpg.jpeg", use_container_width=True)
except:
    pass

st.markdown(f'<div class="admin-msg">📢 {load_message()}</div>', unsafe_allow_html=True)

# 3. ESPACE VOTE
st.subheader("🎯 Fais tes pronos")
nom = st.text_input("Ton Prénom & Nom", placeholder="Ex: Lucas B").strip()

match_data = [
    ("Simple Homme 1", "👨"),
    ("Simple Homme 2", "👨"),
    ("Simple Dame 1", "👩"),
    ("Simple Dame 2", "👩"),
    ("Double Homme", "👬"),
    ("Double Dame", "👭"),
    ("Mixte 1", "👫"),
    ("Mixte 2", "👫")
]

if nom:
    pronos = {}
    for match_name, emoji in match_data:
        st.markdown(f'<div class="match-header">{emoji} {match_name}</div>', unsafe_allow_html=True)
        
        pronos[match_name] = st.radio(
            f"Vainqueur {match_name}", 
            ["St-Nolff 🐺", "Adversaire"], 
            key=f"p_{match_name}", 
            horizontal=True, 
            label_visibility="collapsed"
        )
        st.markdown('<div style="margin-bottom:15px;"></div>', unsafe_allow_html=True)
        
    if st.button("🚀 VALIDER MA GRILLE"):
        df_v = load_data(VOTES_FILE)
        if not df_v.empty and nom.lower() in df_v["Joueur"].str.lower().values:
            st.error("Tu as déjà envoyé tes pronos !")
        else:
            nouveau_vote = {"Joueur": nom}
            cleaned_pronos = {k: ("St-Nolff" if v == "St-Nolff 🐺" else v) for k, v in pronos.items()}
            nouveau_vote.update(cleaned_pronos)
            
            df_v = pd.concat([df_v, pd.DataFrame([nouveau_vote])], ignore_index=True)
            save_data(df_v, VOTES_FILE)
            st.success("Grille validée ! Aouuuuuuh 🐺")
            st.balloons()

st.divider()

# 4. CLASSEMENT
st.subheader("🏆 Classement Général")
df_scores = load_data(SCORES_FILE)

if not df_scores.empty:
    df_scores = df_scores.sort_values(by="Points", ascending=False).reset_index(drop=True)
    df_scores["Rang"] = df_scores.index + 1
    
    if "AncienRang" not in df_scores.columns:
        df_scores["AncienRang"] = 0
        
    def get_evolution_label(row):
        if row["AncienRang"] == 0: return "🆕"
        diff = int(row["AncienRang"]) - int(row["Rang"])
        if diff > 0: return f"🟢 +{diff}"
        elif diff < 0: return f"🔴 {diff}"
        return "〓"

    df_scores["Évo"] = df_scores.apply(get_evolution_label, axis=1)
    st.table(df_scores[["Rang", "Évo", "Joueur", "Points"]].set_index("Rang"))
else:
    st.info("Le classement sera mis à jour après les premiers matchs.")

# --- PHOTO SUPPORTERS ---
try:
    st.image("image_c4423b.jpg.jpeg", use_container_width=True)
except:
    pass

# 5. ADMIN
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Administration"):
    mdp = st.text_input("Code", type="password")
    if mdp == "2003":
        t1, t2, t3, t4 = st.tabs(["Résultats", "Votes", "Message", "Reset"])
        with t1:
            reels = {m[0]: st.selectbox(f"{m[0]}", ["St-Nolff", "Adversaire"], key=f"adm_{m[0]}") for m in match_data}
            if st.button("Valider les résultats"):
                df_v = load_data(VOTES_FILE)
                if not df_v.empty:
                    df_gen = load_data(SCORES_FILE)
                    if not df_gen.empty:
                        df_gen = df_gen.sort_values(by="Points", ascending=False).reset_index(drop=True)
                        df_gen["AncienRang"] = df_gen.index + 1
                    else:
                        df_gen = pd.DataFrame(columns=["Joueur", "Points", "AncienRang"])

                    for _, row in df_v.iterrows():
                        j, b = row['Joueur'], sum(1 for m, _ in match_data if row[m] == reels[m])
                        pts = b + (3 if b == 8 else 0)
                        if j in df_gen['Joueur'].values:
                            df_gen.loc[df_gen['Joueur'] == j, 'Points'] += pts
                        else:
                            df_gen = pd.concat([df_gen, pd.DataFrame([{"Joueur": j, "Points": pts, "AncienRang": 0}])], ignore_index=True)
                    save_data(df_gen, SCORES_FILE)
                    if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                    st.rerun()
        
        with t2:
            st.write("### Liste des votants du jour")
            df_v = load_data(VOTES_FILE)
            if not df_v.empty:
                # On affiche juste la colonne "Joueur"
                st.dataframe(df_v[["Joueur"]].reset_index(drop=True), use_container_width=True)
            else:
                st.info("Aucun vote enregistré pour le moment.")

        with t3:
            msg = st.text_area("Annonce :", load_message())
            if st.button("Mettre à jour"):
                save_message(msg); st.rerun()
        with t4:
            if st.button("RESET CLASSEMENT"):
                if os.path.exists(SCORES_FILE): os.remove(SCORES_FILE)
                st.rerun()
