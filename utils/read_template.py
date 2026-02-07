

def read_template(file_path:str):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Arquivo de template não encontrado: {file_path}")
        raise
    except Exception as e:
        print(f"Erro ao ler o template: {e}")
        raise