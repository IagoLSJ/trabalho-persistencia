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
    marca:  str


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

    #Quando desligado
    try:
        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['placa','cor','modelo','ano','marca']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for carro in dados:
                writer.writerows(carro)
    except Exception as e:
        logging.error(f"Erro ao gravar no arquivo CSV: {e}")
    #Gravar informações de dados no csv



'''
# Funcionalidade 1 - Adicionar uma unidade
Objetivo: Implementar um endpoint para cadastrar uma nova entidade no sistema.
Detalhes: Quando o endpoint for acessado com um JSON contendo os dados da entidade, a API deverá adicionar essa entidade ao arquivo CSV, usando o modo de "append" (ou seja, adicionando ao final do arquivo sem substituir os dados existentes).
Exemplo: Enviar um JSON com os dados de um novo Produto e salvar esses dados no CSV, cada linha representando um produto diferente.
'''
@app.post("/adicionar/", response_model=Carro, status_code=HTTPStatus.CREATED)
def adicionar_carro(carro:Carro):
    if any(c.placa == carro.placa for c in dados):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Carro já existe.")
    
    dados.append(carro.model_dump())

    return carro
