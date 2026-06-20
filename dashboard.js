/* ═══════════════════════════════════════════════════════════
   DASHBOARD.JS — index.html charts, stats, live preview feed
   ═══════════════════════════════════════════════════════════ */
let donutChart = null;
/* ─── Update stat counters ───────────────────────────────── */
function updateStats(data) {
  animateCount('stat-total',      data.total_keystrokes || 0);
  animateCount('stat-regular',    data.regular_keys     || 0);
  animateCount('stat-special',    data.special_keys     || 0);
  animateCount('stat-backspaces', data.backspaces       || 0);
}
function animateCount(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const current = parseInt(el.textContent.replace(/,/g, '')) || 0;
  if (current === target) return;
  const step = Math.ceil(Math.abs(target - current) / 12);
  let val = current;
  const interval = setInterval(() => {
    val = val < target ? Math.min(val + step, target) : Math.max(val - step, target);
    el.textContent = val.toLocaleString();
    if (val === target) clearInterval(interval);
  }, 40);
}
/* ─── Donut Chart ────────────────────────────────────────── */
function initDonutChart() {
  const ctx = document.getElementById('donutChart');
  if (!ctx) return;
  donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Regular Keys', 'Special Keys', 'Backspaces'],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: [
          'rgba(0, 255, 136, 0.7)',
          'rgba(168, 85, 247, 0.7)',
          'rgba(255, 51, 102, 0.7)'
        ],
        borderColor: [
          'rgba(0, 255, 136, 0.9)',
          'rgba(168, 85, 247, 0.9)',
          'rgba(255, 51, 102, 0.9)'
        ],
        borderWidth: 2,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#7ab3cc',
            font: { family: 'JetBrains Mono', size: 12 },
            padding: 16,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(5,25,55,0.95)',
          borderColor: 'rgba(0,212,255,0.3)',
          borderWidth: 1,
          titleColor: '#e2f4ff',
          bodyColor: '#7ab3cc',
          padding: 12,
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed.toLocaleString()}`
          }
        }
      }
    }
  });
}
function updateDonut(regular, special, backspaces) {
  if (!donutChart) return;
  donutChart.data.datasets[0].data = [regular, special, backspaces];
  donutChart.update('active');
}
/* ─── Top Keys List ──────────────────────────────────────── */
function renderTopKeys(topKeys) {
  const container = document.getElementById('top-keys-list');
  if (!container || !topKeys || topKeys.length === 0) return;
  const max = topKeys[0]?.count || 1;
  const colors = ['cyan', 'green', 'purple', 'orange', 'red'];
  container.innerHTML = topKeys.slice(0, 8).map((item, i) => {
    const pct = Math.round((item.count / max) * 100);
    const color = colors[i % colors.length];
    return `
      <div class="progress-bar-wrap">
        <div class="progress-label">${escapeHtml(item.key)}</div>
        <div class="progress-track">
          <div class="progress-fill ${color}" style="width:${pct}%"></div>
        </div>
        <div class="progress-count">${item.count}</div>
      </div>`;
  }).join('');
}
/* ─── Recent feed preview ────────────────────────────────── */
let lastFeedCount = 0;
function updateRecentFeed(keystrokes) {
  const feed = document.getElementById('recent-feed');
  if (!feed || keystrokes.length === lastFeedCount) return;
  const newKeys = keystrokes.slice(lastFeedCount);
  lastFeedCount = keystrokes.length;
  newKeys.forEach(record => {
    const line = document.createElement('div');
    line.className = 'terminal-line';
    const cls = record.type === 'special' ? 't-key-special' : 't-key-regular';
    const ts  = record.timestamp ? record.timestamp.split(' ')[1]?.slice(0,8) : '';
    line.innerHTML = `
      <span class="t-timestamp">${ts}</span>
      <span class="${cls}">${escapeHtml(record.display)}</span>`;
    feed.appendChild(line);
  });
  // Keep last 40 lines
  while (feed.children.length > 40) feed.removeChild(feed.firstChild);
  feed.scrollTop = feed.scrollHeight;
}
/* ─── Main Refresh ───────────────────────────────────────── */
async function refreshCharts() {
  const [status, analytics, live] = await Promise.all([
    apiFetch('/status'),
    apiFetch('/analytics'),
    apiFetch('/live?n=50')
  ]);
  if (status) updateStats(status);
  if (analytics) {
    updateDonut(
      analytics.regular_keys || 0,
      analytics.special_keys || 0,
      0
    );
    renderTopKeys(analytics.top_keys || []);
  }
  if (live && live.keystrokes) {
    updateRecentFeed(live.keystrokes);
  }
}
/* ─── Escape HTML ────────────────────────────────────────── */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
/* ─── Init ───────────────────────────────────────────────── */
initDonutChart();
refreshCharts();
setInterval(refreshCharts, 3000);
