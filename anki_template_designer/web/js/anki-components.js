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
                // Hydrate from HTML data-field attr when loaded from converter
                const df = this.getAttributes()['data-field'];
                if (df) this.set('fieldName', df, { silent: true });
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
    // Anki template syntax: {{cloze:FieldName}}
    dc.addType('anki-cloze', {
        isComponent: (el) => el?.dataset?.gjsType === 'anki-cloze',
        model: {
            defaults: {
                tagName: 'span',
                droppable: false,
                attributes: { 'data-gjs-type': 'anki-cloze' },
                fieldName: 'Text',
                traits: [
                    { type: 'text', name: 'fieldName', label: 'Field Name', changeProp: true },
                ],
            },
            init() {
                const df = this.getAttributes()['data-field'];
                if (df) this.set('fieldName', df, { silent: true });
                this.on('change:fieldName', this._updateContent);
                this._updateContent();
            },
            _updateContent() {
                const name = this.get('fieldName') || 'Text';
                this.set('content', `{{cloze:${name}}}`);
            },
            toHTML() {
                const name = this.get('fieldName') || 'Text';
                return `{{cloze:${name}}}`;
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
                const df = this.getAttributes()['data-field'];
                if (df) this.set('fieldName', df, { silent: true });
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
                const df = this.getAttributes()['data-field'];
                if (df) this.set('fieldName', df, { silent: true });
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
                traits: [
                    { type: 'text', name: 'fieldName', label: 'Field Name', changeProp: true },
                    { type: 'checkbox', name: 'negate', label: 'Negate (hide if present)', changeProp: true },
                ],
            },
            init() {
                // Hydrate from HTML data attrs when loaded from converter
                const attrs = this.getAttributes();
                const df = attrs['data-field'];
                if (df) this.set('fieldName', df, { silent: true });
                const dc = attrs['data-condition'];
                if (dc) this.set('negate', dc === 'hide', { silent: true });
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

    // ═══════════════════════════════════════════════════════════
    //  Rich text & semantic component types
    // ═══════════════════════════════════════════════════════════

    // ── Text Block (with tag type switching) ────────────────────
    // Replaces both the old "Text" and "Heading" blocks.
    // User can switch between div, p, h1-h6, blockquote, pre, code,
    // kbd, samp, var, abbr, cite, dfn, q, mark, small, sub, sup.
    dc.addType('atd-text', {
        extend: 'text',   // inherits GrapeJS inline-editing
        isComponent: (el) => {
            if (!el || !el.dataset) return false;
            return el.dataset.gjsType === 'atd-text';
        },
        model: {
            defaults: {
                tagName: 'div',
                droppable: false,
                editable: true,
                content: 'Insert your text here',
                attributes: { 'data-gjs-type': 'atd-text' },
                textTag: 'div',
                traits: [
                    {
                        type: 'select', name: 'textTag', label: 'Element',
                        changeProp: true,
                        options: [
                            { id: 'div',        name: 'Text (div)' },
                            { id: 'p',          name: 'Paragraph' },
                            { id: 'h1',         name: 'Heading 1' },
                            { id: 'h2',         name: 'Heading 2' },
                            { id: 'h3',         name: 'Heading 3' },
                            { id: 'h4',         name: 'Heading 4' },
                            { id: 'h5',         name: 'Heading 5' },
                            { id: 'h6',         name: 'Heading 6' },
                            { id: 'blockquote', name: 'Blockquote' },
                            { id: 'pre',        name: 'Preformatted' },
                            { id: 'code',       name: 'Code' },
                            { id: 'kbd',        name: 'Keyboard Input' },
                            { id: 'samp',       name: 'Sample Output' },
                            { id: 'var',        name: 'Variable' },
                            { id: 'abbr',       name: 'Abbreviation' },
                            { id: 'cite',       name: 'Citation' },
                            { id: 'dfn',        name: 'Definition' },
                            { id: 'q',          name: 'Inline Quote' },
                            { id: 'mark',       name: 'Highlight' },
                            { id: 'small',      name: 'Small' },
                            { id: 'sub',        name: 'Subscript' },
                            { id: 'sup',        name: 'Superscript' },
                        ],
                    },
                ],
            },
            init() {
                this.on('change:textTag', this._updateTag);
            },
            _updateTag() {
                const tag = this.get('textTag') || 'div';
                if (tag !== this.get('tagName')) {
                    this.set('tagName', tag);
                }
            },
        },
    });

    // ── List (ol/ul with add/remove) ────────────────────────────
    dc.addType('atd-list', {
        isComponent: (el) => {
            if (!el) return false;
            return (el.tagName === 'UL' || el.tagName === 'OL') &&
                   el.dataset?.gjsType === 'atd-list';
        },
        model: {
            defaults: {
                tagName: 'ul',
                droppable: false,
                attributes: { 'data-gjs-type': 'atd-list' },
                listType: 'ul',
                components: [
                    { tagName: 'li', content: 'Item 1', editable: true, draggable: false, droppable: false },
                    { tagName: 'li', content: 'Item 2', editable: true, draggable: false, droppable: false },
                    { tagName: 'li', content: 'Item 3', editable: true, draggable: false, droppable: false },
                ],
                traits: [
                    {
                        type: 'select', name: 'listType', label: 'Type',
                        changeProp: true,
                        options: [
                            { id: 'ul', name: 'Bullet (ul)' },
                            { id: 'ol', name: 'Numbered (ol)' },
                        ],
                    },
                    {
                        type: 'button', name: 'addItem', label: 'Add Item',
                        text: '+ Add Item',
                        command: 'atd-list-add',
                    },
                    {
                        type: 'button', name: 'removeItem', label: 'Remove Last',
                        text: '− Remove Last',
                        command: 'atd-list-remove',
                    },
                ],
            },
            init() {
                this.on('change:listType', this._updateListType);
            },
            _updateListType() {
                const tag = this.get('listType') || 'ul';
                if (tag !== this.get('tagName')) {
                    this.set('tagName', tag);
                }
            },
        },
    });
}
