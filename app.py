import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA E CSS CORPORATIVO T-MINAS
# ---------------------------------------------------------
st.set_page_config(
    page_title="T-Minas Bentonitas | Control Tower PCP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para transformar o Streamlit em um ERP Industrial
st.markdown("""
<style>
    /* Oculta menus padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fundo principal e estrutura */
    .stApp {
        background-color: #3F5E78 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Container Principal da Aplicação */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }

    /* Cards e Containers Brancos Estilo ERP */
    div[data-testid="stVerticalBlock"] > div[data-testid="stBlock"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Barra Superior Corporativa */
    .top-bar-tminas {
        background-color: #1B365D;
        color: #FFFFFF;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }

    /* Títulos e Tipografia */
    h1, h2, h3, h4 {
        color: #1B365D !important;
        font-weight: 700 !important;
    }

    /* Abas de Navegação Personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.15);
        padding: 6px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre;
        background-color: transparent;
        border-radius: 6px;
        color: #FFFFFF !important;
        font-weight: 600;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0066CC !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Estilização de Entradas de Texto e Selects */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        border-radius: 6px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFB !important;
        color: #1E293B !important;
    }

    /* Botões Principais */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: bold !important;
        transition: all 0.2s;
    }

    /* Métricas do Dashboard OEE */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #0066CC !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONEXÃO SUPABASE
# ---------------------------------------------------------
SUPABASE_URL = "https://iyugeblppdtqilxcqujl.supabase.co"
SUPABASE_KEY = "sb_publishable_4tkS_6TLkqctg01Tw8xPQA_PiGwN84D"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase = init_supabase()

def carregar_produtos():
    if not supabase: return []
    try:
        res = supabase.table("cadastros_produtos").select("*").order("codigo").execute()
        return res.data if res.data else []
    except Exception:
        return []

def carregar_ops(status_filtro="Pendente"):
    if not supabase: return []
    try:
        res = supabase.table("ordens_producao").select("*").eq("status", status_filtro).order("id", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

def salvar_nova_op(dados_op):
    if not supabase: return False
    try:
        supabase.table("ordens_producao").insert(dados_op).execute()
        return True
    except Exception:
        return False

def deletar_op(op_num):
    if not supabase: return False
    try:
        supabase.table("ordens_producao").delete().eq("op", str(op_num)).execute()
        return True
    except Exception:
        return False

# ---------------------------------------------------------
# LOGIN E SESSÃO
# ---------------------------------------------------------
if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = "Marcos Mattos"
    st.session_state.perfil = "PCP"

if not st.session_state.logado:
    col_cen1, col_center, col_cen2 = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background-color:#FFFFFF; padding: 30px; border-radius: 12px; border: 1px solid #CBD5E1; text-align: center;'>
            <h2 style='color:#1B365D; margin-bottom: 2px;'>T-MINAS BENTONITAS</h2>
            <p style='color:#64748B; font-size: 11px; font-weight: bold;'>CONTROL TOWER PCP & EXECUÇÃO INDUSTRIAL</p>
            <hr style='border: 0; border-top: 1px solid #E2E8F0; margin: 15px 0;'>
        """, unsafe_allow_html=True)
        
        user_input = st.text_input("Usuário / Matrícula", value="Marcos Mattos")
        perfil_input = st.selectbox("Perfil de Acesso", ["PCP / Gestor (Administrador)", "Operador de Chão de Fábrica"])
        
        if st.button("LOGON NO SISTEMA", type="primary", use_container_width=True):
            st.session_state.logado = True
            st.session_state.usuario = user_input
            st.session_state.perfil = "PCP" if "PCP" in perfil_input else "OPERADOR"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Top Bar T-Minas
    st.markdown(f"""
    <div class="top-bar-tminas">
        <span style="font-weight: bold; font-size: 14px;">T-MINAS BENTONITAS INDUSTRIAIS — CONTROL TOWER</span>
        <span style="font-size: 12px; opacity: 0.9;">Perfil: <b>{st.session_state.perfil}</b> ({st.session_state.usuario})</span>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # MODULO PCP
    # ---------------------------------------------------------
    if st.session_state.perfil == "PCP":
        tab_emissao, tab_bom, tab_oee = st.tabs([
            "📋 Emissão & Monitoramento de OPs", 
            "🏷️ Cadastrar Produtos & Estrutura (BOM)", 
            "📈 Dashboard OEE (Turnos)"
        ])

        # TAB 1: EMISSÃO
        with tab_emissao:
            c_form, c_lista = st.columns([1.1, 1.9])

            with c_form:
                st.markdown("### ➕ Emitir Ordem de Produção")
                moinho_sel = st.selectbox("Moinho Destino", ["M1", "M2", "PN"])
                op_num_in = st.text_input("Número da OP", value="1001")
                cliente_in = st.text_input("Cliente", placeholder="Ex: Clariant")
                
                prods = carregar_produtos()
                list_p = [f"{p['codigo']} - {p['descricao']}" for p in prods] if prods else ["PA12005 - FLOTICOR PA 7225 - BIG BAG S/LINER 1200 KG"]
                prod_sel = st.selectbox("Produto (Cadastro Vivo)", list_p)
                
                lote_in = st.text_input("Lote Sugerido", value="3726F7225M1")
                qtd_in = st.text_input("Quantidade Programada", placeholder="Ex: 50.4 Ton")
                seq_in = st.text_input("Faixa Sequencial Prevista", value="1-40")

                if st.button("🚀 EMITIR ORDEM PARA A PRODUÇÃO", type="primary", use_container_width=True):
                    if cliente_in and qtd_in:
                        dados = {
                            "op": op_num_in,
                            "moinho": moinho_sel,
                            "cliente": cliente_in,
                            "produto": prod_sel,
                            "lote": lote_in,
                            "qtd": qtd_in,
                            "seq": seq_in,
                            "status": "Pendente",
                            "data_coleta": datetime.now().strftime("%d/%m/%Y")
                        }
                        if salvar_nova_op(dados):
                            st.success(f"Ordem de Produção #{op_num_in} enviada com sucesso!")
                            st.rerun()
                    else:
                        st.warning("Preencha o Cliente e a Quantidade!")

            with c_lista:
                st.markdown("### 📋 Fila de Produção de OPs")
                ops_pend = carregar_ops("Pendente")
                if ops_pend:
                    for op in ops_pend:
                        st.markdown(f"""
                        <div style='background-color:#F8FAFB; padding: 12px; border-radius: 6px; border: 1px solid #E2E8F0; margin-bottom: 8px;'>
                            <b style='color:#1B365D;'>OP #{op['op']} ({op.get('moinho', 'M1')}) — {op['cliente']}</b><br>
                            <span style='font-size:12px; color:#475569;'>Produto: {op['produto']} | Qtd: {op['qtd']} | Lote: {op['lote']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🗑️ Apagar OP #{op['op']}", key=f"del_{op['op']}"):
                            if deletar_op(op['op']):
                                st.success("OP Removida!")
                                st.rerun()
                else:
                    st.info("Nenhuma Ordem de Produção pendente no momento.")

        # TAB 2: BOM / PRODUTOS
        with tab_bom:
            st.markdown("### 🏷️ Estrutura de Insumos & Componentes (BOM)")
            col_b1, col_b2 = st.columns([1, 1])

            with col_b1:
                st.text_input("Código do Produto Acabado (PA)", placeholder="Ex: PA12005")
                st.text_input("Descrição Completa", placeholder="Ex: FLOTICOR PA 7225 - BIG BAG S/LINER 1200 KG")
                st.number_input("Tempo Previsto (unid/min)", value=15)
                
                st.markdown("**Lista de Componentes do Produto:**")
                df_ex = pd.DataFrame([
                    {"Tipo": "Item", "Cód": "SA07000", "Descrição": "Floticor MOÍDA #200", "Qtd Base": 0.808, "UM": "ton"},
                    {"Tipo": "Recurso", "Cód": "MOD00020", "Descrição": "MÃO DE OBRA PRODUÇÃO", "Qtd Base": 1.0, "UM": "unid."},
                    {"Tipo": "Item", "Cód": "CG08718", "Descrição": "BAG 1000KG S/ LINER", "Qtd Base": 0.833, "UM": "unid."}
                ])
                st.dataframe(df_ex, use_container_width=True, hide_index=True)

            with col_b2:
                st.markdown("### Base de Produtos Cadastrados")
                prods_cad = carregar_produtos()
                if prods_cad:
                    df_p = pd.DataFrame(prods_cad)[['codigo', 'descricao', 'tempo_previsto_unid_min']]
                    df_p.columns = ['Código', 'Descrição do Item', 'Tempo Prev. (min)']
                    st.dataframe(df_p, use_container_width=True, hide_index=True)
                else:
                    st.info("Carregando banco de dados...")

        # TAB 3: OEE
        with tab_oee:
            st.markdown("### 📊 Indicadores OEE de Desempenho Fabril")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("DISPONIBILIDADE TURNO 1", "87.2%", "Horas: 209.28")
            m2.metric("DISPONIBILIDADE TURNO 2", "86.1%", "Horas: 228.37")
            m3.metric("PERFORMANCE GERAL", "90.0%", "Tempo Real x Meta")
            m4.metric("OEE TOTAL FÁBRICA", "79.2%", "Meta Atingida")

            st.markdown("---")
            st.markdown("**Histórico de OPs Concluídas:**")
            ops_conc = carregar_ops("Concluida")
            if ops_conc:
                df_c = pd.DataFrame(ops_conc)[['op', 'cliente', 'produto', 'tempo_total', 'tempo_paradas', 'turno']]
                df_c.columns = ['OP', 'Cliente', 'Produto', 'Tempo Prod.', 'Tempo Paradas', 'Turno']
                st.dataframe(df_c, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # OPERADOR
    # ---------------------------------------------------------
    else:
        st.markdown("### 🚜 Fila de Processamento do Moinho")
        ops_p = carregar_ops("Pendente")
        if ops_p:
            for op in ops_p:
                st.markdown(f"""
                <div style='background-color:#FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #CBD5E1; margin-bottom: 10px;'>
                    <h3 style='margin:0; color:#1B365D;'>OP #{op['op']} ({op.get('moinho', 'M1')}) — {op['cliente']}</h3>
                    <p style='color:#475569;'><b>Produto:</b> {op['produto']} | <b>Qtd:</b> {op['qtd']} | <b>Lote:</b> {op['lote']}</p>
                </div>
                """, unsafe_allow_html=True)