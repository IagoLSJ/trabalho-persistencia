import csv
import os
from typing import List
from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging

app = FastAPI()

CSV_FILE_PATH = "db.csv"

dados = []

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
            with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                dados = [row for row in reader]
        else:
            logging.warning("Arquivo CSV não encontrado. Um novo será criado ao adicionar o primeiro carro.")
    except FileNotFoundError:
        logging.warning("Arquivo não encontrado")

    yield

    # Opcional: Se você quiser salvar os dados no CSV ao desligar o servidor
    # Pode descomentar o código abaixo se necessário

    # try:
    #     with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
    #         fieldnames = ['placa', 'cor', 'modelo', 'ano', 'marca']
    #         writer = csv.DictWriter(file, fieldnames=fieldnames)
    #         writer.writeheader()
    #         writer.writerows(dados)
    # except Exception as e:
    #     logging.error(f"Erro ao gravar no arquivo CSV: {e}")

@app.post("/adicionar/", response_model=Carro, status_code=HTTPStatus.CREATED)
def adicionar_carro(carro: Carro):
    # Verificar se o carro já existe
    if any(c['placa'] == carro.placa for c in dados):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Carro já existe.")
    
    # Adicionar carro na lista de dados
    dados.append(carro.dict())

    # Escrever o novo carro no CSV imediatamente
    try:
        file_exists = os.path.exists(CSV_FILE_PATH)
        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['placa', 'cor', 'modelo', 'ano', 'marca']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Escrever cabeçalho se o arquivo não existir ou estiver vazio
            if not file_exists or os.stat(CSV_FILE_PATH).st_size == 0:
                writer.writeheader()

            # Escrever o novo carro no CSV
            writer.writerow(carro.dict())
    except Exception as e:
        logging.error(f"Erro ao gravar no arquivo CSV: {e}")

    return carro
