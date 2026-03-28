import streamlit as st
import pandas as pd
import re
from graphviz import Digraph
import xml.etree.ElementTree as ET
import io

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
    if not words: return None
    dot = Digraph()
    dot.attr(rankdir='TB', nodesep='0.8', ranksep='0.6')
    dot.attr('node', fontname="serif", shape='none')
    
    dot.node("0", label="ROOT", fontcolor="red", fontsize="20")
    
    for w in words:
        txt_color = MORPHO_COLORS.get(w.get('postag', 'Substantivo'), "black")
        # Label formatada para o Streamlit
        label = f'<<table border="0" cellborder="0"><tr><td><font point-size="20" color="{txt_color}"><b>{w["form"]}</b></font></td></tr><tr><td><font point-size="14" color="gray30">{w["relation"] or "?"}</font></td></tr></table>>'
        dot.node(str(w['id']), label)
        dot.edge(str(w['head'] or "0"), str(w['id']), color="#cccccc", penwidth='1.5')
    return dot

import xml.etree.ElementTree as ET
import io

def export_xml(words):
    root = ET.Element("treebank")
    s = ET.SubElement(root, "sentence", id="1")
    for w in words:
        ET.SubElement(s, "word", 
                      id=str(w['id']), 
                      form=w['form'], 
                      head=str(w['head']), 
                      relation=w['relation'], 
                      postag=w['postag'])
    
    # Transforma o XML em string e depois em bytes para o download
    xml_str = ET.tostring(root, encoding='utf-8')
    return xml_str

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
    # Definindo 1 para controles e 4 para a árvore (espaço máximo)
    col_edit, col_view = st.columns([1, 4])
    
    with col_edit:
        st.markdown("### ⚙️ Ajustes")
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
        st.markdown("### 📥 Exportar")

        # Gerar XML (Isso funciona perfeitamente)
        xml_data = export_xml(st.session_state.words)
        st.download_button(
            label="📦 Baixar XML",
            data=xml_data,
            file_name="arethusa.xml",
            mime="application/xml",
            use_container_width=True
        )
        
        st.info("💡 Para salvar a imagem, clique com o botão direito na árvore e selecione 'Salvar imagem como'.")

    with col_view:
        # Aqui a árvore terá 80% da largura da tela para brilhar
        # Chamamos a função sem o parâmetro format_type para evitar o erro
        st.graphviz_chart(render_tree(st.session_state.words))

    
