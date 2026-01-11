/**
 * Anki Custom Traits for GrapeJS
 * Defines custom trait types for component properties
 */

(function() {
    'use strict';
    
    /**
     * Register all Anki traits
     * @param {object} editor - GrapeJS editor instance
     */
    window.registerAnkiTraits = function(editor) {
        const traitManager = editor.TraitManager;
        
        // ========== Anki Field Select Trait ========== 
        
        traitManager.addType('anki-field-select', {
            events: {
                'change': 'onChange'
            },
            
            onValueChange() {
                const value = this.model.get('value');
                const component = this.target;
                
                // Update data attribute
                component.addAttributes({ 'data-anki-field': value });
                
                // Update content to show {{FieldName}}
                if (component.components().length === 0) {
                    component.components(`{{${value}}}`);
                }
            },
            
            onChange(ev) {
                const value = ev.target.value;
                this.model.set('value', value);
                this.onValueChange();
            },
            
            getInputEl() {
                if (!this.inputEl) {
                    const fields = window.availableFields || ['Front', 'Back', 'Extra'];
                    
                    const select = document.createElement('select');
                    select.className = 'gjs-field';
                    
                    fields.forEach(field => {
                        const option = document.createElement('option');
                        option.value = field;
                        option.textContent = field;
                        select.appendChild(option);
                    });
                    
                    this.inputEl = select;
                }
                
                return this.inputEl;
            }
        });
        
        // ========== Anki Behavior Trait ========== 
        
        traitManager.addType('anki-behavior', {
            events: {
                'change': 'onChange'
            },
            
            onValueChange() {
                const value = this.model.get('value');
                const component = this.target;
                const trigger = this.model.get('trigger') || 'click';
                
                // Update data attribute
                component.addAttributes({ [`data-anki-${trigger}`]: value });
            },
            
            onChange(ev) {
                const value = ev.target.value;
                this.model.set('value', value);
                this.onValueChange();
            },
            
            getInputEl() {
                if (!this.inputEl) {
                    const behaviors = window.availableBehaviors || [];
                    
                    const select = document.createElement('select');
                    select.className = 'gjs-field';
                    
                    // Add empty option
                    const emptyOpt = document.createElement('option');
                    emptyOpt.value = '';
                    emptyOpt.textContent = '-- Select Behavior --';
                    select.appendChild(emptyOpt);
                    
                    // Group by category
                    const byCategory = {};
                    behaviors.forEach(behavior => {
                        const cat = behavior.category || 'Other';
                        if (!byCategory[cat]) byCategory[cat] = [];
                        byCategory[cat].push(behavior);
                    });
                    
                    Object.keys(byCategory).sort().forEach(category => {
                        const optgroup = document.createElement('optgroup');
                        optgroup.label = category;
                        
                        byCategory[category].forEach(behavior => {
                            const option = document.createElement('option');
                            option.value = behavior.name;
                            option.textContent = `${behavior.name} - ${behavior.description}`;
                            optgroup.appendChild(option);
                        });
                        
                        select.appendChild(optgroup);
                    });
                    
                    this.inputEl = select;
                }
                
                return this.inputEl;
            }
        });
        
        // ========== Trigger Type Trait ========== 
        
        traitManager.addType('trigger-select', {
            events: {
                'change': 'onChange'
            },
            
            onChange(ev) {
                const value = ev.target.value;
                this.model.set('value', value);
            },
            
            getInputEl() {
                if (!this.inputEl) {
                    const triggers = [
                        { value: 'click', label: 'Click' },
                        { value: 'dblclick', label: 'Double Click' },
                        { value: 'mouseover', label: 'Mouse Over' },
                        { value: 'mouseout', label: 'Mouse Out' },
                        { value: 'keydown', label: 'Key Down' },
                        { value: 'load', label: 'On Load' }
                    ];
                    
                    const select = document.createElement('select');
                    select.className = 'gjs-field';
                    
                    triggers.forEach(trigger => {
                        const option = document.createElement('option');
                        option.value = trigger.value;
                        option.textContent = trigger.label;
                        select.appendChild(option);
                    });
                    
                    this.inputEl = select;
                }
                
                return this.inputEl;
            }
        });
        
        // ========== Card Side Select Trait ========== 
        
        traitManager.addType('card-side-select', {
            events: {
                'change': 'onChange'
            },
            
            onValueChange() {
                const value = this.model.get('value');
                const component = this.target;
                
                // Update data attribute
                component.addAttributes({ 'data-card-side': value });
            },
            
            onChange(ev) {
                const value = ev.target.value;
                this.model.set('value', value);
                this.onValueChange();
            },
            
            getInputEl() {
                if (!this.inputEl) {
                    const sides = [
                        { value: 'front', label: 'Front' },
                        { value: 'back', label: 'Back' },
                        { value: 'both', label: 'Both' }
                    ];
                    
                    const select = document.createElement('select');
                    select.className = 'gjs-field';
                    
                    sides.forEach(side => {
                        const option = document.createElement('option');
                        option.value = side.value;
                        option.textContent = side.label;
                        select.appendChild(option);
                    });
                    
                    this.inputEl = select;
                }
                
                return this.inputEl;
            }
        });
        
        console.log('[Traits] Registered all Anki traits');
    };
})();
