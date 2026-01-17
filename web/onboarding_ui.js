/**
 * Issue #47: User Onboarding System - Frontend
 * 
 * Manages the onboarding UI, tutorial flow, guided tour, and template library.
 * Features: Interactive tutorial, guided tour, templates library, progress tracking.
 */

class OnboardingUI {
    /**
     * Initialize the onboarding UI system.
     */
    constructor() {
        this.tutorial_active = false;
        this.tour_active = false;
        this.current_step = null;
        this.progress = null;
        this.api_base = '/api';
        this.init_ui();
    }

    /**
     * Initialize UI elements.
     */
    init_ui() {
        this.create_onboarding_dialog();
        this.create_tutorial_panel();
        this.create_tour_overlay();
        this.create_templates_panel();
        this.create_progress_indicator();
        this.setup_event_listeners();
    }

    /**
     * Create the main onboarding dialog.
     */
    create_onboarding_dialog() {
        const dialog = document.createElement('div');
        dialog.id = 'onboarding-dialog';
        dialog.className = 'onboarding-dialog';
        dialog.innerHTML = `
            <div class="onboarding-content">
                <div class="onboarding-header">
                    <h2>Welcome to Template Designer</h2>
                    <button class="close-btn" aria-label="Close onboarding">&times;</button>
                </div>
                <div class="onboarding-body">
                    <div class="onboarding-options">
                        <button class="onboarding-btn start-tutorial-btn" data-action="start-tutorial">
                            <span class="icon">📚</span>
                            <span class="label">Start Interactive Tutorial</span>
                            <span class="description">Learn step-by-step (10 minutes)</span>
                        </button>
                        <button class="onboarding-btn start-tour-btn" data-action="start-tour">
                            <span class="icon">👁️</span>
                            <span class="label">Take a Quick Tour</span>
                            <span class="description">UI overview (5 minutes)</span>
                        </button>
                        <button class="onboarding-btn view-templates-btn" data-action="view-templates">
                            <span class="icon">🎨</span>
                            <span class="label">Browse Templates</span>
                            <span class="description">Choose a starter template</span>
                        </button>
                        <button class="onboarding-btn skip-btn" data-action="skip">
                            <span class="icon">⏭️</span>
                            <span class="label">Skip for Now</span>
                            <span class="description">Start building (can replay later)</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    }

    /**
     * Create the tutorial step panel.
     */
    create_tutorial_panel() {
        const panel = document.createElement('div');
        panel.id = 'tutorial-panel';
        panel.className = 'tutorial-panel hidden';
        panel.innerHTML = `
            <div class="tutorial-header">
                <h3 class="tutorial-title"></h3>
                <button class="close-btn" aria-label="Close tutorial">&times;</button>
            </div>
            <div class="tutorial-body">
                <div class="step-progress">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <span class="progress-text"></span>
                </div>
                <div class="step-content">
                    <p class="step-description"></p>
                    <div class="step-instructions"></div>
                    <div class="step-hint hidden">
                        <strong>💡 Hint:</strong>
                        <p class="hint-text"></p>
                    </div>
                </div>
            </div>
            <div class="tutorial-footer">
                <button class="tutorial-btn hint-btn" data-action="show-hint">Show Hint</button>
                <button class="tutorial-btn skip-step-btn" data-action="skip-step">Skip Step</button>
                <button class="tutorial-btn next-btn" data-action="next-step">Next</button>
            </div>
        `;
        document.body.appendChild(panel);
    }

    /**
     * Create the tour overlay.
     */
    create_tour_overlay() {
        const overlay = document.createElement('div');
        overlay.id = 'tour-overlay';
        overlay.className = 'tour-overlay hidden';
        overlay.innerHTML = `
            <div class="tour-spotlight"></div>
            <div class="tour-tooltip">
                <div class="tooltip-content">
                    <h4 class="tooltip-title"></h4>
                    <p class="tooltip-description"></p>
                </div>
                <div class="tooltip-footer">
                    <button class="tour-btn prev-btn" data-action="prev-highlight">Previous</button>
                    <button class="tour-btn next-btn" data-action="next-highlight">Next</button>
                    <button class="tour-btn skip-btn" data-action="end-tour">End Tour</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    /**
     * Create the templates panel.
     */
    create_templates_panel() {
        const panel = document.createElement('div');
        panel.id = 'templates-panel';
        panel.className = 'templates-panel hidden';
        panel.innerHTML = `
            <div class="templates-header">
                <h3>Starter Templates</h3>
                <button class="close-btn" aria-label="Close templates">&times;</button>
            </div>
            <div class="templates-filters">
                <button class="filter-btn active" data-category="all">All</button>
                <button class="filter-btn" data-category="cards">Cards</button>
                <button class="filter-btn" data-category="styling">Styling</button>
                <button class="filter-btn" data-category="beginner">Beginner</button>
                <button class="filter-btn" data-category="intermediate">Intermediate</button>
            </div>
            <div class="templates-grid"></div>
        `;
        document.body.appendChild(panel);
    }

    /**
     * Create the progress indicator.
     */
    create_progress_indicator() {
        const indicator = document.createElement('div');
        indicator.id = 'onboarding-progress';
        indicator.className = 'onboarding-progress hidden';
        indicator.innerHTML = `
            <div class="progress-item">
                <span class="progress-label">Tutorial:</span>
                <div class="progress-badge"></div>
            </div>
            <div class="progress-item">
                <span class="progress-label">Tour:</span>
                <div class="progress-badge"></div>
            </div>
            <div class="progress-item">
                <span class="progress-label">Templates:</span>
                <div class="progress-badge"></div>
            </div>
            <button class="replay-btn" data-action="replay-tutorial">Replay Tutorial</button>
        `;
        document.body.appendChild(indicator);
    }

    /**
     * Set up event listeners.
     */
    setup_event_listeners() {
        document.addEventListener('click', (e) => this.handle_click(e));
    }

    /**
     * Handle click events.
     */
    handle_click(e) {
        const action = e.target.closest('[data-action]')?.dataset.action;
        
        switch (action) {
            case 'start-tutorial':
                this.start_tutorial();
                break;
            case 'start-tour':
                this.start_tour();
                break;
            case 'view-templates':
                this.show_templates_panel();
                break;
            case 'skip':
                this.skip_onboarding();
                break;
            case 'next-step':
                this.next_tutorial_step();
                break;
            case 'skip-step':
                this.skip_tutorial_step();
                break;
            case 'show-hint':
                this.show_hint();
                break;
            case 'next-highlight':
                this.next_tour_highlight();
                break;
            case 'prev-highlight':
                this.prev_tour_highlight();
                break;
            case 'end-tour':
                this.end_tour();
                break;
            case 'replay-tutorial':
                this.replay_tutorial();
                break;
        }
    }

    /**
     * Start the interactive tutorial.
     */
    async start_tutorial() {
        try {
            this.tutorial_active = true;
            document.getElementById('onboarding-dialog').classList.add('hidden');
            document.getElementById('tutorial-panel').classList.remove('hidden');
            
            // Load first step from server
            const response = await fetch(`${this.api_base}/onboarding/tutorial/start`);
            const data = await response.json();
            
            if (data.success) {
                this.current_step = data.step;
                this.display_tutorial_step(data.step);
            }
        } catch (error) {
            console.error('Error starting tutorial:', error);
        }
    }

    /**
     * Display a tutorial step.
     */
    display_tutorial_step(step) {
        const panel = document.getElementById('tutorial-panel');
        
        // Update header
        panel.querySelector('.tutorial-title').textContent = step.title;
        
        // Update progress
        const step_number = parseInt(step.step_id.replace('step_', ''));
        const progress_text = `Step ${step_number} of 6`;
        const progress_percentage = (step_number / 6) * 100;
        
        panel.querySelector('.progress-text').textContent = progress_text;
        panel.querySelector('.progress-fill').style.width = `${progress_percentage}%`;
        
        // Update content
        panel.querySelector('.step-description').textContent = step.description;
        panel.querySelector('.step-instructions').innerHTML = `
            <div class="instruction-box">
                <p>${step.instructions}</p>
                <div class="target-element">${step.target_element}</div>
            </div>
        `;
        
        // Update hint
        const hint_element = panel.querySelector('.step-hint');
        if (step.hint) {
            panel.querySelector('.hint-text').textContent = step.hint;
            hint_element.classList.remove('hidden');
        } else {
            hint_element.classList.add('hidden');
        }
        
        // Highlight target element
        this.highlight_element(step.target_element);
    }

    /**
     * Advance to next tutorial step.
     */
    async next_tutorial_step() {
        try {
            const response = await fetch(`${this.api_base}/onboarding/tutorial/advance`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                if (data.step) {
                    this.current_step = data.step;
                    this.display_tutorial_step(data.step);
                } else {
                    this.complete_tutorial();
                }
            }
        } catch (error) {
            console.error('Error advancing tutorial:', error);
        }
    }

    /**
     * Skip a tutorial step.
     */
    async skip_tutorial_step() {
        this.next_tutorial_step();
    }

    /**
     * Show hint for current step.
     */
    show_hint() {
        const hint_element = document.getElementById('tutorial-panel').querySelector('.step-hint');
        hint_element.classList.remove('hidden');
        
        // Scroll to hint
        hint_element.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Complete the tutorial.
     */
    complete_tutorial() {
        this.tutorial_active = false;
        document.getElementById('tutorial-panel').classList.add('hidden');
        this.show_completion_toast('Tutorial Complete! 🎉');
        this.update_progress_indicator();
    }

    /**
     * Start the guided tour.
     */
    async start_tour() {
        try {
            this.tour_active = true;
            document.getElementById('onboarding-dialog').classList.add('hidden');
            document.getElementById('tour-overlay').classList.remove('hidden');
            
            const response = await fetch(`${this.api_base}/onboarding/tour/start`);
            const data = await response.json();
            
            if (data.success) {
                this.display_tour_highlight(data.highlight);
            }
        } catch (error) {
            console.error('Error starting tour:', error);
        }
    }

    /**
     * Display a tour highlight.
     */
    display_tour_highlight(highlight) {
        const overlay = document.getElementById('tour-overlay');
        const tooltip = overlay.querySelector('.tour-tooltip');
        const element = document.getElementById(highlight.element_id);
        
        if (element) {
            // Position spotlight on element
            const rect = element.getBoundingClientRect();
            overlay.querySelector('.tour-spotlight').style.cssText = `
                top: ${rect.top}px;
                left: ${rect.left}px;
                width: ${rect.width}px;
                height: ${rect.height}px;
            `;
        }
        
        // Update tooltip
        tooltip.querySelector('.tooltip-title').textContent = highlight.title;
        tooltip.querySelector('.tooltip-description').textContent = highlight.description;
        
        // Position tooltip based on position preference
        tooltip.className = `tour-tooltip tooltip-${highlight.position}`;
    }

    /**
     * Move to next tour highlight.
     */
    async next_tour_highlight() {
        try {
            const response = await fetch(`${this.api_base}/onboarding/tour/next`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                if (data.highlight) {
                    this.display_tour_highlight(data.highlight);
                } else {
                    this.end_tour();
                }
            }
        } catch (error) {
            console.error('Error advancing tour:', error);
        }
    }

    /**
     * Move to previous tour highlight.
     */
    prev_tour_highlight() {
        // Navigate to previous highlight (if implemented on backend)
        console.log('Previous highlight clicked');
    }

    /**
     * End the guided tour.
     */
    end_tour() {
        this.tour_active = false;
        document.getElementById('tour-overlay').classList.add('hidden');
        this.show_completion_toast('Tour Complete! 👋');
        this.update_progress_indicator();
    }

    /**
     * Show templates panel.
     */
    async show_templates_panel() {
        try {
            document.getElementById('onboarding-dialog').classList.add('hidden');
            document.getElementById('templates-panel').classList.remove('hidden');
            
            // Load templates
            const response = await fetch(`${this.api_base}/onboarding/templates`);
            const data = await response.json();
            
            if (data.success) {
                this.display_templates(data.templates);
            }
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    /**
     * Display templates in grid.
     */
    display_templates(templates) {
        const grid = document.querySelector('.templates-grid');
        grid.innerHTML = '';
        
        templates.forEach(template => {
            const card = document.createElement('div');
            card.className = 'template-card';
            card.innerHTML = `
                <div class="template-header">
                    <h4>${template.name}</h4>
                    <span class="difficulty-badge ${template.difficulty}">${template.difficulty}</span>
                </div>
                <p class="template-description">${template.description}</p>
                <div class="template-fields">
                    <strong>Fields:</strong>
                    <span>${template.expected_fields.join(', ')}</span>
                </div>
                <button class="load-template-btn" data-template-id="${template.template_id}">
                    Use This Template
                </button>
            `;
            
            card.querySelector('.load-template-btn').addEventListener('click', () => {
                this.load_template(template.template_id);
            });
            
            grid.appendChild(card);
        });
    }

    /**
     * Load a template for editing.
     */
    async load_template(template_id) {
        try {
            const response = await fetch(`${this.api_base}/onboarding/templates/${template_id}/load`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                // Load template into editor
                window.dispatchEvent(new CustomEvent('load-template', { 
                    detail: data.template 
                }));
                
                // Close templates panel
                document.getElementById('templates-panel').classList.add('hidden');
                this.show_completion_toast('Template Loaded! 🎨');
                this.update_progress_indicator();
            }
        } catch (error) {
            console.error('Error loading template:', error);
        }
    }

    /**
     * Skip onboarding.
     */
    skip_onboarding() {
        document.getElementById('onboarding-dialog').classList.add('hidden');
        this.show_completion_toast('Onboarding skipped. You can replay it anytime from Help menu.');
    }

    /**
     * Replay the tutorial.
     */
    async replay_tutorial() {
        try {
            const response = await fetch(`${this.api_base}/onboarding/tutorial/replay`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.start_tutorial();
            }
        } catch (error) {
            console.error('Error replaying tutorial:', error);
        }
    }

    /**
     * Highlight an element on the canvas.
     */
    highlight_element(element_id) {
        // Remove previous highlight
        document.querySelectorAll('.highlighted').forEach(el => {
            el.classList.remove('highlighted');
        });
        
        // Add highlight to target element
        const element = document.getElementById(element_id) || 
                       document.querySelector(`[data-element-id="${element_id}"]`);
        if (element) {
            element.classList.add('highlighted');
            element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    /**
     * Update progress indicator.
     */
    update_progress_indicator() {
        const indicator = document.getElementById('onboarding-progress');
        
        // Fetch updated progress from server
        fetch(`${this.api_base}/onboarding/progress`)
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const progress = data.progress;
                    
                    // Update badges
                    const badges = indicator.querySelectorAll('.progress-badge');
                    badges[0].textContent = progress.tutorial_progress;
                    badges[0].className = `progress-badge ${progress.tutorial_progress === '6/6' ? 'complete' : ''}`;
                    
                    badges[1].textContent = progress.tour_completed ? '✓' : '○';
                    badges[1].className = `progress-badge ${progress.tour_completed ? 'complete' : ''}`;
                    
                    badges[2].textContent = progress.templates_viewed > 0 ? `${progress.templates_viewed}` : '○';
                    badges[2].className = `progress-badge ${progress.first_template_created ? 'complete' : ''}`;
                    
                    if (progress.is_fully_onboarded) {
                        indicator.querySelector('.replay-btn').classList.remove('hidden');
                    }
                }
            })
            .catch(error => console.error('Error updating progress:', error));
    }

    /**
     * Show a completion toast notification.
     */
    show_completion_toast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Fade out after 3 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Show onboarding dialog.
     */
    show_onboarding() {
        document.getElementById('onboarding-dialog').classList.remove('hidden');
    }

    /**
     * Hide all onboarding UI elements.
     */
    hide_all() {
        document.getElementById('onboarding-dialog').classList.add('hidden');
        document.getElementById('tutorial-panel').classList.add('hidden');
        document.getElementById('tour-overlay').classList.add('hidden');
        document.getElementById('templates-panel').classList.add('hidden');
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.onboarding_ui = new OnboardingUI();
});
