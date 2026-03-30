import streamlit as st
import pandas as pd
import re
import graphviz
import xml.etree.ElementTree as ET
import io

# 1. Configurações de Página
st.set_page_config(layout="wide", page_title="Arethusa Editor")

# Cores Filológicas (Atualizadas com Numeral Neon)
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

# 2. FUNÇÃO DE RENDERIZAÇÃO ATUALIZADA (PROGRESSIVA + ALEGREYA + TB)
def render_tree(words):
    if not words:
        return None
    
    # Criamos o objeto usando o import 'graphviz'
    dot = graphviz.Digraph(format='svg')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.6')
    dot.attr('node', fontname='Alegreya', fontsize='16') 

    # Nó mestre [ROOT]
    dot.node('0', '[ROOT]', shape='doublecircle', color='black', fontcolor='black', fontsize='12')

    for w in words:
        # LÓGICA PROGRESSIVA:
        # Só desenha o nó se tiver pai definido, ou se for Predicado/Pontuação essencial
        tem_pai = w.get('head') not in ["", None, "0"]
        conectado_ao_root = w.get('head') == "0"
        e_essencial = w.get('relation') in ['AuxK', 'PRED']
        
        if not (tem_pai or conectado_ao_root or e_essencial):
            continue 

        node_id = str(w['id'])
        color = get_color_by_postag(w.get('postag', ''))
        
        # Label com Form em Negrito
        label = f"<<table border='0' cellborder='0'><tr><td><b>{w['form']}</b></td></tr><tr><td><font point-size='10'>{w['relation']}</font></td></tr></table>>"
        
        dot.node(node_id, label=label, shape='none', fontcolor=color)
        
        # Cria a linha se houver um head definido
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

# 3. INTERFACE
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
        
        sel_idx = st.selectbox("FILHO", range(len(w_opts)), format_func=lambda x: w_opts[x])
        sel_head = st.selectbox("PAI", ["0: ROOT"] + w_opts)
        sel_rel = st.selectbox("RELAÇÃO", RELATIONS)
        sel_morph = st.selectbox("CLASSE", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR 🔄", use_container_width=True):
            st.session_state.words[sel_idx]['head'] = sel_head.split(":")[0]
            st.session_state.words[sel_idx]['relation'] = sel_rel
            st.session_state.words[sel_idx]['postag'] = sel_morph
            st.rerun()

# 4. ÁREA VISUAL (Ocupando a largura total)
if st.session_state.words:
    dot_objeto = render_tree(st.session_state.words)
    if dot_objeto:
        st.graphviz_chart(dot_objeto, use_container_width=True)
    
    st.divider()
    st.markdown("#### 📥 Exportar")
    xml_data = export_xml(st.session_state.words)
    st.download_button(
        label="📦 Baixar XML",
        data=xml_data,
        file_name="arethusa.xml",
        mime="application/xml",
        use_container_width=True
    )
