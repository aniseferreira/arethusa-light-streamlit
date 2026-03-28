import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações de Estilo para Fontes Grandes na Interface
st.set_page_config(layout="wide", page_title="Arethusa Greek Editor")
st.markdown("""
    <style>
    .stApp { font-size: 20px !important; }
    .stTextInput font { size: 22px !important; }
    .stSelectbox label { font-size: 22px !important; font-weight: bold; color: #1E88E5 !important; }
    button { height: 3em !important; font-weight: bold !important; font-size: 18px !important; }
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

# 2. Renderização da Árvore com Fontes Grandes
def render_tree(words):
    dot = Digraph(format='svg')
    dot.attr(dpi='300')
    # Fonte 30 para ser bem legível
    dot.attr('node', fontsize='30', fontname='Arial', shape='none')
    dot.attr(rankdir='TB', nodesep='1.0', ranksep='1.2')
    
    dot.node("0", "ROOT", fontcolor="red", fontsize="35")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        lbl = f"{w['form']}\n({w['relation']})"
        dot.node(w['id'], lbl, fontcolor=color)
        dot.edge(w['head'], w['id'], color="#cccccc", penwidth="2.0")
    return dot

st.title("🏛️ Arethusa Editor - Streamlit")

# --- BLOCO QUE TINHA SUMIDO: GERADOR DE TOKENS ---
st.subheader("1. Inserir Texto Grego")
input_text = st.text_input("Digite ou cole a sentença aqui:", placeholder="Ex: ἐν ἀρχῇ ἦν ὁ λόγος")

if st.button("GERAR TOKENS 🚀"):
    if input_text:
        # Captura palavras gregas e pontuação
        tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
        st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
        st.rerun()

st.divider()

# 3. Área de Trabalho (Aparece após gerar os tokens)
if st.session_state.words:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("2. Configurar Relações")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # Ordem lógica: Escolhe o PAI primeiro
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("PALAVRA PAI (HEAD)", h_options)
        
        # Escolhe o FILHO
        target_idx = st.selectbox("PALAVRA FILHO (DEPENDENTE)", range(len(w_options)), format_func=lambda x: w_options[x])
        
        new_rel = st.selectbox("RELAÇÃO SINTÁTICA", RELATIONS)
        new_morph = st.selectbox("CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR E ATUALIZAR ÁRVORE 🔄"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col2:
        st.subheader("3. Visualização")
        # Gerar e mostrar o gráfico
        grafico = render_tree(st.session_state.words)
        st.graphviz_chart(grafico, use_container_width=False)
