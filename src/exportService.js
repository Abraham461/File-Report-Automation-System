import fs from 'node:fs';
import path from 'node:path';

const exportDir = path.resolve('storage/exports');

function ensureExportDir() {
  fs.mkdirSync(exportDir, { recursive: true });
}

function escapePdfText(text) {
  return text.replaceAll('\\', '\\\\').replaceAll('(', '\\(').replaceAll(')', '\\)');
}

export async function exportToPdf(reportId, reportText) {
  ensureExportDir();
  const filepath = path.join(exportDir, `${reportId}.pdf`);

  const lines = reportText.split('\n');
  const commands = ['BT', '/F1 11 Tf', '40 800 Td'];

  lines.forEach((line, index) => {
    if (index > 0) {
      commands.push('0 -14 Td');
    }
    commands.push(`(${escapePdfText(line)}) Tj`);
  });

  commands.push('ET');
  const stream = commands.join('\n');

  const objects = [
    '1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
    '2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
    '3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj',
    '4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
    `5 0 obj << /Length ${stream.length} >> stream\n${stream}\nendstream endobj`
  ];

  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  objects.forEach((obj) => {
    offsets.push(pdf.length);
    pdf += `${obj}\n`;
  });

  const xrefStart = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += '0000000000 65535 f \n';
  offsets.slice(1).forEach((offset) => {
    pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
  });
  pdf += `trailer << /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`;

  fs.writeFileSync(filepath, pdf, 'binary');
  return filepath;
}
