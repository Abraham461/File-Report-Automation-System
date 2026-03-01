// DEPRECATED: Python FastAPI backend in app/ is the default runtime.
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { appendReport, readStore } from './reportStore.js';
import { getTemplateById } from '../data/reportTemplates.js';
import { exportToPdf } from './exportService.js';

function validateRequiredFields(template, payload) {
  const missing = [];

  for (const field of template.requiredFields) {
    if (field === 'fileList' && (!payload.files || payload.files.length === 0)) {
      missing.push(field);
    }

    if (field === 'activityEvents' && (!payload.activityEvents || payload.activityEvents.length === 0)) {
      missing.push(field);
    }

    if (!['fileList', 'activityEvents'].includes(field) && !payload.metadata?.[field]) {
      missing.push(field);
    }
  }

  return missing;
}

function renderStatusBreakdown(files) {
  const counts = files.reduce((acc, file) => {
    const status = file.status || 'unknown';
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});

  return Object.entries(counts)
    .map(([status, count]) => `- ${status}: ${count}`)
    .join('\n');
}

function renderFileTable(files) {
  return files
    .map(
      (file, index) =>
        `${index + 1}. ${file.name} | owner: ${file.owner || 'n/a'} | category: ${file.category || 'n/a'} | size: ${file.size || 'n/a'} | status: ${file.status || 'n/a'}`
    )
    .join('\n');
}

function renderRiskFindings(events) {
  const risky = events.filter((event) => ['delete', 'permission-change', 'failed-login'].includes(event.type));
  if (!risky.length) {
    return 'No high-risk findings identified.';
  }

  return risky
    .map((event) => `- [${event.timestamp}] ${event.actor} performed ${event.type} on ${event.target}`)
    .join('\n');
}

function renderEventTimeline(events) {
  return events
    .slice()
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .map((event) => `${event.timestamp} | ${event.actor} | ${event.type} | ${event.target}`)
    .join('\n');
}

function templateContext(templateId, payload) {
  const files = payload.files || [];
  const events = payload.activityEvents || [];

  if (templateId === 'file-summary-report') {
    return {
      ...payload.metadata,
      fileCount: files.length,
      totalSize: files.reduce((acc, file) => acc + (Number(file.sizeBytes) || 0), 0) + ' bytes',
      statusBreakdown: renderStatusBreakdown(files),
      fileTable: renderFileTable(files)
    };
  }

  if (templateId === 'activity-audit-report') {
    return {
      ...payload.metadata,
      eventCount: events.length,
      uniqueActors: new Set(events.map((event) => event.actor)).size,
      riskFindings: renderRiskFindings(events),
      eventTimeline: renderEventTimeline(events)
    };
  }

  return payload.metadata || {};
}

function applyTemplate(template, context) {
  const renderedSections = template.sections.map((section) => {
    let body = section.body;

    for (const placeholder of template.placeholders) {
      const value = context[placeholder] ?? `{{${placeholder}}}`;
      body = body.replaceAll(`{{${placeholder}}}`, String(value));
    }

    return { ...section, body };
  });

  const fullText = [template.title, ...renderedSections.map((section) => `${section.heading}\n${section.body}`)].join('\n\n');

  return { renderedSections, fullText };
}

export async function generateReport(payload) {
  const template = getTemplateById(payload.templateId);
  if (!template) {
    throw new Error('Template not found');
  }

  const missingFields = validateRequiredFields(template, payload);
  if (missingFields.length) {
    throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
  }

  const context = templateContext(template.id, payload);
  const { renderedSections, fullText } = applyTemplate(template, context);
  const reportId = randomUUID();

  const exports = [];
  const requestedFormats = payload.exportFormats?.length ? payload.exportFormats : ['pdf'];

  for (const format of requestedFormats) {
    if (format === 'pdf') {
      const pdfPath = await exportToPdf(reportId, fullText);
      exports.push({ format, path: pdfPath, downloadUrl: `/api/reports/${reportId}/download/pdf` });
    }
  }

  if (!exports.length) {
    const pdfPath = await exportToPdf(reportId, fullText);
    exports.push({ format: 'pdf', path: pdfPath, downloadUrl: `/api/reports/${reportId}/download/pdf` });
  }

  const reportRecord = {
    id: reportId,
    templateId: template.id,
    title: payload.title || template.title,
    metadata: payload.metadata || {},
    files: payload.files || [],
    activityEvents: payload.activityEvents || [],
    generatedAt: new Date().toISOString(),
    sections: renderedSections,
    fullText,
    exports: exports.map((entry) => ({ ...entry, path: path.relative(process.cwd(), entry.path) }))
  };

  return appendReport(reportRecord);
}

export function getReportHistory() {
  return readStore().history;
}

export function getReportById(reportId) {
  return readStore().reports.find((report) => report.id === reportId);
}
