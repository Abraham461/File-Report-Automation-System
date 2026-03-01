const form = document.getElementById('search-form');
const resultsEl = document.getElementById('results');
const statusEl = document.getElementById('status');
const resetBtn = document.getElementById('reset');

function fillSelect(id, values) {
  const select = document.getElementById(id);
  for (const value of values) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }
}

async function loadFilters() {
  const res = await fetch('/api/filters');
  const data = await res.json();
  fillSelect('uploader', data.uploaders);
  fillSelect('category', data.categories);
  fillSelect('fileType', data.fileTypes);
}

function renderResults(items, searchMode) {
  resultsEl.innerHTML = '';

  if (!items.length) {
    const li = document.createElement('li');
    li.className = 'empty';
    li.textContent = 'No files matched your search criteria. Try removing some filters or using broader terms.';
    resultsEl.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${item.title}</strong> <span class="meta">(${item.filename})</span>
      <div>${item.description || ''}</div>
      <div class="meta">
        tags: ${item.tags || '-'} • uploader: ${item.uploader} • category: ${item.category} • type: ${item.file_type} • date: ${item.uploaded_at}
      </div>
      <div class="meta">mode: ${searchMode}</div>
    `;
    resultsEl.appendChild(li);
  });
}

async function runSearch() {
  const data = new FormData(form);
  const params = new URLSearchParams();
  for (const [key, value] of data.entries()) {
    if (value) {
      params.set(key, value);
    }
  }

  const queryActive = Array.from(params.keys()).length > 0;
  if (!queryActive) {
    statusEl.textContent = 'Empty state: enter a keyword and/or choose filters to start searching.';
    resultsEl.innerHTML = '<li class="empty">No search has been run yet.</li>';
    return;
  }

  const res = await fetch(`/api/search?${params.toString()}`);
  const payload = await res.json();

  statusEl.textContent = `${payload.total} result(s) found.`;
  renderResults(payload.results, payload.searchMode);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  await runSearch();
});

resetBtn.addEventListener('click', () => {
  form.reset();
  statusEl.textContent = 'Empty state: enter a keyword and/or choose filters to start searching.';
  resultsEl.innerHTML = '<li class="empty">No search has been run yet.</li>';
});

async function bootstrap() {
  await loadFilters();
  statusEl.textContent = 'Empty state: enter a keyword and/or choose filters to start searching.';
  resultsEl.innerHTML = '<li class="empty">No search has been run yet.</li>';
}

bootstrap();
