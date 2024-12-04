import os
import pandas as pd
from typing import List
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging


LOG_FILE = "app.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CSV_FILE_PATH = "db.csv"

class Carro(BaseModel):
    placa: str
    cor: str
    modelo: str
    ano: int
    marca: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    global dados
    # Quando o servidor iniciar, ler os dados do CSV
    try:
        if os.path.exists(CSV_FILE_PATH):
            dados = pd.read_csv(CSV_FILE_PATH)
        else:
            dados = pd.DataFrame(columns=["placa", "cor", "modelo", "ano", "marca"])
            logging.info("Arquivo CSV não encontrado. Um novo será criado ao adicionar o primeiro carro.")
    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo CSV: {e}")
        dados = pd.DataFrame(columns=["placa", "cor", "modelo", "ano", "marca"])

    yield

    # Opcional: Salvar os dados no CSV ao desligar o servidor
    try:
        dados.to_csv(CSV_FILE_PATH, index=False)
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo CSV: {e}")


app = FastAPI(lifespan=lifespan)


@app.post("/adicionar/", response_model=Carro, status_code=HTTPStatus.CREATED)
def adicionar_carro(carro: Carro):
    global dados

    # Verificar se o carro já existe
    if not dados[dados['placa'] == carro.placa].empty:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Carro já existe.")

    # Adicionar o carro ao DataFrame
    novo_carro = pd.DataFrame([carro.model_dump()])
    dados = pd.concat([dados, novo_carro], ignore_index=True)

    # Salvar no CSV
    try:
        dados.to_csv(CSV_FILE_PATH, index=False)
    except Exception as e:
        logging.error(f"Erro ao gravar no arquivo CSV: {e}")

    return carro

@app.get("/dados/")
def retornar_dados():
    global dados
    # Retornar os dados como uma lista de dicionários
    return dados.to_dict(orient="records")
