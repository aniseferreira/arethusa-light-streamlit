import streamlit as st
import pandas as pd
import re
from graphviz import Digraph
import xml.etree.ElementTree as ET
import io

# 1. Configurações de Página
st.set_page_config(page_icon="𐂷", layout="wide", page_title="Arethusa Editor")

MORPHO_COLORS = {
    "Substantivo": "forestgreen", "Verbo": "crimson", "Adjetivo": "royalblue",
    "Artigo": "darkcyan", "Pronome": "#8C2E64", "Advérbio": "darkorange",
    "Preposição": "#006060", "Conjunção": "hotpink", "Partícula": "goldenrod",
    "Pontuação": "black", "Artificial": "purple", "Numeral": "#00FF00"
}

RELATIONS = sorted([
    "PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
    "PRED_CO", "SBJ_CO", "OBJ_CO", "ADV_CO", "ATR_CO", "PNOM_CO", 
    "AuxP", "AuxC", "AuxY", "AuxZ", "AuxG", "AuxK", "AuxX", "ExD", "OBJ_AP", "SBJ_AP"
])

if 'words' not in st.session_state:
    st.session_state.words = []

def render_tree(words):
    if not words: return None
    dot = Digraph()
    dot.attr(rankdir='TB', nodesep='0.8', ranksep='0.6')
    dot.attr('node', fontname="serif", shape='none')
    
    # ROOT Original mantido
    dot.node("0", label="ROOT", fontcolor="red", fontsize="20")
    
    for w in words:
        # --- MODIFICAÇÃO: FILTRO PARA ÁRVORE LIMPA ---
        # Só renderiza se tiver um pai definido (head != "0") 
        # OU se for pontuação final/verbo principal
        tem_pai = w.get('head') not in ["0", "", None]
        e_essencial = w.get('relation') in ['AuxK', 'PRED']
        
        if not (tem_pai or e_essencial):
            continue 
        # --------------------------------------------

        txt_color = MORPHO_COLORS.get(w.get('postag', 'Substantivo'), "black")
        # Aumentado levemente para 24 para visibilidade na faculdade
        label = f'<<table border="0" cellborder="0"><tr><td><font point-size="24" color="{txt_color}"><b>{w["form"]}</b></font></td></tr><tr><td><font point-size="14" color="gray30">{w["relation"] or "?"}</font></td></tr></table>>'
        dot.node(str(w['id']), label)
        dot.edge(str(w['head'] or "0"), str(w['id']), color="#cccccc", penwidth='1.5')
    return dot

def export_xml(words):
    root = ET.Element("treebank")
    s = ET.SubElement(root, "sentence", id="1")
    for w in words:
        ET.SubElement(s, "word", id=str(w['id']), form=w['form'], head=str(w['head']), relation=w['relation'], postag=w['postag'])
    return ET.tostring(root, encoding='utf-8')

st.title("𐂷 Arethusa Editor de Treebank AGDT Light")
st.markdown(" [Ver diretrizes de anotação AGDT2](https://github.com/PerseusDL/treebank_data/blob/master/AGDT2/guidelines/Greek_guidelines.md#3-prague-syntactic-layer)/ [ AGDT1 em inglês](https://github.com/PerseusDL/treebank_data/blob/master/v1/greek/docs/guidelines.pdf)/ [ AGDT1 em por-br](https://github.com/aniseferreira/LetrasClassicasDigitais/blob/master/treebank_guidelines_translated/Manual_AGDT(1)Feb_2015(rev18).pdf)")

col_in1, col_in2 = st.columns([2, 1])

with col_in1:
    input_text = st.text_input("Inserir aqui sentença Grega:")
    if st.button("GERAR TOKENS 🚀"):
        tokens = re.findall(r"[\w\u0370-\u03FF]+|[.,;:·!?]", input_text)
        # Ao gerar, todos começam apontando para "0" (ROOT), mas o filtro acima esconderá da árvore
        st.session_state.words = [{"id": str(i+1), "form": t, "postag": "Substantivo", "head": "0", "relation": "ROOT"} for i, t in enumerate(tokens)]
        st.rerun()

with col_in2:
    at_val = st.text_input("Token Artificial:", value="[aT1]")
    if st.button("INSERIR aT ➕"):
        new_id = str(len(st.session_state.words) + 1)
        st.session_state.words.append({"id": new_id, "form": at_val, "postag": "Artificial", "head": "0", "relation": "COORD"})
        st.rerun()

st.divider()

if st.session_state.words:
    col_edit, col_view = st.columns([1, 4])
    
    with col_edit:
        st.markdown("#### ⚙️ Etiquetar e vincular dependências")
        w_opts = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        c1, c2 = st.columns(2)
        with c1:
            sel_head = st.selectbox("PAI", ["0: ROOT"] + w_opts)
            sel_rel = st.selectbox("RELAÇÃO", RELATIONS)
        with c2:
            sel_idx = st.selectbox("FILHO", range(len(w_opts)), format_func=lambda x: w_opts[x])
            sel_morph = st.selectbox("CLASSE", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR 🔄", use_container_width=True):
            st.session_state.words[sel_idx]['head'] = sel_head.split(":")[0]
            st.session_state.words[sel_idx]['relation'] = sel_rel
            st.session_state.words[sel_idx]['postag'] = sel_morph
            st.rerun()

        st.divider()
        xml_data = export_xml(st.session_state.words)
        st.download_button(label="📦 Baixar XML", data=xml_data, file_name="arethusa.xml", mime="application/xml", use_container_width=True)

    with col_view:
        st.graphviz_chart(render_tree(st.session_state.words))
