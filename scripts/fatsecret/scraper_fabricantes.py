import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import string
import urllib.parse
import logging
import sys
import sqlite3

# --- 1. CONFIGURAÇÃO DO LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("extracao.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- 2. CONSTANTES E CONFIGURAÇÕES GLOBAIS ---
BASE_URL = "https://www.fatsecret.com.br"
DB_NAME = "fabricantes_alimentos.db"

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 30
# --- NOVO: Constante para a lógica de otimização ---
CONSECUTIVE_OTHERS_LIMIT = 5 # Parar de paginar após encontrar 5 produtos seguidos de outras marcas

ALL_COLUMNS = [
    'Fabricante', 'Produto', 'Porcao', 'Energia_kcal', 'Energia_kj', 
    'Proteinas', 'Carboidratos', 'Acucar', 'Gorduras', 'Gordura_Saturada', 
    'Gordura_Poliinsaturada', 'Gordura_Monoinsaturada', 'Gordura_Trans', 
    'Colesterol', 'Fibras', 'Sodio', 'Potassio'
]
COLUMN_MAP = {
    'Porção': 'Porcao', 'Energia (kcal)': 'Energia_kcal', 'Energia (kj)': 'Energia_kj',
    'Proteínas': 'Proteinas', 'Carboidratos': 'Carboidratos', 'Açúcar': 'Acucar', 
    'Gorduras': 'Gorduras', 'Gordura Saturada': 'Gordura_Saturada', 
    'Gordura Poliinsaturada': 'Gordura_Poliinsaturada', 'Gordura Monoinsaturada': 'Gordura_Monoinsaturada',
    'Gordura Trans': 'Gordura_Trans', 'Colesterol': 'Colesterol', 'Fibras': 'Fibras',
    'Sódio': 'Sodio', 'Potássio': 'Potassio'
}

def setup_database():
    """Cria o arquivo de banco de dados e a tabela 'alimentos' se não existirem."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        columns_sql = ", ".join([f'"{col}" TEXT' for col in ALL_COLUMNS])
        create_table_query = f'CREATE TABLE IF NOT EXISTS alimentos ({columns_sql})'
        cursor.execute(create_table_query)
        conn.commit()
        logging.info(f"Banco de dados '{DB_NAME}' e tabela 'alimentos' prontos para uso.")
        return conn
    except Exception as e:
        logging.critical(f"NÃO FOI POSSÍVEL INICIAR O BANCO DE DADOS. Erro: {e}")
        return None

def save_to_db(conn, product_data):
    """Salva um único dicionário de produto no banco de dados SQLite."""
    try:
        cursor = conn.cursor()
        values = [product_data.get(col) for col in ALL_COLUMNS]
        placeholders = ", ".join(["?" for _ in ALL_COLUMNS])
        insert_query = f'INSERT INTO alimentos ({", ".join(f"`{c}`" for c in ALL_COLUMNS)}) VALUES ({placeholders})'
        cursor.execute(insert_query, values)
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar o produto '{product_data.get('Produto')}' no banco de dados: {e}")
        return False

def get_soup(url):
    """Faz uma requisição para a URL com lógica de retentativa para erros 429."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retries += 1
                logging.warning(f"Erro 429 em {url}. Tentativa {retries}/{MAX_RETRIES}. Aguardando {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                logging.error(f"Erro HTTP {e.response.status_code} em {url}: {e}")
                return None
        except requests.exceptions.RequestException as e:
            retries += 1
            logging.warning(f"Erro de rede em {url}: {e}. Tentativa {retries}/{MAX_RETRIES}. Aguardando 10s...")
            time.sleep(10)
    logging.error(f"FALHA FINAL: Não foi possível acessar a URL {url} após {MAX_RETRIES} tentativas.")
    return None

def scrape_product_details(product_url):
    """Extrai todos os detalhes nutricionais e mapeia os nomes para as colunas do DB."""
    soup = get_soup(product_url)
    if not soup: return None
    details_raw, details_mapped = {}, {}
    nutrition_facts_div = soup.find('div', class_='nutrition_facts international')
    if not nutrition_facts_div: return None
    details_raw['Porção'] = nutrition_facts_div.find('div', class_='serving_size_value').get_text(strip=True) if nutrition_facts_div.find('div', class_='serving_size_value') else 'N/A'
    nutrient_divs = nutrition_facts_div.find_all('div', class_='nutrient')
    last_label = ''
    for div in nutrient_divs:
        if 'left' in div.get('class', []):
            label_text = div.get_text(strip=True)
            if label_text: last_label = label_text
        elif 'right' in div.get('class', []):
            value_text = div.get_text(strip=True)
            if last_label == 'Energia':
                if 'kcal' in value_text: details_raw['Energia (kcal)'] = value_text
                elif 'kj' in value_text: details_raw['Energia (kj)'] = value_text
            elif last_label:
                details_raw[last_label] = value_text
                last_label = ''
    for key, value in details_raw.items():
        if key in COLUMN_MAP: details_mapped[COLUMN_MAP[key]] = value
    time.sleep(1)
    return details_mapped

def main():
    """Função principal que orquestra todo o processo."""
    logging.info("==========================================================")
    logging.info("=== INICIANDO SCRIPT DE SCRAPING - VERSÃO FINAL OTIMIZADA ===")
    logging.info("==========================================================")

    conn = setup_database()
    if not conn: return

    letters_to_scrape = list(string.ascii_lowercase) + ['*']
    unique_manufacturers = set()
    logging.info("--- ETAPA 1: Coletando a lista de todos os fabricantes ---")
    for letter in letters_to_scrape:
        page = 0
        while True:
            brands_url = f"{BASE_URL}/Default.aspx?pa=brands&f={letter}&t=1&pg={page}"
            soup = get_soup(brands_url)
            if not soup: break
            manufacturers_on_page = soup.select('td.leftCell h2 > a')
            if not manufacturers_on_page: break
            for tag in manufacturers_on_page: unique_manufacturers.add(tag.get_text(strip=True))
            time.sleep(2)
            page += 1
    logging.info(f"--- ETAPA 1 CONCLUÍDA: {len(unique_manufacturers)} fabricantes únicos encontrados. ---")

    logging.info("--- ETAPA 2: Iniciando a coleta e salvamento de produtos no banco de dados. ---")
    products_scraped_count, error_count = 0, 0
    
    for i, manufacturer in enumerate(sorted(list(unique_manufacturers)), 1):
        logging.info(f"PROCESSANDO FABRICANTE {i}/{len(unique_manufacturers)}: '{manufacturer}'")
        page = 0
        
        # --- NOVO: Contador para otimização da paginação ---
        consecutive_other_brands_count = 0
        
        while True:
            query = urllib.parse.quote_plus(manufacturer)
            search_url = f"{BASE_URL}/calorias-nutrição/search?q={query}&pg={page}"
            soup = get_soup(search_url)
            if not soup: break
            
            product_rows = soup.select('table.searchResult tr')
            if not product_rows: break
            
            found_target_brand_on_page = False # Flag para verificar se a página teve algum resultado útil

            for row in product_rows:
                link = row.select_one('a.prominent')
                if not link: continue

                try:
                    brand_tag = row.select_one('a.brand')
                    if not brand_tag: continue

                    brand_on_page = brand_tag.get_text(strip=True).strip('()')

                    # Compara a marca encontrada com a marca alvo
                    if brand_on_page.strip().lower() == manufacturer.strip().lower():
                        # MARCA CORRETA: Zera o contador e processa o produto
                        consecutive_other_brands_count = 0
                        found_target_brand_on_page = True # Marca a página como útil
                        
                        product_name = link.get_text(strip=True)
                        product_url = BASE_URL + link['href']
                        
                        product_details = scrape_product_details(product_url)
                        if product_details:
                            product_details['Fabricante'] = manufacturer
                            product_details['Produto'] = product_name
                            if save_to_db(conn, product_details):
                                products_scraped_count += 1
                                logging.info(f"    SALVO: '{product_name}'")
                            else: error_count += 1
                    else:
                        # MARCA INCORRETA: Incrementa o contador
                        consecutive_other_brands_count += 1
                        logging.info(f"    IGNORANDO: Produto da marca '{brand_on_page}'. Contagem de outras marcas: {consecutive_other_brands_count}")
                
                except Exception as e:
                    error_count += 1
                    logging.error(f"    ERRO INESPERADO ao processar uma linha. Erro: {e}")
            
            # --- NOVO: Lógica de parada antecipada ---
            # Se o contador atingir o limite, para de paginar para este fabricante.
            if consecutive_other_brands_count >= CONSECUTIVE_OTHERS_LIMIT:
                logging.info(f"  OTIMIZAÇÃO: Parando a busca para '{manufacturer}', pois {consecutive_other_brands_count} produtos de outras marcas foram encontrados em sequência.")
                break # Sai do loop 'while True'

            # Se a página inteira foi processada e não encontramos NENHUM produto da marca alvo,
            # é seguro parar a paginação também.
            if not found_target_brand_on_page and page > 0:
                 logging.info(f"  OTIMIZAÇÃO: Nenhuma produto de '{manufacturer}' encontrado na página {page+1}. Parando a busca.")
                 break

            time.sleep(2)
            page += 1
    
    logging.info("--- ETAPA 2 CONCLUÍDA: Coleta de dados finalizada. ---")
    
    conn.close()
    
    logging.info("==========================================")
    logging.info("========= RESUMO DA EXECUÇÃO =========")
    logging.info(f"Fabricantes únicos processados: {len(unique_manufacturers)}")
    logging.info(f"Produtos salvos no banco de dados: {products_scraped_count}")
    logging.info(f"Erros encontrados: {error_count}")
    logging.info(f"Dados estão no arquivo: '{DB_NAME}'")
    logging.info("==========================================")
    logging.info("SCRIPT FINALIZADO.")

if __name__ == "__main__":
    main()