/* ═══════════════════════════════════════════════════════════
   MAIN.JS — Shared utilities across all pages
   Matrix rain, clock, toast, API helpers, logger controls
   ═══════════════════════════════════════════════════════════ */
const API = 'http://localhost:5000/api';
/* ─── Clock ──────────────────────────────────────────────── */
function updateClock() {
  const el = document.getElementById('current-time');
  if (el) el.textContent = new Date().toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();
/* ─── Toast Notifications ────────────────────────────────── */
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'fadeIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
/* ─── API Helpers ────────────────────────────────────────── */
async function apiFetch(endpoint, options = {}) {
  try {
    const res = await fetch(API + endpoint, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`[API] ${endpoint}:`, err.message);
    return null;
  }
}
/* ─── Logger Controls ────────────────────────────────────── */
async function startLogger() {
  const data = await apiFetch('/start', { method: 'POST' });
  if (data && data.status === 'started') {
    showToast('Keylogger started successfully!', 'success');
    updateRunningUI(true);
  } else if (data && data.status === 'already_running') {
    showToast('Logger is already running.', 'warning');
  } else {
    showToast('Could not reach backend. Is server.py running?', 'error');
  }
}
async function stopLogger() {
  const data = await apiFetch('/stop', { method: 'POST' });
  if (data) {
    showToast('Keylogger stopped.', 'info');
    updateRunningUI(false);
  }
}
async function clearLogs() {
  if (!confirm('⚠️ Delete ALL log files? This cannot be undone.')) return;
  const data = await apiFetch('/clear', { method: 'DELETE' });
  if (data) {
    showToast('All logs cleared.', 'success');
    setTimeout(() => location.reload(), 1000);
  }
}
function updateRunningUI(isRunning) {
  const btnStart = document.getElementById('btn-start');
  const btnStop  = document.getElementById('btn-stop');
  const sidebarStatus = document.getElementById('sidebar-status');
  if (btnStart) btnStart.style.display = isRunning ? 'none' : 'flex';
  if (btnStop)  btnStop.style.display  = isRunning ? 'flex' : 'none';
  if (sidebarStatus) {
    sidebarStatus.className = `status-badge ${isRunning ? 'online' : 'offline'}`;
    sidebarStatus.innerHTML = `<span class="status-dot"></span>${isRunning ? 'LIVE' : 'IDLE'}`;
  }
  // Session badge on dashboard
  const badge = document.getElementById('session-status-badge');
  if (badge) {
    badge.className = `badge ${isRunning ? 'badge-green' : 'badge-orange'}`;
    badge.textContent = isRunning ? 'RUNNING' : 'IDLE';
  }
  // Live badge on monitor
  ['live-badge', 'live-badge-2'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = isRunning ? 'flex' : 'none';
  });
}
/* ─── Poll status on load ────────────────────────────────── */
async function pollStatus() {
  const data = await apiFetch('/status');
  if (!data) return;
  updateRunningUI(data.is_running);
  // Update session info panel (dashboard)
  const elId    = document.getElementById('session-id');
  const elStart = document.getElementById('session-start');
  const elRun   = document.getElementById('session-running');
  if (elId)    elId.textContent    = data.session_id   || '—';
  if (elStart) elStart.textContent = data.start_time
    ? new Date(data.start_time).toLocaleString() : '—';
  if (elRun) {
    elRun.innerHTML = data.is_running
      ? '<span class="badge badge-green">RUNNING</span>'
      : '<span class="badge badge-orange">IDLE</span>';
  }
}
pollStatus();
setInterval(pollStatus, 5000);
/* ─── Matrix Rain ────────────────────────────────────────── */
(function initMatrix() {
  const canvas = document.getElementById('matrix-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);
  const chars = '01アイウエオカキクケコサシスセソタチツテトABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*';
  const fontSize = 13;
  let columns = Math.floor(canvas.width / fontSize);
  let drops = Array(columns).fill(1);
  function draw() {
    ctx.fillStyle = 'rgba(2, 11, 26, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#00d4ff';
    ctx.font = `${fontSize}px JetBrains Mono, monospace`;
    columns = Math.floor(canvas.width / fontSize);
    while (drops.length < columns) drops.push(Math.random() * canvas.height / fontSize);
    for (let i = 0; i < drops.length; i++) {
      const char = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillText(char, i * fontSize, drops[i] * fontSize);
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
  }
  setInterval(draw, 60);
})();
