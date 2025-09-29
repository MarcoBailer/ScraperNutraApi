import pandas as pd
import sqlite3
import os

# Pega o caminho absoluto da pasta onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- CONFIGURAÇÃO CORRIGIDA ---
# Nome do arquivo Excel de entrada
XLSX_ENTRADA = 'tbca_dados_alimentos_pivot.xlsx'

# Nome da aba (planilha) dentro do arquivo Excel
NOME_DA_ABA = 'Sheet1'

# Cria o caminho completo para o arquivo Excel
XLSX_CAMINHO_COMPLETO = os.path.join(script_dir, XLSX_ENTRADA)

# Nome do novo arquivo de banco de dados que será criado
DB_SAIDA = 'tbca_alimentos.db'
DB_CAMINHO_COMPLETO = os.path.join(script_dir, DB_SAIDA)

# Nome da tabela que será criada dentro do banco de dados
NOME_DA_TABELA = 'alimentos'

def converter_excel_para_sqlite():
    """
    Lê uma aba de um arquivo Excel (.xlsx) e a converte para uma tabela 
    em um banco de dados SQLite.
    """
    print(f"Iniciando a conversão de '{XLSX_ENTRADA}' (Aba: '{NOME_DA_ABA}') para '{DB_SAIDA}'...")

    # --- Validação do arquivo de entrada ---
    if not os.path.exists(XLSX_CAMINHO_COMPLETO):
        print(f"ERRO: O arquivo '{XLSX_ENTRADA}' não foi encontrado.")
        print(f"Por favor, certifique-se de que o script e o arquivo Excel estão na mesma pasta: '{script_dir}'")
        return

    try:
        # --- ETAPA 1: Ler a aba do arquivo Excel com pandas ---
        print(f"Lendo o arquivo Excel... (Isso pode levar um momento)")
        # A função agora é pd.read_excel, especificando a aba
        df = pd.read_excel(XLSX_CAMINHO_COMPLETO, sheet_name=NOME_DA_ABA)
        print(f"-> {len(df)} linhas lidas com sucesso.")
        print(f"-> Colunas encontradas: {', '.join(df.columns)}")

        # --- ETAPA 2: Limpeza dos nomes das colunas (Opcional, mas recomendado) ---
        print("\nLimpando nomes das colunas para serem compatíveis com SQL...")
        colunas_limpas = {col: str(col).replace(' ', '_').replace('(', '').replace(')', '').replace(',', '') for col in df.columns}
        df.rename(columns=colunas_limpas, inplace=True)
        print(f"-> Novos nomes de colunas: {', '.join(df.columns)}")

        # --- ETAPA 3: Salvar o DataFrame no banco de dados SQLite ---
        print(f"\nCriando e populando o banco de dados '{DB_SAIDA}'...")
        if os.path.exists(DB_CAMINHO_COMPLETO):
            os.remove(DB_CAMINHO_COMPLETO)
            print(f"-> Arquivo de banco de dados antigo '{DB_SAIDA}' removido.")
            
        conn = sqlite3.connect(DB_CAMINHO_COMPLETO)
        
        df.to_sql(NOME_DA_TABELA, conn, index=False, if_exists='replace')
        
        conn.close()

        print("\n-------------------------------------------------")
        print("PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"Os dados do Excel foram salvos no arquivo: {DB_SAIDA}")
        print(f"Dentro do banco, os dados estão na tabela: '{NOME_DA_TABELA}'")
        print("-------------------------------------------------")

    except Exception as e:
        print(f"\nOcorreu um erro durante o processo: {e}")

if __name__ == '__main__':
    converter_excel_para_sqlite()