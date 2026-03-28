import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações Básicas
st.set_page_config(layout="wide")

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

# 2. Renderização Simples (Igual à primeira, mas com fonte definida)
def render_tree(words):
    dot = Digraph(format='svg')
    # ESTE É O SEGREDO: Forçamos o tamanho da fonte no nó de forma simples
    dot.attr('node', fontsize='30', fontname='Arial', shape='none')
    dot.attr(rankdir='TB', nodesep='1.0', ranksep='1.2')
    
    dot.node("0", "ROOT", fontcolor="red", fontsize="35")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Texto simples com quebra de linha, sem HTML complexo
        lbl = f"{w['form']}\n[{w['relation']}]"
        dot.node(w['id'], lbl, fontcolor=color)
        dot.edge(w['head'], w['id'], color="#cccccc")
    return dot

st.title("🏛️ Arethusa Editor - Streamlit")

# 3. Entrada
input_text = st.text_input("Sentença Grega")
if st.button("GERAR TOKENS"):
    tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
    st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
    st.rerun()

# 4. Interface de Anotação
if st.session_state.words:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuração")
        w_options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # Ordem: Pai primeiro
        h_options = ["0: ROOT"] + w_options
        new_head = st.selectbox("PALAVRA PAI (HEAD)", h_options)
        
        target_idx = st.selectbox("PALAVRA FILHO (DEPENDENTE)", range(len(w_options)), format_func=lambda x: w_options[x])
        
        new_rel = st.selectbox("RELAÇÃO", RELATIONS)
        new_morph = st.selectbox("CLASSE", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR E ATUALIZAR"):
            st.session_state.words[target_idx]['head'] = new_head.split(":")[0]
            st.session_state.words[target_idx]['relation'] = new_rel
            st.session_state.words[target_idx]['postag'] = new_morph
            st.rerun()

    with col2:
        st.subheader("Árvore")
        # use_container_width=False evita que o Streamlit "esmague" a imagem
        st.graphviz_chart(render_tree(st.session_state.words), use_container_width=False)
