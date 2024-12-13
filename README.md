# Projeto de Cadastro de Carros
Este projeto consiste em uma API desenvolvida em **FastAPI** para gerenciar um cadastro de carros armazenados em um arquivo CSV. É possível adicionar, listar, atualizar, filtrar e remover registros de carros, além de compactar o arquivo de dados em um ZIP e obter o hash do arquivo.

## Autores:
- Guilherme Moretti - 536179
- Jose Iago Lima - 500038

## Como executar o projeto com Pipenv

1. **Instalar o Pipenv**: Caso ainda não possua, instale o [Pipenv](https://pipenv.pypa.io/en/latest/) em seu sistema:
   ```bash
   pip install --user pipenv
   ```

2. **Criar ambiente virtual e instalar dependências**: Na pasta raiz do seu projeto (onde o `Pipfile` deverá existir), execute:
   ```bash
   pipenv install
   ```
   Isso irá criar um ambiente virtual e instalar todas as dependências listadas no `Pipfile`.

3. **Ativar o ambiente virtual**:
   ```bash
   pipenv shell
   ```

4. **Iniciar o servidor (utilizando o uvicorn)**:
   ```bash
   uvicorn main:app --reload
   ```
   Por padrão, o servidor ficará disponível em `http://127.0.0.1:8000`.

## Resumo do Projeto

Este projeto é uma simples API REST que faz a gestão de um conjunto de carros. Os dados são persistidos em um arquivo CSV e pode-se:

- **Adicionar** um carro.
- **Listar** todos os carros ou filtrar por critérios (cor, marca, ano, modelo, placa).
- **Atualizar** um carro existente.
- **Remover** um carro do cadastro.
- **Verificar a quantidade** total de carros.
- **Compactar** o arquivo de dados CSV em um arquivo ZIP para download.
- **Obter o hash SHA-256** do arquivo CSV para verificação de integridade.

A aplicação registra logs em um arquivo (`server.log`) para acompanhamento das operações.
