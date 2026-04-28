# 🪙 g-crypto Pro v2...

**g-crypto Pro v2** é a evolução definitiva em rastreamento de criptomoedas. Desenvolvido em Python, ele combina análise técnica avançada, interface moderna no terminal e um **Interpretador Web de alta performance** para monitoramento em tempo real.

---

## ✨ Funcionalidades Pro...

- **⚡ Cache Inteligente**: Sistema de cache otimizado para a API do CoinGecko, evitando bloqueios por excesso de requisições e garantindo performance instantânea.
- **📊 Análise Técnica**: Cálculo automático de Médias Móveis (SMA-7 e SMA-20) para identificação precisa de tendências de mercado.
- **📄 Relatórios PDF**: Geração de documentos executivos profissionais com tabelas dinâmicas e gráficos de alta resolução integrados.
- **🖥️ Interface Moderna (TUI)**: Terminal interativo rico em detalhes, com tabelas coloridas, painéis de status e barras de progresso animadas (via `rich`).
- **📉 Gráficos Dinâmicos**: Visualização de histórico de preços com gradientes modernos, indicadores técnicos e suporte a múltiplos períodos.
- **💾 Exportação Multi-Formato**: Exportação completa de dados em formatos `.json`, `.png` (gráficos) e `.pdf` (relatórios).
- **🔍 Busca Global**: Localização instantânea de qualquer ativo listado no ecossistema CoinGecko através de nome, símbolo ou ID.

---

## 📦 Instalação

### 1. Requisitos
- Python 3.9 ou superior recomendado.

### 2. Instalação Simplificada
```bash
pip install -r requirements.txt
```

---

## ▶️ Modo de Operação

### 🖥️ Terminal (Análise Executiva)
Execute o dashboard principal para gerar relatórios e analisar ativos via CLI:
```bash
python g_crypto.py
```

### 🌐 Interpretador Web (Monitoramento Live)
Acesse a interface visual de última geração com gráficos interativos e interpretação de dados em tempo real:
```bash
python web_app.py
```
Abra em: `http://localhost:8000`

**Nota:** Gere relatórios executivos profissionais instantaneamente **sem a necessidade de chaves de API**.

**Recursos Web:**
1. **Filtros Dinâmicos**: Alterne entre moedas e períodos de histórico instantaneamente.
2. **Monitoramento Live**: Ajuste a frequência de atualização (ex: a cada 8 segundos).
3. **Analytics**: Acompanhe Preço (USD/BRL), Market Cap, Volume e Médias Móveis em uma única tela.

---

## 📁 Ecossistema de Arquivos

| Artefato | Finalidade |
|---|---|
| `report_[id].pdf` | Relatório Executivo pronto para apresentação |
| `chart_[id].png` | Visualização de Análise Técnica em alta definição |
| `crypto_[id].json` | Estrutura de dados brutos para integração externa |

---

## 🛠 Stack Tecnológica

- **Core**: Python 3.9+
- **Data Engine**: Pandas & API CoinGecko
- **Visuals**: Matplotlib (Dark Theme) & Chart.js (Web)
- **UI/UX**: Rich (Terminal) & Flask (Web Service)
- **Reporting**: ReportLab PDF Engine

---

## 📄 Licença

Desenvolvido por **Gêrlan Cardoso** para máxima eficiência e transparência. Licença MIT.
