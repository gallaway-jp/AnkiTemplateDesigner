/**
 * i18n-enabled Component Guide Helper
 * 
 * This module provides functions to retrieve translated component definitions.
 * It works with both the vanilla JS bridge and React components.
 */

import i18next from './config';

/**
 * Get translated component guide
 * Returns the COMPONENT_GUIDE object with all strings translated
 */
function getTranslatedComponentGuide() {
    const t = (key) => i18next?.t(key) || key;

    return {
        // Basic Components
        'text': {
            label: t('components.text.label'),
            category: 'Basic',
            description: t('components.text.description'),
            help: t('components.text.help'),
            examples: [
                'Labels',
                'Instructions',
                'Section headers'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'field': {
            label: t('components.field.label'),
            category: 'Basic',
            description: t('components.field.description'),
            help: t('components.field.help'),
            examples: [
                'Card front',
                'Card back',
                'Extra info'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'image': {
            label: t('components.image.label'),
            category: 'Media',
            description: t('components.image.description'),
            help: t('components.image.help'),
            examples: [
                'Photos',
                'Diagrams',
                'Flashcard images'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'video': {
            label: t('components.video.label'),
            category: 'Media',
            description: t('components.video.description'),
            help: t('components.video.help'),
            examples: [
                'Pronunciation guides',
                'Demonstrations',
                'Tutorials'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'audio': {
            label: t('components.audio.label'),
            category: 'Media',
            description: t('components.audio.description'),
            help: t('components.audio.help'),
            examples: [
                'Pronunciation',
                'Language lessons',
                'Music'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'container': {
            label: t('components.container.label'),
            category: 'Layout',
            description: t('components.container.description'),
            help: t('components.container.help'),
            examples: [
                'Header section',
                'Content area',
                'Footer'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'row': {
            label: t('components.row.label'),
            category: 'Layout',
            description: t('components.row.description'),
            help: t('components.row.help'),
            examples: [
                'Two-column layout',
                'Buttons in a line',
                'Side-by-side images'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'column': {
            label: t('components.column.label'),
            category: 'Layout',
            description: t('components.column.description'),
            help: t('components.column.help'),
            examples: [
                'Vertical list',
                'Stacked content',
                'Info blocks'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'cloze': {
            label: t('components.cloze.label'),
            category: 'Anki Features',
            description: t('components.cloze.description'),
            help: t('components.cloze.help'),
            examples: [
                'Fill-in-the-blank questions',
                'Study with hints',
                'Progressive reveal'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html#cloze-deletion'
        },
        'hint': {
            label: t('components.hint.label'),
            category: 'Anki Features',
            description: t('components.hint.description'),
            help: t('components.hint.help'),
            examples: [
                'Hints',
                'Clues',
                'Study aids'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'conditional': {
            label: t('components.conditional.label'),
            category: 'Anki Features',
            description: t('components.conditional.description'),
            help: t('components.conditional.help'),
            examples: [
                'Optional fields',
                'Extra info sections',
                'Conditional content'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html#conditionals'
        },
        'button': {
            label: t('components.button.label'),
            category: 'Interactive',
            description: t('components.button.description'),
            help: t('components.button.help'),
            examples: [
                'Navigation',
                'Links',
                'Actions'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'link': {
            label: t('components.link.label'),
            category: 'Interactive',
            description: t('components.link.description'),
            help: t('components.link.help'),
            examples: [
                'References',
                'Sources',
                'External links'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'badge': {
            label: t('components.badge.label'),
            category: 'Visual',
            description: t('components.badge.description'),
            help: t('components.badge.help'),
            examples: [
                'Tags',
                'Categories',
                'Status indicators'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'alert': {
            label: 'Alert',
            category: 'Visual',
            description: 'Highlighted warning/info box',
            help: 'Important notice box that stands out. Use for warnings, important information, or callouts.',
            examples: [
                'Important notes',
                'Warnings',
                'Key information'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        },
        'separator': {
            label: t('components.divider.label'),
            category: 'Visual',
            description: t('components.divider.description'),
            help: t('components.divider.help'),
            examples: [
                'Section breaks',
                'Visual dividers',
                'Content separation'
            ],
            moreLink: 'https://docs.ankiweb.net/templates/intro.html'
        }
    };
}

/**
 * Get a specific component's information with translation
 */
function getComponentInfo(componentType) {
    const guide = getTranslatedComponentGuide();
    return guide[componentType] || null;
}

/**
 * Get component label (translated)
 */
function getComponentLabel(componentType) {
    const info = getComponentInfo(componentType);
    return info ? info.label : componentType;
}

/**
 * Get component description (translated)
 */
function getComponentDescription(componentType) {
    const info = getComponentInfo(componentType);
    return info ? info.description : '';
}

/**
 * Get component help text (translated)
 */
function getComponentHelp(componentType) {
    const info = getComponentInfo(componentType);
    return info ? info.help : '';
}

// Export for global usage
if (typeof window !== 'undefined') {
    window.i18nComponentGuide = {
        getTranslatedComponentGuide,
        getComponentInfo,
        getComponentLabel,
        getComponentDescription,
        getComponentHelp
    };
}
