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
                        changeProp: true,
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
                    { type: 'text', name: 'clozeIndex', label: 'Cloze #', changeProp: true },
                    { type: 'text', name: 'clozeText', label: 'Text', changeProp: true },
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
                    { type: 'text', name: 'fieldName', label: 'Hint Field', changeProp: true },
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
                    { type: 'text', name: 'fieldName', label: 'Compare Field', changeProp: true },
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
                    { type: 'text', name: 'fieldName', label: 'Field Name', changeProp: true },
                    { type: 'checkbox', name: 'negate', label: 'Negate (hide if present)', changeProp: true },
                ],
            },
            toHTML() {
                const name = this.get('fieldName') || 'Extra';
                const prefix = this.get('negate') ? '^' : '#';
                const inner = this.getInnerHTML();
                return `{{${prefix}${name}}}${inner}{{/${name}}}`;
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

    // ═══════════════════════════════════════════════════════════
    //  Layout component types
    // ═══════════════════════════════════════════════════════════

    // ── Section ─────────────────────────────────────────────────
    dc.addType('atd-section', {
        isComponent: (el) => el?.tagName === 'SECTION' && el?.classList?.contains('atd-section'),
        model: {
            defaults: {
                tagName: 'section',
                droppable: true,
                classes: ['atd-section'],
                style: {
                    'padding': '16px',
                    'min-height': '60px',
                },
                traits: [
                    {
                        type: 'select', name: 'display', label: 'Display',
                        changeProp: true,
                        options: [
                            { id: 'block', name: 'Block' },
                            { id: 'flex', name: 'Flex' },
                            { id: 'grid', name: 'Grid' },
                        ],
                    },
                    {
                        type: 'select', name: 'flexDirection', label: 'Direction',
                        changeProp: true,
                        options: [
                            { id: 'column', name: 'Vertical' },
                            { id: 'row', name: 'Horizontal' },
                        ],
                    },
                    {
                        type: 'text', name: 'gap', label: 'Gap',
                        changeProp: true,
                        placeholder: 'e.g. 12px',
                    },
                ],
                display: 'block',
                flexDirection: 'column',
                gap: '',
            },
            init() {
                this.on('change:display change:flexDirection change:gap', this._applyLayout);
            },
            _applyLayout() {
                const display = this.get('display') || 'block';
                const style = { ...this.getStyle(), display };
                if (display === 'flex' || display === 'grid') {
                    style['flex-direction'] = this.get('flexDirection') || 'column';
                    const gap = this.get('gap');
                    if (gap) style['gap'] = gap;
                } else {
                    delete style['flex-direction'];
                    delete style['gap'];
                }
                this.setStyle(style);
            },
        },
    });

    // ── Row (flex container) ────────────────────────────────────
    dc.addType('atd-row', {
        isComponent: (el) => el?.classList?.contains('atd-row'),
        model: {
            defaults: {
                tagName: 'div',
                droppable: true,
                classes: ['atd-row'],
                style: {
                    'display': 'flex',
                    'gap': '12px',
                    'min-height': '60px',
                },
                traits: [
                    {
                        type: 'select', name: 'flexDirection', label: 'Direction',
                        changeProp: true,
                        options: [
                            { id: 'row', name: 'Horizontal' },
                            { id: 'column', name: 'Vertical' },
                        ],
                    },
                    {
                        type: 'select', name: 'justifyContent', label: 'Justify',
                        changeProp: true,
                        options: [
                            { id: 'flex-start', name: 'Start' },
                            { id: 'center', name: 'Center' },
                            { id: 'flex-end', name: 'End' },
                            { id: 'space-between', name: 'Space Between' },
                            { id: 'space-around', name: 'Space Around' },
                        ],
                    },
                    {
                        type: 'select', name: 'alignItems', label: 'Align',
                        changeProp: true,
                        options: [
                            { id: 'stretch', name: 'Stretch' },
                            { id: 'flex-start', name: 'Start' },
                            { id: 'center', name: 'Center' },
                            { id: 'flex-end', name: 'End' },
                        ],
                    },
                    {
                        type: 'select', name: 'flexWrap', label: 'Wrap',
                        changeProp: true,
                        options: [
                            { id: 'nowrap', name: 'No Wrap' },
                            { id: 'wrap', name: 'Wrap' },
                        ],
                    },
                    {
                        type: 'text', name: 'gap', label: 'Gap',
                        changeProp: true,
                        placeholder: 'e.g. 12px',
                    },
                ],
                flexDirection: 'row',
                justifyContent: 'flex-start',
                alignItems: 'stretch',
                flexWrap: 'nowrap',
                gap: '12px',
            },
            init() {
                this.on('change:flexDirection change:justifyContent change:alignItems change:flexWrap change:gap', this._applyLayout);
            },
            _applyLayout() {
                const style = { ...this.getStyle() };
                style['flex-direction'] = this.get('flexDirection') || 'row';
                style['justify-content'] = this.get('justifyContent') || 'flex-start';
                style['align-items'] = this.get('alignItems') || 'stretch';
                style['flex-wrap'] = this.get('flexWrap') || 'nowrap';
                const gap = this.get('gap');
                if (gap) style['gap'] = gap;
                this.setStyle(style);
            },
        },
    });

    // ── Column (flex child) ─────────────────────────────────────
    dc.addType('atd-column', {
        isComponent: (el) => el?.classList?.contains('atd-col'),
        model: {
            defaults: {
                tagName: 'div',
                droppable: true,
                classes: ['atd-col'],
                style: {
                    'flex': '1',
                    'min-height': '60px',
                    'padding': '8px',
                },
                traits: [
                    {
                        type: 'text', name: 'flexValue', label: 'Flex',
                        changeProp: true,
                        placeholder: 'e.g. 1, 2, 0 0 auto',
                    },
                ],
                flexValue: '1',
            },
            init() {
                this.on('change:flexValue', this._applyFlex);
            },
            _applyFlex() {
                const style = { ...this.getStyle() };
                style['flex'] = this.get('flexValue') || '1';
                this.setStyle(style);
            },
        },
    });

    // ── Container (centered wrapper) ────────────────────────────
    dc.addType('atd-container', {
        isComponent: (el) => el?.classList?.contains('atd-container'),
        model: {
            defaults: {
                tagName: 'div',
                droppable: true,
                classes: ['atd-container'],
                style: {
                    'max-width': '800px',
                    'margin': '0 auto',
                    'padding': '16px',
                    'min-height': '60px',
                },
                traits: [
                    {
                        type: 'text', name: 'maxWidth', label: 'Max Width',
                        changeProp: true,
                        placeholder: 'e.g. 800px, 90%',
                    },
                ],
                maxWidth: '800px',
            },
            init() {
                this.on('change:maxWidth', this._applyWidth);
            },
            _applyWidth() {
                const style = { ...this.getStyle() };
                style['max-width'] = this.get('maxWidth') || '800px';
                this.setStyle(style);
            },
        },
    });

    // ── Divider ─────────────────────────────────────────────────
    dc.addType('atd-divider', {
        isComponent: (el) => el?.tagName === 'HR' && el?.classList?.contains('atd-divider'),
        model: {
            defaults: {
                tagName: 'hr',
                droppable: false,
                void: true,
                classes: ['atd-divider'],
                style: {
                    'border': 'none',
                    'border-top': '1px solid #ccc',
                    'margin': '12px 0',
                },
                traits: [
                    {
                        type: 'select', name: 'dividerStyle', label: 'Style',
                        changeProp: true,
                        options: [
                            { id: 'solid', name: 'Solid' },
                            { id: 'dashed', name: 'Dashed' },
                            { id: 'dotted', name: 'Dotted' },
                        ],
                    },
                    {
                        type: 'text', name: 'dividerColor', label: 'Color',
                        changeProp: true,
                        placeholder: '#ccc',
                    },
                ],
                dividerStyle: 'solid',
                dividerColor: '#ccc',
            },
            init() {
                this.on('change:dividerStyle change:dividerColor', this._applyDivider);
            },
            _applyDivider() {
                const style = { ...this.getStyle() };
                const lineStyle = this.get('dividerStyle') || 'solid';
                const color = this.get('dividerColor') || '#ccc';
                style['border-top'] = `1px ${lineStyle} ${color}`;
                this.setStyle(style);
            },
        },
    });

    // ── Spacer ──────────────────────────────────────────────────
    dc.addType('atd-spacer', {
        isComponent: (el) => el?.classList?.contains('atd-spacer'),
        model: {
            defaults: {
                tagName: 'div',
                droppable: false,
                classes: ['atd-spacer'],
                style: {
                    'height': '24px',
                },
                traits: [
                    {
                        type: 'text', name: 'spacerHeight', label: 'Height',
                        changeProp: true,
                        placeholder: 'e.g. 24px, 2em',
                    },
                ],
                spacerHeight: '24px',
            },
            init() {
                this.on('change:spacerHeight', this._applyHeight);
            },
            _applyHeight() {
                const style = { ...this.getStyle() };
                style['height'] = this.get('spacerHeight') || '24px';
                this.setStyle(style);
            },
        },
    });
}
