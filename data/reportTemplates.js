export const reportTemplates = [
  {
    id: 'file-summary-report',
    title: 'File Summary Report',
    description: 'Summarizes selected files by ownership, category, and status.',
    requiredFields: ['reportDate', 'preparedBy', 'fileList'],
    placeholders: [
      'reportDate',
      'preparedBy',
      'fileCount',
      'totalSize',
      'statusBreakdown',
      'fileTable'
    ],
    sections: [
      {
        heading: 'Overview',
        body:
          'Report Date: {{reportDate}}\nPrepared By: {{preparedBy}}\nTotal Files: {{fileCount}}\nTotal Size: {{totalSize}}'
      },
      {
        heading: 'Status Breakdown',
        body: '{{statusBreakdown}}'
      },
      {
        heading: 'File Details',
        body: '{{fileTable}}'
      }
    ]
  },
  {
    id: 'activity-audit-report',
    title: 'Activity & Audit Report',
    description: 'Tracks user activity, actions, and potential policy violations.',
    requiredFields: ['reportDate', 'preparedBy', 'activityEvents'],
    placeholders: [
      'reportDate',
      'preparedBy',
      'eventCount',
      'uniqueActors',
      'riskFindings',
      'eventTimeline'
    ],
    sections: [
      {
        heading: 'Executive Summary',
        body:
          'Report Date: {{reportDate}}\nPrepared By: {{preparedBy}}\nTotal Events: {{eventCount}}\nUnique Actors: {{uniqueActors}}'
      },
      {
        heading: 'Risk Findings',
        body: '{{riskFindings}}'
      },
      {
        heading: 'Event Timeline',
        body: '{{eventTimeline}}'
      }
    ]
  }
];

export function getTemplateById(templateId) {
  return reportTemplates.find((template) => template.id === templateId);
}
