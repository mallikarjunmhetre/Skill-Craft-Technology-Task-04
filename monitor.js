/* ═══════════════════════════════════════════════════════════
   MONITOR.JS — Live keystroke feed, key bubbles, KPM meter
   ═══════════════════════════════════════════════════════════ */
let isPaused        = false;
let filterType      = 'all';
let lastSeenCount   = 0;
let feedEntryCount  = 0;
let kpmWindow       = [];   // timestamps for rolling KPM
const MAX_BUBBLES   = 24;
const MAX_FEED_ROWS = 200;
/* ─── Escape HTML ────────────────────────────────────────── */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
/* ─── Pause / Resume ─────────────────────────────────────── */
function togglePause() {
  isPaused = !isPaused;
  const btn = document.getElementById('btn-pause');
  const el  = document.getElementById('pause-status');
  if (btn) {
    btn.innerHTML = isPaused
      ? '<i class="fas fa-play"></i> Resume Feed'
      : '<i class="fas fa-pause"></i> Pause Feed';
  }
  if (el) el.textContent = isPaused ? 'Yes' : 'No';
}
/* ─── Clear the terminal view ────────────────────────────── */
function clearFeed() {
  const feed = document.getElementById('live-feed');
  if (feed) feed.innerHTML = '';
  feedEntryCount = 0;
  lastSeenCount  = 0;
  document.getElementById('feed-count').textContent = '0';
  document.getElementById('key-bubbles').innerHTML  = '';
  kpmWindow = [];
}
/* ─── Filter type ────────────────────────────────────────── */
function applyFilter() {
  filterType = document.getElementById('filter-type')?.value || 'all';
}
/* ─── Compute KPM (keys per minute, rolling 60 s) ───────── */
function computeKPM() {
  const now = Date.now();
  kpmWindow = kpmWindow.filter(t => now - t < 60000);
  return kpmWindow.length;
}
/* ─── Add a line to the live terminal ───────────────────── */
function addFeedLine(record) {
  const feed = document.getElementById('live-feed');
  if (!feed) return;
  const isSpecial = record.type === 'special';
  const keyCls    = isSpecial ? 't-key-special' : 't-key-regular';
  const ts        = record.timestamp
    ? record.timestamp.split(' ')[1]?.slice(0, 12) || ''
    : '';
  const line = document.createElement('div');
  line.className = 'terminal-line';
  line.innerHTML = `
    <span class="t-timestamp">${ts}</span>
    <span class="t-prefix">›</span>
    <span class="${keyCls}">${escapeHtml(record.display)}</span>
    <span class="badge ${isSpecial ? 'badge-orange' : 'badge-green'}" style="font-size:10px;padding:2px 6px;margin-left:8px;">${record.type}</span>`;
  feed.appendChild(line);
  feedEntryCount++;
  // Trim old rows
  while (feed.children.length > MAX_FEED_ROWS) feed.removeChild(feed.firstChild);
  feed.scrollTop = feed.scrollHeight;
  const countEl = document.getElementById('feed-count');
  if (countEl) countEl.textContent = feedEntryCount;
}
/* ─── Update "Last Key" big display ─────────────────────── */
function updateLastKey(record) {
  const display = document.getElementById('last-key-display');
  const typeEl  = document.getElementById('last-key-type');
  if (!display) return;
  const isSpecial = record.type === 'special';
  display.style.color = isSpecial
    ? 'var(--neon-orange)'
    : 'var(--neon-green)';
  display.style.textShadow = isSpecial
    ? '0 0 30px rgba(255,140,0,0.6)'
    : '0 0 30px rgba(0,255,136,0.6)';
  display.textContent = escapeHtml(record.display).slice(0, 8);
  if (typeEl) {
    typeEl.className = `badge ${isSpecial ? 'badge-orange' : 'badge-green'} mt-8`;
    typeEl.textContent = isSpecial ? 'SPECIAL' : 'REGULAR';
    typeEl.style.margin = 'auto';
  }
}
/* ─── Add a key bubble ───────────────────────────────────── */
function addKeyBubble(record) {
  const container = document.getElementById('key-bubbles');
  if (!container) return;
  const bubble = document.createElement('div');
  bubble.className = `key-bubble ${record.type === 'special' ? 'special' : ''}`;
  bubble.textContent = escapeHtml(record.display).slice(0, 6);
  container.appendChild(bubble);
  // Keep only last MAX_BUBBLES
  while (container.children.length > MAX_BUBBLES) {
    container.removeChild(container.firstChild);
  }
}
/* ─── Update KPM bar ─────────────────────────────────────── */
function updateKPM() {
  const kpm    = computeKPM();
  const kpmEl  = document.getElementById('kpm');
  const kpmBar = document.getElementById('kpm-bar');
  if (kpmEl)  kpmEl.textContent = kpm;
  if (kpmBar) kpmBar.style.width = Math.min(kpm / 3, 100) + '%'; // 300 KPM = 100%
}
/* ─── Update mini stat cards ─────────────────────────────── */
function updateMiniStats(data) {
  const ids = { 'm-total': 'total_keystrokes', 'm-regular': 'regular_keys',
                'm-special': 'special_keys',   'm-backspaces': 'backspaces' };
  Object.entries(ids).forEach(([elId, key]) => {
    const el = document.getElementById(elId);
    if (el) el.textContent = (data[key] || 0).toLocaleString();
  });
}
/* ─── Main polling loop ──────────────────────────────────── */
async function pollLiveFeed() {
  const [status, live] = await Promise.all([
    apiFetch('/status'),
    apiFetch('/live?n=100')
  ]);
  if (status) updateMiniStats(status);
  if (!live || isPaused) return;
  const allKeys = live.keystrokes || [];
  const total   = live.total || 0;
  // Find genuinely new records
  const newKeys = allKeys.filter(r => {
    const index = allKeys.indexOf(r);
    return index >= allKeys.length - (total - lastSeenCount);
  });
  // Simpler: just process keys we haven't shown yet by comparing total
  if (total > lastSeenCount) {
    const newCount   = total - lastSeenCount;
    const toShow     = allKeys.slice(Math.max(0, allKeys.length - newCount));
    toShow.forEach(record => {
      if (filterType !== 'all' && record.type !== filterType) return;
      addFeedLine(record);
      updateLastKey(record);
      addKeyBubble(record);
      kpmWindow.push(Date.now());
    });
    lastSeenCount = total;
  }
  updateKPM();
}
/* ─── Init ───────────────────────────────────────────────── */
pollLiveFeed();
setInterval(pollLiveFeed, 1000);
setInterval(updateKPM, 5000);
