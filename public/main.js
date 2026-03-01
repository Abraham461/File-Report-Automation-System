const templateSelect = document.getElementById('templateSelect');
const metadataInput = document.getElementById('metadataInput');
const filesInput = document.getElementById('filesInput');
const eventsInput = document.getElementById('eventsInput');
const previewBtn = document.getElementById('previewBtn');
const saveBtn = document.getElementById('saveBtn');
const preview = document.getElementById('preview');
const downloadLinks = document.getElementById('downloadLinks');
const historyList = document.getElementById('historyList');
const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

let latestReport = null;

metadataInput.value = JSON.stringify({ reportDate: '2026-03-01', preparedBy: 'Automation Bot' }, null, 2);
filesInput.value = JSON.stringify(
  [
    { name: 'contract-001.pdf', owner: 'legal', category: 'contract', size: '120KB', sizeBytes: 120000, status: 'approved' },
    { name: 'invoice-2026-03.csv', owner: 'finance', category: 'invoice', size: '80KB', sizeBytes: 80000, status: 'pending' }
  ],
  null,
  2
);
eventsInput.value = JSON.stringify(
  [
    { timestamp: '2026-03-01T08:00:00Z', actor: 'jane.doe', type: 'view', target: 'contract-001.pdf' },
    { timestamp: '2026-03-01T08:05:00Z', actor: 'admin', type: 'permission-change', target: 'finance-folder' }
  ],
  null,
  2
);

async function loadTemplates() {
  const response = await fetch('/api/report-templates');
  const data = await response.json();

  templateSelect.innerHTML = data.templates
    .map((template) => `<option value="${template.id}">${template.title} — ${template.description}</option>`)
    .join('');
}

function parseJson(text, fallback) {
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

function selectedFormats() {
  return [...document.querySelectorAll('input[type="checkbox"]:checked')].map((input) => input.value);
}

function buildPayload() {
  return {
    templateId: templateSelect.value,
    metadata: parseJson(metadataInput.value, {}),
    files: parseJson(filesInput.value, []),
    activityEvents: parseJson(eventsInput.value, []),
    exportFormats: selectedFormats()
  };
}

previewBtn.addEventListener('click', async () => {
  const payload = buildPayload();

  const response = await fetch('/api/reports/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await response.json();

  if (!response.ok) {
    preview.textContent = data.error;
    return;
  }

  latestReport = data.report;
  saveBtn.disabled = false;
  preview.textContent = latestReport.fullText;
});

saveBtn.addEventListener('click', () => {
  if (!latestReport) {
    return;
  }

  downloadLinks.innerHTML = latestReport.exports
    .map((entry) => `<a href="${entry.downloadUrl}">Download ${entry.format.toUpperCase()}</a>`)
    .join('');

  refreshHistory();
});

async function refreshHistory() {
  const response = await fetch('/api/reports/history');
  const data = await response.json();

  historyList.innerHTML = data.history
    .map(
      (record) =>
        `<li><strong>${record.title}</strong> (${record.templateId}) — ${record.generatedAt} — exports: ${record.exports.join(', ')}</li>`
    )
    .join('');
}

refreshHistoryBtn.addEventListener('click', refreshHistory);

await loadTemplates();
await refreshHistory();
