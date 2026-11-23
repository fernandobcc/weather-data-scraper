const $ = (id) => document.getElementById(id);

async function request(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? body.detail[0].msg : body.detail;
    throw new Error(detail || res.statusText);
  }
  return res.status === 204 ? null : res.json();
}

function showStatus(message, kind) {
  $("status").textContent = message;
  $("status").className = kind;
}

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text ?? "—";
  return td;
}

function row(city) {
  const tr = document.createElement("tr");
  tr.append(cell(city.City), cell(city.Latitude), cell(city.Longitude));
  const remove = document.createElement("button");
  remove.className = "danger";
  remove.textContent = "Remove";
  remove.setAttribute("aria-label", `Remove ${city.City}`);
  remove.addEventListener("click", () => removeCity(city.City));
  const actions = document.createElement("td");
  actions.append(remove);
  tr.append(actions);
  return tr;
}

async function loadCities() {
  const cities = await request("/api/cities");
  $("count").textContent = `Saved cities (${cities.length})`;
  $("rows").replaceChildren(...cities.map(row));
}

async function removeCity(name) {
  try {
    await request(`/api/cities/${encodeURIComponent(name)}`, { method: "DELETE" });
    showStatus(`Removed ${name}.`, "ok");
    await loadCities();
  } catch (err) {
    showStatus(err.message, "error");
  }
}

$("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const lat = $("lat").value, lon = $("lon").value;
  if ((lat === "") !== (lon === "")) return showStatus("Give both latitude and longitude, or neither.", "error");
  const body = { name: $("name").value.trim() };
  if (lat !== "") Object.assign(body, { latitude: Number(lat), longitude: Number(lon) });

  const button = e.submitter;
  button.disabled = true;
  try {
    const city = await request("/api/cities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    showStatus(`Added ${city.City} (${city.Latitude}, ${city.Longitude}).`, "ok");
    e.target.reset();
    await loadCities();
  } catch (err) {
    showStatus(err.message, "error");
  } finally {
    button.disabled = false;
  }
});

loadCities().catch((err) => showStatus(err.message, "error"));
