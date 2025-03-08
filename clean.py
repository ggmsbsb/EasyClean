import os
import pandas as pd
import unicodedata

def arquivos_diretorio(directory):
    files_list = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            files_list.append(filename)
    return files_list

def remove_diacritico(text):
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Função para converter colunas de data em padrões conhecidos
def convert_date_columns(df, date_format):
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='raise').dt.strftime(date_format)
        except (ValueError, TypeError):
            continue
    return df

def clean_dataframe(df, columns_to_remove=None, date_format=None):
    # Remover diacríticos
    df.columns = [remove_diacritico(col) for col in df.columns]
    
    # Remover espaços em branco e converter para minúsculas
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Remover duplicatas
    df.drop_duplicates(inplace=True)
    
    # Tratar valores ausentes
    total_entries = len(df)
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_percentage = (missing_count / total_entries) * 100
        
        if missing_percentage > 5:
            if df[col].dtype == 'float64' or df[col].dtype == 'int64':
                df[col] = df[col].fillna(df[col].mean())  # Média 
            elif df[col].dtype == 'object':
                df[col] = df[col].fillna(df[col].mode()[0])  # Moda
        else:
            # Remover linhas com menos de 5% de dados preenchidos
            df = df.dropna(subset=[col], thresh=int(0.95 * total_entries)) 

    # Remover acentos e caracteres especiais
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: remove_diacritico(x) if isinstance(x, str) else x)
        df[col] = df[col].str.replace(r'[^\w\s]', '', regex=True).str.strip().str.lower()
    
    if columns_to_remove:
        columns_to_remove = [col for col in columns_to_remove if col in df.columns]
        df.drop(columns=columns_to_remove, inplace=True)
    
    # Converter colunas de data
    if date_format:
        df = convert_date_columns(df, date_format)
    
    return df

def get_columns(df):
    return df.columns.tolist()