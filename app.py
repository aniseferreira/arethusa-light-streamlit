import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações de Interface
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
    "Artigo": "#555555", "Pronome": "darkorchid", "Advérbio": "darkorange",
    "Preposição": "saddlebrown", "Conjunção": "darkcyan", "Partícula": "goldenrod", "Pontuação": "black"
}

RELATIONS = sorted(["PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
                   "PRED_CO", "SBJ_CO", "OBJ_CO", "ADV_CO", "ATR_CO", "PNOM_CO", 
                   "AuxP", "AuxC", "AuxR", "AuxV", "AuxK", "AuxX"])

if 'words' not in st.session_state:
    st.session_state.words = []

# 2. Função de Renderização à prova de falhas
def render_tree(words):
    dot = Digraph(format='svg')
    dot.attr(dpi='300')
    # Usamos fontes grandes e simples. O '\n' faz a quebra de linha.
    dot.attr('node', shape='ellipse', fontname='Arial', fontsize='24')
    dot.attr('edge', color='#cccccc', penwidth='2.0')
    
    dot.node("0", "ROOT", fontcolor="red", fontsize="28")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Texto simples: Palavra e Relação em linhas diferentes
        display_text = f"{w['form']}\n({w['relation']})"
        dot.node(w['id'], display_text, fontcolor=color, color=color)
        dot.edge(w['head'], w['id'])
        
    return dot

st.title("🏛️ Arethusa Editor - Streamlit")

# 3. Gerador de Tokens
with st.container():
    input_text = st.text_input("1. DIGITE A SENTENÇA GREGA:", key="input_grego")
    if st.button("GERAR TOKENS"):
        if input_text:
            tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
            st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
            st.rerun()

# 4. Área de Trabalho (Só aparece se houver palavras)
if st.session_state.words:
    col_input, col_tree = st.columns([1, 2])
    
    with col_input:
        st.subheader("Configuração")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("A. PALAVRA PAI (HEAD)", h_options)
        target_idx = st.selectbox("B. PALAVRA FILHO (DEPENDENTE)", range(len(w_options)), format_func=lambda x: w_options[x])
        new_rel = st.selectbox("C. TIPO DE RELAÇÃO", RELATIONS)
        new_morph = st.selectbox("D. CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("ATUALIZAR ÁRVORE 🔄"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col_tree:
        st.subheader("Árvore Sintática")
        # Gerar o gráfico
        grafico = render_tree(st.session_state.words)
        st.graphviz_chart(grafico)
