import streamlit as st
from graphviz import Digraph
import re

# Configuração de Estilo
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp {font-size: 22px !important;}
    .stSelectbox label {font-size: 24px !important; font-weight: bold; color: #1E88E5;}
    </style>
    """, unsafe_allow_html=True)

MORPHO_COLORS = {
    "Substantivo": "royalblue", "Verbo": "crimson", "Adjetivo": "seagreen",
    "Artigo": "gray", "Pronome": "darkorchid", "Advérbio": "darkorange",
    "Preposição": "saddlebrown", "Conjunção": "darkcyan", "Partícula": "goldenrod", "Pontuação": "black"
}

RELATIONS = sorted(["PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
                   "PRED_CO", "SBJ_CO", "OBJ_CO", "ADV_CO", "ATR_CO", "PNOM_CO", 
                   "AuxP", "AuxC", "AuxR", "AuxV", "AuxK", "AuxX"])

if 'words' not in st.session_state:
    st.session_state.words = []

def render_tree(words):
    dot = Digraph(format='svg')
    dot.attr(dpi='300', rankdir='TB', nodesep='1.0', ranksep='1.2')
    dot.node("0", "ROOT", fontcolor="red", fontsize="30", shape="none")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Usando f-string simples para evitar erro de renderização
        label_html = f'<<table border="0"><tr><td><font point-size="30" color="{color}"><b>{w["form"]}</b></font></td></tr><tr><td><font point-size="18" color="#555555">{w["relation"]}</font></td></tr></table>>'
        dot.node(w['id'], label_html, shape="none")
        dot.edge(w['head'], w['id'], color="#aaaaaa", penwidth="2.0")
    return dot

st.title("🏛️ Arethusa Editor - Streamlit")

# Entrada de Texto
input_text = st.text_input("Sentença Grega", placeholder="Cole o texto aqui...")
if st.button("GERAR TOKENS"):
    tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
    st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]

if st.session_state.words:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configurar Relação")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # --- MUDANÇA AQUI: ORDEM INVERTIDA ---
        
        # 1. Primeiro escolhemos o PAI (Head)
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("1. ESCOLHA A PALAVRA PAI (HEAD)", h_options)
        
        # 2. Depois escolhemos o FILHO (Dependente)
        target_idx = st.selectbox("2. ESCOLHA A PALAVRA FILHO", range(len(w_options)), format_func=lambda x: w_options[x])
        
        # 3. Relação e Classe
        new_rel = st.selectbox("3. TIPO DE RELAÇÃO", RELATIONS)
        new_morph = st.selectbox("4. CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR E ATUALIZAR ÁRVORE"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col2:
        st.subheader("Visualização da Árvore")
        # use_container_width=True para garantir que ela apareça
        st.graphviz_chart(render_tree(st.session_state.words), use_container_width=True)
