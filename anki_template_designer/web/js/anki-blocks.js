/**
 * Anki-specific GrapeJS blocks.
 *
 * Adds draggable blocks to the block manager so users can build
 * Anki templates visually.
 */

/**
 * Register all Anki blocks on the given GrapeJS editor.
 * @param {import('grapesjs').Editor} editor
 */
function registerAnkiBlocks(editor) {
    const bm = editor.BlockManager;

    // ═══════════════════════════════════════════════════════════
    //  Anki-specific blocks
    // ═══════════════════════════════════════════════════════════

    bm.add('anki-field', {
        label: '{{Field}}',
        category: 'Anki',
        content: { type: 'anki-field' },
        attributes: { class: 'gjs-block-anki' },
    });

    bm.add('anki-cloze', {
        label: 'Cloze',
        category: 'Anki',
        content: { type: 'anki-cloze' },
        attributes: { class: 'gjs-block-anki' },
    });

    bm.add('anki-hint', {
        label: 'Hint',
        category: 'Anki',
        content: { type: 'anki-hint' },
        attributes: { class: 'gjs-block-anki' },
    });

    bm.add('anki-type-answer', {
        label: 'Type Answer',
        category: 'Anki',
        content: { type: 'anki-type-answer' },
        attributes: { class: 'gjs-block-anki' },
    });

    bm.add('anki-conditional', {
        label: 'Conditional',
        category: 'Anki',
        content: { type: 'anki-conditional' },
        attributes: { class: 'gjs-block-anki' },
    });

    bm.add('anki-tags', {
        label: 'Tags',
        category: 'Anki',
        content: { type: 'anki-tags' },
        attributes: { class: 'gjs-block-anki' },
    });

    bm.add('anki-frontside', {
        label: 'FrontSide',
        category: 'Anki',
        content: { type: 'anki-frontside' },
        attributes: { class: 'gjs-block-anki' },
    });

    // ═══════════════════════════════════════════════════════════
    //  Layout blocks
    // ═══════════════════════════════════════════════════════════

    bm.add('section', {
        label: 'Section',
        category: 'Layout',
        content: { type: 'atd-section' },
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('columns-2', {
        label: '2 Columns',
        category: 'Layout',
        content: {
            type: 'atd-row',
            components: [
                { type: 'atd-column' },
                { type: 'atd-column' },
            ],
        },
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('columns-3', {
        label: '3 Columns',
        category: 'Layout',
        content: {
            type: 'atd-row',
            components: [
                { type: 'atd-column' },
                { type: 'atd-column' },
                { type: 'atd-column' },
            ],
        },
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('container', {
        label: 'Container',
        category: 'Layout',
        content: { type: 'atd-container' },
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('divider', {
        label: 'Divider',
        category: 'Layout',
        content: { type: 'atd-divider' },
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('spacer', {
        label: 'Spacer',
        category: 'Layout',
        content: { type: 'atd-spacer' },
        attributes: { class: 'gjs-block-layout' },
    });

    // ═══════════════════════════════════════════════════════════
    //  Basic HTML blocks
    // ═══════════════════════════════════════════════════════════

    bm.add('text', {
        label: 'Text',
        category: 'Basic',
        content: { type: 'atd-text' },
        attributes: { class: 'gjs-block-basic' },
    });

    bm.add('image', {
        label: 'Image',
        category: 'Basic',
        select: true,
        activate: true,
        content: { type: 'image' },
        attributes: { class: 'gjs-block-basic' },
    });

    bm.add('link', {
        label: 'Link',
        category: 'Basic',
        content: '<a href="#" data-gjs-type="link">Link text</a>',
        attributes: { class: 'gjs-block-basic' },
    });

    bm.add('list', {
        label: 'List',
        category: 'Basic',
        content: { type: 'atd-list' },
        attributes: { class: 'gjs-block-basic' },
    });
}
