import streamlit as st
import pandas as pd
import re

# Configuração básica do layout para tela inteira
st.set_page_config(layout="wide")  # Deixar o layout mais amplo

# Título principal
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Controle de Dieta Semanal</h1>", unsafe_allow_html=True)

# Cadastro de alimentos disponíveis
st.markdown("<h2 style='color: #FF5733;'>Cadastro de Alimentos e Totais</h2>", unsafe_allow_html=True)

# Criação de duas colunas no topo da página
col1, col2 = st.columns(2)

with col1:
    # Tabela para cadastrar alimentos e suas unidades
    if "alimentos_cadastrados" not in st.session_state:
        st.session_state["alimentos_cadastrados"] = pd.DataFrame(columns=["Alimento", "Unidade"])

    # Função para adicionar alimentos
    def adicionar_alimento():
        novo_alimento = st.text_input("Nome do Alimento")
        unidade = st.text_input("Unidade (ex: gramas, unidades, ml)")
        if st.button("Adicionar Alimento"):
            if novo_alimento and unidade:
                novo_item = pd.DataFrame({"Alimento": [novo_alimento], "Unidade": [unidade]})
                st.session_state["alimentos_cadastrados"] = pd.concat([st.session_state["alimentos_cadastrados"], novo_item], ignore_index=True)

    adicionar_alimento()

    # Exibindo a tabela de alimentos cadastrados
    st.markdown("<h4 style='color: #2E86C1;'>Lista de Alimentos</h4>", unsafe_allow_html=True)
    st.dataframe(st.session_state["alimentos_cadastrados"])

# Função para calcular os totais dos alimentos consumidos
def calcular_totais_refeicoes(dados):
    alimentos_totais = {}
    pattern = re.compile(r"(\d+)\s*([a-zA-Zçãé]+\s*[a-zA-Zçãé]*)\s*de\s*([a-zA-Zçãé\s]+)")

    for dia, refeicoes in dados.iterrows():
        for refeicao, descricao in refeicoes.items():
            if isinstance(descricao, str) and "Alimento não encontrado" not in descricao:
                itens = descricao.split(", ")
                for item in itens:
                    match = pattern.match(item)
                    if match:
                        quantidade = int(match.group(1))  # Extrair a quantidade
                        unidade = match.group(2).strip().lower()  # Extrair a unidade
                        alimento = match.group(3).strip().lower()  # Extrair o nome do alimento

                        # Somar a quantidade para o mesmo alimento
                        chave_alimento = f"{alimento} ({unidade})"
                        if chave_alimento in alimentos_totais:
                            alimentos_totais[chave_alimento] += quantidade
                        else:
                            alimentos_totais[chave_alimento] = quantidade
    return alimentos_totais

# Colocando a soma dos alimentos na segunda coluna
with col2:
    st.markdown("<h4 style='color: #2E86C1;'>Totais de Alimentos Consumidos</h4>", unsafe_allow_html=True)

    # Criar a tabela de refeições da semana e calcular os totais
    if "dados_semana" not in st.session_state:
        st.session_state["dados_semana"] = pd.DataFrame()  # Inicializando a tabela de refeições se ainda não existir

    totais = calcular_totais_refeicoes(st.session_state["dados_semana"])

    # Exibir os totais de forma organizada
    if totais:
        df_totais = pd.DataFrame(list(totais.items()), columns=["Alimento (Unidade)", "Total Consumido"])
        st.dataframe(df_totais)
    else:
        st.write("Nenhum alimento foi selecionado ainda.")

# Seção para selecionar alimentos para cada dia da semana e refeição
st.markdown("<h2 style='color: #FF5733;'>Seleção de Refeições</h2>", unsafe_allow_html=True)

# Lista de dias e refeições
dias_da_semana = [("Segunda Feira", "🌞"), ("Terça Feira", "🌝"), ("Quarta Feira", "🍂"), 
                  ("Quinta Feira", "🌻"), ("Sexta Feira", "🌟"), ("Sábado", "🎉"), ("Domingo", "🍽️")]
refeicoes = ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Café da Tarde", "Janta"]

# Função para criar a tabela de seleção de alimentos
def criar_tabela_refeicoes():
    tabela_refeicoes = pd.DataFrame(index=[dia for dia, _ in dias_da_semana], columns=refeicoes)
    
    # Cores diferentes para cada dia
    cores_dias = ["#FDEBD0", "#D1F2EB", "#F9E79F", "#F5B7B1", "#A9CCE3", "#FADBD8", "#D5F5E3"]
    
    for idx, (dia, emoji) in enumerate(dias_da_semana):
        cor_fundo = cores_dias[idx]
        st.markdown(f"<h3 style='background-color: {cor_fundo}; padding: 10px;'>{emoji} {dia}</h3>", unsafe_allow_html=True)
        
        cols = st.columns(len(refeicoes))  # Dividindo em colunas para as refeições
        for col_idx, refeicao in enumerate(refeicoes):
            with cols[col_idx]:
                st.markdown(f"**{refeicao}**")
                
                # Multiselect para escolher múltiplos alimentos
                alimentos_selecionados = st.multiselect(f"Selecionar Alimentos ({dia}, {refeicao})", 
                                                        st.session_state["alimentos_cadastrados"]["Alimento"], 
                                                        key=f"{dia}_{refeicao}_alimentos")
                
                if alimentos_selecionados:
                    descricao_refeicao = []
                    for alimento in alimentos_selecionados:
                        quantidade = st.number_input(f"Quantidade ({alimento})", min_value=0, key=f"{dia}_{refeicao}_{alimento}_quantidade")
                        
                        # Encontrar a unidade do alimento no DataFrame
                        alimento_info = st.session_state["alimentos_cadastrados"].loc[st.session_state["alimentos_cadastrados"]["Alimento"] == alimento]
                        if not alimento_info.empty:
                            unidade = alimento_info["Unidade"].values[0]
                            descricao_refeicao.append(f"{quantidade} {unidade} de {alimento}")
                        else:
                            descricao_refeicao.append("Alimento não encontrado")
                    
                    # Salvando a descrição de todos os alimentos da refeição
                    tabela_refeicoes.at[dia, refeicao] = ", ".join(descricao_refeicao)
    
    return tabela_refeicoes

# Criar a tabela de refeições da semana
st.session_state["dados_semana"] = criar_tabela_refeicoes()

# Exibir tabela de refeições preenchida em tela cheia
st.markdown("<h2 style='color: #4CAF50;'>Refeições da Semana</h2>", unsafe_allow_html=True)
st.dataframe(st.session_state["dados_semana"], width=2000, height=800)  # Definir o tamanho da tabela para preencher a tela
