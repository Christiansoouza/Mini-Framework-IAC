

def read_json_file(file_path: str) -> dict:
    """Lê um arquivo JSON e retorna seu conteúdo como um dicionário."""
    import json
    with open(file_path, "r") as file:
        data = json.load(file)
    return data