/* TestForge Dashboard — app.js
 * Loads reports/summary.json (relative to repo root) and renders the dashboard.
 * All figures come from actual test execution output.
 */

"use strict";

// ── Helpers ──────────────────────────────────────────────────────────────────

function el(id) { return document.getElementById(id); }

function show(id) { el(id).classList.remove("hidden"); }
function hide(id) { el(id).classList.add("hidden"); }

function pct(val) { return `${val}%`; }

function fmtDuration(secs) {
  if (secs < 1) return `${(secs * 1000).toFixed(0)} ms`;
  if (secs < 60) return `${secs.toFixed(1)} s`;
  const m = Math.floor(secs / 60);
  const s = Math.round(secs % 60);
  return `${m}m ${s}s`;
}

function fmtTimestamp(iso) {
  if (!iso || iso === "—") return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });
  } catch { return iso; }
}

function progressFill(pct) {
  let color = "var(--pass)";
  if (pct < 60) color = "var(--fail)";
  else if (pct < 85) color = "var(--skip)";
  return `<div class="progress-bar-bg">
    <div class="progress-bar-fill" style="width:${pct}%;background:${color}"></div>
  </div><span style="font-size:.75rem;color:var(--text-2);margin-left:.4rem">${pct}%</span>`;
}

function coverageFill(pct) {
  let color = "var(--pass)";
  if (pct < 60) color = "var(--fail)";
  else if (pct < 80) color = "var(--skip)";
  return `<div class="progress-bar-bg" style="min-width:80px">
    <div class="cov-bar-fill" style="width:${pct}%;background:${color}"></div>
  </div>`;
}

function statusPill(outcome) {
  const map = {
    passed: '<span class="pill pill-pass">PASS</span>',
    failed: '<span class="pill pill-fail">FAIL</span>',
    skipped:'<span class="pill pill-skip">SKIP</span>',
    error:  '<span class="pill pill-fail">ERROR</span>',
  };
  return map[outcome] || `<span class="pill">${outcome}</span>`;
}

function shortName(nodeId) {
  // e.g. tests/integration/test_auth.py::TestLogin::test_valid_login_returns_200
  const parts = nodeId.split("::");
  return parts[parts.length - 1] || nodeId;
}

// ── Donut chart ───────────────────────────────────────────────────────────────
function updateDonut(passed, failed, skipped, total) {
  if (total === 0) return;
  const circ = 100; // circumference units for r=15.9155
  const passPct = (passed / total) * circ;
  const failPct = (failed / total) * circ;
  const skipPct = (skipped / total) * circ;

  const passEl = el("donut-pass");
  const failEl = el("donut-fail");
  const skipEl = el("donut-skip");

  passEl.style.strokeDasharray = `${passPct} ${circ - passPct}`;
  passEl.style.strokeDashoffset = "0";

  failEl.style.strokeDasharray = `${failPct} ${circ - failPct}`;
  failEl.style.strokeDashoffset = `${-(passPct)}`;

  skipEl.style.strokeDasharray = `${skipPct} ${circ - skipPct}`;
  skipEl.style.strokeDashoffset = `${-(passPct + failPct)}`;
}

// ── Suite table ───────────────────────────────────────────────────────────────
function renderSuites(suites) {
  const tbody = el("suite-tbody");
  if (!suites || suites.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--text-3)">No suite data</td></tr>';
    return;
  }
  tbody.innerHTML = suites.map(s => `
    <tr>
      <td>${s.name}</td>
      <td class="num">${s.total}</td>
      <td class="num pill-num-pass">${s.passed}</td>
      <td class="num ${s.failed > 0 ? "pill-num-fail" : ""}">${s.failed}</td>
      <td class="num ${s.skipped > 0 ? "pill-num-skip" : ""}">${s.skipped}</td>
      <td><div class="progress-wrap">${progressFill(s.pass_rate)}</div></td>
      <td class="num">${fmtDuration(s.duration)}</td>
    </tr>
  `).join("");
}

// ── Coverage table ────────────────────────────────────────────────────────────
function renderCoverage(modules) {
  const tbody = el("coverage-tbody");
  if (!modules || modules.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-3)">No coverage data</td></tr>';
    return;
  }
  tbody.innerHTML = modules.map(m => `
    <tr>
      <td style="font-family:var(--mono);font-size:.8rem">${m.name}</td>
      <td class="num">${m.stmts}</td>
      <td class="num ${m.miss > 0 ? "pill-num-fail" : ""}">${m.miss}</td>
      <td class="num"><strong>${m.cover}%</strong></td>
      <td>${coverageFill(m.cover)}</td>
    </tr>
  `).join("");
}

// ── Failed tests table ────────────────────────────────────────────────────────
function renderFailedTests(failedTests) {
  const badge = el("failed-count-badge");
  badge.textContent = failedTests.length;

  if (failedTests.length === 0) {
    show("failed-empty");
    hide("failed-table-wrap");
    return;
  }
  hide("failed-empty");
  show("failed-table-wrap");

  el("failed-tbody").innerHTML = failedTests.map((t, i) => `
    <tr>
      <td style="font-family:var(--mono);font-size:.75rem;color:var(--text-3)">TC-${String(i + 1).padStart(3, "0")}</td>
      <td style="max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${t.node_id}">${shortName(t.node_id)}</td>
      <td class="num">${fmtDuration(t.duration)}</td>
      <td><span class="pill pill-fail">${t.category}</span></td>
      <td><span class="failure-msg" title="${t.failure_message}">${t.failure_message || "—"}</span></td>
    </tr>
  `).join("");
}

// ── All tests table ───────────────────────────────────────────────────────────
function renderAllTests(tests) {
  el("all-tests-count").textContent = tests.length;
  el("all-tests-tbody").innerHTML = tests.map(t => `
    <tr>
      <td style="font-family:var(--mono);font-size:.78rem;color:var(--text-2)">${t.node_id}</td>
      <td>${t.category}</td>
      <td class="num">${t.duration.toFixed(3)}</td>
      <td>${statusPill(t.outcome)}</td>
    </tr>
  `).join("");
}

// ── Toggle all-tests section ──────────────────────────────────────────────────
function toggleAllTests() {
  const content = el("all-tests-content");
  const arrow   = el("all-tests-toggle");
  if (content.classList.contains("hidden")) {
    content.classList.remove("hidden");
    arrow.textContent = "▼";
  } else {
    content.classList.add("hidden");
    arrow.textContent = "▶";
  }
}
window.toggleAllTests = toggleAllTests; // expose for onclick

// ── Main render ───────────────────────────────────────────────────────────────
function render(data) {
  // KPI cards
  el("kpi-total").textContent    = data.total;
  el("kpi-passed").textContent   = data.passed;
  el("kpi-failed").textContent   = data.failed;
  el("kpi-skipped").textContent  = data.skipped;
  el("kpi-rate").textContent     = pct(data.pass_rate);
  el("kpi-coverage").textContent = pct(data.coverage_total);
  el("kpi-coverage-scope").textContent = data.coverage_scope || "";
  el("kpi-duration").textContent = fmtDuration(data.duration);

  // Trend arrow colour
  const trend = el("kpi-trend");
  if (data.pass_rate >= 90) {
    trend.textContent = "↑";
    trend.style.color = "var(--pass)";
  } else if (data.pass_rate >= 70) {
    trend.textContent = "→";
    trend.style.color = "var(--skip)";
  } else {
    trend.textContent = "↓";
    trend.style.color = "var(--fail)";
  }

  // Timestamp
  const ts = fmtTimestamp(data.timestamp);
  el("run-timestamp").textContent = ts ? `Run: ${ts}` : "—";
  el("footer-timestamp").textContent = ts;

  updateDonut(data.passed, data.failed, data.skipped, data.total);
  renderSuites(data.suites);
  renderCoverage(data.coverage_modules);
  renderFailedTests(data.failed_tests || []);
  renderAllTests(data.all_tests || []);
}

// ── Data loading ──────────────────────────────────────────────────────────────
async function loadData() {
  hide("dashboard");
  hide("error-state");
  show("loading-state");

  // Try multiple paths so the dashboard works both when opened from
  // the dashboard/ folder and from the repo root.
  const candidates = [
    "../reports/summary.json",
    "./reports/summary.json",
    "reports/summary.json",
  ];

  let data = null;
  for (const path of candidates) {
    try {
      const res = await fetch(path, { cache: "no-store" });
      if (res.ok) {
        data = await res.json();
        break;
      }
    } catch {
      // try next
    }
  }

  hide("loading-state");

  if (!data) {
    show("error-state");
    return;
  }

  render(data);
  show("dashboard");
}

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", loadData);
