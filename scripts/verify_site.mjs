// Verifica il sito in un browser headless: ogni pagina risponde, Plotly si carica,
// i grafici contengono dati e l'animazione disegna sul canvas. Esce con codice 1 se qualcosa manca.
// Uso: node scripts/verify_site.mjs https://viciuslio.github.io/skill-cliff-abm/
import { chromium } from "playwright";

const base = (process.argv[2] || "http://localhost:8000/").replace(/\/?$/, "/");
const failures = [];
const check = (ok, msg) => { console.log(`${ok ? "OK  " : "FAIL"} ${msg}`); if (!ok) failures.push(msg); };

async function plotTraces(page, sel) {
  return page.$$eval(sel, (els) => els.map((el) => (el.data || []).filter((t) => (t.y || []).length > 0).length));
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));

for (const path of ["", "dinamica.html", "lezione.html", "fase2.html", "paper.pdf", "data/fase1.json", "data/dinamica.json", "data/fase2.json", "plotly-loader.js"]) {
  const r = await page.request.get(base + path);
  check(r.status() === 200, `${base}${path} -> HTTP ${r.status()}`);
}
// Il vecchio indirizzo della lezione deve portare alla lezione.
await page.goto(base + "presentazione.html", { waitUntil: "networkidle" });
check(page.url().includes("lezione.html"), `presentazione.html reindirizza a ${page.url()}`);

await page.goto(base, { waitUntil: "networkidle" });
await page.waitForFunction(() => document.querySelectorAll(".js-plotly-plot").length >= 5, null, { timeout: 30000 }).catch(() => {});
check(await page.evaluate(() => !!window.Plotly), "index: Plotly caricato");
const idx = await plotTraces(page, ".chart");
check(idx.length === 5 && idx.every((n) => n > 0), `index: 5 grafici con dati (${idx.join(",")})`);

await page.goto(base + "dinamica.html", { waitUntil: "networkidle" });
await page.waitForTimeout(1500);
const ink = await page.$eval("#cv", (cv) => {
  const d = cv.getContext("2d").getImageData(0, 0, cv.width, cv.height).data;
  let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
  return n;
});
check(ink > 5000, `dinamica: canvas disegnato (${ink} pixel)`);
const flows = await plotTraces(page, "#c-flows");
check(flows[0] === 3, `dinamica: grafico dei flussi con 3 serie (${flows})`);

await page.goto(base + "fase2.html", { waitUntil: "networkidle" });
await page.waitForTimeout(800);
const f2 = await plotTraces(page, ".chart");
// ogni serie è una linea più la sua banda di confidenza
check(f2.length === 2 && f2[0] === 10 && f2[1] === 4, `fase2: bersagli (5 serie) e corsa (2 serie) con dati (${f2})`);
check((await page.$$eval("#t-targets tbody tr", (r) => r.length)) === 5, "fase2: tabella dei 5 bersagli");
await page.$eval("#theta", (el) => { el.value = "0.2"; el.dispatchEvent(new Event("input")); });
check((await page.$eval("#v-y", (e) => e.textContent)).startsWith("+"), "fase2: con θ = 0,2 l'output a fine orizzonte cresce");

for (const [slide, id] of [[9, "c-profile"], [10, "c-B"], [12, "c-classes"], [13, "c-Bshock"]]) {
  await page.goto(`${base}lezione.html#${slide}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  const t = await plotTraces(page, `#${id}`);
  check(t[0] > 0, `lezione: slide ${slide} grafico ${id} con dati (${t})`);
}
check(errors.length === 0, `nessun errore JavaScript${errors.length ? ": " + errors.join(" | ") : ""}`);

await browser.close();
if (failures.length) { console.error(`\n${failures.length} controlli falliti`); process.exit(1); }
console.log("\nTutti i controlli superati");
