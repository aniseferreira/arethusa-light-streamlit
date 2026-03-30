import streamlit as st
import pandas as pd
import re
import graphviz
import xml.etree.ElementTree as ET
import io

# 1. Configurações de Página
st.set_page_config(layout="wide", page_title="Arethusa Editor")

MORPHO_COLORS = {
    "Substantivo": "forestgreen", "Verbo": "crimson", "Adjetivo": "royalblue",
    "Artigo": "darkcyan", "Pronome": "#8C2E64", "Advérbio": "darkorange",
    "Preposição": "#006060", "Conjunção": "hotpink", "Partícula": "goldenrod",
    "Pontuação": "black", "Artificial": "purple", "Numeral": "#00FF00"
}

RELATIONS = sorted([
    "PRED", "SBJ", "OBJ", "ADV", "ATR", "PNOM", "COORD", "APOS", 
    "AuxK", "AuxX", "AuxY", "AuxZ", "AuxG", "AuxC", "AuxV", "AuxP", "ExD"
])

def get_color_by_postag(postag):
    return MORPHO_COLORS.get(postag, "black")

# 2. RENDERIZAÇÃO COM TRAVAS DE TAMANHO (Para não deformar)
def render_tree(words):
    if not words:
        return None
    
    dot = graphviz.Digraph(format='svg')
    # ranksep menor para não esticar demais verticalmente
    dot.attr(rankdir='TB', nodesep='0.3', ranksep='0.3', margin='0')
    
    # Configuração global dos nós (Palavras)
    dot.attr('node', fontname='Alegreya', fontsize='14', height='0.1', width='0.1')
    # Configuração das flechas (Finas)
    dot.attr('edge', arrowsize='0.5', color='gray')

    # Nó [ROOT] - Forçado a ser pequeno e discreto
    dot.node('0', '[ROOT]', shape='none', fontcolor='black', fontsize='11', fixedsize='true', width='0.6', height='0.2')

    for w in words:
        tem_pai = w.get('head') not in ["", None, "0"]
        conectado_ao_root = w.get('head') == "0"
        e_essencial = w.get('relation') in ['AuxK', 'PRED']
        
        if not (tem_pai or conectado_ao_root or e_essencial):
            continue 

        node_id = str(w['id'])
        color = get_color_by_postag(w.get('postag', ''))
        
        # Label limpo: Palavra em negrito, relação pequena embaixo
        label = f"<<table border='0' cellborder='0' cellpadding='0'><tr><td><b>{w['form']}</b></td></tr><tr><td><font point-size='9'>{w['relation']}</font></td></tr></table>>"
        
        dot.node(node_id, label=label, shape='none', fontcolor=color)
        
        if w.get('head') not in ["", None]:
            dot.edge(str(w['head']), node_id)

    return dot

def export_xml(words):
    root = ET.Element("treebank", version="1.5", lang="grc")
    sentence = ET.SubElement(root, "sentence", id="1", document_id="arethusa")
    for w in words:
        ET.SubElement(sentence, "word", id=str(w['id']), form=w['form'], head=str(w['head']), relation=w['relation'], postag=w['postag'])
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)

# 3. INTERFACE ORGANIZADA POR LINHAS (Fácil para o aluno)
st.title("🏛️ Arethusa Lite (Editor)")

if 'words' not in st.session_state:
    st.session_state.words = []

with st.sidebar:
    st.header("1. Entrada de Texto")
    text_input = st.text_area("Cole a sentença grega:", height=100)
    if st.button("GERAR TOKENS ⚡", use_container_width=True):
        tokens = re.findall(r"[\w\u0370-\u03FF\u1F00-\u1FFF]+|[.,;:·]", text_input)
        st.session_state.words = [{"id": i+1, "form": t, "head": "", "relation": "", "postag": ""} for i, t in enumerate(tokens)]
        st.rerun()

    if st.session_state.words:
        st.divider()
        st.header("2. Anotação")
        w_opts = [f"{w['id']}: {w['form']}" for w in st.session_state.words]
        
        # Sequência lógica de cima para baixo
        sel_idx = st.selectbox("1. SELECIONE O FILHO (Palavra)", range(len(w_opts)), format_func=lambda x: w_opts[x])
        st.write("---")
        sel_head = st.selectbox("2. SELECIONE O PAI (Head)", ["0: ROOT"] + w_opts)
        sel_rel = st.selectbox("3. DEFINA A RELAÇÃO", RELATIONS)
        sel_morph = st.selectbox("4. DEFINA A CLASSE", list(MORPHO_COLORS.keys()))
        
        if st.button("VINCULAR AGORA 🔄", use_container_width=True):
            st.session_state.words[sel_idx]['head'] = sel_head.split(":")[0]
            st.session_state.words[sel_idx]['relation'] = sel_rel
            st.session_state.words[sel_idx]['postag'] = sel_morph
            st.rerun()

        st.divider()
        xml_data = export_xml(st.session_state.words)
        st.download_button(label="📦 Baixar XML", data=xml_data, file_name="arethusa.xml", mime="application/xml", use_container_width=True)

# 4. ÁREA DA ÁRVORE
if st.session_state.words:
    dot_objeto = render_tree(st.session_state.words)
    if dot_objeto:
        # container_width garante que ela não ultrapasse a tela lateral
        st.graphviz_chart(dot_objeto, use_container_width=True)
