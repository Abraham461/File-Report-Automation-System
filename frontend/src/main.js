import './styles.css';

import { dashboardPage } from './pages/dashboard.js';
import { filesPage } from './pages/files.js';
import { searchPage } from './pages/search.js';
import { reportTemplatesPage } from './pages/report-templates.js';
import { reportHistoryPage } from './pages/report-history.js';

const app = document.querySelector('#app');

const renderPageSection = (page) => {
  if (Array.isArray(page.description)) {
    return `
      <section>
        <h2>${page.title}</h2>
        <ul>${page.description.map((item) => `<li>${item}</li>`).join('')}</ul>
      </section>
    `;
  }

  return `
    <section>
      <h2>${page.title}</h2>
      <p>${page.description}</p>
    </section>
  `;
};

app.innerHTML = `
  <main class="app-shell">
    <h1>File & Report Automation System</h1>
    <p>App shell is running. Use this starter to build business workflows.</p>

    ${renderPageSection(dashboardPage)}
    ${renderPageSection(filesPage)}
    ${renderPageSection(searchPage)}
    ${renderPageSection(reportTemplatesPage)}
    ${renderPageSection(reportHistoryPage)}

    <section>
      <h2>Backend Health</h2>
      <p id="health-status">Checking backend connectivity...</p>
    </section>
  </main>
`;

const healthNode = document.querySelector('#health-status');

fetch('http://localhost:4000/health')
  .then((res) => res.json())
  .then((data) => {
    healthNode.textContent = `✅ ${data.service} is ${data.status}`;
  })
  .catch(() => {
    healthNode.textContent = '⚠️ Could not reach backend health endpoint at http://localhost:4000/health';
  });
