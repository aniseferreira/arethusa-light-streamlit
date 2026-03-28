import streamlit as st
from graphviz import Digraph
import re

st.set_page_config(layout="wide")

if 'words' not in st.session_state:
    st.session_state.words = []

def render_tree(words):
    dot = Digraph()
    dot.node("0", "ROOT")
    for w in words:
        # Formato mais simples possível para não quebrar
        label = f"{w['form']} ({w['relation']})"
        dot.node(w['id'], label)
        dot.edge(w['head'], w['id'])
    return dot

st.title("Arethusa Editor - Teste de Estabilidade")

# 1. Gerador de Tokens
input_text = st.text_input("Sentença Grega:")
col_btn1, col_btn2 = st.columns(2)

if col_btn1.button("GERAR TOKENS"):
    tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
    st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
    st.rerun()

if col_btn2.button("ADICIONAR ARTIFICIAL (aT)"):
    new_id = str(len(st.session_state.words) + 1)
    st.session_state.words.append({"id": new_id, "form": "[aT]", "postag": "Artificial", "head": "0", "relation": "COORD"})
    st.rerun()

# 2. Área de Trabalho
if st.session_state.words:
    col_edit, col_view = st.columns([1, 2])
    
    with col_edit:
        options = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # PAI primeiro
        sel_head = st.selectbox("PALAVRA PAI (HEAD)", ["0: ROOT"] + options)
        # FILHO depois
        sel_child_idx = st.selectbox("PALAVRA FILHO", range(len(options)), format_func=lambda x: options[x])
        sel_rel = st.selectbox("RELAÇÃO", ["PRED", "SBJ", "OBJ", "ADV", "ATR", "COORD", "AuxP", "OBJ_CO", "SBJ_CO"])
        
        if st.button("VINCULAR AGORA"):
            st.session_state.words[sel_child_idx]['head'] = sel_head.split(":")[0]
            st.session_state.words[sel_child_idx]['relation'] = sel_rel
            st.rerun()

    with col_view:
        # Se o Graphviz estiver funcionando, a árvore APARECE aqui
        st.graphviz_chart(render_tree(st.session_state.words))
