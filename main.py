import os
import pandas as pd
from typing import List
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging


LOG_FILE = "server.log"
CSV_FILE_PATH = "db.csv"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class Carro(BaseModel):
    placa: str
    cor: str
    modelo: str
    ano: int
    marca: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if not os.path.exists(CSV_FILE_PATH):
            dados = pd.DataFrame(columns=["placa", "cor", "modelo", "ano", "marca"])
            dados.to_csv(CSV_FILE_PATH, index=False)
            logging.info("Arquivo CSV não encontrado. Um novo foi criado.")
        else:
            logging.info("Arquivo CSV encontrado com sucesso.")
        yield
    except Exception as e:
        logging.error(f"Erro ao configurar o arquivo CSV: {e}")
        raise


app = FastAPI(lifespan=lifespan)


@app.post("/adicionar/", response_model=Carro, status_code=HTTPStatus.CREATED)
def adicionar_carro(carro: Carro):
    dados = pd.read_csv(CSV_FILE_PATH)
    if (dados['placa'] == carro.placa).any():
        logging.warning(f"Carro com placa {carro.placa} já existe.")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Carro já existe.")

    novo_carro = pd.DataFrame([carro.model_dump()])
    dados = pd.concat([dados, novo_carro], ignore_index=True)

    try:
        dados.to_csv(CSV_FILE_PATH, index=False)
        logging.info(f"Carro com placa {carro.placa} adicionado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao gravar no arquivo CSV: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Erro ao salvar os dados.")

    return carro


@app.get("/listar/", response_model=List[Carro], status_code=HTTPStatus.OK)
def retornar_carros():
    dados = pd.read_csv(CSV_FILE_PATH)
    logging.info("Solicitação para listar todos os carros.")
    return dados.to_dict(orient="records")

@app.get("/listar/{placa}", response_model=Carro, status_code=HTTPStatus.OK)
def retornar_carro(placa: str):
    logging.info(f"Solicitação para verificar carro com placa: {placa}")

    dados = pd.read_csv(CSV_FILE_PATH)

    carro = dados[dados['placa'] == placa]

    if carro.empty:
        logging.warning(f"Carro com placa {placa} não encontrado para verificação.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Carro não encontrado.")

    return carro.iloc[0].to_dict()

@app.delete("/apagar/{placa}", response_model=Carro, status_code=HTTPStatus.OK)
def apagar_carro(placa: str):
    dados = pd.read_csv(CSV_FILE_PATH)
    index_placa_igual = dados[dados['placa'] == placa].index

    if index_placa_igual.empty:
        logging.warning(f"Carro com placa {placa} não encontrado para exclusão.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Carro não encontrado.")

    carro_removido = dados.loc[index_placa_igual[0]].to_dict()
    dados.drop(index=index_placa_igual, inplace=True)
    dados.reset_index(drop=True, inplace=True)

    try:
        dados.to_csv(CSV_FILE_PATH, index=False)
        logging.info(f"Carro com placa {placa} removido com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo CSV após exclusão: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Erro ao salvar os dados.")

    return carro_removido


@app.put("/atualizar/{placa}", response_model=Carro, status_code=HTTPStatus.OK)
def atualizar_carro(placa: str, carroAtualizado: Carro):
    dados = pd.read_csv(CSV_FILE_PATH)

    index_placa_igual = dados[dados['placa'] == placa].index

    if index_placa_igual.empty:
        logging.warning(f"Carro com placa {placa} não encontrado para atualização.")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Carro não encontrado.")

    if carroAtualizado.placa != placa:
        logging.warning("A placa no corpo da requisição não corresponde à placa na rota.")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="A placa na requisição não pode ser diferente da placa na rota."
        )

    index = index_placa_igual[0]
    dados.loc[index, ['cor', 'modelo', 'ano', 'marca']] = [
        carroAtualizado.cor,
        carroAtualizado.modelo,
        carroAtualizado.ano,
        carroAtualizado.marca
    ]

    try:
        dados.to_csv(CSV_FILE_PATH, index=False)
        logging.info(f"Carro com placa {placa} atualizado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo CSV após atualização: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Erro ao salvar os dados.")

    return carroAtualizado


@app.get("/quantidade/", status_code=HTTPStatus.OK)
def quantidade_carros():
    
    dados = pd.read_csv(CSV_FILE_PATH)
    
    logging.info("Solicitação para saber a quantidade de carros.")
    
    resposta = {
        "quantidade" : dados.shape[0]
    }

    logging.info(f"Quantidade de carros: {resposta}")
    return resposta