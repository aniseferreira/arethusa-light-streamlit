import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações Visuais da Página (Fontes Maiores)
st.set_page_config(layout="wide", page_title="Arethusa Editor")
st.markdown("""
    <style>
    .stApp { font-size: 20px !important; }
    /* Estilo para os labels dos campos de seleção */
    .stSelectbox label { font-size: 22px !important; font-weight: bold; color: #1E88E5 !important; }
    button { height: 3em !important; font-weight: bold !important; font-size: 18px !important; }
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

# 3. Função de Renderização (Fontes Robustas)
def render_tree(words):
    dot = Digraph(format='svg')
    dot.attr(dpi='300')
    # Forçamos o tamanho da fonte global para 30 (bem visível)
    dot.attr('node', shape='none', fontname='Arial', fontsize='30')
    dot.attr('edge', color='#cccccc', penwidth='2.0')
    
    # Nó Raiz
    dot.node("0", "ROOT", fontcolor="red", fontsize="34", fontname="Arial-Bold")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Criamos o label com a palavra grande e a relação menor abaixo
        # O uso de HTML-like label aqui é mais seguro no Streamlit
        label = f'<<table border="0" cellborder="0"><tr><td><font point-size="32" color="{color}"><b>{w["form"]}</b></font></td></tr><tr><td><font point-size="18" color="#666666">{w["relation"]}</font></td></tr></table>>'
        
        dot.node(w['id'], label)
        dot.edge(w['head'], w['id'])
        
    return dot

st.title("🏛️ Arethusa Editor - Streamlit")

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
        new_head = st.selectbox("A. ESCOLHA A PALAVRA PAI (HEAD)", h_options)
        
        target_idx = st.selectbox("B. ESCOLHA A PALAVRA FILHO (DEPENDENTE)", range(len(w_options)), format_func=lambda x: w_options[x])
        
        new_rel = st.selectbox("C. TIPO DE RELAÇÃO", RELATIONS)
        new_morph = st.selectbox("D. CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("ATUALIZAR ÁRVORE 🔄"):
            # CORREÇÃO DO ERRO NAMEERROR AQUI:
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col_tree:
        st.subheader("Visualização da Árvore")
        # Exibe a árvore ocupando a largura da coluna
        st.graphviz_chart(render_tree(st.session_state.words), use_container_width=True)
