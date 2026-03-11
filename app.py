import streamlit as st
import pandas as pd
import os

# 1. CONFIGURATION
st.set_page_config(page_title="Le MPP de l'AOBD", page_icon="🏸", layout="centered")

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
    return "Prochaine rencontre à venir..."

# 2. STYLE CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .header-box { 
        background-color: #004a99; 
        color: white !important; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        border-bottom: 4px solid #ffcc00; 
        margin-bottom: 10px;
    }
    .header-box h1 { color: white !important; font-size: 1.6rem !important; margin: 0; }
    .header-box p { color: white !important; font-size: 0.8rem !important; }
    .admin-msg {
        background-color: #fff3cd;
        color: #856404;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ffeeba;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
    }
    .match-card { background: #f1f3f5; padding: 10px; border-radius: 8px; border-left: 5px solid #004a99; margin-top: 10px; font-weight: bold; color: #004a99 !important; }
    </style>
    """, unsafe_allow_html=True)

# TITRE
st.markdown("""
    <div class="header-box">
        <h1>🏸 Pronos AOBD</h1>
        <p>1pt par bon prono + 3pts bonus si 8/8</p>
    </div>
    """, unsafe_allow_html=True)

# --- IMAGE 1 : L'ÉQUIPE (Noms de fichiers mis à jour) ---
try:
    st.image("image_c4425f.jpg.jpeg", use_container_width=True, caption="L'équipe AOBD Saint-Nolff")
except Exception:
    st.info("📸 Photo d'équipe (Vérifie le nom du fichier sur GitHub)")

# MESSAGE DE L'ADMIN
st.markdown(f'<div class="admin-msg">📢 {load_message()}</div>', unsafe_allow_html=True)

# 3. INTERFACE JOUEUR
st.subheader("1️⃣ Ton Prono")
nom = st.text_input("Prénom & Nom :", placeholder="Ex: Lucas B").strip()

matchs = ["Simple Homme 1", "Simple Homme 2", "Simple Dame 1", "Simple Dame 2", 
          "Double Homme", "Double Dame", "Mixte 1", "Mixte 2"]

if nom:
    pronos = {}
    for m in matchs:
        st.markdown(f'<div class="match-card">{m}</div>', unsafe_allow_html=True)
        pronos[m] = st.radio(f"Vainqueur {m}", ["St-Nolff", "Adversaire"], key=f"p_{m}", horizontal=True, label_visibility="collapsed")
    
    if st.button("🚀 VALIDER MES PRONOS"):
        df_v = load_data(VOTES_FILE)
        nouveau_vote = {"Joueur": nom}
        nouveau_vote.update(pronos)
        df_v = pd.concat([df_v, pd.DataFrame([nouveau_vote])], ignore_index=True)
        save_data(df_v, VOTES_FILE)
        st.success("Pronos enregistrés !")
        st.balloons()

st.divider()

# 4. CLASSEMENT GÉNÉRAL
st.subheader("🏆 Classement")
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
        else: return "〓"

    df_scores["Évolution"] = df_scores.apply(get_evolution_label, axis=1)
    st.table(df_scores[["Rang", "Évolution", "Joueur", "Points"]].set_index("Rang"))
else:
    st.info("Le classement arrivera bientôt !")

# --- IMAGE 2 : LES SUPPORTERS ---
try:
    st.image("image_c4423b.jpg.jpeg", use_container_width=True, caption="La Meute fait la loi ! 🐺")
except Exception:
    pass

# 5. ESPACE ADMIN
st.divider()
with st.expander("🛠️ Admin"):
    mdp = st.text_input("Code :", type="password")
    if mdp == "2003":
        tab1, tab2, tab3, tab4 = st.tabs(["✅ Résultats", "👥 Votes", "📢 Message", "⚠️ Reset"])
        
        with tab1:
            reels = {m: st.selectbox(f"Gagnant {m}", ["St-Nolff", "Adversaire"], key=f"adm_{m}") for m in matchs}
            if st.button("CALCULER LES POINTS"):
                df_v = load_data(VOTES_FILE)
                if not df_v.empty:
                    df_gen = load_data(SCORES_FILE)
                    if not df_gen.empty:
                        df_gen = df_gen.sort_values(by="Points", ascending=False).reset_index(drop=True)
                        df_gen["AncienRang"] = df_gen.index + 1
                    else:
                        df_gen = pd.DataFrame(columns=["Joueur", "Points", "AncienRang"])

                    for _, row in df_v.iterrows():
                        joueur, bons = row['Joueur'], sum(1 for m in matchs if row[m] == reels[m])
                        pts = bons + (3 if bons == 8 else 0)
                        if joueur in df_gen['Joueur'].values:
                            df_gen.loc[df_gen['Joueur'] == joueur, 'Points'] += pts
                        else:
                            df_gen = pd.concat([df_gen, pd.DataFrame([{"Joueur": joueur, "Points": pts, "AncienRang": 0}])], ignore_index=True)
                    save_data(df_gen, SCORES_FILE)
                    if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                    st.rerun()

        with tab2:
            df_v = load_data(VOTES_FILE)
            if not df_v.empty:
                st.write(f"Nombre de votes : {len(df_v)}")
                st.dataframe(df_v[["Joueur"]], use_container_width=True)
            else:
                st.info("Aucun vote en cours.")

        with tab3:
            new_msg = st.text_area("Texte de l'annonce :", load_message())
            if st.button("Mettre à jour"):
                save_message(new_msg)
                st.rerun()

        with tab4:
            if st.button("🗑️ RESET TOTAL"):
                for f in [SCORES_FILE, VOTES_FILE]:
                    if os.path.exists(f): os.remove(f)
                st.rerun()
