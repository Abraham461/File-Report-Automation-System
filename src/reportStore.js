// DEPRECATED: Python FastAPI backend in app/ is the default runtime.
import fs from 'node:fs';
import path from 'node:path';

const storagePath = path.resolve('storage/generatedReports.json');

function ensureStore() {
  if (!fs.existsSync(storagePath)) {
    fs.writeFileSync(storagePath, JSON.stringify({ reports: [], history: [] }, null, 2));
  }
}

export function readStore() {
  ensureStore();
  return JSON.parse(fs.readFileSync(storagePath, 'utf-8'));
}

export function writeStore(data) {
  ensureStore();
  fs.writeFileSync(storagePath, JSON.stringify(data, null, 2));
}

export function appendReport(reportRecord) {
  const store = readStore();
  store.reports.push(reportRecord);
  store.history.unshift({
    reportId: reportRecord.id,
    generatedAt: reportRecord.generatedAt,
    templateId: reportRecord.templateId,
    title: reportRecord.title,
    exports: reportRecord.exports.map((entry) => entry.format)
  });
  writeStore(store);
  return reportRecord;
}
