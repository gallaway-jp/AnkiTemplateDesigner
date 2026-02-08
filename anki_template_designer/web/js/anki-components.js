/**
 * Anki-specific GrapeJS component types.
 *
 * Registers custom component types so GrapeJS understands Anki template
 * syntax ({{Field}}, {{cloze:}}, {{hint:}}, {{#Conditional}}, etc.)
 * and renders meaningful previews inside the visual editor.
 */

/**
 * Register all Anki component types on the given GrapeJS editor.
 * @param {import('grapesjs').Editor} editor
 */
function registerAnkiComponents(editor) {
    const dc = editor.DomComponents;

    // ── Anki Field ──────────────────────────────────────────────
    dc.addType('anki-field', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-field',
        model: {
            defaults: {
                tagName: 'span',
                droppable: false,
                attributes: { 'data-gjs-type': 'anki-field' },
                fieldName: 'Front',
                traits: [
                    {
                        type: 'text',
                        name: 'fieldName',
                        label: 'Field Name',
                        placeholder: 'e.g. Front, Back, Extra',
                    },
                ],
            },
            init() {
                this.on('change:fieldName', this._updateContent);
                this._updateContent();
            },
            _updateContent() {
                const name = this.get('fieldName') || 'Front';
                this.set('content', `{{${name}}}`);
            },
            toHTML() {
                const name = this.get('fieldName') || 'Front';
                return `{{${name}}}`;
            },
        },
    });

    // ── Cloze Deletion ──────────────────────────────────────────
    dc.addType('anki-cloze', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-cloze',
        model: {
            defaults: {
                tagName: 'span',
                droppable: false,
                attributes: { 'data-gjs-type': 'anki-cloze' },
                clozeIndex: '1',
                clozeText: 'answer',
                traits: [
                    { type: 'text', name: 'clozeIndex', label: 'Cloze #' },
                    { type: 'text', name: 'clozeText', label: 'Text' },
                ],
            },
            init() {
                this.on('change:clozeIndex change:clozeText', this._updateContent);
                this._updateContent();
            },
            _updateContent() {
                const idx = this.get('clozeIndex') || '1';
                const txt = this.get('clozeText') || 'answer';
                this.set('content', `{{c${idx}::${txt}}}`);
            },
            toHTML() {
                const idx = this.get('clozeIndex') || '1';
                const txt = this.get('clozeText') || 'answer';
                return `{{c${idx}::${txt}}}`;
            },
        },
    });

    // ── Hint Field ──────────────────────────────────────────────
    dc.addType('anki-hint', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-hint',
        model: {
            defaults: {
                tagName: 'span',
                droppable: false,
                attributes: { 'data-gjs-type': 'anki-hint' },
                fieldName: 'Extra',
                traits: [
                    { type: 'text', name: 'fieldName', label: 'Hint Field' },
                ],
            },
            init() {
                this.on('change:fieldName', this._updateContent);
                this._updateContent();
            },
            _updateContent() {
                const name = this.get('fieldName') || 'Extra';
                this.set('content', `{{hint:${name}}}`);
            },
            toHTML() {
                const name = this.get('fieldName') || 'Extra';
                return `{{hint:${name}}}`;
            },
        },
    });

    // ── Type Answer ─────────────────────────────────────────────
    dc.addType('anki-type-answer', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-type-answer',
        model: {
            defaults: {
                tagName: 'span',
                droppable: false,
                attributes: { 'data-gjs-type': 'anki-type-answer' },
                fieldName: 'Front',
                traits: [
                    { type: 'text', name: 'fieldName', label: 'Compare Field' },
                ],
            },
            init() {
                this.on('change:fieldName', this._updateContent);
                this._updateContent();
            },
            _updateContent() {
                const name = this.get('fieldName') || 'Front';
                this.set('content', `{{type:${name}}}`);
            },
            toHTML() {
                const name = this.get('fieldName') || 'Front';
                return `{{type:${name}}}`;
            },
        },
    });

    // ── Conditional Section ─────────────────────────────────────
    dc.addType('anki-conditional', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-conditional',
        model: {
            defaults: {
                tagName: 'div',
                droppable: true,
                attributes: { 'data-gjs-type': 'anki-conditional' },
                fieldName: 'Extra',
                negate: false,
                components: [
                    { type: 'text', content: 'Conditional content here' },
                ],
                traits: [
                    { type: 'text', name: 'fieldName', label: 'Field Name' },
                    { type: 'checkbox', name: 'negate', label: 'Negate (hide if present)' },
                ],
            },
            toHTML() {
                const name = this.get('fieldName') || 'Extra';
                const prefix = this.get('negate') ? '^' : '#';
                const closePrefix = this.get('negate') ? '^' : '/';
                const inner = this.getInnerHTML();
                return `{{${prefix}${name}}}${inner}{{${closePrefix}${name}}}`;
            },
        },
    });

    // ── Tags Display ────────────────────────────────────────────
    dc.addType('anki-tags', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-tags',
        model: {
            defaults: {
                tagName: 'span',
                droppable: false,
                content: '{{Tags}}',
                attributes: { 'data-gjs-type': 'anki-tags' },
            },
            toHTML() {
                return '{{Tags}}';
            },
        },
    });

    // ── FrontSide (for back template) ───────────────────────────
    dc.addType('anki-frontside', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-frontside',
        model: {
            defaults: {
                tagName: 'div',
                droppable: false,
                content: '{{FrontSide}}',
                attributes: { 'data-gjs-type': 'anki-frontside' },
            },
            toHTML() {
                return '{{FrontSide}}';
            },
        },
    });
}
