import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações de Estilo
st.set_page_config(layout="wide", page_title="Arethusa Editor")
st.markdown("""
    <style>
    .stApp { font-size: 20px !important; }
    .stSelectbox label { font-size: 22px !important; font-weight: bold; color: #1E88E5 !important; }
    button { height: 3em !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

MORPHO_COLORS = {
    "Substantivo": "royalblue", "Verbo": "crimson", "Adjetivo": "seagreen",
    "Artigo": "gray", "Pronome": "darkorchid", "Advérbio": "darkorange",
    "Preposição": "saddlebrown", "Conjunção": "darkcyan", "Partícula": "goldenrod", "Pontuação": "black",
    "Artificial": "purple"
}

RELATIONS = sorted(["PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
                   "PRED_CO", "SBJ_CO", "OBJ_CO", "ADV_CO", "ATR_CO", "PNOM_CO", 
                   "AuxP", "AuxC", "AuxR", "AuxV", "AuxK", "AuxX"])

if 'words' not in st.session_state:
    st.session_state.words = []

# 2. Renderização da Árvore (Ultra Estável)
def render_tree(words):
    dot = Digraph(format='svg')
    dot.attr(dpi='300')
    # Fonte 30 para ser bem GRANDE e legível
    dot.attr('node', fontsize='30', fontname='Arial', shape='none')
    dot.attr(rankdir='TB', nodesep='1.0', ranksep='1.2')
    
    dot.node("0", "ROOT", fontcolor="red", fontsize="35")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Formato simples: Palavra + Relação entre colchetes
        lbl = f"{w['form']}\n[{w['relation']}]"
        dot.node(w['id'], lbl, fontcolor=color)
        dot.edge(w['head'], w['id'], color="#cccccc", penwidth="2.0")
    return dot

st.title("🏛️ Arethusa Editor - Streamlit")

# 3. Gerador de Tokens e Artificial Token
col_a, col_b = st.columns([2, 1])

with col_a:
    input_text = st.text_input("Inserir Sentença Grega:")
    if st.button("GERAR TOKENS 🚀"):
        tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
        st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
        st.rerun()

with col_b:
    at_form = st.text_input("Artificial Token:", value="[aT1]")
    if st.button("INSERIR TOKEN ARTIFICIAL"):
        new_id = str(len(st.session_state.words) + 1)
        st.session_state.words.append({"id": new_id, "form": at_form, "postag": "Artificial", "head": "0", "relation": "COORD"})
        st.rerun()

st.divider()

# 4. Área de Trabalho
if st.session_state.words:
    col_input, col_tree = st.columns([1, 2])
    
    with col_input:
        st.subheader("Configuração")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # --- PAI (HEAD) PRIMEIRO ---
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("PALAVRA PAI (HEAD)", h_options)
        
        # --- FILHO (DEPENDENTE) DEPOIS ---
        target_idx = st.selectbox("PALAVRA FILHO (DEPENDENTE)", range(len(w_options)), format_func=lambda x: w_options[x])
        
        new_rel = st.selectbox("RELAÇÃO SINTÁTICA", RELATIONS)
        new_morph = st.selectbox("CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR E ATUALIZAR 🔄"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col_tree:
        st.subheader("Árvore Sintática")
        # use_container_width=False para garantir que a fonte 30 seja respeitada
        st.graphviz_chart(render_tree(st.session_state.words), use_container_width=False)
