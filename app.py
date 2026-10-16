from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__)
DATA_FILE = "carteira.json"

if not os.path.exists(DATA_FILE):
    dados_iniciais = [
        {"id": 1, "mercado": "fii", "ticker": "XPML11", "moeda": "BRL", "qtd": 10, "precoMedio": 106.32, "precoAtual": 107.39},
        {"id": 2, "mercado": "fii", "ticker": "MXRF11", "moeda": "BRL", "qtd": 100, "precoMedio": 10.10, "precoAtual": 10.45},
        {"id": 3, "mercado": "cripto", "ticker": "BTC", "moeda": "USD", "qtd": 0.05, "precoMedio": 60000.0, "precoAtual": 68000.0}
    ]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados_iniciais, f)

def carregar_carteira():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_carteira(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/carteira", methods=["GET", "POST"])
def gerenciar_carteira():
    if request.method == "POST":
        nova_carteira = request.json
        salvar_carteira(nova_carteira)
        return jsonify({"status": "sucesso"})
    return jsonify(carregar_carteira())

@app.route("/api/cotacao/<ticker>")
def obter_cotacao(ticker):
    ticker = ticker.upper().strip()
    crypto_map = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
    if ticker in crypto_map:
        try:
            res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_map[ticker]}&vs_currencies=usd", timeout=5)
            data = res.json()
            preco = data[crypto_map[ticker]]["usd"]
            return jsonify({"ticker": ticker, "preco": preco})
        except:
            pass

    try:
        url = f"https://brapi.dev/api/quote/{ticker}"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "results" in data and len(data["results"]) > 0:
            preco = data["results"][0]["regularMarketPrice"]
            return jsonify({"ticker": ticker, "preco": preco})
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")

    return jsonify({"ticker": ticker, "preco": None}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
