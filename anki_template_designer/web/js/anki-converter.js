/**
 * Anki Template ↔ GrapeJS HTML converter.
 *
 * Handles the bidirectional conversion between Anki's Mustache-style
 * template syntax and our custom GrapeJS component HTML.
 *
 * Anki template syntax reference:
 *   {{FieldName}}            – field replacement
 *   {{cloze:Text}}           – cloze deletion
 *   {{hint:FieldName}}       – hint toggle
 *   {{type:FieldName}}       – type-in-the-answer
 *   {{#FieldName}}...{{/FieldName}}  – conditional (show if non-empty)
 *   {{^FieldName}}...{{/FieldName}}  – conditional (show if empty / negated)
 *   {{FrontSide}}            – insert front side on back template
 *   {{Tags}}                 – card tags
 *
 * Our GrapeJS component elements:
 *   <span data-gjs-type="anki-field" data-field="FieldName">{{FieldName}}</span>
 *   <span data-gjs-type="anki-cloze" data-field="Text">{{cloze:Text}}</span>
 *   <span data-gjs-type="anki-hint"  data-field="FieldName">{{hint:FieldName}}</span>
 *   <span data-gjs-type="anki-type-answer" data-field="FieldName">{{type:FieldName}}</span>
 *   <div data-gjs-type="anki-conditional" data-field="FieldName" data-condition="show">
 *       ...inner content...
 *   </div>
 *   <div data-gjs-type="anki-conditional" data-field="FieldName" data-condition="hide">
 *       ...inner content...
 *   </div>
 *   <span data-gjs-type="anki-frontside">{{FrontSide}}</span>
 *   <span data-gjs-type="anki-tags">{{Tags}}</span>
 */

/* ================================================================== */
/*  Anki HTML → GrapeJS HTML  (load path)                             */
/* ================================================================== */

/**
 * Convert raw Anki template HTML into GrapeJS-compatible HTML
 * where Mustache tokens are replaced by custom component elements.
 *
 * @param {string} html  Raw Anki template HTML
 * @returns {string}     HTML with custom component elements
 */
function ankiHtmlToGrapejs(html) {
    if (!html) return '';

    let result = html;

    // 1. Convert conditional blocks first (they wrap inner content).
    //    Must handle nested conditionals, so we work from innermost out.
    //    We use a loop that keeps replacing until no more matches.
    let prevResult;
    const MAX_ITERATIONS = 50;
    let iterations = 0;

    do {
        prevResult = result;
        iterations++;

        // {{#Field}} ... {{/Field}}  →  show-if-non-empty conditional
        result = result.replace(
            /\{\{#([^}]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g,
            (_match, field, inner) => {
                const escapedInner = inner;
                return `<div data-gjs-type="anki-conditional" data-field="${_escAttr(field)}" data-condition="show">${escapedInner}</div>`;
            }
        );

        // {{^Field}} ... {{/Field}}  →  show-if-empty conditional (negated)
        result = result.replace(
            /\{\{\^([^}]+)\}\}([\s\S]*?)\{\{\/\1\}\}/g,
            (_match, field, inner) => {
                return `<div data-gjs-type="anki-conditional" data-field="${_escAttr(field)}" data-condition="hide">${inner}</div>`;
            }
        );

    } while (result !== prevResult && iterations < MAX_ITERATIONS);

    // 2. Convert inline tokens (order matters – more specific first)

    // {{cloze:Text}}
    result = result.replace(
        /\{\{cloze:([^}]+)\}\}/g,
        (_m, field) => `<span data-gjs-type="anki-cloze" data-field="${_escAttr(field)}">{{cloze:${field}}}</span>`
    );

    // {{hint:Field}}
    result = result.replace(
        /\{\{hint:([^}]+)\}\}/g,
        (_m, field) => `<span data-gjs-type="anki-hint" data-field="${_escAttr(field)}">{{hint:${field}}}</span>`
    );

    // {{type:Field}}
    result = result.replace(
        /\{\{type:([^}]+)\}\}/g,
        (_m, field) => `<span data-gjs-type="anki-type-answer" data-field="${_escAttr(field)}">{{type:${field}}}</span>`
    );

    // {{FrontSide}}
    result = result.replace(
        /\{\{FrontSide\}\}/g,
        '<span data-gjs-type="anki-frontside">{{FrontSide}}</span>'
    );

    // {{Tags}}
    result = result.replace(
        /\{\{Tags\}\}/g,
        '<span data-gjs-type="anki-tags">{{Tags}}</span>'
    );

    // {{FieldName}} — generic field (must be LAST so it doesn't match the above)
    // Exclude fields that start with # ^ / (conditional markers already handled)
    result = result.replace(
        /\{\{([^#^/}:][^}]*)\}\}/g,
        (_m, field) => {
            // Skip if already wrapped (shouldn't happen, but safety net)
            const trimmed = field.trim();
            if (trimmed === 'FrontSide' || trimmed === 'Tags') return _m;
            return `<span data-gjs-type="anki-field" data-field="${_escAttr(trimmed)}">{{${trimmed}}}</span>`;
        }
    );

    return result;
}


/* ================================================================== */
/*  GrapeJS HTML → Anki HTML  (save path)                             */
/* ================================================================== */

/**
 * Convert GrapeJS editor HTML back to raw Anki template HTML.
 *
 * @param {string} html  HTML from editor.getHtml()
 * @returns {string}     Clean Anki template HTML
 */
function grapejsHtmlToAnki(html) {
    if (!html) return '';

    // Use a DOMParser for reliable round-tripping
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    _convertNodeToAnki(doc.body);

    // Serialize back to HTML string
    let result = doc.body.innerHTML;

    // Clean up GrapeJS artefacts
    result = _cleanGrapejsAttributes(result);

    return result;
}

/**
 * Recursively walk the DOM and convert our custom component elements
 * back into Anki Mustache tokens.
 */
function _convertNodeToAnki(node) {
    if (!node) return;

    // Process children first (depth-first) so inner conditionals convert before outer
    const children = Array.from(node.childNodes);
    children.forEach((child) => _convertNodeToAnki(child));

    if (node.nodeType !== Node.ELEMENT_NODE) return;

    const gjsType = node.dataset?.gjsType || node.getAttribute?.('data-gjs-type');
    if (!gjsType) return;

    const field = node.dataset?.field || node.getAttribute?.('data-field') || '';

    switch (gjsType) {
        case 'anki-field': {
            const text = document.createTextNode(`{{${field}}}`);
            node.parentNode.replaceChild(text, node);
            break;
        }
        case 'anki-cloze': {
            const text = document.createTextNode(`{{cloze:${field}}}`);
            node.parentNode.replaceChild(text, node);
            break;
        }
        case 'anki-hint': {
            const text = document.createTextNode(`{{hint:${field}}}`);
            node.parentNode.replaceChild(text, node);
            break;
        }
        case 'anki-type-answer': {
            const text = document.createTextNode(`{{type:${field}}}`);
            node.parentNode.replaceChild(text, node);
            break;
        }
        case 'anki-frontside': {
            const text = document.createTextNode('{{FrontSide}}');
            node.parentNode.replaceChild(text, node);
            break;
        }
        case 'anki-tags': {
            const text = document.createTextNode('{{Tags}}');
            node.parentNode.replaceChild(text, node);
            break;
        }
        case 'anki-conditional': {
            const condition = node.dataset?.condition || node.getAttribute?.('data-condition') || 'show';
            const prefix = condition === 'hide' ? `{{^${field}}}` : `{{#${field}}}`;
            const suffix = `{{/${field}}}`;
            const inner = node.innerHTML;

            // Create a wrapper fragment that preserves the inner content
            const frag = document.createDocumentFragment();
            const startText = document.createTextNode(prefix);
            frag.appendChild(startText);

            // Insert inner HTML via a temp container
            const temp = document.createElement('template');
            temp.innerHTML = inner;
            frag.appendChild(temp.content);

            const endText = document.createTextNode(suffix);
            frag.appendChild(endText);

            node.parentNode.replaceChild(frag, node);
            break;
        }
        // Non-Anki types (atd-text, atd-list, etc.) – just strip our data attrs
        default:
            break;
    }
}

/**
 * Remove GrapeJS / ATD data attributes and classes from the output HTML
 * so we get clean Anki-compatible HTML.
 */
function _cleanGrapejsAttributes(html) {
    return html
        // Remove data-gjs-type attributes
        .replace(/\s*data-gjs-type="[^"]*"/g, '')
        // Remove data-gjs attributes (drag/drop tracking)
        .replace(/\s*data-gjs[a-z-]*="[^"]*"/g, '')
        // Remove data-field attributes (our custom attr)
        .replace(/\s*data-field="[^"]*"/g, '')
        // Remove data-condition attributes
        .replace(/\s*data-condition="[^"]*"/g, '')
        // Remove empty class attributes left behind
        .replace(/\s*class=""/g, '')
        // Remove GrapeJS-generated IDs (i**** pattern)
        .replace(/\s*id="i[a-z0-9]+"/g, '')
        // Collapse multiple spaces
        .replace(/  +/g, ' ')
        // Clean empty tags that are just whitespace
        .replace(/(<[^/][^>]*>)\s*(<\/[^>]+>)/g, '$1$2');
}


/* ================================================================== */
/*  CSS handling                                                       */
/* ================================================================== */

/**
 * GrapeJS getCss() returns all styles including component-specific ones.
 * We may want to merge the editor-generated CSS with the user's original CSS.
 * For now, the strategy is:
 *   - On load: inject Anki CSS into GrapeJS as a style tag
 *   - On save: extract editor CSS and return it
 *
 * @param {string} editorCss  CSS from editor.getCss()
 * @param {string} originalCss  Original Anki CSS (for reference)
 * @returns {string}  Merged CSS suitable for Anki
 */
function mergeEditorCss(editorCss, originalCss) {
    // GrapeJS getCss() includes styles for all components,
    // including ones with generated selectors like #iabc { ... }
    // We want to keep user-defined CSS and GrapeJS structural CSS.
    // Strategy: use the editor CSS as-is since it represents the current state.
    // The original CSS was loaded into the editor, so any user edits are reflected.
    return editorCss || '';
}


/* ================================================================== */
/*  Helpers                                                            */
/* ================================================================== */

function _escAttr(str) {
    return str.replace(/&/g, '&amp;')
              .replace(/"/g, '&quot;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;');
}
