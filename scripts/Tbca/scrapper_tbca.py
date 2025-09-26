import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time
import re

# URL base do site
BASE_URL = "https://www.tbca.net.br/base-dados/composicao_alimentos.php"

# Lista para armazenar todos os dados
dados_brutos = []

# Função para extrair o número máximo de páginas
def get_pagination_info(soup):
    pagination_div = soup.find('div', {'id': 'block_1'})
    if pagination_div:
        text = pagination_div.text.strip()
        match = re.search(r'Exibindo página \d+ de (\d+)', text)
        if match:
            max_pages = int(match.group(1))
            return max_pages
    return 57  # Fallback

# Função para processar uma página
def processar_pagina(url, atuald):
    print(f"Acessando página: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar a tabela dentro de <div class="bd-example">
    div_example = soup.find('div', {'class': 'bd-example'})
    if not div_example:
        print(f"Div bd-example não encontrada em {url}")
        return []

    tabela = div_example.find('table', {'class': 'table table-striped'})
    if not tabela:
        print(f"Tabela não encontrada em {url}")
        return []

    alimentos = []
    linhas = tabela.find_all('tr')[1:]  # Ignorar cabeçalho
    for linha in linhas:
        colunas = linha.find_all('td')
        if len(colunas) < 5:
            continue

        codigo = colunas[0].text.strip()
        nome = colunas[1].text.strip()
        nome_cientifico = colunas[2].text.strip()  # Extrair 'Nome Científico'
        grupo = colunas[3].text.strip()  # Extrair 'Grupo'
        marca = colunas[4].text.strip()  # Extrair 'Marca'
        links = [col.find('a')['href'] for col in colunas if col.find('a')]
        if not links:
            print(f"Nenhum link encontrado para o alimento {nome}")
            continue

        link_alimento = urljoin(BASE_URL, links[0])
        alimentos.append((codigo, nome, nome_cientifico, grupo, marca, link_alimento))

    return alimentos

# Função para processar a página detalhada de um alimento
def processar_alimento(codigo, nome, nome_cientifico, grupo, marca, link_alimento):
    print(f"Acessando alimento: {nome} ({link_alimento})")
    try:
        response = requests.get(link_alimento, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao acessar {link_alimento}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Tentar encontrar a tabela na página detalhada
    tabela = soup.find('table', {'class': 'table table-striped'})
    if not tabela:
        tabela = soup.find('table')
        if not tabela:
            print(f"Tabela detalhada não encontrada para {nome}")
            return []

    dados_alimento = []
    linhas_alimento = tabela.find_all('tr')[1:]  # Ignorar cabeçalho
    for linha_alimento in linhas_alimento:
        colunas_alimento = linha_alimento.find_all('td')
        if len(colunas_alimento) < 3:
            continue

        componente = colunas_alimento[0].text.strip()
        unidades = colunas_alimento[1].text.strip()
        valor_por_100g = colunas_alimento[2].text.strip()

        # Concatenar a unidade ao componente, exceto para 'Energia' que já foi tratado
        if componente == 'Energia':
            componente = f'Energia ({unidades})'
        else:
            componente = f'{componente}_{unidades}' if unidades else componente

        dados_alimento.append({
            'Código': codigo,
            'Nome': nome,
            'Nome_Científico': nome_cientifico,
            'Grupo': grupo,
            'Marca': marca,
            'Componente': componente,
            'Valor por 100g': valor_por_100g
        })

    return dados_alimento

# Determinar o número máximo de atuald
max_atuald = 6

# Iterar por todas as páginas
for atuald in range(1, max_atuald + 1):
    url_inicial = f"{BASE_URL}?pagina=1&atuald={atuald}"
    try:
        response = requests.get(url_inicial, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        max_pages = get_pagination_info(soup)
    except requests.RequestException as e:
        print(f"Erro ao acessar {url_inicial}: {e}")
        max_pages = 57

    print(f"Processando atuald={atuald} com {max_pages} páginas")

    for pagina in range(1, max_pages + 1):
        url = f"{BASE_URL}?pagina={pagina}&atuald={atuald}"
        alimentos = processar_pagina(url, atuald)

        for codigo, nome, nome_cientifico, grupo, marca, link_alimento in alimentos:
            dados_alimento = processar_alimento(codigo, nome, nome_cientifico, grupo, marca, link_alimento)
            dados_brutos.extend(dados_alimento)
            time.sleep(1)  # Delay para evitar sobrecarga

        time.sleep(1)  # Delay entre páginas

# Criar DataFrame com os dados brutos
df_bruto = pd.DataFrame(dados_brutos)

# Pivotar os dados para transformar 'Componente' em colunas
if not df_bruto.empty:
    df_pivot = df_bruto.pivot_table(
        index=['Código', 'Nome', 'Nome_Científico', 'Grupo', 'Marca'],
        columns='Componente',
        values='Valor por 100g',
        aggfunc='first'
    ).reset_index()

    # Renomear colunas para evitar caracteres especiais
    df_pivot.columns = [col.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace(',', '') for col in df_pivot.columns]

    # Salvar em Excel
    df_pivot.to_excel('tbca_dados_alimentos_pivot.xlsx', index=False, engine='openpyxl')
    print("Dados salvos em 'tbca_dados_alimentos_pivot.xlsx'")
else:
    print("Nenhum dado foi coletado.")