from fastapi import FastAPI, HTTPException
import pandas as pd
from pathlib import Path
from main import descompact

app = FastAPI(
    title="API de Tipos",
    description="Retorna o nome do tipo baseado no ID fornecido."
)

csv_path = Path('./data_extracted/tipos.csv')
dict_types = {}

def data_prepare():
    """Garante que os dados existam e os carrega para a memória."""
    global dict_types

    if not csv_path.exists():
        print("CSV file not founded by API. Extracting ZIP...")
        descompact()
    
    if csv_path.exists():
        df_tipos = pd.read_csv(csv_path)
        dict_types = pd.Series(df_tipos['nome'].values, index=df_tipos['id']).to_dict()
        print("Data loaded on memory with success!")
    else:
        print(f"CRITICAL ERROR: THE FILE {csv_path} COULD NOT BE GENERATED. VERIFY ZIP FILE")

data_prepare()

@app.get("/tipos/{tipo_id}")
def get_type_by_id(tipo_id: int):
    """
    Recebe um ID de tipo na URL e retorna o nome correspondente.
    """
    type_name = dict_types.get(tipo_id)

    if type_name:
        return{"id": tipo_id, "tipo": type_name}
    else:
        raise HTTPException(status_code=404, detail="Type not founded in the file")
