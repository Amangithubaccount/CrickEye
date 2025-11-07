// static/script.js
async function fetchJson(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return await r.json();
}

function formatAlerts(alertArray) {
  if (!Array.isArray(alertArray)) return "[]";
  return alertArray.map(a => `${a.timestamp} — ${a.alert_message}`).join("\n\n");
}

function renderTable(rows) {
  const tbody = document.querySelector("#history-table tbody");
  tbody.innerHTML = "";
  rows.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${r.player_name}</td><td>${r.match_date}</td><td>${r.performance_type}</td><td>${r.performance_value}</td>`;
    tbody.appendChild(tr);
  });
}

let recentEntries = [];

function renderPreview() {
  const el = document.getElementById("player-data");
  if (recentEntries.length === 0) {
    el.textContent = "No player data yet.";
  } else {
    el.textContent = JSON.stringify(recentEntries.slice(-10).reverse(), null, 2);
  }
}

function buildChartData(rows) {
  // Map player_name -> { batting: number|null, bowling: number|null }
  // We use a Map and delete+set to ensure the latest occurrence of a player is at the end (recent last).
  const latest = new Map();

  rows.forEach(r => {
    const pname = r.player_name;
    // parse numeric performance_value where possible
    const num = Number(r.performance_value);
    const val = isNaN(num) ? null : num;

    // if player already exists, remove it so re-setting moves it to the end (recent)
    if (latest.has(pname)) {
      const existing = latest.get(pname);
      // merge existing with updated type
      const merged = Object.assign({}, existing);
      merged[r.performance_type] = val;
      latest.delete(pname);
      latest.set(pname, merged);
    } else {
      const obj = {};
      obj[r.performance_type] = val;
      latest.set(pname, obj);
    }
  });

  // Convert Map -> arrays. We want the most recent players at the end, so we take the last N.
  const allPlayers = Array.from(latest.keys());

  // Change this to show more (or all) players if you want:
  const MAX_PLAYERS = rows.length; // or a large number like 999
 // show players to keep chart readable
  const selectedPlayers = (MAX_PLAYERS >= allPlayers.length)
    ? allPlayers
    : allPlayers.slice(-MAX_PLAYERS);

  const labels = selectedPlayers;
  const strikeData = selectedPlayers.map(p => {
    const v = latest.get(p).batting;
    return (v === undefined || v === null) ? null : Number(v);
  });
  const econData = selectedPlayers.map(p => {
    const v = latest.get(p).bowling;
    return (v === undefined || v === null) ? null : Number(v);
  });

  return { labels, strikeData, econData };
}

let chartInstance = null;
function renderChart(rows) {
  const ctx = document.getElementById('chart').getContext('2d');
  const { labels, strikeData, econData } = buildChartData(rows);

  if (chartInstance) {
    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].data = strikeData;
    chartInstance.data.datasets[1].data = econData;
    chartInstance.update();
    return;
  }

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Strike Rate (batting)', data: strikeData, yAxisID: 'y' },
        { label: 'Economy (bowling)', data: econData, yAxisID: 'y1' }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: { type: 'linear', position: 'left', title: { display: true, text: 'Strike Rate' } },
        y1: { type: 'linear', position: 'right', title: { display: true, text: 'Economy' }, grid: { drawOnChartArea: false } }
      }
    }
  });
}

async function loadAll() {
  try {
    const rows = await fetchJson('/player-data');
    // rows might be {"error":"..."} if no data
    if (rows && rows.error) {
      document.getElementById("player-data").textContent = rows.error;
      document.getElementById("alerts").textContent = "";
      renderTable([]);
      return;
    }

    renderPreview(rows);
    renderTable(rows);
    renderChart(rows);

    const alerts = await fetchJson('/alerts');
    document.getElementById("alerts").textContent = formatAlerts(alerts);
  } catch (err) {
    document.getElementById("player-data").textContent = "Error: " + err.message;
    document.getElementById("alerts").textContent = "";
  }
}

async function postNewEntry(obj) {
  const r = await fetch('/player-data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(obj)
  });
  return r.json();
}

window.addEventListener('DOMContentLoaded', () => {
  loadAll();

  const form = document.getElementById("add-form");
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const player_name = document.getElementById('player_name').value.trim();
    const match_date = document.getElementById('match_date').value;
    const performance_type = document.getElementById('performance_type').value;
    const performance_value = document.getElementById('performance_value').value.trim();

    const payload = { player_name, match_date, performance_type, performance_value };
    try {
      const res = await postNewEntry(payload);
      document.getElementById('form-status').textContent = res.message || JSON.stringify(res);
      recentEntries.push(payload);
      renderPreview();
      // refresh data and alerts
      await loadAll();
      // clear form
      form.reset();
      setTimeout(()=>document.getElementById('form-status').textContent = "", 3000);
    } catch (err) {
      document.getElementById('form-status').textContent = "Error: " + err.message;
    }
  });
});
