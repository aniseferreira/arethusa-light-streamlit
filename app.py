import streamlit as st
import pandas as pd
import re
import graphviz
import xml.etree.ElementTree as ET
import io

# 1. Configurações de Página
st.set_page_config(layout="wide", page_title="Arethusa Editor")

MORPHO_COLORS = {
    "Substantivo": "forestgreen",   
    "Verbo": "crimson",             
    "Adjetivo": "royalblue",        
    "Artigo": "darkcyan",           
    "Pronome": "#8C2E64",           
    "Advérbio": "darkorange",       
    "Preposição": "#006060",        
    "Conjunção": "hotpink",         
    "Partícula": "goldenrod",       
    "Pontuação": "black",           
    "Artificial": "purple",          
    "Numeral": "#00FF00"            
}

RELATIONS = sorted([
    "PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
    "PRED_CO", "SBJ_CO", "OBJ_CO", "ADV_CO", "ATR_CO", "PNOM_CO", "COORD_CO", "APOS_CO",
    "AuxK", "AuxX", "AuxY", "AuxZ", "AuxG", "AuxC", "AuxV", "AuxP", "ExD"
])

def get_color_by_postag(postag):
    return MORPHO_COLORS.get(postag, "black")

# 2. RENDERIZAÇÃO CORRIGIDA (ROOT DISCRETO + PROGRESSIVA)
def render_tree(words):
    if not words:
        return None
    
    dot = graphviz.Digraph(format='svg')
    dot.attr(rankdir='TB', nodesep='0.4', ranksep='0.4')
    dot.attr('node', fontname='Alegreya', fontsize='16') 

    # ROOT Simples para não deformar a árvore
    dot.node('0', '[ROOT]', shape='none', fontcolor='black', fontsize='12', width='0.5')

    for w in words:
        # Só aparece o que já tem pai, ou é predicado/pontuação
        tem_pai = w.get('head') not in ["", None, "0"]
        conectado_ao_root = w.get('head') == "0"
        e_essencial = w.get('relation') in ['AuxK', 'PRED']
        
        if not (tem_pai or conectado_ao_root or e_essencial):
            continue 

        node_id = str(w['id'])
        color = get_color_by_postag(w.get('postag', ''))
        
        label = f"<<table border='0' cellborder='0'><tr><td><b>{w['form']}</b></td></tr><tr><td><font point-size='10'>{w['relation']}</font></td></tr></table>>"
        
        dot.node(node_id, label=label, shape='none', fontcolor=color)
        
        if w.get('head') not in ["", None]:
            dot.edge(str(w['head']), node_id)

    return dot

def export_xml(words):
    root = ET.Element("treebank", version="1.5", lang="grc")
    sentence = ET.SubElement(root, "sentence", id="1", document_id="arethusa")
    for w in words:
        ET.SubElement(sentence, "word", 
                      id=str(w['id']), 
                      form=w['form'], 
                      head=str(w['head']), 
                      relation=w['relation'],
                      postag=w['postag'])
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

# 3. INTERFACE (ORDEM DOS MENUS CORRIGIDA)
st.title("🏛️ Arethusa Lite (Editor)")

if 'words' not in st.session_state:
    st.session_state.words = []

with st.sidebar:
    st.header("1. Texto Fonte")
    text_input = st.text_area("Cole a sentença grega:", height=150)
    if st.button("GERAR TOKENS ⚡", use_container_width=True):
        tokens = re.findall(r"[\w\u0370-\u03FF\u1F00-\u1FFF]+|[.,;:·]", text_input)
        st.session_state.words = [
            {"id": i+1, "form": t, "head": "", "relation": "", "postag": ""} 
            for i, t in enumerate(tokens)
        ]
        st.rerun()

    if st.session_state.words:
        st.divider()
        st.header("3. Anotação")
        w_opts = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # --- ORDEM DOS MENUS QUE VOCÊ PREFERE ---
        c1, c2 = st.columns(2)
        with c1:
            sel_head = st.selectbox("PAI", ["0: ROOT"] + w_opts)
            sel_rel = st.selectbox("RELAÇÃO", RELATIONS)
        with c2:
            sel_morph = st.selectbox("CLASSE", list(MORPHO_COLORS.keys()))
        
        # Filho embaixo para maior destaque
        sel_idx = st.selectbox("FILHO (Palavra a ser anotada)", range(len(w_opts)), format_func=lambda x: w_opts[x])
        
        if st.button("VINCULAR 🔄", use_container_width=True):
            st.session_state.words[sel_idx]['head'] = sel_head.split(":")[0]
            st.session_state.words[sel_idx]['relation'] = sel_rel
            st.session_state.words[sel_idx]['postag'] = sel_morph
            st.rerun()

        st.divider()
        xml_data = export_xml(st.session_state.words)
        st.download_button(label="📦 Baixar XML", data=xml_data, file_name="arethusa.xml", mime="application/xml", use_container_width=True)

# 4. ÁREA VISUAL
if st.session_state.words:
    dot_objeto = render_tree(st.session_state.words)
    if dot_objeto:
        st.graphviz_chart(dot_objeto, use_container_width=True)
