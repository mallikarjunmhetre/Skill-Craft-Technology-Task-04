/* ═══════════════════════════════════════════════════════════
   REPORTS.JS — Paginated log table, search/filter, exports
   ═══════════════════════════════════════════════════════════ */
let allRecords  = [];
let filtered    = [];
let currentPage = 1;
let perPage     = 50;
/* ─── Escape HTML ────────────────────────────────────────── */
function escapeHtml(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
/* ─── Load all records ───────────────────────────────────── */
async function loadRecords() {
  const data = await apiFetch('/logs/export');
  if (!data || !Array.isArray(data)) {
    allRecords = [];
    filtered   = [];
  } else {
    allRecords = data;
    filtered   = [...data];
  }
  currentPage = 1;
  renderTable();
}
/* ─── Apply filter + search ──────────────────────────────── */
function applyReportFilter() {
  const search  = (document.getElementById('search-key')?.value || '').toLowerCase().trim();
  const keyType = document.getElementById('filter-key-type')?.value || 'all';
  perPage       = parseInt(document.getElementById('per-page')?.value) || 50;
  filtered = allRecords.filter(r => {
    const matchType   = keyType === 'all' || r.type === keyType;
    const display     = (r.display || r.key || '').toLowerCase();
    const matchSearch = !search || display.includes(search);
    return matchType && matchSearch;
  });
  currentPage = 1;
  renderTable();
  showToast(`Filter applied — ${filtered.length.toLocaleString()} entries`, 'info');
}
function resetFilter() {
  document.getElementById('search-key').value        = '';
  document.getElementById('filter-key-type').value   = 'all';
  document.getElementById('per-page').value          = '50';
  filtered    = [...allRecords];
  currentPage = 1;
  perPage     = 50;
  renderTable();
}
/* ─── Render paginated table ─────────────────────────────── */
function renderTable() {
  const tbody       = document.getElementById('log-table-body');
  const totalBadge  = document.getElementById('total-badge');
  const pageInfoEl  = document.getElementById('page-info');
  const curPageEl   = document.getElementById('current-page');
  const totalPagesEl = document.getElementById('total-pages');
  const btnPrev     = document.getElementById('btn-prev');
  const btnNext     = document.getElementById('btn-next');
  const total      = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / perPage));
  if (totalBadge)   totalBadge.textContent = `${total.toLocaleString()} entries`;
  if (curPageEl)    curPageEl.textContent   = currentPage;
  if (totalPagesEl) totalPagesEl.textContent = totalPages;
  if (pageInfoEl)   pageInfoEl.textContent  =
    `Showing ${Math.min((currentPage-1)*perPage+1, total)}–${Math.min(currentPage*perPage, total)} of ${total.toLocaleString()}`;
  if (btnPrev) btnPrev.disabled = currentPage <= 1;
  if (btnNext) btnNext.disabled = currentPage >= totalPages;
  if (!tbody) return;
  if (total === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-muted);">
      No records found. Adjust your filter or start the keylogger.
    </td></tr>`;
    return;
  }
  const start   = (currentPage - 1) * perPage;
  const pageRows = filtered.slice(start, start + perPage);
  tbody.innerHTML = pageRows.map((r, i) => {
    const rowNum   = start + i + 1;
    const isSpecial = r.type === 'special';
    const isBs     = r.is_backspace;
    return `<tr>
      <td class="mono text-muted text-xs">${rowNum.toLocaleString()}</td>
      <td class="mono text-xs" style="color:var(--text-muted);">${escapeHtml(r.timestamp || '—')}</td>
      <td class="mono" style="font-size:13px;color:var(--text-primary);">${escapeHtml(r.key || '—')}</td>
      <td>
        <span style="font-family:var(--font-mono);font-size:13px;
          color:${isSpecial ? 'var(--neon-orange)' : 'var(--neon-green)'};">
          ${escapeHtml(r.display || r.key || '—')}
        </span>
      </td>
      <td>
        <span class="badge ${isSpecial ? 'badge-purple' : 'badge-green'}" style="font-size:10px;">
          ${escapeHtml(r.type || '—')}
        </span>
      </td>
      <td>
        ${isBs
          ? '<span class="badge badge-red" style="font-size:10px;">YES</span>'
          : '<span class="text-muted text-xs">—</span>'}
      </td>
      <td class="mono text-xs" style="color:var(--text-muted);max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
        ${escapeHtml((r.session_id || '—').slice(-12))}
      </td>
    </tr>`;
  }).join('');
}
/* ─── Pagination ─────────────────────────────────────────── */
function prevPage() {
  if (currentPage > 1) { currentPage--; renderTable(); }
}
function nextPage() {
  const totalPages = Math.ceil(filtered.length / perPage);
  if (currentPage < totalPages) { currentPage++; renderTable(); }
}
/* ─── Export helpers ─────────────────────────────────────── */
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 500);
}
function exportJSON() {
  if (!allRecords.length) { showToast('No data to export.', 'warning'); return; }
  const ts = new Date().toISOString().slice(0,19).replace(/:/g,'-');
  downloadFile(
    JSON.stringify(allRecords, null, 2),
    `keystrokes_${ts}.json`,
    'application/json'
  );
  showToast(`Exported ${allRecords.length.toLocaleString()} records as JSON`, 'success');
}
function exportCSV() {
  if (!allRecords.length) { showToast('No data to export.', 'warning'); return; }
  const headers = ['timestamp', 'key', 'display', 'type', 'is_backspace', 'session_id'];
  const rows    = allRecords.map(r =>
    headers.map(h => `"${String(r[h] ?? '').replace(/"/g, '""')}"`).join(',')
  );
  const csv = [headers.join(','), ...rows].join('\r\n');
  const ts  = new Date().toISOString().slice(0,19).replace(/:/g,'-');
  downloadFile(csv, `keystrokes_${ts}.csv`, 'text/csv;charset=utf-8');
  showToast(`Exported ${allRecords.length.toLocaleString()} records as CSV`, 'success');
}
async function exportTXT() {
  const data = await apiFetch('/logs/text');
  if (!data || !data.lines?.length) { showToast('No text log available.', 'warning'); return; }
  const ts = new Date().toISOString().slice(0,19).replace(/:/g,'-');
  downloadFile(data.lines.join('\n'), `keystrokes_${ts}.txt`, 'text/plain');
  showToast(`Exported ${data.lines.length.toLocaleString()} lines as TXT`, 'success');
}
/* ─── Init ───────────────────────────────────────────────── */
loadRecords();
setInterval(loadRecords, 5000);
