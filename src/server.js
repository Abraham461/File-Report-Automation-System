// DEPRECATED: Python FastAPI backend in app/ is the default runtime.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { URL } from 'node:url';
import { reportTemplates } from '../data/reportTemplates.js';
import { generateReport, getReportById, getReportHistory } from './reportService.js';

const port = Number(process.env.PORT || 3000);
const publicDir = path.resolve('public');

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(payload));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > 2 * 1024 * 1024) {
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch {
        reject(new Error('Invalid JSON body'));
      }
    });
    req.on('error', reject);
  });
}

function contentTypeFor(filePath) {
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.js')) return 'application/javascript; charset=utf-8';
  if (filePath.endsWith('.pdf')) return 'application/pdf';
  return 'application/octet-stream';
}

function sendFile(res, filePath, downloadName) {
  if (!fs.existsSync(filePath)) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  const headers = { 'Content-Type': contentTypeFor(filePath) };
  if (downloadName) {
    headers['Content-Disposition'] = `attachment; filename="${downloadName}"`;
  }

  res.writeHead(200, headers);
  fs.createReadStream(filePath).pipe(res);
}

function normalizeBaseUrl(baseUrl) {
  return baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
}

function extractJsonBody(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('Body must be a JSON object');
  }

  return payload;
}

function handleUpload(payload) {
  const body = extractJsonBody(payload);
  const files = Array.isArray(body.files) ? body.files : [];
  if (!files.length) {
    throw new Error('files must contain at least one item');
  }

  return {
    accepted: files.length,
    receivedAt: new Date().toISOString()
  };
}

function handleSearch(baseUrl, query) {
  const q = (query.get('q') || '').trim();
  if (!q) {
    throw new Error('q query parameter is required');
  }

  const qLower = q.toLowerCase();
  const historyMatches = getReportHistory()
    .filter((report) => report.title.toLowerCase().includes(qLower) || report.templateId.toLowerCase().includes(qLower))
    .map((report) => ({
      type: 'report-history',
      id: report.reportId,
      title: report.title,
      templateId: report.templateId,
      generatedAt: report.generatedAt,
      url: `${normalizeBaseUrl(baseUrl)}/api/reports/${report.reportId}`
    }));

  const templateMatches = reportTemplates
    .filter((template) => template.title.toLowerCase().includes(qLower) || template.description.toLowerCase().includes(qLower))
    .map((template) => ({
      type: 'template',
      id: template.id,
      title: template.title,
      description: template.description,
      url: `${normalizeBaseUrl(baseUrl)}/api/report-templates#${template.id}`
    }));

  return { query: q, results: [...historyMatches, ...templateMatches] };
}

const server = http.createServer(async (req, res) => {
  const requestUrl = new URL(req.url, `http://localhost:${port}`);
  const { pathname } = requestUrl;

  if (pathname === '/api/report-templates' && req.method === 'GET') {
    return sendJson(res, 200, { templates: reportTemplates });
  }

  if (pathname === '/api/reports/history' && req.method === 'GET') {
    return sendJson(res, 200, { history: getReportHistory() });
  }

  if (pathname === '/api/upload' && req.method === 'POST') {
    try {
      const payload = await readBody(req);
      return sendJson(res, 201, { upload: handleUpload(payload) });
    } catch (error) {
      return sendJson(res, 400, { error: error.message });
    }
  }

  if (pathname === '/api/search' && req.method === 'GET') {
    try {
      return sendJson(res, 200, handleSearch(`http://localhost:${port}`, requestUrl.searchParams));
    } catch (error) {
      return sendJson(res, 400, { error: error.message });
    }
  }

  if (pathname === '/api/reports' && req.method === 'POST') {
    try {
      const payload = await readBody(req);
      const report = await generateReport(payload);
      return sendJson(res, 201, { report });
    } catch (error) {
      return sendJson(res, 400, { error: error.message });
    }
  }

  if (pathname === '/api/reports/generate' && req.method === 'POST') {
    try {
      const payload = await readBody(req);
      const report = await generateReport(payload);
      return sendJson(res, 201, { report });
    } catch (error) {
      return sendJson(res, 400, { error: error.message });
    }
  }

  const downloadMatch = pathname.match(/^\/api\/reports\/([^/]+)\/download\/(pdf)$/);
  if (downloadMatch && req.method === 'GET') {
    const [, reportId, format] = downloadMatch;
    const report = getReportById(reportId);
    if (!report) return sendJson(res, 404, { error: 'Report not found' });

    const exportEntry = report.exports.find((entry) => entry.format === format);
    if (!exportEntry) return sendJson(res, 404, { error: 'Export format not found for this report' });

    return sendFile(res, path.resolve(exportEntry.path), `${reportId}.${format}`);
  }

  const reportMatch = pathname.match(/^\/api\/reports\/([^/]+)$/);
  if (reportMatch && req.method === 'GET') {
    const [, reportId] = reportMatch;
    const report = getReportById(reportId);
    if (!report) return sendJson(res, 404, { error: 'Report not found' });

    return sendJson(res, 200, { report });
  }

  if (pathname === '/health') {
    return sendJson(res, 200, { ok: true });
  }

  if (['/login', '/upload', '/search', '/reports'].includes(pathname) && req.method === 'GET') {
    return sendFile(res, path.resolve(path.join(publicDir, `${pathname.slice(1)}.html`)));
  }

  const safePath = pathname === '/' ? '/index.html' : pathname;
  const filePath = path.resolve(path.join(publicDir, safePath));
  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    return sendFile(res, filePath);
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(port, () => {
  console.log(`Report service listening on http://localhost:${port}`);
});
