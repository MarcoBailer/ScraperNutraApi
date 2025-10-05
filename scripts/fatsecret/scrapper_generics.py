import requests
from bs4 import BeautifulSoup
import time
import string
import urllib.parse
import logging
import sys
import sqlite3

# --- 1. CONFIGURAÇÃO DA COLETA ---
# Opções válidas: 'fabricante', 'fastfood', 'generico'
TIPO_DE_COLETA = 'generico'

# --- 2. CONFIGURAÇÃO DO LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("scraping.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- 3. CONSTANTES E CONFIGURAÇÕES GLOBAIS ---
BASE_URL = "https://www.fatsecret.com.br"
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 30
CONSECUTIVE_OTHERS_LIMIT = 5

ALL_COLUMNS_MARCAS = [
    'Fabricante', 'Produto', 'Porcao', 'Energia_kcal', 'Energia_kj', 'Proteinas', 
    'Carboidratos', 'Acucar', 'Gorduras', 'Gordura_Saturada', 'Gordura_Poliinsaturada', 
    'Gordura_Monoinsaturada', 'Gordura_Trans', 'Colesterol', 'Fibras', 'Sodio', 'Potassio'
]
ALL_COLUMNS_GENERICO = [
    'Categoria_Principal', 'Sub_Categoria', 'Produto', 'Porcao', 'Energia_kcal', 'Energia_kj', 
    'Proteinas', 'Carboidratos', 'Acucar', 'Gorduras', 'Gordura_Saturada', 'Gordura_Poliinsaturada', 
    'Gordura_Monoinsaturada', 'Gordura_Trans', 'Colesterol', 'Fibras', 'Sodio', 'Potassio'
]

COLUMN_MAP = {
    'Porção': 'Porcao', 'Energia (kcal)': 'Energia_kcal', 'Energia (kj)': 'Energia_kj',
    'Proteínas': 'Proteinas', 'Carboidratos': 'Carboidratos', 'Açúcar': 'Acucar', 
    'Gorduras': 'Gorduras', 'Gordura Saturada': 'Gordura_Saturada', 
    'Gordura Poliinsaturada': 'Gordura_Poliinsaturada', 'Gordura Monoinsaturada': 'Gordura_Monoinsaturada',
    'Gordura Trans': 'Gordura_Trans', 'Colesterol': 'Colesterol', 'Fibras': 'Fibras',
    'Sódio': 'Sodio', 'Potássio': 'Potassio'
}

def setup_database(db_name, columns):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        columns_sql = ", ".join([f'"{col}" TEXT' for col in columns])
        create_table_query = f'CREATE TABLE IF NOT EXISTS dados ({columns_sql})'
        cursor.execute(create_table_query)
        conn.commit()
        logging.info(f"Banco de dados '{db_name}' e tabela 'dados' prontos para uso.")
        return conn
    except Exception as e:
        logging.critical(f"NÃO FOI POSSÍVEL INICIAR O BANCO DE DADOS. Erro: {e}")
        return None

def save_to_db(conn, product_data, columns):
    try:
        cursor = conn.cursor()
        values = [product_data.get(col) for col in columns]
        placeholders = ", ".join(["?" for _ in columns])
        insert_query = f'INSERT INTO dados ({", ".join(f"`{c}`" for c in columns)}) VALUES ({placeholders})'
        cursor.execute(insert_query, values)
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar o produto '{product_data.get('Produto')}' no banco de dados: {e}")
        return False

def get_soup(url):
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

def run_brands_scraper(conn, parametro_t, tipo_str):
    """Lógica de scraping para Fabricantes e Fast Food."""
    # (Esta função permanece inalterada)
    letters_to_scrape = list(string.ascii_lowercase) + ['*']
    unique_manufacturers = set()
    logging.info(f"--- ETAPA 1: Coletando a lista de todos os {tipo_str} ---")
    for letter in letters_to_scrape:
        page = 0
        while True:
            brands_url = f"{BASE_URL}/Default.aspx?pa=brands&f={letter}&t={parametro_t}&pg={page}"
            soup = get_soup(brands_url)
            if not soup: break
            manufacturers_on_page = soup.select('td.leftCell h2 > a')
            if not manufacturers_on_page: break
            for tag in manufacturers_on_page: unique_manufacturers.add(tag.get_text(strip=True))
            time.sleep(2)
            page += 1
    logging.info(f"--- ETAPA 1 CONCLUÍDA: {len(unique_manufacturers)} {tipo_str} únicos encontrados. ---")
    logging.info("--- ETAPA 2: Iniciando a coleta e salvamento de produtos no banco de dados. ---")
    products_scraped_count, error_count = 0, 0
    for i, manufacturer in enumerate(sorted(list(unique_manufacturers)), 1):
        logging.info(f"PROCESSANDO {i}/{len(unique_manufacturers)}: '{manufacturer}'")
        page, consecutive_other_brands_count = 0, 0
        while True:
            query = urllib.parse.quote_plus(manufacturer)
            search_url = f"{BASE_URL}/calorias-nutrição/search?q={query}&pg={page}"
            soup = get_soup(search_url)
            if not soup: break
            product_rows, found_target_brand_on_page = soup.select('table.searchResult tr'), False
            if not product_rows: break
            for row in product_rows:
                link = row.select_one('a.prominent')
                if not link: continue
                try:
                    brand_tag = row.select_one('a.brand')
                    if not brand_tag: continue
                    brand_on_page = brand_tag.get_text(strip=True).strip('()')
                    if brand_on_page.strip().lower() == manufacturer.strip().lower():
                        consecutive_other_brands_count, found_target_brand_on_page = 0, True
                        product_name = link.get_text(strip=True)
                        product_url = BASE_URL + link['href']
                        product_details = scrape_product_details(product_url)
                        if product_details:
                            product_details['Fabricante'] = manufacturer
                            product_details['Produto'] = product_name
                            if save_to_db(conn, product_details, ALL_COLUMNS_MARCAS):
                                products_scraped_count += 1
                                logging.info(f"    SALVO: '{product_name}'")
                            else: error_count += 1
                    else:
                        consecutive_other_brands_count += 1
                except Exception as e:
                    error_count += 1
                    logging.error(f"    ERRO INESPERADO ao processar uma linha. Erro: {e}")
            if consecutive_other_brands_count >= CONSECUTIVE_OTHERS_LIMIT: break
            if not found_target_brand_on_page and page > 0: break
            time.sleep(2)
            page += 1
    return len(unique_manufacturers), products_scraped_count, error_count

def run_generic_scraper(conn):
    """Lógica de scraping aprimorada para Alimentos Genéricos."""
    products_scraped_count, error_count = 0, 0
    
    logging.info("--- ETAPA 1: Coletando as categorias principais ---")
    main_page_url = f"{BASE_URL}/calorias-nutrição/"
    soup = get_soup(main_page_url)
    if not soup: return 0, 0, 1

    main_categories = [{"name": link.get_text(strip=True), "url": BASE_URL + link['href']} for link in soup.select('table.generic.common a.prominent')]
    logging.info(f"--- ETAPA 1 CONCLUÍDA: {len(main_categories)} categorias principais encontradas. ---")

    for i, category in enumerate(main_categories, 1):
        logging.info(f"PROCESSANDO CATEGORIA {i}/{len(main_categories)}: '{category['name']}'")
        soup_cat = get_soup(category['url'])
        if not soup_cat: continue

        sub_group_headers = soup_cat.select('div.secHolder h2')
        for h2_tag in sub_group_headers:
            sub_group_name = h2_tag.get_text(strip=True)
            logging.info(f"  --> Iniciando busca por sub-grupo: '{sub_group_name}'")
            
            page = 0
            while True:
                query = urllib.parse.quote_plus(sub_group_name)
                search_url = f"{BASE_URL}/calorias-nutrição/search?q={query}&pg={page}"
                logging.info(f"      Buscando na página {page + 1} de resultados...")
                
                soup_search = get_soup(search_url)
                if not soup_search: break

                product_rows = soup_search.select('table.searchResult td.borderBottom')
                if not product_rows:
                    logging.info("      Nenhum resultado encontrado nesta página. Finalizando busca para este sub-grupo.")
                    break

                for row in product_rows:
                    try:
                        brand_tag = row.select_one('a.brand')
                        # Se existe uma marca, ignora este item
                        if brand_tag:
                            logging.info(f"          IGNORANDO (com marca): '{row.select_one('a.prominent').get_text(strip=True)}'")
                            continue
                        
                        # Se não tem marca, é um alimento genérico que queremos
                        link = row.select_one('a.prominent')
                        if not link: continue

                        product_name = link.get_text(strip=True)
                        product_url = BASE_URL + link['href']
                        
                        product_details = scrape_product_details(product_url)
                        if product_details:
                            product_details['Categoria_Principal'] = category['name']
                            product_details['Sub_Categoria'] = sub_group_name
                            product_details['Produto'] = product_name

                            if save_to_db(conn, product_details, ALL_COLUMNS_GENERICO):
                                products_scraped_count += 1
                                logging.info(f"          SALVO: '{product_name}' (Porção: {product_details.get('Porcao')})")
                            else: error_count += 1
                    except Exception as e:
                        error_count += 1
                        logging.error(f"          ERRO INESPERADO ao processar item. Erro: {e}")
                
                # Verifica se há um link para a "próxima" página para continuar a paginação
                next_link = soup_search.select_one('span.next > a')
                if not next_link:
                    break # Sai do loop while se não houver mais páginas
                
                time.sleep(2)
                page += 1
    
    return len(main_categories), products_scraped_count, error_count

def main():
    """Função principal que seleciona qual scraper rodar."""
    # (Esta função permanece inalterada)
    if TIPO_DE_COLETA in ['fabricante', 'fastfood']:
        if TIPO_DE_COLETA == 'fastfood':
            parametro_t, db_name, tipo_str = '2', "fastfood.db", "Restaurantes/Fast Food"
        else:
            parametro_t, db_name, tipo_str = '1', "alimentos.db", "Fabricantes de Alimentos"
        logging.info(f"=== INICIANDO SCRAPING - MODO: {tipo_str.upper()} ===")
        conn = setup_database(db_name, ALL_COLUMNS_MARCAS)
        if not conn: return
        entities_count, products_count, error_count = run_brands_scraper(conn, parametro_t, tipo_str)
        entity_label = "Entidades"
    elif TIPO_DE_COLETA == 'generico':
        db_name, tipo_str = "genericos.db", "Alimentos Genéricos"
        logging.info(f"=== INICIANDO SCRAPING - MODO: {tipo_str.upper()} ===")
        conn = setup_database(db_name, ALL_COLUMNS_GENERICO)
        if not conn: return
        entities_count, products_count, error_count = run_generic_scraper(conn)
        entity_label = "Categorias Principais"
    else:
        logging.error(f"TIPO_DE_COLETA '{TIPO_DE_COLETA}' inválido.")
        return

    if conn: conn.close()
    
    logging.info("==========================================")
    logging.info("========= RESUMO DA EXECUÇÃO =========")
    logging.info(f"Tipo de coleta: {tipo_str}")
    logging.info(f"{entity_label} processadas: {entities_count}")
    logging.info(f"Itens salvos no banco de dados: {products_count}")
    logging.info(f"Erros encontrados: {error_count}")
    logging.info(f"Dados estão no arquivo: '{db_name}'")
    logging.info("==========================================")
    logging.info("SCRIPT FINALIZADO.")

if __name__ == "__main__":
    main()