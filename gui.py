import os
import tkinter as tk
from tkinter import (
    MULTIPLE,
    BooleanVar,
    Button,
    Checkbutton,
    LabelFrame,
    Listbox,
    Toplevel,
    filedialog,
    messagebox,
)

import pandas as pd

from clean import arquivos_diretorio, clean_dataframe, get_columns


class DatasetCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EZClean")

        self.label = tk.Label(root, text="Selecione o diretório do dataset:")
        self.label.pack(pady=10)

        self.path_label = tk.Label(root, text="", fg="blue")
        self.path_label.pack(pady=5)

        self.browse_button = tk.Button(
            root, text="Selecionar Diretório", command=self.browse_directory
        )
        self.browse_button.pack(pady=10)

        # Checkbox para ignorar valores ausentes
        self.skip_missing_values = BooleanVar(value=False)
        self.skip_missing_checkbox = Checkbutton(
            root,
            text="Pular tratamento de valores ausentes",
            variable=self.skip_missing_values,
        )
        self.skip_missing_checkbox.pack(pady=5)

        self.clean_button = tk.Button(
            root, text="Limpar Datasets", command=self.clean_datasets
        )
        self.clean_button.pack(pady=10)

        self.directory_path = ""
        self.columns_to_remove = {}

    def browse_directory(self):
        # Seleciona o diretório
        self.directory_path = filedialog.askdirectory()
        self.path_label.config(text=self.directory_path)

    def select_columns(self, dataframes):
        # Janela para selecionar colunas a remover
        top = Toplevel(self.root)
        top.title("Selecione as colunas para remover")

        # Adiciona área com scroll
        frame = tk.Frame(top)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        listbox_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=listbox_frame, anchor="nw")

        listboxes = {}

        for filename, df in dataframes.items():
            # Cria lista de colunas para cada arquivo
            columns = get_columns(df)
            frame = LabelFrame(listbox_frame, text=filename)
            frame.pack(fill="both", expand="yes", padx=10, pady=10)

            listbox = Listbox(frame, selectmode=MULTIPLE, exportselection=False)
            for col in columns:
                listbox.insert(tk.END, col)
            listbox.pack(pady=10)

            listboxes[filename] = listbox

        def on_confirm():
            # Salva colunas selecionadas
            for filename, listbox in listboxes.items():
                selected_indices = listbox.curselection()
                self.columns_to_remove[filename] = [
                    listbox.get(i) for i in selected_indices
                ]

            top.destroy()
            self.execute_cleaning(dataframes)

        confirm_button = Button(top, text="Confirmar", command=on_confirm)
        confirm_button.pack(pady=10)

def clean_datasets(self):
    # Limpa os datasets
    if not self.directory_path:
        messagebox.showerror("Erro", "Por favor, selecione um diretório primeiro.")
        return

    files_list = arquivos_diretorio(self.directory_path)
    dataframes = {}

    for filename in files_list:
        file_path = os.path.join(self.directory_path, filename)
        try:
            if filename.endswith(".csv"):
                # Use 'utf-8-sig' para CSV com byte order mark
                df = pd.read_csv(
                    file_path, encoding="utf-8-sig", delimiter=";", on_bad_lines="skip"
                )
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                print(f"Formato de arquivo não suportado: {filename}")
                continue
            dataframes[filename] = df
            print(f"Dataset {filename} carregado corretamente.")
        except Exception as e:
            print(f"Erro ao carregar o dataset {filename}: {e}")

    if dataframes:
        self.select_columns(dataframes)

def execute_cleaning(self, dataframes):
    # Executa a limpeza dos datasets
    skip_missing = self.skip_missing_values.get()
    for filename, df in dataframes.items():
        columns_to_remove = self.columns_to_remove.get(filename, [])
        df = clean_dataframe(
            df, columns_to_remove, skip_missing_values=skip_missing
        )
        if filename.endswith(".csv"):
            df.to_csv(
                os.path.join(self.directory_path, filename),
                index=False,
                encoding="utf-8",
                sep=";",
            )
        elif filename.endswith(".xlsx"):
            df.to_excel(os.path.join(self.directory_path, filename), index=False)
        print(f"Dataset {filename} limpo e salvo.")

    messagebox.showinfo("Sucesso", "Datasets limpos e salvos com sucesso.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetCleanerApp(root)
    root.mainloop()
