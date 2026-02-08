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
        content: '<section class="atd-section"><div>Section content</div></section>',
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('columns-2', {
        label: '2 Columns',
        category: 'Layout',
        content: `<div class="atd-row" data-gjs-droppable=".atd-col" style="display:flex;gap:12px;">
            <div class="atd-col" style="flex:1;min-height:60px;padding:8px;">Column 1</div>
            <div class="atd-col" style="flex:1;min-height:60px;padding:8px;">Column 2</div>
        </div>`,
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('columns-3', {
        label: '3 Columns',
        category: 'Layout',
        content: `<div class="atd-row" data-gjs-droppable=".atd-col" style="display:flex;gap:12px;">
            <div class="atd-col" style="flex:1;min-height:60px;padding:8px;">Col 1</div>
            <div class="atd-col" style="flex:1;min-height:60px;padding:8px;">Col 2</div>
            <div class="atd-col" style="flex:1;min-height:60px;padding:8px;">Col 3</div>
        </div>`,
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('container', {
        label: 'Container',
        category: 'Layout',
        content: '<div class="atd-container" style="max-width:800px;margin:0 auto;padding:16px;min-height:60px;">Container</div>',
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('divider', {
        label: 'Divider',
        category: 'Layout',
        content: '<hr class="atd-divider" style="border:none;border-top:1px solid #ccc;margin:12px 0;">',
        attributes: { class: 'gjs-block-layout' },
    });

    bm.add('spacer', {
        label: 'Spacer',
        category: 'Layout',
        content: '<div class="atd-spacer" style="height:24px;"></div>',
        attributes: { class: 'gjs-block-layout' },
    });

    // ═══════════════════════════════════════════════════════════
    //  Basic HTML blocks
    // ═══════════════════════════════════════════════════════════

    bm.add('text', {
        label: 'Text',
        category: 'Basic',
        content: '<div data-gjs-type="text">Insert your text here</div>',
        attributes: { class: 'gjs-block-basic' },
    });

    bm.add('heading', {
        label: 'Heading',
        category: 'Basic',
        content: '<h2>Heading</h2>',
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
        content: '<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>',
        attributes: { class: 'gjs-block-basic' },
    });
}
