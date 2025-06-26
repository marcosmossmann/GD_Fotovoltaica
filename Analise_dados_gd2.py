import pandas as pd
import matplotlib.pyplot as plt
import os

# Carregar o arquivo CSV
df = pd.read_csv("empreendimento-geracao-distribuida.csv", delimiter=";", encoding="latin-1", low_memory=False)
print(df.columns)
print("Arquivo carregado com sucesso!")

# Criar a coluna "Ano" a partir de "DthAtualizaCadastralEmpreend"
df["Ano"] = df["DthAtualizaCadastralEmpreend"].astype(str).str[:4]  # Extrai apenas o ano

# Remover dados do ano de 2025
df_filtrado = df[df["Ano"] != "2025"].copy()  # .copy() evita alterações indesejadas
print("Dados do ano de 2025 removidos da análise.")

# Criar pasta para salvar os gráficos
os.makedirs("graficosgd", exist_ok=True)

# Filtrar apenas os registros de energia solar fotovoltaica
df_fotovoltaico = df_filtrado[df_filtrado["SigTipoGeracao"] == "UFV"]

# Mostrar os tipos únicos de fontes geradoras nesse subset
print(df_fotovoltaico["DscFonteGeracao"].unique())

# Mostrar o período dos dados disponíveis no arquivo
print("Período de dados disponíveis:")
print(df_filtrado["Ano"].unique())  # Lista os anos disponíveis
print(df_filtrado["DthAtualizaCadastralEmpreend"].min())  # Mostra a data mais antiga de atualização

# Lista das colunas que devem ser numéricas
colunas_numericas = ["MdaPotenciaInstaladaKW", "QtdUCRecebeCredito", "NumCoordNEmpreendimento", "NumCoordEEmpreendimento"]
# Converter todas as colunas da lista para float
for coluna in colunas_numericas:
    df_filtrado[coluna] = pd.to_numeric(df_filtrado[coluna].astype(str).str.replace(",", "."), errors="coerce")
print("Conversão de colunas para valores numéricos concluída.")

# Contar número de instalações por ano
instalacoes_por_ano = df_filtrado["Ano"].value_counts().sort_index()

# 1.Criar o gráfico de número de instalações por ano
plt.figure(figsize=(10, 5))
plt.plot(instalacoes_por_ano.index, instalacoes_por_ano.values, marker="o", linestyle="-", color="royalblue")
# Configurações do gráfico
plt.xlabel("Ano")
plt.ylabel("Número de Instalações")
plt.title("Número de Instalações por Ano (Sem 2025)")
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.7)
# Salvar gráfico
plt.savefig("graficosgd/Numero_instalacoes_ano.png", dpi=300, bbox_inches="tight")
print("Gráfico 1 salvo com sucesso!")
# Exibir o gráfico
plt.show()

# 2. Calcular a potência média instalada por ano
# Calcular a potência média instalada por ano
potencia_media_por_ano = df_filtrado.groupby("Ano")["MdaPotenciaInstaladaKW"].mean()
# Calcular o total de potência instalada por ano e converter para GW
potencia_total_por_ano = df_filtrado.groupby("Ano")["MdaPotenciaInstaladaKW"].sum() / 1e6  # Convertendo kW para GW
# Criar o gráfico com dois eixos Y
fig, ax1 = plt.subplots(figsize=(10, 5))
# Primeiro eixo Y (potência média instalada em kW)
ax1.set_xlabel("Ano")
ax1.set_ylabel("Potência Média Instalada (kW)", color="darkorange")
ax1.plot(potencia_media_por_ano.index, potencia_media_por_ano.values, marker="o", linestyle="-", color="darkorange", label="Potência Média Instalada")
ax1.tick_params(axis='y', labelcolor="darkorange")
# Segundo eixo Y (total de potência instalada em GW)
ax2 = ax1.twinx()
ax2.set_ylabel("Total de Potência Instalada (GW)", color="royalblue")
ax2.plot(potencia_total_por_ano.index, potencia_total_por_ano.values, marker="s", linestyle="--", color="royalblue", label="Total de Potência Instalada")
ax2.tick_params(axis='y', labelcolor="royalblue")
# Adicionar título e configurar layout
plt.title("Evolução da Potência Média Instalada (kW) e Total Instalada (GW) por Ano")
fig.tight_layout()
# Salvar gráfico
plt.savefig("graficosgd/Potencia_media_total_instalada_ano_duplo_eixo.png", dpi=300, bbox_inches="tight")
print("Gráfico atualizado com dois eixos Y gerado com sucesso!")
# Exibir o gráfico
plt.show()

# 3. Gerar gráfico de distribuição geográfica dos empreendimentos
# Contar número de empreendimentos por UF
empreendimentos_por_uf = df_filtrado["SigUF"].value_counts().sort_values(ascending=False) #ordena pelos empreendimentos em ordem decrescente
# Somar a potência instalada por UF
potencia_por_uf = df_filtrado.groupby("SigUF")["MdaPotenciaInstaladaKW"].sum().reindex(empreendimentos_por_uf.index)
# Converter potência instalada para GW
potencia_por_uf = potencia_por_uf / 1_000_000  # Converte de kW para GW
# Criar figura e eixo
fig, ax1 = plt.subplots(figsize=(12, 6))
# Gráfico de barras - Número de empreendimentos
ax1.bar(empreendimentos_por_uf.index, empreendimentos_por_uf.values, color="royalblue", alpha=0.7, label="Nº de Empreendimentos")
ax1.set_xlabel("UF")
ax1.set_ylabel("Número de Empreendimentos", color="royalblue")
ax1.tick_params(axis="y", labelcolor="royalblue")
ax1.set_title("Distribuição Geográfica: Empreendimentos x Potência Instalada por UF")
# Criar segundo eixo para a potência instalada
ax2 = ax1.twinx()
ax2.plot(potencia_por_uf.index, potencia_por_uf.values, marker="o", linestyle="-", color="darkorange", label="Potência Instalada (GW)")
ax2.set_ylabel("Potência Instalada (GW)", color="darkorange")
ax2.tick_params(axis="y", labelcolor="darkorange")
# Adicionar grid e legendas
ax1.grid(axis="y", linestyle="--", alpha=0.7)
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
# Criar pasta para salvar os gráficos, se não existir
os.makedirs("graficosgd", exist_ok=True)
# Salvar gráfico
plt.savefig("graficosgd/Distribuição Geográfica.png", dpi=300, bbox_inches="tight")
print("Gráfico 3 salvo com sucesso!")
# Exibir o gráfico
plt.show()

# 4. Gráfico de Potência Instalada por Tipo de Geração
potencia_por_tipo = df_filtrado.groupby("DscFonteGeracao")["MdaPotenciaInstaladaKW"].sum().sort_values(ascending=False) 
potencia_por_tipo = potencia_por_tipo / 1_000_000  
# Converte de kW para GW
print(potencia_por_tipo)
# Criar gráfico de barras (horizontal para melhorar visualização)
plt.figure(figsize=(17, 8))
potencia_por_tipo.plot(kind="barh", color="teal")
# Aplicar escala logarítmica no eixo X
plt.xscale("log")
# Configurações do gráfico
plt.ylabel("Tipo de Geração")
plt.xlabel("Potência Instalada (GW)")
plt.title("Potência Instalada por Tipo de Geração (Sem 2025)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
# Salvar gráfico
plt.savefig("graficosgd/Potencia_instalada_tipo_geracao.png", dpi=300, bbox_inches="tight")
print("Gráfico 4 salvo com sucesso!")
# Exibir o gráfico
plt.show()



