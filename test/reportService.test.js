import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { reportTemplates } from '../data/reportTemplates.js';
import { generateReport } from '../src/reportService.js';

const storePath = 'storage/generatedReports.json';

function resetStore() {
  fs.writeFileSync(storePath, JSON.stringify({ reports: [], history: [] }, null, 2));
}

test.beforeEach(() => {
  resetStore();
});

test.after(() => {
  resetStore();
});

test('has predefined templates', () => {
  assert.equal(reportTemplates.length >= 2, true);
  assert.equal(reportTemplates.some((template) => template.id === 'file-summary-report'), true);
  assert.equal(reportTemplates.some((template) => template.id === 'activity-audit-report'), true);
});

test('generates report with exports metadata', async () => {
  const report = await generateReport({
    templateId: 'file-summary-report',
    metadata: { reportDate: '2026-03-01', preparedBy: 'Tester' },
    files: [{ name: 'a.txt', sizeBytes: 10, size: '10B', status: 'approved' }],
    exportFormats: []
  });

  assert.equal(report.templateId, 'file-summary-report');
  assert.equal(report.exports.length, 1);
  assert.equal(report.exports[0].format, 'pdf');
});
