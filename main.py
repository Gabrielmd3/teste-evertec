import zipfile
import pandas as pd
from pathlib import Path
import sqlite3
from typing import Any

def descompact(zip_name: str = 'dados 1.zip', extract_folder: str = './data_extracted') -> Path:
    """Descompacta o arquivo zip no diretório especificado, se necessário.."""
    caminho_zip = Path(zip_name)
    destiny_folder = Path(extract_folder)
    destiny_folder.mkdir(parents=True, exist_ok=True)

    if not caminho_zip.exists():
        print(f"Erro: O arquivo {zip_name} não foi encontrado.")
        return destiny_folder

    # Descompacta somente se os arquivos CSV ainda não estiverem lá
    origem_file = destiny_folder / "origem-dados.csv"
    tipos_file = destiny_folder / "tipos.csv"
    if not origem_file.exists() or not tipos_file.exists():
        print("Arquivos ausentes. Iniciando descompactação...")
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall(destiny_folder)
            print(f"Arquivos extraídos com sucesso em: {destiny_folder}")
    else:
        print(f"Arquivos já descompactados em: {destiny_folder}")
        
    return destiny_folder


def read_files(folder: Path) -> pd.DataFrame:
    """Lê os CSVs, filtra, ordena e faz o merge dos dados."""
    origem_dados_file = folder / "origem-dados.csv"
    tipos_file = folder / "tipos.csv"
    
    # Processamento do arquivo de origem
    df_origem_dados = pd.read_csv(origem_dados_file)
    df_filtrado = df_origem_dados[df_origem_dados['status'] == 'CRITICO'].copy()
    df_filtrado['created_at'] = pd.to_datetime(df_filtrado['created_at'])
    df_ordenado = df_filtrado.sort_values(by='created_at', ascending=True)
    
    # Processamento e Merge com o arquivo de tipos
    df_tipos = pd.read_csv(tipos_file)
    df_final = pd.merge(left=df_ordenado, right=df_tipos, how='left', left_on='tipo', right_on='id')
    
    # Limpeza e renomeação
    df_final = df_final.drop(columns=['id'])
    df_final.rename(columns={'nome': 'nome_tipo'}, inplace=True)
    
    return df_final


def format_data(value: Any) -> str:
    """Formata valores individuais para o padrão de query SQL."""
    if pd.isna(value):
        return "NULL"
    elif isinstance(value, (int, float, bool)):
        return str(value)
    else:
        text_value = str(value).replace("'", "''")
        return f"'{text_value}'"


def create_sql_inserts(df: pd.DataFrame, folder_name: str = "database") -> Path:
    """Gera um arquivo .sql com os comandos de INSERT a partir do DataFrame."""
    table_name = "dados_finais"
    sql_file_path = Path(folder_name) / "insert-dados.sql"
    sql_file_path.parent.mkdir(parents=True, exist_ok=True)
    sql_columns = ", ".join(df.columns)

    with open(sql_file_path, 'w', encoding='utf-8') as file:
        for _, row in df.iterrows():
            format_values = [format_data(v) for v in row]
            sql_values = ", ".join(format_values)
            query = f"INSERT INTO {table_name} ({sql_columns}) VALUES ({sql_values});\n"
            file.write(query)
            
    print(f"Arquivo SQL gerado com sucesso em: {sql_file_path}")
    return sql_file_path


def created_sql_table(sql_file_path: Path) -> Path:
    """Cria o banco de dados SQLite e executa o script de inserts."""
    db_path = Path('database/database.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Criação da tabela garantindo que as colunas batam com as inseridas
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS dados_finais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME,
        product_code TEXT,
        customer_code TEXT,
        status TEXT,
        tipo INTEGER,
        nome_tipo TEXT
    );
    ''')

    with open(sql_file_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()
        
    print('Inserindo dados no banco...')
    cursor.executescript(sql_script)
    connection.commit()
    connection.close()
    
    print(f"DATABASE CREATED WITH SUCCESS IN: {db_path.absolute()}")
    return db_path


def quantity_items_by_type(db_path: Path) -> None:
    """Executa a query de agrupamento e exibe o resultado."""
    connection = sqlite3.connect(db_path)

    query = """
    SELECT DATE(created_at) as date,
           nome_tipo as type_name,
           COUNT(*) as quantity
    FROM dados_finais
    GROUP BY DATE(created_at), nome_tipo
    ORDER BY date ASC, quantity DESC;
    """
    
    df_results = pd.read_sql_query(query, connection)
    print("\n--- Relatório de Itens por Dia e Tipo ---")
    print(df_results)
    
    connection.close()


def main():
    folder = descompact()
    # Verifica se a extração ocorreu antes de tentar ler
    if (folder / "origem-dados.csv").exists():
        df = read_files(folder)
        sql_file_path = create_sql_inserts(df)
        db_path = created_sql_table(sql_file_path)
        quantity_items_by_type(db_path)

if __name__ == "__main__":
    main()