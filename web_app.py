from datetime import datetime, timezone
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from g_crypto import CryptoAnalyzer


app = Flask(__name__)
analyzer = CryptoAnalyzer()


def _resolve_coin(query: str) -> Dict[str, str]:
    """Resolve a coin by id, popular name, or CoinGecko search term."""
    if not query:
        return {"coin_id": "bitcoin", "name": "Bitcoin"}

    termo = query.strip().lower()

    for nome, coin_id in analyzer.moedas_populares.items():
        if termo == nome.lower() or termo == coin_id.lower():
            return {"coin_id": coin_id, "name": nome}

    coin_id, nome = analyzer.buscar_por_nome(query)
    if not coin_id:
        raise ValueError("Moeda nao encontrada")

    return {"coin_id": coin_id, "name": nome}


@app.route("/")
def index() -> str:
    return render_template("index.html", populares=analyzer.moedas_populares)


@app.route("/api/coin/resolve")
def api_resolve_coin() -> Any:
    query = request.args.get("q", "bitcoin")
    try:
        result = _resolve_coin(query)
        return jsonify(result)
    except Exception as exc:  # pragma: no cover - resilience for API failures
        return jsonify({"error": str(exc)}), 400


@app.route("/api/market")
def api_market() -> Any:
    query = request.args.get("coin", "bitcoin")
    try:
        resolved = _resolve_coin(query)
        market = analyzer.obter_dados_mercado(resolved["coin_id"])
        return jsonify({
            "coin_id": resolved["coin_id"],
            "name": resolved["name"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market": market,
        })
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 400


@app.route("/api/history")
def api_history() -> Any:
    query = request.args.get("coin", "bitcoin")
    dias = int(request.args.get("days", "30"))
    dias = max(1, min(dias, 365))

    try:
        resolved = _resolve_coin(query)
        df = analyzer.obter_historico(resolved["coin_id"], dias)
        payload = []
        for idx, row in df.iterrows():
            payload.append(
                {
                    "date": idx.isoformat(),
                    "price": float(row["price"]),
                    "sma_7": float(row["SMA_7"]) if row.get("SMA_7") == row.get("SMA_7") else None,
                    "sma_20": float(row["SMA_20"]) if row.get("SMA_20") == row.get("SMA_20") else None,
                }
            )

        return jsonify(
            {
                "coin_id": resolved["coin_id"],
                "name": resolved["name"],
                "days": dias,
                "history": payload,
            }
        )
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
