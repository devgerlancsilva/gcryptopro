const state = {
  coin: "bitcoin",
  days: 30,
  refresh: 8,
  timer: null,
  chart: null,
};

const coinSelect = document.getElementById("coinSelect");
const daysInput = document.getElementById("daysInput");
const refreshInput = document.getElementById("refreshInput");
const applyBtn = document.getElementById("applyBtn");
const statusText = document.getElementById("statusText");

const priceUsd = document.getElementById("priceUsd");
const priceBrl = document.getElementById("priceBrl");
const change24h = document.getElementById("change24h");
const marketCap = document.getElementById("marketCap");
const volume24h = document.getElementById("volume24h");
const updatedAt = document.getElementById("updatedAt");
const chartTitle = document.getElementById("chartTitle");

function formatMoney(value, currency = "USD") {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value ?? 0);
}

function formatCompact(value) {
  return new Intl.NumberFormat("pt-BR", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value ?? 0);
}

async function fetchJson(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Falha na requisicao");
  }
  return data;
}

function setStatus(text) {
  statusText.textContent = text;
}

function updateMarketCards(payload) {
  const market = payload.market;
  const change = market.usd_24h_change || 0;

  priceUsd.textContent = formatMoney(market.usd, "USD");
  priceBrl.textContent = formatMoney(market.brl, "BRL");
  change24h.textContent = `${change.toFixed(2)}%`;
  change24h.classList.remove("positive", "negative");
  change24h.classList.add(change >= 0 ? "positive" : "negative");
  marketCap.textContent = formatCompact(market.usd_market_cap);
  volume24h.textContent = formatCompact(market.usd_24h_vol);

  const stamp = new Date(payload.timestamp).toLocaleString("pt-BR");
  updatedAt.textContent = `Atualizado em: ${stamp}`;
}

function buildOrUpdateChart(historyPayload) {
  const labels = historyPayload.history.map((item) => new Date(item.date).toLocaleDateString("pt-BR"));
  const prices = historyPayload.history.map((item) => item.price);
  const sma7 = historyPayload.history.map((item) => item.sma_7);
  const sma20 = historyPayload.history.map((item) => item.sma_20);

  chartTitle.textContent = `${historyPayload.name} - historico (${historyPayload.days} dias)`;

  if (state.chart) {
    state.chart.data.labels = labels;
    state.chart.data.datasets[0].data = prices;
    state.chart.data.datasets[1].data = sma7;
    state.chart.data.datasets[2].data = sma20;
    state.chart.update();
    return;
  }

  const ctx = document.getElementById("priceChart");
  state.chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Preco USD",
          data: prices,
          borderColor: "#23d18b",
          backgroundColor: "rgba(35, 209, 139, 0.15)",
          borderWidth: 2,
          fill: true,
          tension: 0.25,
          pointRadius: 0,
        },
        {
          label: "SMA 7",
          data: sma7,
          borderColor: "#6ea8ff",
          borderWidth: 1.6,
          pointRadius: 0,
          tension: 0.2,
        },
        {
          label: "SMA 20",
          data: sma20,
          borderColor: "#ffcf5a",
          borderWidth: 1.4,
          pointRadius: 0,
          borderDash: [5, 5],
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#d6e6ff" },
        },
      },
      scales: {
        x: {
          ticks: { color: "#9bb2dd" },
          grid: { color: "rgba(146, 167, 202, 0.15)" },
        },
        y: {
          ticks: { color: "#9bb2dd" },
          grid: { color: "rgba(146, 167, 202, 0.15)" },
        },
      },
    },
  });
}

async function refreshDashboard() {
  try {
    setStatus("Atualizando dados...");
    const market = await fetchJson(`/api/market?coin=${encodeURIComponent(state.coin)}`);
    const history = await fetchJson(`/api/history?coin=${encodeURIComponent(state.coin)}&days=${state.days}`);
    updateMarketCards(market);
    buildOrUpdateChart(history);
    setStatus(`Monitorando ${history.name} em tempo real.`);
  } catch (error) {
    setStatus(`Erro: ${error.message}`);
  }
}

function restartTimer() {
  if (state.timer) {
    clearInterval(state.timer);
  }
  state.timer = setInterval(refreshDashboard, state.refresh * 1000);
}

function applySettings() {
  state.coin = coinSelect.value || "bitcoin";
  state.days = Math.max(1, Math.min(365, Number(daysInput.value) || 30));
  state.refresh = Math.max(3, Math.min(120, Number(refreshInput.value) || 8));
  restartTimer();
  refreshDashboard();
}

applyBtn.addEventListener("click", applySettings);
window.addEventListener("load", applySettings);
