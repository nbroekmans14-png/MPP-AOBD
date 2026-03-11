import streamlit as st
import pandas as pd
import os

# 1. CONFIGURATION
st.set_page_config(page_title="Pronos St-Nolff", page_icon="🏸", layout="centered")

# Fichiers de sauvegarde
VOTES_FILE = "tous_les_votes.csv"
SCORES_FILE = "classement_general.csv"
INFO_FILE = "info_rencontre.txt"

# Fonctions de gestion des données
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_info(text):
    with open(INFO_FILE, "w", encoding="utf-8") as f:
        f.write(text)

def load_info():
    if os.path.exists(INFO_FILE):
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "Prochaine rencontre à venir..."

# 2. STYLE CSS
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .header-box { background-color: #004a99; color: white !important; padding: 20px; border-radius: 12px; text-align: center; border-bottom: 4px solid #ffcc00; }
    .info-box { background-color: #fff9c4; color: #333 !important; padding: 15px; border-radius: 8px; text-align: center; margin-top: 15px; border: 1px solid #fbc02d; font-weight: bold; font-size: 1.1rem; }
    .match-card { background: #f1f3f5; padding: 10px; border-radius: 8px; border-left: 5px solid #004a99; margin-top: 10px; font-weight: bold; color: #004a99 !important; }
    </style>
    """, unsafe_allow_html=True)

# Présentation
st.markdown('<div class="header-box"><h1>🏸 Le MPP de l\'AOBD</h1><p>1pt par bonne réponse + 3pts bonus si 8/8.</p></div>', unsafe_allow_html=True)
st.markdown(f'<div class="info-box">📢 {load_info()}</div>', unsafe_allow_html=True)

# 3. INTERFACE JOUEUR (VOTE)
st.subheader("1️⃣ Fais ton prono !")
nom_input = st.text_input("Ton Prénom & Nom :", placeholder="Ex: Lucas B").strip()

matchs = ["Simple Homme 1", "Simple Homme 2", "Simple Dame 1", "Simple Dame 2", 
          "Double Homme", "Double Dame", "Mixte 1", "Mixte 2"]

if nom_input:
    df_v_check = load_data(VOTES_FILE)
    
    # Vérifie uniquement si le nom est déjà dans les votes EN COURS
    deja_prie = False
    if not df_v_check.empty and "Joueur" in df_v_check.columns:
        if nom_input.lower() in df_v_check["Joueur"].str.lower().values:
            deja_prie = True

    if deja_prie:
        st.warning(f"⚠️ Quelqu'un a déjà voté avec le nom '{nom_input}' pour cette rencontre.")
    else:
        pronos = {}
        for m in matchs:
            st.markdown(f'<div class="match-card">{m}</div>', unsafe_allow_html=True)
            pronos[m] = st.radio(f"Vainqueur {m}", ["St-Nolff", "Adversaire"], key=f"p_{m}", horizontal=True, label_visibility="collapsed")
        
        if st.button("🚀 ENREGISTRER MON VOTE"):
            df_v = load_data(VOTES_FILE)
            nouveau_vote = {"Joueur": nom_input}
            nouveau_vote.update(pronos)
            df_v = pd.concat([df_v, pd.DataFrame([nouveau_vote])], ignore_index=True)
            save_data(df_v, VOTES_FILE)
            st.success("C'est enregistré ! Bonne chance pour tes pronos.")
            st.balloons()
            st.rerun()

st.divider()

# 4. CLASSEMENT GÉNÉRAL AVEC ÉVOLUTION (+/- places)
st.subheader("🏆 CLASSEMENT GÉNÉRAL")
df_scores = load_data(SCORES_FILE)

if not df_scores.empty:
    # On trie pour définir le rang actuel
    df_scores = df_scores.sort_values(by="Points", ascending=False).reset_index(drop=True)
    df_scores['Rang'] = range(1, len(df_scores) + 1)

    def format_tendance(row):
        if 'AncienRang' not in row or pd.isna(row['AncienRang']) or row['AncienRang'] == 999:
            return "⚪ ="
        diff = int(row['AncienRang']) - int(row['Rang'])
        if diff > 0: return f"🟢 +{diff}"
        elif diff < 0: return f"🔴 {diff}"
        return "⚪ ="

    df_scores['Evolution'] = df_scores.apply(format_tendance, axis=1)
    st.table(df_scores[['Rang', 'Evolution', 'Joueur', 'Points']])
else:
    st.info("Le classement sera mis à jour après la validation des matchs par l'admin.")

# 5. ESPACE ADMIN
st.divider()
with st.expander("🛠️ ACCÈS ADMINISTRATEUR"):
    mdp = st.text_input("Code secret :", type="password")
    if mdp == "2003":
        tab_ann, tab_res, tab_vot, tab_dan = st.tabs(["📢 Annonce", "✅ Résultats", "👥 Votes", "⚠️ Danger"])

        with tab_ann:
            st.write("### Modifier l'annonce")
            nouvelle_info = st.text_area("Texte (Date, lieu, adversaire...)", value=load_info())
            if st.button("Mettre à jour l'annonce"):
                save_info(nouvelle_info)
                st.success("Annonce mise à jour !")
                st.rerun()

        with tab_res:
            st.write("### Valider la rencontre")
            reels = {m: st.selectbox(f"Gagnant {m}", ["-", "St-Nolff", "Adversaire"], key=f"adm_{m}") for m in matchs}
            if st.button("✅ CALCULER LES POINTS ET CLÔTURER"):
                df_v = load_data(VOTES_FILE)
                if df_v.empty: st.error("Personne n'a encore voté !")
                elif any(v == "-" for v in reels.values()): st.error("Veuillez remplir tous les scores.")
                else:
                    df_gen = load_data(SCORES_FILE)
                    
                    # Avant la mise à jour, on enregistre le rang actuel comme "AncienRang"
                    if not df_gen.empty:
                        df_gen = df_gen.sort_values(by="Points", ascending=False).reset_index(drop=True)
                        df_gen['AncienRang'] = range(1, len(df_gen) + 1)
                    else:
                        df_gen = pd.DataFrame(columns=["Joueur", "Points", "AncienRang"])

                    for _, row in df_v.iterrows():
                        joueur = row['Joueur']
                        bons = sum(1 for m in matchs if row[m] == reels[m])
                        pts_j = bons + (3 if bons == 8 else 0)
                        
                        if joueur in df_gen['Joueur'].values:
                            df_gen.loc[df_gen['Joueur'] == joueur, 'Points'] += pts_j
                        else:
                            df_gen = pd.concat([df_gen, pd.DataFrame([{"Joueur": joueur, "Points": pts_j, "AncienRang": 999}])], ignore_index=True)
                    
                    save_data(df_gen, SCORES_FILE)
                    if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                    st.success("Classement mis à jour et votes archivés !")
                    st.rerun()

        with tab_vot:
            st.write("### Suivi des votes pour cette journée")
            df_v_d = load_data(VOTES_FILE)
            if not df_v_d.empty:
                st.write(f"Nombre de participants : **{len(df_v_d)}**")
                st.dataframe(df_v_d[["Joueur"]], use_container_width=True)
            else:
                st.info("Aucun vote enregistré pour le moment.")

        with tab_dan:
            st.write("### Zone de réinitialisation")
            if st.button("🗑️ RÉINITIALISER LE CLASSEMENT GÉNÉRAL"):
                if os.path.exists(SCORES_FILE): os.remove(SCORES_FILE)
                if os.path.exists(VOTES_FILE): os.remove(VOTES_FILE)
                st.warning("Tout a été supprimé.")
                st.rerun()
    elif mdp != "":
        st.error("Mot de passe incorrect.")
