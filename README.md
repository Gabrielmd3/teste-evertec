# Projeto de Processamento de Dados e API de Tipos

Este projeto consiste em uma aplicação backend dividida em duas partes principais: um pipeline de processamento de dados (ETL) e uma API RESTful rápida construída com FastAPI. 

A aplicação foi desenvolvida para extrair dados de um arquivo compactado, realizar limpezas, transformações e cruzamentos de informações, persistir esses dados em um banco de dados SQLite e disponibilizar consultas rápidas em memória através de uma API.

## 🚀 Tecnologias Utilizadas

* **Python 3.x**
* **Pandas:** Manipulação, filtragem e cruzamento de dados (DataFrames).
* **SQLite3:** Banco de dados relacional embarcado.
* **FastAPI:** Criação da API RESTful.
* **Uvicorn:** Servidor ASGI para rodar a aplicação web.

## 📂 Estrutura do Projeto

* `main.py`: Script principal responsável pelo pipeline de dados (descompactação, leitura, tratamento, geração de SQL, criação do banco SQLite e relatório analítico).
* `api.py`: Aplicação FastAPI que serve os dados dos tipos cruzados.
* `dados.zip`: Arquivo compactado original contendo `origem-dados.csv` e `tipos.csv` (deve estar na raiz do projeto).
* `data_extracted/`: Diretório gerado automaticamente contendo os CSVs extraídos.
* `database/`: Diretório gerado automaticamente contendo o arquivo SQL de inserção e o banco de dados `database.db`.

## ⚙️ Pré-requisitos e Instalação

1. Certifique-se de ter o Python instalado em sua máquina.
2. É recomendada a criação de um ambiente virtual (venv):
   ```bash
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```
3. Instale as dependências necessárias:
   `pip install pandas fastapi uvicorn`

## 🛠️ Como Executar o Projeto

A aplicação possui mecanismos de resiliência. Você pode iniciar pelo processamento de dados ou direto pela API, e o sistema garantirá que os arquivos necessários sejam extraídos.
Opção 1: Executar o Pipeline de Dados Completo

Para rodar a extração, tratamento, criação do banco de dados e visualizar o relatório de agrupamento no terminal, execute:
`python main.py`

O que este script faz:

   * Descompacta dados.zip.
   * Filtra registros com status "CRÍTICO" e ordena por data.
   * Faz o merge com o arquivo de tipos para obter a nomenclatura correta.
   *  Gera um arquivo insert-dados.sql.
   *  Cria e popula o banco de dados database.db.
   *  Imprime um relatório analítico agrupando itens por dia e tipo.

Opção 2: Iniciar a API

Para iniciar o servidor da API (que carrega os dados em memória para alta performance), execute:
`python -m uvicorn api:app --reload`
(O servidor iniciará, por padrão, em http://127.0.0.1:8000)

##📡 Endpoints da API
Obter Tipo por ID

Retorna o nome correspondente ao ID do tipo fornecido.

    URL: /tipos/{tipo_id}

    Método: GET

    Parâmetros de Rota: tipo_id (Inteiro)

Exemplo de Requisição:

`GET [http://127.0.0.1:8000/tipos/1](http://127.0.0.1:8000/tipos/1)`

Exemplo de Resposta de Sucesso (200 OK):
```
{
  "id": 1,
  "tipo": "Nome do Tipo Correspondente"
}
```

Exemplo de Resposta de Erro (404 Not Found):
```
{
  "detail": "Tipo não encontrado no arquivo."
}
```
