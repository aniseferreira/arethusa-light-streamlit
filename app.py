import streamlit as st
from graphviz import Digraph
import re

# 1. Configurações de Página
st.set_page_config(layout="wide", page_title="Arethusa Editor")

# Cores Filológicas (Mantendo a estética)
MORPHO_COLORS = {
    "Substantivo": "forestgreen",   # Verde Floresta
    "Verbo": "crimson",             # Mantido (Vermelho)
    "Adjetivo": "royalblue",        # Azul Royal
    "Artigo": "darkcyan",           # Ciano Escuro (que dá o tom azul claro)
    "Pronome": "#8C2E64",           # Bordeaux (seu código específico)
    "Advérbio": "darkorange",       # Mantido
    "Preposição": "#006060",        # Verde Petróleo (Teal escuro)
    "Conjunção": "hotpink",         # Hot Pink (Rosa forte)
    "Partícula": "goldenrod",       # Mantido (Dourado)
    "Pontuação": "black",           # Mantido
    "Artificial": "purple"          # Mantido
}

# 2. TODAS AS ETIQUETAS QUE VOCÊ PRECISA
RELATIONS = sorted([
    "PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
    "PRED_CO", "SBJ_CO", "OBJ_CO", "ADV_CO", "ATR_CO", "PNOM_CO", 
    "AuxP", "AuxC", "AuxY", "AuxZ", "AuxG", "AuxK", "AuxX", "ExD", "OBJ_AP", "SBJ_AP"
])

if 'words' not in st.session_state:
    st.session_state.words = []

# 3. Renderização Estável (Sem HTML complexo para não sumir)
def render_tree(words):
    dot = Digraph()
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.8')
    # Fonte 14 ou 16 é o limite de segurança para o Streamlit não "espremer"
    dot.attr('node', fontname='Alegreya', fontsize='18', shape='none') 
    
    dot.node("0", "ROOT", fontcolor="red", fontsize="20")
    
    for w in words:
        color = MORPHO_COLORS.get(w['postag'], "black")
        # Rótulo simples que o Graphviz ama: Palavra + Relação
        label = f"{w['form']}\n({w['relation']})"
        dot.node(w['id'], label, fontcolor=color)
        dot.edge(w['head'], w['id'], color="#cccccc")
    return dot

st.title("🏛️ Arethusa Editor Light - Funcional")

# --- BLOCO DE INSERÇÃO ---
col_in1, col_in2 = st.columns([2, 1])

with col_in1:
    input_text = st.text_input("Sentença Grega:")
    if st.button("GERAR TOKENS 🚀"):
        tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
        st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
        st.rerun()

with col_in2:
    at_val = st.text_input("Token Artificial:", value="[aT1]")
    if st.button("INSERIR aT ➕"):
        new_id = str(len(st.session_state.words) + 1)
        st.session_state.words.append({"id": new_id, "form": at_val, "postag": "Artificial", "head": "0", "relation": "COORD"})
        st.rerun()

st.divider()

# --- ÁREA DE ANOTAÇÃO ---
if st.session_state.words:
    col_edit, col_view = st.columns([1, 2])
    
    with col_edit:
        st.subheader("Configuração")
        w_opts = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # Ordem: PAI primeiro (conforme solicitado)
        sel_head = st.selectbox("PALAVRA PAI (HEAD)", ["0: ROOT"] + w_opts)
        
        # FILHO (Dependente)
        sel_idx = st.selectbox("PALAVRA FILHO", range(len(w_opts)), format_func=lambda x: w_opts[x])
        
        # Etiquetas Completas
        sel_rel = st.selectbox("RELAÇÃO SINTÁTICA", RELATIONS)
        sel_morph = st.selectbox("CLASSE GRAMATICAL", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR E ATUALIZAR 🔄"):
            st.session_state.words[sel_idx]['head'] = sel_head.split(":")[0]
            st.session_state.words[sel_idx]['relation'] = sel_rel
            st.session_state.words[sel_idx]['postag'] = sel_morph
            st.rerun()

    with col_view:
        st.subheader("Árvore Sintática")
        st.graphviz_chart(render_tree(st.session_state.words))
