import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações Visuais da Página
st.set_page_config(layout="wide", page_title="Arethusa Editor")
st.markdown("""
    <style>
    .stApp { font-size: 20px !important; }
    .stSelectbox label { font-size: 24px !important; font-weight: bold; color: #d32f2f !important; }
    button { height: 3em !important; width: 100% !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Paleta de Cores Filológicas
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

# 3. Função de Renderização Robusta
def render_tree(words):
    # Criamos o gráfico com DPI alto para não ficar embaçado
    dot = Digraph(format='svg')
    dot.attr(dpi='300')
    
    # Configurações globais: Letra tamanho 28 para os nós
    dot.attr('node', shape='plain', fontname='Arial', fontsize='28')
    dot.attr('edge', color='#cccccc', penwidth='2.0')
    
    # Nó Raiz
    dot.node("0", "ROOT", fontcolor="red", fontsize="32", fontname="Arial-Bold")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Label simples: Palavra em cima, Relação embaixo entre parênteses
        # O '\n' cria a quebra de linha que o Graphviz entende nativamente
        clean_label = f"{w['form']}\n({w['relation']})"
        
        dot.node(w['id'], clean_label, fontcolor=color)
        dot.edge(w['head'], w['id'])
        
    return dot

st.title("🏛️ Arethusa Editor - Versão Estável")

# 4. Entrada de Dados
input_text = st.text_input("1. DIGITE A SENTENÇA GREGA:", placeholder="Ex: ἐν ἀρχῇ ἦν ὁ λόγος")
if st.button("GERAR TOKENS"):
    tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
    st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]

# 5. Área de Trabalho
if st.session_state.words:
    col_input, col_tree = st.columns([1, 2])
    
    with col_input:
        st.subheader("Configuração")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # --- ORDEM INVERTIDA: PAI PRIMEIRO ---
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("A. PALAVRA PAI (HEAD)", h_options)
        
        target_idx = st.selectbox("B. PALAVRA FILHO (DEPENDENTE)", range(len(w_options)), format_func=lambda x: w_options[x])
        
        new_rel = st.selectbox("C. TIPO DE RELAÇÃO", RELATIONS)
        new_morph = st.selectbox("D. CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("ATUALIZAR ÁRVORE 🔄"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new
