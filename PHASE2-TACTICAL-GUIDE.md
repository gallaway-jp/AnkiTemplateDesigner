# Phase 2 Tactical Guide - Day-by-Day Implementation

**Purpose:** Day-by-day breakdown for developers  
**Duration:** 2 weeks (10 business days)  
**Total Effort:** 12-14 hours  
**Approach:** Sequential with options for parallelization

---

## 📅 Week 1: Foundation (5-6 hours)

### Monday-Tuesday: Sprint 1.1 - Theme & Accessibility (1.5-2h)

**Goal:** Implement WCAG AAA compliant theme system

#### Monday (1-1.5 hours)

**Pre-work (15 min):**
- Read: Section "Issue #10" in [UX-PHASE2-ANALYSIS.md](docs/UX-PHASE2-ANALYSIS.md)
- Review: CSS variables example in specs

**Implementation (45 min - 1h):**
1. Open `web/designer.css`
2. Update CSS variables for WCAG AAA:
   ```css
   :root {
       /* Light mode */
       --text-primary: #1a1a1a;      /* 18:1 contrast */
       --text-secondary: #424242;    /* 12:1 contrast */
       --accent-color: #1976d2;
       /* ... (see specs for all variables) */
   }
   
   body[data-theme="dark"] {
       /* Dark mode */
       --text-primary: #ffffff;      /* 21:1 contrast */
       --text-secondary: #bdbdbd;    /* 8:1 contrast */
       --accent-color: #90caf9;
       /* ... (see specs) */
   }
   ```
3. Add high contrast mode variables
4. Add focus state styling

**Testing (15-30 min):**
- [ ] Check contrast with online tool (WebAIM)
- [ ] Test light mode text on light backgrounds
- [ ] Test dark mode text on dark backgrounds
- [ ] Verify focus states on buttons

**Deliverable:** WCAG AAA color scheme implemented

---

#### Tuesday (30 min - 1h)

**Implementation (30 min - 1h):**
1. Update GrapeJS panel styling:
   ```css
   .gjs-blocks-view,
   .gjs-traits-view,
   .gjs-layers-view {
       background: var(--bg-secondary) !important;
       color: var(--text-primary) !important;
   }
   ```
2. Add all element styling (buttons, inputs, etc.)
3. Implement high contrast mode toggle

**Testing (15-30 min):**
- [ ] All panels properly themed
- [ ] High contrast mode toggle works
- [ ] Colors consistent across UI
- [ ] No color conflicts

**Commit:** "feat: WCAG AAA theme system with high contrast mode"

---

### Wednesday-Thursday: Sprint 1.2 - Component Help System (1.5-2h)

**Goal:** Create help system for all components with interactive panel

#### Wednesday (1-1.5 hours)

**Pre-work (15 min):**
- Read: Section "Issue #9" in [UX-PHASE2-ANALYSIS.md](docs/UX-PHASE2-ANALYSIS.md)
- Review: ComponentGuide data structure in specs

**Implementation (1-1.5h):**
1. Open `web/designer.js`
2. Add COMPONENT_GUIDE object at top:
   ```javascript
   const COMPONENT_GUIDE = {
       'text': {
           label: 'Text',
           icon: 'Aa',
           description: 'Static text content (not dynamic)',
           help: 'Use for labels, instructions, or static content...',
           examples: ['Labels', 'Instructions', 'Formatting'],
           category: 'Content',
       },
       'field': { /* ... */ },
       // ... all 85+ components
   };
   ```
3. Create ComponentHelp class (see specs)
4. Add hover listeners to blocks

**Testing (15 min):**
- [ ] Component guide data loads
- [ ] Hover on components shows tooltips
- [ ] Help button appears on hover
- [ ] No console errors

**Deliverable:** Component guide data structure complete

---

#### Thursday (30 min - 1h)

**Implementation (30 min - 1h):**
1. Create help panel HTML/CSS:
   - Panel slides in from right
   - Shows component info
   - Has "Learn more" link
2. Implement ComponentHelp class methods:
   - `show(componentId)` - opens help
   - `hide()` - closes help
   - `updateContent()` - loads new content
3. Wire up help buttons

**Testing (15-30 min):**
- [ ] Help panel opens/closes smoothly
- [ ] Content updates correctly
- [ ] Animations smooth
- [ ] Mobile responsive

**Commit:** "feat: Interactive component help system with descriptions"

---

### Friday: Sprint 1.3 - Save/Load Feedback (1-1.5h)

**Goal:** Visual feedback when saving templates

**Pre-work (15 min):**
- Read: Section "Issue #6" in [UX-PHASE2-ANALYSIS.md](docs/UX-PHASE2-ANALYSIS.md)
- Review: SaveState implementation in specs

**Implementation (45 min - 1h):**
1. Open `gui/designer_dialog.py`
2. Add SaveState tracking:
   ```python
   @dataclass
   class SaveState:
       is_saving: bool = False
       last_save_time: Optional[float] = None
       save_success: bool = False
       save_error: Optional[str] = None
   ```
3. Update `_handle_save()` method with:
   - Disable button during save
   - Show progress state
   - Add success notification
   - Add error handling
4. Add helper methods for notifications

**Testing (15-30 min):**
- [ ] Save button disables during save
- [ ] Success message appears
- [ ] Error message appears on failure
- [ ] Button re-enables after save

**Commit:** "feat: Save/load user feedback with progress and status"

**Week 1 Complete:** 3 major fixes done, all tested ✅

---

## 📅 Week 2: Polish & Advanced (4-5 hours)

### Monday-Tuesday: Sprint 2.1 - Undo/Redo Feedback (1-1.5h)

**Goal:** Clear indication of undo/redo availability

**Pre-work (10 min):**
- Read: Section "Issue #8" in [UX-PHASE2-ANALYSIS.md](docs/UX-PHASE2-ANALYSIS.md)
- Review: UndoRedoManager in specs

**Implementation (45 min - 1h):**
1. Open `web/designer.js`
2. Create UndoRedoManager class:
   ```javascript
   class UndoRedoManager {
       constructor(editor) {
           this.editor = editor;
           this.undoBtn = document.querySelector('[data-action="undo"]');
           this.redoBtn = document.querySelector('[data-action="redo"]');
           this.setup();
       }
       
       setup() {
           this.editor.on('change', () => this.updateButtonState());
       }
       
       updateButtonState() {
           const hasUndo = this.undoManager?.hasUndo?.() || false;
           this.undoBtn.disabled = !hasUndo;
       }
   }
   ```
3. Wire up in registerCustomizations()
4. Add notifications on undo/redo

**Testing (15-30 min):**
- [ ] Buttons disable when nothing to undo
- [ ] Buttons enable when history available
- [ ] Notifications appear on undo/redo
- [ ] No visual glitches

**Commit:** "feat: Undo/redo button state and notifications"

---

### Wednesday-Friday: Sprint 2.2 - Mobile Preview (2-2.5h)

**Goal:** Realistic phone preview with device switching

**Pre-work (15 min):**
- Read: Section "Issue #7" in [UX-PHASE2-ANALYSIS.md](docs/UX-PHASE2-ANALYSIS.md)
- Review: DEVICES object and mobile frame in specs

**Wednesday (1-1.5h):**

**Implementation:**
1. Open `web/designer.js`
2. Define DEVICES object:
   ```javascript
   const DEVICES = {
       DESKTOP: {
           id: 'desktop',
           name: 'Desktop',
           width: 'auto',
           height: 'auto',
       },
       MOBILE: {
           id: 'mobile',
           name: 'Mobile (Portrait)',
           width: '390px',
           height: '844px',
           statusBar: 25,
       },
       // ... other devices
   };
   ```
3. Create setupDevicePreview() function
4. Implement device buttons and switching

**Testing (15-30 min):**
- [ ] Device buttons appear
- [ ] Clicking buttons switches devices
- [ ] Canvas resizes to device dimensions
- [ ] No layout breaks

---

**Thursday-Friday (1h):**

**Implementation:**
1. Style device frames in `web/designer.css`:
   - Phone bezel effect
   - Safe area visualization
   - Status bar
   - Home indicator (for iOS)
2. Test responsive behavior
3. Add device info display

**Testing (30 min):**
- [ ] Phone frame renders
- [ ] Bezel looks realistic
- [ ] Safe areas visible
- [ ] Orientation switching works
- [ ] Looks professional

**Commit:** "feat: Mobile device preview with realistic phone frame"

**Week 2 Complete:** All 5 Phase 2 fixes done, all tested ✅

---

## 🧪 Testing Timeline

### Daily Testing (as you code)
- 15-30 min per day
- Test feature as implemented
- Check console for errors
- Manual browser testing

### Wednesday EOD Review
- All Week 1 fixes working?
- Any regressions?
- QA spot checks
- Code quality OK?

### Friday Final Testing
- Complete VERIFICATION-CHECKLIST.md
- All Phase 1 features still work?
- No new errors?
- Ready to merge?

---

## 🔄 Parallel Work (If 2 Developers)

### Developer A: UI/CSS (Days 1-5)
```
Mon-Tue:  Theme & Accessibility
Wed-Thu:  Component Help CSS
Fri:      Testing & refinement
```

### Developer B: Functionality (Days 1-10)
```
Mon:      Save/Load Feedback
Tue-Wed:  Undo/Redo Feedback
Thu-Fri:  Mobile Preview (Part 1)
Mon-Tue:  Mobile Preview (Part 2)
Wed:      Testing & finalization
```

**Result:** Both developers finish Wednesday, buffer for fixes Thursday-Friday

---

## 💻 Technical Shortcuts

### Leverage Phase 1 Code
**Copy from Phase 1 where applicable:**
- Welcome overlay structure → Help panel
- Loading progress pattern → Save progress
- Keyboard shortcut setup → Undo/redo setup
- CSS variable pattern → All styling

### Reuse Components
- QDialog for help panel (PyQt)
- QMessageBox for notifications
- CSS animations from Phase 1

### Quick Testing Tactics
- Use browser console for quick tests
- Print statements for debugging
- Visual inspection before regression tests

---

## 📋 Daily Checklist

### Each Morning
- [ ] Know what you're implementing today
- [ ] Have specs open (UX-PHASE2-ANALYSIS.md)
- [ ] Understand acceptance criteria
- [ ] Any blockers from yesterday?

### Each Afternoon
- [ ] Feature mostly implemented
- [ ] Quick manual testing done
- [ ] Console clean (no errors)
- [ ] Commit ready (if done)

### Each Evening
- [ ] Code compiles/runs
- [ ] No new errors introduced
- [ ] Tomorrow's work planned
- [ ] Any blockers documented

---

## 🚨 Troubleshooting

### "Console errors appearing"
→ Check specs for edge cases you might have missed

### "Feature doesn't look right"
→ Reference Phase 1 implementations for styling patterns

### "Tests are failing"
→ Make sure you didn't modify Phase 1 code unintentionally

### "Behind schedule"
→ Skip lowest-impact feature (Mobile Preview) and come back

### "Unexpected blocker"
→ Escalate immediately, don't try to solve alone

---

## ✅ Definition of Done

**Per Feature:**
- [ ] Code implemented per specs
- [ ] No console errors
- [ ] Manual testing passed
- [ ] Accessibility verified
- [ ] Code review approved
- [ ] VERIFICATION-CHECKLIST items passing

**For Phase 2:**
- [ ] All 5 features complete
- [ ] All 25 existing tests passing
- [ ] No regressions from Phase 1
- [ ] Ready for user testing/deployment

---

## 📞 Getting Help

### If You Need Clarification
- Reference: UX-PHASE2-ANALYSIS.md (detailed specs with code examples)
- Reference: Phase 1 code (working examples)
- Ask: Project lead

### If You Find a Bug in Specs
- Document it
- Work around it
- Report for later fix
- Continue forward

### If Blocked
- Try for 30 min
- Ask for help
- Don't get stuck
- Move to next task

---

## 🎯 Success Indicators

**Day 2:** Theme changes looking good, no contrast issues  
**Day 4:** Help system functional, all components documented  
**Day 5:** Save feedback working, users know when saved  
**Day 7:** Undo/redo buttons state correct  
**Day 10:** Mobile preview complete, all 5 features ready  

---

**Start Date:** [Your choice]  
**Expected Completion:** 10 business days later  
**Ready to begin?** 🚀
