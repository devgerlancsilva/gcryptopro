"""
g-crypto Pro - Rastreador Profissional de Criptomoedas
Versão 2.0: Interface Moderna, Análise Técnica e Relatórios PDF.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import os
from datetime import datetime, timedelta
from typing import Union, Tuple, List, Optional, Dict

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich import print as rprint
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table as PDFTable, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# Configuração Global
console = Console()
BASE_URL = "https://api.coingecko.com/api/v3"

class CryptoAnalyzer:
    def __init__(self, cache_expire_seconds: int = 60):
        self.moedas_populares = {
            "Bitcoin": "bitcoin",
            "Ethereum": "ethereum",
            "Solana": "solana",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "Cardano": "cardano",
            "Dogecoin": "dogecoin",
            "Chainlink": "chainlink",
            "Polkadot": "polkadot",
            "Avalanche": "avalanche-2"
        }
        self._cache = {}
        self._cache_expire_seconds = cache_expire_seconds

    def _get_api(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        # Gerar chave de cache baseada na URL e params
        cache_key = f"{endpoint}_{json.dumps(params, sort_keys=True)}"
        
        # Verificar se o dado está no cache e ainda é válido
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_expire_seconds):
                return data

        url = f"{BASE_URL}/{endpoint}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers={"User-Agent": "g-crypto-pro/2.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
                # Armazenar no cache
                self._cache[cache_key] = (data, datetime.now())
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                # Se houver dado no cache, retorna mesmo expirado em caso de 429
                if cache_key in self._cache:
                    return self._cache[cache_key][0]
                raise Exception("Limite de requisições da API atingido (Rate Limit). Tente novamente em alguns minutos.")
            raise Exception(f"Erro na API ({e.code}): {e.reason}")
        except Exception as e:
            raise Exception(f"Erro de conexão com API: {e}")

    def buscar_por_nome(self, termo: str) -> Union[Tuple[str, str], Tuple[None, None]]:
        dados = self._get_api("search", {"query": termo})
        coins = dados.get("coins", [])
        if not coins:
            return None, None
        return coins[0]["id"], coins[0]["name"]

    def obter_dados_mercado(self, coin_id: str) -> Dict:
        params = {
            "ids": coin_id,
            "vs_currencies": "usd,brl",
            "include_24hr_change": "true",
            "include_market_cap": "true",
            "include_24hr_vol": "true"
        }
        dados = self._get_api("simple/price", params)
        return dados.get(coin_id, {})

    def obter_historico(self, coin_id: str, dias: int = 30) -> pd.DataFrame:
        params = {
            "vs_currency": "usd",
            "days": dias,
            "interval": "daily" if dias > 1 else "hourly"
        }
        dados = self._get_api(f"coins/{coin_id}/market_chart", params)
        precos = dados.get("prices", [])
        
        df = pd.DataFrame(precos, columns=["timestamp", "price"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("date", inplace=True)
        
        # Indicadores Técnicos
        df["SMA_7"] = df["price"].rolling(window=7).mean()
        df["SMA_20"] = df["price"].rolling(window=20).mean()
        
        return df

    def salvar_grafico(self, df: pd.DataFrame, nome: str, arquivo: str):
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Cores modernas
        cor_principal = "#00ff9d" if df["price"].iloc[-1] >= df["price"].iloc[0] else "#ff4d4d"
        
        ax.plot(df.index, df["price"], color=cor_principal, linewidth=2, label="Preço USD")
        if "SMA_7" in df.columns:
            ax.plot(df.index, df["SMA_7"], color="#3399ff", linestyle="--", alpha=0.7, label="SMA 7")
        
        ax.fill_between(df.index, df["price"], df["price"].min(), alpha=0.1, color=cor_principal)
        
        ax.set_title(f"Histórico: {nome}", fontsize=16, fontweight="bold", pad=20)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.grid(True, alpha=0.2)
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(arquivo, dpi=150)
        plt.close()

    def gerar_pdf(self, nome: str, market_data: Dict, df: pd.DataFrame, img_path: str, pdf_path: str):
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Cabeçalho
        elements.append(Paragraph(f"Relatório de Mercado: {nome}", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Tabela de Dados Atuais
        data = [
            ["Métrica", "Valor (USD)", "Valor (BRL)"],
            ["Preço Atual", f"${market_data.get('usd', 0):,.2f}", f"R$ {market_data.get('brl', 0):,.2f}"],
            ["Variação 24h", f"{market_data.get('usd_24h_change', 0):+.2f}%", "-"],
            ["Market Cap", f"${market_data.get('usd_market_cap', 0):,.0f}", "-"],
            ["Volume 24h", f"${market_data.get('usd_24h_vol', 0):,.0f}", "-"]
        ]
        t = PDFTable(data, colWidths=[150, 150, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 30))

        # Imagem do Gráfico
        if os.path.exists(img_path):
            img = Image(img_path, width=450, height=225)
            elements.append(img)

        doc.build(elements)

def exibir_menu(analyzer: CryptoAnalyzer):
    table = Table(title="[bold cyan]g-crypto Pro: Menu Principal[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Opção", justify="center", style="dim")
    table.add_column("Moeda", style="bold white")
    
    for i, (nome, _) in enumerate(analyzer.moedas_populares.items(), 1):
        table.add_row(str(i), nome)
    table.add_row("0", "Buscar outra moeda...")
    
    console.print(table)

def main():
    analyzer = CryptoAnalyzer()
    
    console.print(Panel.fit(
        "[bold gold1][CRIPTO] g-crypto Pro[/bold gold1]\n[italic]O Futuro do seu Portfólio começa aqui[/italic]",
        border_style="cyan"
    ))

    exibir_menu(analyzer)
    
    try:
        opcao = console.input("\n[bold yellow]Escolha uma opção (ou o nome da moeda): [/bold yellow]").strip()
        
        if opcao == "0" or not opcao.isdigit():
            busca = opcao if not opcao.isdigit() else console.input("[bold blue]Digite o nome da moeda: [/bold blue]")
            with console.status("[bold green]Buscando no CoinGecko...") as status:
                coin_id, nome = analyzer.buscar_por_nome(busca)
        else:
            idx = int(opcao) - 1
            nomes = list(analyzer.moedas_populares.keys())
            if 0 <= idx < len(nomes):
                nome = nomes[idx]
                coin_id = analyzer.moedas_populares[nome]
            else:
                rprint("[bold red]Opção inválida![/bold red]")
                return

        if not coin_id:
            rprint("[bold red]Moeda não encontrada![/bold red]")
            return

        dias = console.input("[bold blue]Dias de histórico (padrão 30): [/bold blue]") or "30"
        dias = int(dias)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task1 = progress.add_task(description=f"Obtendo dados de {nome}...", total=None)
            market_data = analyzer.obter_dados_mercado(coin_id)
            
            task2 = progress.add_task(description="Processando séries temporais...", total=None)
            df = analyzer.obter_historico(coin_id, dias)
            
            task3 = progress.add_task(description="Gerando gráficos...", total=None)
            img_file = f"chart_{coin_id}.png"
            analyzer.salvar_grafico(df, nome, img_file)
            
            task4 = progress.add_task(description="Compilando relatório PDF...", total=None)
            pdf_file = f"report_{coin_id}.pdf"
            analyzer.gerar_pdf(nome, market_data, df, img_file, pdf_file)

        # Dashboard Final
        console.print(f"\n[bold green][OK] Análise concluída para {nome}![/bold green]")
        
        summary_table = Table(show_header=False, padding=(0, 2))
        summary_table.add_row("Preço USD:", f"[bold cyan]${market_data.get('usd', 0):,.2f}[/bold cyan]")
        summary_table.add_row("Preço BRL:", f"[bold green]R$ {market_data.get('brl', 0):,.2f}[/bold green]")
        var = market_data.get('usd_24h_change', 0)
        cor_var = "green" if var >= 0 else "red"
        summary_table.add_row("Variação 24h:", f"[{cor_var}]{var:+.2f}%[/{cor_var}]")
        
        console.print(Panel(summary_table, title=f"[bold]{nome} Status[/bold]", border_style="bright_blue"))
        
        rprint(f"\n[ARQUIVOS] [bold white]Arquivos Gerados:[/bold white]")
        rprint(f"  - [blue]{img_file}[/blue] (Gráfico)")
        rprint(f"  - [red]{pdf_file}[/red] (Relatório Profissional PDF)")
        rprint(f"  - [yellow]crypto_{coin_id}.json[/yellow] (Dados brutos)")
        
        # Salvar JSON (compatibilidade com versão anterior)
        df_json = df.reset_index()
        df_json['date'] = df_json['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        with open(f"crypto_{coin_id}.json", "w") as f:
            json.dump({
                "meta": {"coin": nome, "date": datetime.now().isoformat()},
                "market": market_data,
                "history": df_json.to_dict(orient="records")
            }, f, indent=4)

    except Exception as e:
        console.print(f"[bold red]Ocorreu um erro crítico: {e}[/bold red]")

if __name__ == "__main__":
    main()
