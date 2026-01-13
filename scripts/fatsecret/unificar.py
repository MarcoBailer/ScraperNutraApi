import sqlite3
import pandas as pd
import os

# --- CONFIGURAÇÃO CENTRALIZADA ---
# C:\Users\maico\source\repos\FoodDataApi\scripts\fatsecret\db\fabricantes_alimentos.db
FONTES_DE_DADOS = [
    {
        "arquivo_origem": "./db/fabricantes_alimentos.db",
        "tabela_origem": "alimentos",
        "tabela_destino": "fabricantes"
    },
    {
        "arquivo_origem": "./db/restaurante_fastfood_alimentos.db",
        "tabela_origem": "alimentos",
        "tabela_destino": "fast_food"
    },
    {
        "arquivo_origem": "./db/tbca_alimentos.db",
        "tabela_origem": "alimentos",
        "tabela_destino": "tbca"
    },
    {
        "arquivo_origem": "./db/genericos.db",
        "tabela_origem": "dados",
        "tabela_destino": "genericos"
    }
]

DB_UNIFICADO = 'alimentos.db'


def verificar_se_tabela_existe(conn, nome_tabela):
    """Verifica se uma tabela já existe no banco de dados conectado."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
    resultado = cursor.fetchone()
    return resultado is not None

def unificar_bancos_de_dados():
    """
    Lê uma lista de fontes de dados e as insere como tabelas separadas em um
    banco de dados unificado, verificando se as tabelas já existem.
    """
    print(f"Iniciando o processo de unificação para o banco de dados '{DB_UNIFICADO}'...")

    try:
        # Conecta-se ao banco de dados unificado (ou o cria se não existir)
        conn_unificado = sqlite3.connect(DB_UNIFICADO)

        # Itera sobre cada fonte de dados definida na configuração
        for fonte in FONTES_DE_DADOS:
            arquivo_origem = fonte["arquivo_origem"]
            tabela_origem = fonte["tabela_origem"]
            tabela_destino = fonte["tabela_destino"]
            
            print(f"\n--- Processando: '{arquivo_origem}' -> Tabela '{tabela_destino}' ---")

            # --- Validação do arquivo de origem ---
            if not os.path.exists(arquivo_origem):
                print(f"AVISO: O arquivo de origem '{arquivo_origem}' não foi encontrado. Pulando.")
                continue

            # --- Verificação se a tabela de destino já existe ---
            if verificar_se_tabela_existe(conn_unificado, tabela_destino):
                print(f"INFO: A tabela '{tabela_destino}' já existe no banco unificado. Nenhuma ação necessária.")
                continue
            
            # Se a tabela não existe, procede com a inserção
            print(f"A tabela '{tabela_destino}' não existe. Adicionando...")
            
            conn_origem = sqlite3.connect(arquivo_origem)
            
            # Lê os dados da tabela de origem para um DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {tabela_origem}", conn_origem)
            conn_origem.close()
            
            # Escreve o DataFrame na nova tabela no banco unificado
            df.to_sql(tabela_destino, conn_unificado, index=False, if_exists='append')
            print(f"-> SUCESSO: {len(df)} registros adicionados à tabela '{tabela_destino}'.")

        conn_unificado.close()

        print("\n-------------------------------------------------")
        print("PROCESSO DE UNIFICAÇÃO CONCLUÍDO!")
        print(f"O banco de dados '{DB_UNIFICADO}' está atualizado.")
        print("-------------------------------------------------")

    except Exception as e:
        print(f"\nOcorreu um erro durante o processo: {e}")

if __name__ == '__main__':
    unificar_bancos_de_dados()