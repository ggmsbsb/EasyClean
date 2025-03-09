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

def clean_dataframe(df, columns_to_remove=None):
    # Remover diacríticos dos nomes das colunas
    df.columns = [remove_diacritico(col) for col in df.columns]
    
    # Remover espaços em branco extras e converter para minúsculas
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Remover duplicatas
    df.drop_duplicates(inplace=True)
    
    # Tratar valores ausentes
    for col in df.columns:
        if df[col].dtype == 'float64' or df[col].dtype == 'int64':
            mean_value = df[col].mean()
            df[col] = df[col].apply(lambda x: mean_value if pd.isna(x) else x)
        elif df[col].dtype == 'object':
            mode_value = df[col].mode()[0]
            df[col] = df[col].apply(lambda x: mode_value if pd.isna(x) else x)
    
    # Remover acentos e caracteres especiais
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: remove_diacritico(x) if isinstance(x, str) else x)
        df[col] = df[col].str.replace(r'[^\w\s]', '', regex=True).str.strip().str.lower()
    
    if columns_to_remove:
        columns_to_remove = [col for col in columns_to_remove if col in df.columns]
        df.drop(columns=columns_to_remove, inplace=True)
    
    return df

def get_columns(df):
    return df.columns.tolist()