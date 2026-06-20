/* ═══════════════════════════════════════════════════════════
   ANALYTICS.JS — Charts, heatmap, frequency bars
   ═══════════════════════════════════════════════════════════ */
let topKeysChart = null;
let typeDonut    = null;
let hourlyChart  = null;
/* ─── Escape HTML ────────────────────────────────────────── */
function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
/* ─── Chart defaults ─────────────────────────────────────── */
const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#7ab3cc', font: { family: 'JetBrains Mono', size: 11 }, padding: 14 }
    },
    tooltip: {
      backgroundColor: 'rgba(5,25,55,0.95)',
      borderColor: 'rgba(0,212,255,0.3)',
      borderWidth: 1,
      titleColor: '#e2f4ff',
      bodyColor: '#7ab3cc',
      padding: 12
    }
  }
};
/* ─── Init Top Keys Bar Chart ────────────────────────────── */
function initTopKeysChart() {
  const ctx = document.getElementById('topKeysChart');
  if (!ctx) return;
  topKeysChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Press Count',
        data: [],
        backgroundColor: (ctx) => {
          const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 300);
          g.addColorStop(0, 'rgba(0, 212, 255, 0.85)');
          g.addColorStop(1, 'rgba(0, 212, 255, 0.15)');
          return g;
        },
        borderColor: 'rgba(0, 212, 255, 0.9)',
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false
      }]
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,212,255,0.05)' },
          ticks: { color: '#7ab3cc', font: { family: 'JetBrains Mono', size: 11 } }
        },
        y: {
          grid: { color: 'rgba(0,212,255,0.05)' },
          ticks: { color: '#e2f4ff', font: { family: 'JetBrains Mono', size: 12 }, maxTicksLimit: 15 }
        }
      }
    }
  });
}
/* ─── Init Type Doughnut Chart ───────────────────────────── */
function initTypeDonut() {
  const ctx = document.getElementById('typeDonut');
  if (!ctx) return;
  typeDonut = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Regular Keys', 'Special Keys'],
      datasets: [{
        data: [0, 0],
        backgroundColor: ['rgba(0,255,136,0.75)', 'rgba(168,85,247,0.75)'],
        borderColor:      ['rgba(0,255,136,0.9)',  'rgba(168,85,247,0.9)'],
        borderWidth: 2,
        hoverOffset: 8
      }]
    },
    options: {
      ...CHART_DEFAULTS,
      cutout: '65%',
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: {
          position: 'bottom',
          labels: { color: '#7ab3cc', font: { family: 'JetBrains Mono', size: 12 }, padding: 16, usePointStyle: true }
        }
      }
    }
  });
}
/* ─── Init Hourly Bar Chart ──────────────────────────────── */
function initHourlyChart() {
  const ctx = document.getElementById('hourlyChart');
  if (!ctx) return;
  hourlyChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2,'0')}:00`),
      datasets: [{
        label: 'Keystrokes',
        data: Array(24).fill(0),
        backgroundColor: (ctx) => {
          const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 280);
          g.addColorStop(0, 'rgba(255,140,0,0.8)');
          g.addColorStop(1, 'rgba(255,140,0,0.1)');
          return g;
        },
        borderColor: 'rgba(255,140,0,0.9)',
        borderWidth: 1,
        borderRadius: 3
      }]
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,212,255,0.04)' },
          ticks: { color: '#7ab3cc', font: { family: 'JetBrains Mono', size: 10 }, maxRotation: 45 }
        },
        y: {
          grid: { color: 'rgba(0,212,255,0.05)' },
          ticks: { color: '#7ab3cc', font: { family: 'JetBrains Mono', size: 11 } }
        }
      }
    }
  });
}
/* ─── Keyboard Heatmap (visual rows) ─────────────────────── */
const KB_ROWS = [
  ['`','1','2','3','4','5','6','7','8','9','0','-','='],
  ['q','w','e','r','t','y','u','i','o','p','[',']','\\'],
  ['a','s','d','f','g','h','j','k','l',';',"'"],
  ['z','x','c','v','b','n','m',',','.','/']
];
function renderKeyboardHeatmap(freqMap) {
  const container = document.getElementById('keyboard-heatmap');
  if (!container) return;
  const maxCount = Math.max(...Object.values(freqMap), 1);
  const html = KB_ROWS.map(row => {
    const keys = row.map(k => {
      const count = freqMap[k] || 0;
      const pct   = count / maxCount;
      const alpha = (0.05 + pct * 0.85).toFixed(2);
      const textColor = pct > 0.5 ? '#020b1a' : '#00d4ff';
      const bg = `rgba(0,212,255,${alpha})`;
      const size = count > 0
        ? `title="${k}: ${count} presses"`
        : '';
      return `<span ${size} style="
        display:inline-flex;align-items:center;justify-content:center;
        width:34px;height:34px;margin:2px;border-radius:5px;
        font-size:12px;font-weight:600;cursor:default;
        background:${bg};color:${textColor};
        border:1px solid rgba(0,212,255,${Math.min(pct + 0.1, 0.5).toFixed(2)});
        transition:all 0.3s ease;
      ">${escapeHtml(k)}</span>`;
    }).join('');
    return `<div style="margin-bottom:4px;white-space:nowrap;">${keys}</div>`;
  }).join('');
  container.innerHTML = html;
}
/* ─── Frequency Bars (detail list) ──────────────────────── */
function renderFreqBars(topKeys) {
  const container = document.getElementById('freq-bars');
  if (!container || !topKeys.length) return;
  const max    = topKeys[0]?.count || 1;
  const colors = ['cyan','green','purple','orange','red','cyan','green','purple','orange','red',
                  'cyan','green','purple','orange','red','cyan','green','purple','orange','red'];
  const total  = topKeys.reduce((s, k) => s + k.count, 0);
  container.innerHTML = topKeys.slice(0, 20).map((item, i) => {
    const pct  = Math.round((item.count / max) * 100);
    const share = ((item.count / total) * 100).toFixed(1);
    return `
      <div class="progress-bar-wrap" style="margin-bottom:12px;align-items:center;">
        <div class="progress-label" style="min-width:70px;text-align:right;font-size:13px;color:var(--text-primary);">
          ${escapeHtml(item.key)}
        </div>
        <div class="progress-track" style="flex:1;">
          <div class="progress-fill ${colors[i]}" style="width:${pct}%;"></div>
        </div>
        <div class="progress-count" style="min-width:60px;display:flex;gap:8px;align-items:center;">
          <span>${item.count.toLocaleString()}</span>
          <span class="text-muted text-xs">${share}%</span>
        </div>
      </div>`;
  }).join('');
}
/* ─── Load & render analytics ────────────────────────────── */
async function loadAnalytics() {
  const btn = document.getElementById('btn-refresh');
  if (btn) { btn.innerHTML = '<i class="fas fa-sync animate-spin"></i> Refreshing…'; btn.disabled = true; }
  const data = await apiFetch('/analytics');
  if (btn) { btn.innerHTML = '<i class="fas fa-sync"></i> Refresh'; btn.disabled = false; }
  if (!data || data.error) {
    showToast('No log data found. Start the keylogger first.', 'warning');
    return;
  }
  // Summary stats
  ['a-total', 'a-regular', 'a-special'].forEach(id => {
    const map = { 'a-total': 'total_keystrokes', 'a-regular': 'regular_keys', 'a-special': 'special_keys' };
    const el = document.getElementById(id);
    if (el) el.textContent = (data[map[id]] || 0).toLocaleString();
  });
  const total   = data.total_keystrokes || 0;
  const regular = data.regular_keys || 0;
  const special = data.special_keys || 0;
  const accEl = document.getElementById('a-accuracy');
  if (accEl) accEl.textContent = total > 0 ? ((regular / total) * 100).toFixed(1) + '%' : '—%';
  const pctReg = document.getElementById('pct-regular');
  const pctSpc = document.getElementById('pct-special');
  if (pctReg) pctReg.textContent = total > 0 ? ((regular / total) * 100).toFixed(1) + '%' : '—%';
  if (pctSpc) pctSpc.textContent = total > 0 ? ((special / total) * 100).toFixed(1) + '%' : '—%';
  // Top Keys chart
  const topKeys = data.top_keys || [];
  if (topKeysChart) {
    topKeysChart.data.labels   = topKeys.slice(0, 15).map(k => k.key);
    topKeysChart.data.datasets[0].data = topKeys.slice(0, 15).map(k => k.count);
    topKeysChart.update();
  }
  // Type donut
  if (typeDonut) {
    typeDonut.data.datasets[0].data = [regular, special];
    typeDonut.update();
  }
  // Hourly chart
  const hourly = data.hourly_distribution || [];
  if (hourlyChart && hourly.length) {
    hourlyChart.data.datasets[0].data = hourly.map(h => h.count);
    hourlyChart.update();
  }
  // Build freq map from topKeys for heatmap
  const freqMap = {};
  topKeys.forEach(k => { freqMap[k.key.toLowerCase()] = k.count; });
  renderKeyboardHeatmap(freqMap);
  renderFreqBars(topKeys);
}
/* ─── Init ───────────────────────────────────────────────── */
initTopKeysChart();
initTypeDonut();
initHourlyChart();
loadAnalytics();
setInterval(loadAnalytics, 8000);
