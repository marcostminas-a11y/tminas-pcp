import streamlit as st
import pandas as pd
import time
from datetime import datetime
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="T-Minas Industrial | Control Tower PCP",
    page_icon="🏭",
    layout="wide"
)

# Conexão Supabase
SUPABASE_URL = "https://iyugeblppdtqilxcqujl.supabase.co"
SUPABASE_KEY = "sb_publishable_4tkS_6TLkqctg01Tw8xPQA_PiGwN84D"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erro ao conectar com Supabase: {e}")
        return None

supabase = init_supabase()

# ---------------------------------------------------------
# FUNÇÕES DE BANCO DE DADOS
# ---------------------------------------------------------
def carregar_produtos():
    if not supabase: return []
    try:
        res = supabase.table("cadastros_produtos").select("*").order("codigo").execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao carregar produtos: {e}")
        return []

def carregar_ops(status_filtro="Pendente"):
    if not supabase: return []
    try:
        res = supabase.table("ordens_producao").select("*").eq("status", status_filtro).order("id", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Erro ao carregar OPs: {e}")
        return []

def salvar_nova_op(dados_op):
    if not supabase: return False
    try:
        supabase.table("ordens_producao").insert(dados_op).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar OP: {e}")
        return False

def deletar_op(op_num):
    if not supabase: return False
    try:
        supabase.table("ordens_producao").delete().eq("op", str(op_num)).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar OP: {e}")
        return False

# ---------------------------------------------------------
# AUTENTICAÇÃO E PERFIL
# ---------------------------------------------------------
if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.perfil = "PCP"

if not st.session_state.logado:
    st.title("🏭 T-MINAS INDUSTRIAL")
    st.subheader("Sistema de Control Tower, PCP & OEE")
    
    with st.form("form_login"):
        user_input = st.text_input("Usuário / Matrícula", value="Marcos Mattos")
        perfil_input = st.selectbox("Perfil de Acesso", ["PCP / Gestor (Administrador)", "Operador de Chão de Fábrica"])
        btn_login = st.form_submit_button("ENTRAR NO SISTEMA")
        
        if btn_login:
            st.session_state.logado = True
            st.session_state.usuario = user_input
            st.session_state.perfil = "PCP" if "PCP" in perfil_input else "OPERADOR"
            st.rerun()

else:
    # BARRA SUPERIOR
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.caption(f"📍 T-MINAS BENTONITAS INDUSTRIAL | Usuário: **{st.session_state.usuario}** ({st.session_state.perfil})")
    with col_t2:
        if st.button("🚪 Sair / Trocar Usuário"):
            st.session_state.logado = False
            st.rerun()

    st.markdown("---")

    # ---------------------------------------------------------
    # PAINEL PCP / ADMINISTRADOR
    # ---------------------------------------------------------
    if st.session_state.perfil == "PCP":
        tab1, tab2, tab3 = st.tabs(["📋 Emissão & Monitoramento de OPs", "🏷️ Cadastrar Produtos & Estrutura (BOM)", "📈 Dashboard OEE"])

        # ABA 1: EMISSÃO DE OP
        with tab1:
            col_form, col_list = st.columns([1, 1.5])
            
            with col_form:
                st.subheader("➕ Nova Ordem de Produção")
                produtos = carregar_produtos()
                lista_prods_str = [f"{p['codigo']} - {p['descricao']}" for p in produtos] if produtos else ["PA12005 - FLOTICOR PA 7225 - BIG BAG S/LINER 1200 KG"]
                
                moinho_sel = st.selectbox("Moinho Destino", ["M1", "M2", "PN"])
                op_num_in = st.text_input("Número da OP", value="1001")
                cliente_in = st.text_input("Cliente", placeholder="Ex: Clariant")
                prod_sel = st.selectbox("Produto Acabado", lista_prods_str)
                lote_in = st.text_input("Lote", value="3726F7225M1")
                qtd_in = st.text_input("Quantidade Programada", placeholder="Ex: 50.4 Ton")
                seq_in = st.text_input("Sequência de Etiquetas", value="1-40")

                if st.button("🚀 EMITIR ORDEM PARA O MOINHO", type="primary", use_container_width=True):
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
                        st.warning("Preencha Cliente e Quantidade!")

            with col_list:
                st.subheader("📋 Fila de Ordens de Produção")
                ops_pendentes = carregar_ops("Pendente")
                if ops_pendentes:
                    for op in ops_pendentes:
                        with st.expander(f"OP #{op['op']} ({op.get('moinho', 'M1')}) - {op['cliente']}"):
                            st.write(f"**Produto:** {op['produto']}")
                            st.write(f"**Qtd:** {op['qtd']} | **Lote:** {op['lote']} | **Seq:** {op.get('seq', '-')}")
                            if st.button("🗑️ Apagar OP", key=f"del_{op['op']}"):
                                if deletar_op(op['op']):
                                    st.success(f"OP #{op['op']} deletada!")
                                    st.rerun()
                else:
                    st.info("Nenhuma OP pendente na fila.")

        # ABA 2: CADASTRO DE PRODUTOS & BOM
        with tab2:
            st.subheader("🏷️ Estrutura de Produtos (BOM)")
            col_c1, col_c2 = st.columns([1, 1])
            
            with col_c1:
                cod_pa = st.text_input("Código do Item (Nº PA)", placeholder="Ex: PA12005")
                desc_pa = st.text_input("Descrição Completa", placeholder="Ex: FLOTICOR PA 7225 - BIG BAG S/LINER 1200 KG")
                tempo_p = st.number_input("Tempo Previsto (unid/min)", min_value=1.0, value=15.0)
                
                st.write("**Componentes da Estrutura (Exemplo):**")
                df_bom_ex = pd.DataFrame([
                    {"Tipo": "Item", "Código": "SA07000", "Descrição": "Floticor MOÍDA #200", "Qtd Base": 0.808, "UM": "ton"},
                    {"Tipo": "Recurso", "Código": "MOD00020", "Descrição": "MÃO DE OBRA PRODUÇÃO", "Qtd Base": 1.0, "UM": "unid."},
                    {"Tipo": "Item", "Código": "CG08718", "Descrição": "BAG 1000KG S/ LINER", "Qtd Base": 0.833, "UM": "unid."}
                ])
                st.dataframe(df_bom_ex, use_container_width=True)

            with col_c2:
                st.subheader("Produtos Cadastrados na Base")
                prods_cad = carregar_produtos()
                if prods_cad:
                    df_p = pd.DataFrame(prods_cad)[['codigo', 'descricao', 'tempo_previsto_unid_min']]
                    st.dataframe(df_p, use_container_width=True)
                else:
                    st.info("Nenhum produto cadastrado ainda.")

        # ABA 3: OEE
        with tab3:
            st.subheader("📊 Indicadores OEE de Fábrica (Por Turno)")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("DISPONIBILIDADE (TURNO 1)", "87.2%", "Horas: 209.28")
            m2.metric("DISPONIBILIDADE (TURNO 2)", "86.1%", "Horas: 228.37")
            m3.metric("PERFORMANCE GERAL", "90.0%", "Tempo Real x Meta")
            m4.metric("OEE TOTAL FÁBRICA", "79.2%", "Meta Atingida", delta_color="normal")

            st.write("---")
            st.write("**Histórico de Ordens Concluídas:**")
            ops_conc = carregar_ops("Concluida")
            if ops_conc:
                st.dataframe(pd.DataFrame(ops_conc)[['op', 'cliente', 'produto', 'tempo_total', 'tempo_paradas', 'turno']], use_container_width=True)
            else:
                st.info("Nenhuma OP concluída registrada ainda.")

    # ---------------------------------------------------------
    # PAINEL OPERADOR / CHÃO DE FÁBRICA
    # ---------------------------------------------------------
    else:
        st.subheader("🚜 Chão de Fábrica - Fila de Processamento")
        ops_pend = carregar_ops("Pendente")
        
        if ops_pend:
            for op in ops_pend:
                st.info(f"📍 **OP #{op['op']}** ({op.get('moinho', 'M1')}) | Cliente: {op['cliente']} | Produto: {op['produto']} | Qtd: {op['qtd']}")
        else:
            st.success("🎉 Nenhuma OP pendente no momento!")