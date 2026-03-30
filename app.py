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
    "Artificial": "purple",          # Mantido
    "Numeral": "#00FF00"            # Verde Neon adicionado aqui
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
    if not words:
        return None
    
    # Criamos o gráfico. TB = Top to bottom (Raiz em cima)
    dot = graphviz.Digraph(format='svg')
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.6')
    dot.attr('node', fontname='Alegreya', fontsize='16') # Fonte maior para a faculdade

    # Criamos o nó mestre [ROOT]
    dot.node('0', '[ROOT]', shape='doublecircle', color='black', fontcolor='black', fontsize='16')

    for w in words:
        # REGRA: Só aparece se tiver pai, se for Predicado ou se for Pontuação
        tem_pai = w.get('head') not in ["", None]
        e_essencial = w.get('relation') in ['AuxK', 'PRED']
        
        if not (tem_pai or e_essencial):
            continue 

        node_id = str(w['id'])
        # (Aqui entra sua lógica de cores que já temos...)
        color = get_color_by_postag(w.get('postag', ''))
        
        # Rótulo com Form em Negrito
        label = f"<<table border='0' cellborder='0'><tr><td><b>{w['form']}</b></td></tr><tr><td><font point-size='10'>{w['relation']}</font></td></tr></table>>"
        
        dot.node(node_id, label=label, shape='none', fontcolor=color)
        
        # Conecta ao pai
        if tem_pai:
            dot.edge(str(w['head']), node_id)

    return dot

# NA PARTE DE EXIBIÇÃO (Final do arquivo):
# Use use_container_width=True para ocupar a tela toda do monitor
st.graphviz_chart(dot, use_container_width=True)

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

st.title("🏛️ Arethusa Editor de Treebank AGDT Light")
st.markdown(" [Ver diretrizes de anotação AGDT2](https://github.com/PerseusDL/treebank_data/blob/master/AGDT2/guidelines/Greek_guidelines.md#3-prague-syntactic-layer)/ [ AGDT1 em inglês](https://github.com/PerseusDL/treebank_data/blob/master/v1/greek/docs/guidelines.pdf)/ [ AGDT1 em por-br](https://github.com/aniseferreira/LetrasClassicasDigitais/blob/master/treebank_guidelines_translated/Manual_AGDT(1)Feb_2015(rev18).pdf)")

# --- BLOCO DE INSERÇÃO ---
col_in1, col_in2 = st.columns([2, 1])

with col_in1:
    input_text = st.text_input("Inserir aqui sentença Grega:")
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
        st.markdown("#### 📥 Exportar")

        # Gerar XML (Isso funciona perfeitamente)
        xml_data = export_xml(st.session_state.words)
        st.download_button(
            label="📦 Baixar XML",
            data=xml_data,
            file_name="arethusa.xml",
            mime="application/xml",
            use_container_width=True
        )
        
        st.info("💡 Para salvar a imagem, clique no ícone fullscreen ao lado da árvore, capture a imagem ou imprima como PDF.")

    with col_view:
        # Aqui a árvore terá 80% da largura da tela para brilhar
        # Chamamos a função sem o parâmetro format_type para evitar o erro
        st.graphviz_chart(render_tree(st.session_state.words))

    
