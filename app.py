import streamlit as st
from graphviz import Digraph
import xml.etree.ElementTree as ET
import tempfile
import re

# Configuração da Página para Fontes Grandes
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp {font-size: 22px !important;}
    button {height: 3em !important; font-size: 20px !important;}
    .stSelectbox label, .stTextInput label {font-size: 24px !important; font-weight: bold;}
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
    # Aumentamos o DPI para a imagem não perder nitidez
    dot = Digraph(format='svg')
    dot.attr(dpi='300') 
    
    # Forçamos o tamanho da fonte global da árvore
    dot.attr('node', fontsize='30', fontname='Arial')
    dot.attr(rankdir='TB', nodesep='1.5', ranksep='1.2')
    
    dot.node("0", "ROOT", fontcolor="red", fontsize="35", shape="none")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        
        # Usamos HTML label para garantir que o texto da palavra seja GRANDE
        # O "point-size" aqui é o segredo para vencer o 1mm de altura
        lbl = f'''<
        <table border="0" cellborder="0" cellspacing="0">
          <tr><td><font point-size="32" color="{color}"><b>{w["form"]}</b></font></td></tr>
          <tr><td><font point-size="20" color="#666666">{w["relation"]}</font></td></tr>
        </table>>'''
        
        dot.node(w['id'], lbl, shape="none")
        dot.edge(w['head'], w['id'], color="#cccccc", penwidth="2.0")
        
    return dot

st.title("🏛️ Arethusa Streamlit Edition")

# Aba 1: Iniciar
input_text = st.text_input("Sentença Grega", placeholder="Ex: ἐν ἀρχῇ ἦν ὁ λόγος")
if st.button("GERAR TOKENS"):
    tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
    st.session_state.words = [{"id": str(i+1), "form": t, "lemma": "", "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]

# Aba 2: Anotação
if st.session_state.words:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Anotação")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        target_idx = st.selectbox("Palavra Filho", range(len(w_options)), format_func=lambda x: w_options[x])
        
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("Palavra Pai (Head)", h_options)
        new_rel = st.selectbox("Relação", RELATIONS)
        new_morph = st.selectbox("Classe Gramatical", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR E ATUALIZAR"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col2:
        st.subheader("Árvore Sintática")
        st.graphviz_chart(render_tree(st.session_state.words))
