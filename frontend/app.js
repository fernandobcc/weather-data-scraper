const METRICS = {
  temperature: { title: "Temperature", metric: ["Temperature (C)", "°C"], imperial: ["Temperature (F)", "°F"] },
  humidity: { title: "Relative humidity", metric: ["Humidity (%)", "%"], imperial: ["Humidity (%)", "%"] },
  wind: { title: "Wind speed", metric: ["Wind Speed (m/s)", "m/s"], imperial: ["Wind Speed (mph)", "mph"] },
};
const TABLE_COLUMNS = ["City", "Temperature (C)", "Temperature (F)", "Humidity (%)",
  "Wind Speed (m/s)", "Wind Speed (mph)", "Temperature Rank"];
const TILES = [
  ["hottest", "Hottest", "temperature"], ["coldest", "Coldest", "temperature"],
  ["driest", "Lowest humidity", "humidity"], ["most_humid", "Most humid", "humidity"],
  ["windiest", "Windiest", "wind"],
];

const state = { rows: [], rankings: {}, metric: "temperature", cities: "" };
const $ = (id) => document.getElementById(id);
const esc = (v) => String(v).replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`);
const css = (name) => getComputedStyle(document.body).getPropertyValue(name).trim();
let chart;

const query = () => (state.cities ? `?cities=${encodeURIComponent(state.cities)}` : "");
const field = (key) => METRICS[key][$("imperial").checked ? "imperial" : "metric"];

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res.json();
}

async function load() {
  $("error").hidden = true;
  try {
    [state.rows, state.rankings] = await Promise.all([
      getJSON(`/api/weather${query()}`), getJSON(`/api/rankings${query()}`),
    ]);
    $("observed").textContent = `observed ${state.rows[0]["Observed At (UTC)"]} UTC`;
    $("download").href = `/api/weather.csv${query()}`;
    render();
  } catch (err) {
    $("error").textContent = err.message;
    $("error").hidden = false;
  }
}

function render() {
  renderTiles();
  renderChart();
  renderTable();
  $("png").src = `/api/charts/${state.metric}.png${query()}`;
}

function renderTiles() {
  const byCity = Object.fromEntries(state.rows.map((r) => [r.City, r]));
  $("tiles").innerHTML = TILES.map(([key, label, metric]) => {
    const city = state.rankings[key].city;
    const [column, unit] = field(metric);
    return `<div class="tile"><div class="label">${label}</div>
      <div class="value">${byCity[city][column]} ${unit}</div><div class="city">${esc(city)}</div></div>`;
  }).join("");
}

function renderChart() {
  const [column, unit] = field(state.metric);
  const rows = [...state.rows].sort((a, b) => b[column] - a[column]);
  $("chart-title").textContent = `${METRICS[state.metric].title} (${unit})`;
  const data = {
    labels: rows.map((r) => r.City),
    datasets: [{
      label: `${METRICS[state.metric].title} (${unit})`,
      data: rows.map((r) => r[column]),
      backgroundColor: css("--series-1"),
      borderRadius: 4,
      borderSkipped: "start",
      barPercentage: 0.7,
    }],
  };
  const ink = css("--text-secondary");
  const options = {
    indexAxis: "y",
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (ctx) => ` ${ctx.parsed.x} ${unit}` } },
    },
    scales: {
      x: { grid: { color: css("--border") }, ticks: { color: ink }, border: { display: false } },
      y: { grid: { display: false }, ticks: { color: ink } },
    },
  };
  if (chart) chart.destroy();
  chart = new Chart($("chart"), { type: "bar", data, options });
}

function renderTable() {
  const head = `<tr>${TABLE_COLUMNS.map((c) => `<th>${c}</th>`).join("")}</tr>`;
  const body = state.rows
    .map((r) => `<tr>${TABLE_COLUMNS.map((c) => `<td>${esc(r[c])}</td>`).join("")}</tr>`)
    .join("");
  $("table").innerHTML = head + body;
}

$("controls").addEventListener("submit", (e) => {
  e.preventDefault();
  state.cities = $("cities").value.trim();
  load();
});
document.querySelectorAll(".segmented button").forEach((btn) =>
  btn.addEventListener("click", () => {
    document.querySelectorAll(".segmented button").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.metric = btn.dataset.metric;
    render();
  }),
);
$("imperial").addEventListener("change", render);

load();
