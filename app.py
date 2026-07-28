import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E CSS INDUSTRIAL PREMIUM
# ---------------------------------------------------------
st.set_page_config(
    page_title="T-MINAS | Control Tower Industrial",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Oculta barras nativas */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Fundo Global Industrial */
    .stApp {
        background-color: #2E4057 !important;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }

    /* Container Principal Estilo Painel ERP */
    .main .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 98% !important;
    }

    /* BARRA SUPERIOR EXECUTIVA */
    .top-header {
        background: linear-gradient(90deg, #1B2A4A 0%, #2E4057 100%);
        color: #FFFFFF;
        padding: 14px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #0066CC;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .top-header h2 {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-size: 20px !important;
        letter-spacing: 0.5px;
    }
    .top-header span {
        font-size: 13px;
        color: #93C5FD;
    }

    /* FIX DE COR DOS RÓTULOS E TÍTULOS (ALTO CONTRASTE) */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, label, .stSelectbox label, .stTextInput label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* INPUTS & DROPDOWNS REFORMATADOS */
    .stTextInput input, .stSelectbox select, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 6px !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 500 !important;
    }

    /* CONTAINERS BRANCOS (CARDS DE CONTEÚDO) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ABAS DE NAVEGAÇÃO BEM DEFINIDAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: transparent;
        border-radius: 6px;
        color: #CBD5E1 !important;
        font-weight: 600;
        border: none !important;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066CC !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0,102,204,0.4);
    }

    /* CARD DE OP DA FILA (ESTILO INDUSTRIAL) */
    .op-card {
        background-color: #F8FAFB;
        border-left: 5px solid #0066CC;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
    }
    .op-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .op-title {
        font-size: 16px;
        font-weight: 700;
        color: #1B2A4A;
    }
    .op-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
    .op-details {
        font-size: 13px;
        color: #475569;
    }

    /* BOTÕES COM HOVER ELEGANTE */
    .stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SUPABASE DATABASE
# ---------------------------------------------------------
SUPABASE_URL = "https://iyugeblppdtqilxcqujl.supabase.co"
SUPABASE_KEY = "sb_publishable_4tkS_6TLkqctg01Tw8xPQA_PiGwN84D"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
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
# SESSÃO E AUTH
# ---------------------------------------------------------
if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = "Marcos Mattos"
    st.session_state.perfil = "PCP"

if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, center, c2 = st.columns([1, 1.2, 1])
    with center:
        with st.container(border=True):
            st.markdown("<h2 style='text-align:center; color:#1B2A4A !important;'>T-MINAS INDUSTRIAL</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#64748B; font-size:12px; margin-top:-10px;'>SISTEMA DE CONTROL TOWER & PCP</p>", unsafe_allow_html=True)
            st.markdown("---")
            user_in = st.text_input("Usuário / Matrícula", value="Marcos Mattos")
            perfil_in = st.selectbox("Perfil de Acesso", ["PCP / Gestor (Administrador)", "Operador de Chão de Fábrica"])
            
            if st.button("LOGON NO SISTEMA", type="primary", use_container_width=True):
                st.session_state.logado = True
                st.session_state.usuario = user_in
                st.session_state.perfil = "PCP" if "PCP" in perfil_in else "OPERADOR"
                st.rerun()

else:
    # Header Topo
    st.markdown(f"""
    <div class="top-header">
        <h2>🏭 T-MINAS BENTONITAS — CONTROL TOWER</h2>
        <span>Perfil: <b>{st.session_state.perfil}</b> ({st.session_state.usuario})</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.perfil == "PCP":
        tab1, tab2, tab3 = st.tabs([
            "📋 Emissão & Fila de OPs", 
            "🏷️ Cadastrar Produtos & Estrutura (BOM)", 
            "📈 Dashboard OEE"
        ])

        # TAB 1: EMISSÃO E FILA
        with tab1:
            col_form, col_fila = st.columns([1, 1.4])

            with col_form:
                with st.container(border=True):
                    st.markdown("<h3 style='color:#1B2A4A !important; margin-top:0;'>➕ Emitir Ordem de Produção</h3>", unsafe_allow_html=True)
                    
                    moinho_sel = st.selectbox("Moinho Destino", ["M1", "M2", "PN"])
                    op_num_in = st.text_input("Número da OP", value="1001")
                    cliente_in = st.text_input("Cliente", placeholder="Ex: Clariant")
                    
                    prods = carregar_produtos()
                    list_p = [f"{p['codigo']} - {p['descricao']}" for p in prods] if prods else ["PA12005 - FLOTICOR PA 7225 - BIG BAG S/LINER 1200 KG"]
                    prod_sel = st.selectbox("Produto (Cadastro Vivo)", list_p)
                    
                    lote_in = st.text_input("Lote Sugerido", value="3726F7225M1")
                    qtd_in = st.text_input("Quantidade Programada", placeholder="Ex: 50.4 Ton")
                    seq_in = st.text_input("Faixa Sequencial Prevista", value="1-40")

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🚀 EMITIR ORDEM PARA PRODUÇÃO", type="primary", use_container_width=True):
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
                                st.success(f"OP #{op_num_in} emitida com sucesso!")
                                st.rerun()
                        else:
                            st.warning("Preencha o Cliente e a Quantidade!")

            with col_fila:
                with st.container(border=True):
                    st.markdown("<h3 style='color:#1B2A4A !important; margin-top:0;'>📋 Fila de Produção no Chão de Fábrica</h3>", unsafe_allow_html=True)
                    ops_pendentes = carregar_ops("Pendente")
                    
                    if ops_pendentes:
                        for op in ops_pendentes:
                            st.markdown(f"""
                            <div class="op-card">
                                <div class="op-card-header">
                                    <span class="op-title">OP #{op['op']} ({op.get('moinho', 'M1')}) — {op['cliente']}</span>
                                    <span class="op-badge">EM FILA</span>
                                </div>
                                <div class="op-details">
                                    <b>Produto:</b> {op['produto']}<br>
                                    <b>Quantidade:</b> {op['qtd']} | <b>Lote:</b> {op['lote']} | <b>Seq:</b> {op.get('seq', '-')}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c_btn1, c_btn2 = st.columns([1, 4])
                            with c_btn1:
                                if st.button("🗑️ Apagar", key=f"del_{op['op']}", help="Remover esta OP"):
                                    if deletar_op(op['op']):
                                        st.success("Removida!")
                                        st.rerun()
                            st.markdown("---")
                    else:
                        st.info("Nenhuma Ordem de Produção pendente na fila.")

        # TAB 2: BOM / ESTRUTURA
        with tab2:
            with st.container(border=True):
                st.markdown("<h3 style='color:#1B2A4A !important; margin-top:0;'>🏷️ Estrutura de Produtos e Componentes (BOM)</h3>", unsafe_allow_html=True)
                col_b1, col_b2 = st.columns([1, 1.2])

                with col_b1:
                    st.text_input("Código PA", placeholder="Ex: PA12005")
                    st.text_input("Descrição Completa", placeholder="Ex: FLOTICOR PA 7225 - BIG BAG S/LINER 1200 KG")
                    st.number_input("Tempo Previsto (unid/min)", value=15)
                    
                    st.markdown("<b style='color:#1B2A4A;'>Exemplo de Tabela de Insumos:</b>", unsafe_allow_html=True)
                    df_ex = pd.DataFrame([
                        {"Tipo": "Item", "Cód": "SA07000", "Descrição": "Floticor MOÍDA #200", "Qtd Base": 0.808, "UM": "ton"},
                        {"Tipo": "Recurso", "Cód": "MOD00020", "Descrição": "MÃO DE OBRA PRODUÇÃO", "Qtd Base": 1.0, "UM": "unid."},
                        {"Tipo": "Item", "Cód": "CG08718", "Descrição": "BAG 1000KG S/ LINER", "Qtd Base": 0.833, "UM": "unid."}
                    ])
                    st.dataframe(df_ex, use_container_width=True, hide_index=True)

                with col_b2:
                    st.markdown("<b style='color:#1B2A4A;'>Produtos Cadastrados na Base:</b>", unsafe_allow_html=True)
                    prods_cad = carregar_produtos()
                    if prods_cad:
                        df_p = pd.DataFrame(prods_cad)[['codigo', 'descricao', 'tempo_previsto_unid_min']]
                        df_p.columns = ['Código', 'Descrição do Item', 'Tempo Prev. (min)']
                        st.dataframe(df_p, use_container_width=True, hide_index=True)

        # TAB 3: OEE
        with tab3:
            with st.container(border=True):
                st.markdown("<h3 style='color:#1B2A4A !important; margin-top:0;'>📊 Indicadores OEE de Desempenho Fabril</h3>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("DISPONIBILIDADE T1", "87.2%", "209.28h")
                m2.metric("DISPONIBILIDADE T2", "86.1%", "228.37h")
                m3.metric("PERFORMANCE GERAL", "90.0%", "Real x Meta")
                m4.metric("OEE TOTAL FÁBRICA", "79.2%", "Meta Atingida")

                st.markdown("---")
                st.markdown("<b style='color:#1B2A4A;'>Histórico de OPs Finalizadas:</b>", unsafe_allow_html=True)
                ops_conc = carregar_ops("Concluida")
                if ops_conc:
                    df_c = pd.DataFrame(ops_conc)[['op', 'cliente', 'produto', 'tempo_total', 'tempo_paradas', 'turno']]
                    df_c.columns = ['OP', 'Cliente', 'Produto', 'Tempo Prod.', 'Tempo Paradas', 'Turno']
                    st.dataframe(df_c, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhuma OP finalizada registrada até o momento.")

    else:
        with st.container(border=True):
            st.markdown("<h3 style='color:#1B2A4A !important; margin-top:0;'>🚜 Fila de Processamento do Moinho</h3>", unsafe_allow_html=True)
            ops_p = carregar_ops("Pendente")
            if ops_p:
                for op in ops_p:
                    st.markdown(f"""
                    <div class="op-card">
                        <div class="op-card-header">
                            <span class="op-title">OP #{op['op']} ({op.get('moinho', 'M1')}) — {op['cliente']}</span>
                        </div>
                        <div class="op-details">
                            <b>Produto:</b> {op['produto']} | <b>Qtd:</b> {op['qtd']} | <b>Lote:</b> {op['lote']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)