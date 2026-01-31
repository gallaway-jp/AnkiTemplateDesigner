/**
 * Anki Bridge Mock Responses
 * Fixtures for mocking Python bridge communication in E2E tests
 */

export const mockAnkiResponses = {
  // Field-related responses
  getAnkiFields: () => ({
    success: true,
    data: [
      { name: 'Front', ordinal: 0 },
      { name: 'Back', ordinal: 1 },
      { name: 'Extra', ordinal: 2 },
    ],
  }),
  
  // Behavior-related responses
  getAnkiBehaviors: () => ({
    success: true,
    data: {
      reveal: true,
      typeAnswer: true,
      autoplay: false,
    },
  }),
  
  // Template operations
  saveTemplate: (templateData?: any) => ({
    success: true,
    data: {
      id: 123,
      name: templateData?.name || 'Saved Template',
      timestamp: Date.now(),
    },
  }),
  
  loadTemplate: (templateId?: number) => ({
    success: true,
    data: {
      id: templateId || 123,
      name: 'Loaded Template',
      html: '<div class="card">{{Front}}</div>',
      css: '.card { background: white; padding: 20px; }',
      fields: ['Front', 'Back'],
      createdAt: Date.now() - 86400000, // 1 day ago
      updatedAt: Date.now(),
    },
  }),
  
  previewTemplate: (html?: string, css?: string) => ({
    success: true,
    data: {
      html: html || '<div>Preview</div>',
      css: css || '.preview { color: black; }',
    },
  }),
  
  exportHTML: () => ({
    success: true,
    data: '<div class="exported-template">{{Front}}</div>',
  }),
  
  // Note type operations
  getNoteTypes: () => ({
    success: true,
    data: [
      { id: 1, name: 'Basic' },
      { id: 2, name: 'Basic (and reversed card)' },
      { id: 3, name: 'Cloze' },
    ],
  }),
  
  // Error responses
  error: (message: string = 'Operation failed') => ({
    success: false,
    error: message,
  }),
};

/**
 * Sample template data for testing
 */
export const sampleTemplates = {
  basic: {
    name: 'Basic Template',
    html: '<div class="card"><div class="front">{{Front}}</div></div>',
    css: '.card { font-family: Arial; } .front { font-size: 20px; }',
    fields: ['Front', 'Back'],
  },
  
  withImage: {
    name: 'Template with Image',
    html: '<div class="card"><img src="{{Image}}" /><p>{{Text}}</p></div>',
    css: '.card img { max-width: 100%; } .card p { margin-top: 10px; }',
    fields: ['Image', 'Text'],
  },
  
  cloze: {
    name: 'Cloze Template',
    html: '<div class="cloze">{{cloze:Text}}</div>',
    css: '.cloze { background: #f0f0f0; padding: 15px; }',
    fields: ['Text'],
  },
};

/**
 * Sample field data for preview
 */
export const sampleFieldData = {
  Front: 'What is the capital of France?',
  Back: 'Paris',
  Extra: 'Paris is the largest city in France',
  Image: 'https://example.com/paris.jpg',
  Text: 'This is a {{c1::cloze}} deletion example',
};
