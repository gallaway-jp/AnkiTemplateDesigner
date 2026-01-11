# 04e - Component Library: Charts & Data Visualization

> **Purpose**: Define GrapeJS blocks for Data Visualization and Analytics components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026
> **Updated**: Based on COMPONENT-AUDIT.md - removed all social media components

---

## Social Components (REMOVED)

The following social media components are not applicable to Anki templates:
- Profile Card
- Social Stats
- Post Card
- Comment
- Comment Input
- Share Buttons
- Reaction Bar
- Follow Button
- User List Item
- Notification Item
- Activity Item

**Reason**: Anki templates are for flashcard study, not social networking. No user interactions or social features are needed.

---

## Charts & Data Visualization

### `web/blocks/charts.js`

Charts can be useful for study templates to display:
- Learning progress/statistics
- Performance metrics
- Distribution of knowledge areas
- Study streaks and trends

```javascript
/**
 * Charts & Data Visualization Blocks
 * Note: These are visual representations. For interactive charts, 
 * users should integrate Chart.js or similar libraries.
 */

export function registerSocialBlocks(editor) {
export function registerChartBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Charts & Data';
    
    // Bar Chart
    bm.add('bar-chart', {
        label: 'Bar Chart',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-chart', 'atd-bar-chart'],
            style: { padding: '20px', background: '#fff', 'border-radius': '12px' },
            components: [
                { tagName: 'h4', content: 'Bar Chart', style: { margin: '0 0 16px' } },
                { tagName: 'div', style: { display: 'flex', 'align-items': 'flex-end', gap: '12px', height: '150px' }, components: [
                    { tagName: 'div', style: { flex: '1', height: '60%', background: '#1976d2', 'border-radius': '4px 4px 0 0' } },
                    { tagName: 'div', style: { flex: '1', height: '80%', background: '#1976d2', 'border-radius': '4px 4px 0 0' } },
                    { tagName: 'div', style: { flex: '1', height: '45%', background: '#1976d2', 'border-radius': '4px 4px 0 0' } },
                    { tagName: 'div', style: { flex: '1', height: '90%', background: '#1976d2', 'border-radius': '4px 4px 0 0' } },
                    { tagName: 'div', style: { flex: '1', height: '70%', background: '#1976d2', 'border-radius': '4px 4px 0 0' } }
                ]},
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-around', 'margin-top': '8px', color: '#666', 'font-size': '12px' }, components: [
                    { tagName: 'span', content: 'Mon' }, { tagName: 'span', content: 'Tue' }, { tagName: 'span', content: 'Wed' }, { tagName: 'span', content: 'Thu' }, { tagName: 'span', content: 'Fri' }
                ]}
            ]
        }
    });
    
    // Line Chart (SVG-based)
    bm.add('line-chart', {
        label: 'Line Chart',
        category,
        content: `<div class="atd-chart atd-line-chart" style="padding: 20px; background: #fff; border-radius: 12px;">
            <h4 style="margin: 0 0 16px;">Line Chart</h4>
            <svg viewBox="0 0 200 100" style="width: 100%; height: 120px;">
                <polyline points="0,80 40,60 80,70 120,30 160,40 200,20" fill="none" stroke="#1976d2" stroke-width="2"/>
                <circle cx="0" cy="80" r="4" fill="#1976d2"/>
                <circle cx="40" cy="60" r="4" fill="#1976d2"/>
                <circle cx="80" cy="70" r="4" fill="#1976d2"/>
                <circle cx="120" cy="30" r="4" fill="#1976d2"/>
                <circle cx="160" cy="40" r="4" fill="#1976d2"/>
                <circle cx="200" cy="20" r="4" fill="#1976d2"/>
            </svg>
        </div>`
    });
    
    // Pie Chart (SVG-based)
    bm.add('pie-chart', {
        label: 'Pie Chart',
        category,
        content: `<div class="atd-chart atd-pie-chart" style="padding: 20px; background: #fff; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0 0 16px;">Pie Chart</h4>
            <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#1976d2" stroke-width="20" stroke-dasharray="125.6 251.2" transform="rotate(-90 50 50)"/>
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#42a5f5" stroke-width="20" stroke-dasharray="62.8 251.2" stroke-dashoffset="-125.6" transform="rotate(-90 50 50)"/>
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#90caf9" stroke-width="20" stroke-dasharray="62.8 251.2" stroke-dashoffset="-188.4" transform="rotate(-90 50 50)"/>
            </svg>
            <div style="display: flex; justify-content: center; gap: 16px; margin-top: 12px; font-size: 12px;">
                <span><span style="color: #1976d2;">●</span> 50%</span>
                <span><span style="color: #42a5f5;">●</span> 25%</span>
                <span><span style="color: #90caf9;">●</span> 25%</span>
            </div>
        </div>`
    });
    
    // Donut Chart
    bm.add('donut-chart', {
        label: 'Donut Chart',
        category,
        content: `<div class="atd-chart atd-donut-chart" style="padding: 20px; background: #fff; border-radius: 12px; text-align: center;">
            <h4 style="margin: 0 0 16px;">Donut Chart</h4>
            <div style="position: relative; display: inline-block;">
                <svg viewBox="0 0 100 100" style="width: 120px; height: 120px;">
                    <circle cx="50" cy="50" r="35" fill="transparent" stroke="#e0e0e0" stroke-width="10"/>
                    <circle cx="50" cy="50" r="35" fill="transparent" stroke="#1976d2" stroke-width="10" stroke-dasharray="165 220" transform="rotate(-90 50 50)"/>
                </svg>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 24px; font-weight: 700;">75%</div>
            </div>
        </div>`
    });
    
    // Stat Card
    bm.add('stat-card', {
        label: 'Stat Card',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-stat-card'],
            style: { padding: '20px', background: '#fff', 'border-radius': '12px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'align-items': 'flex-start' }, components: [
                    { tagName: 'div', components: [
                        { tagName: 'p', content: 'Total Revenue', style: { margin: '0 0 4px', color: '#666', 'font-size': '14px' } },
                        { tagName: 'h2', content: '$45,231', style: { margin: '0', 'font-size': '28px' } }
                    ]},
                    { tagName: 'div', content: '📈', style: { 'font-size': '32px' } }
                ]},
                { tagName: 'div', style: { display: 'flex', 'align-items': 'center', gap: '4px', 'margin-top': '12px' }, components: [
                    { tagName: 'span', content: '↑ 12%', style: { color: '#4caf50', 'font-weight': '600' } },
                    { tagName: 'span', content: 'vs last month', style: { color: '#666', 'font-size': '13px' } }
                ]}
            ]
        }
    });
    
    // KPI Display
    bm.add('kpi-display', {
        label: 'KPI Display',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-kpi'],
            style: { display: 'flex', gap: '20px', padding: '20px', background: '#fff', 'border-radius': '12px' },
            components: [
                { tagName: 'div', style: { flex: '1', 'text-align': 'center', padding: '16px', background: '#e3f2fd', 'border-radius': '8px' }, components: [{ tagName: 'div', content: '2,847', style: { 'font-size': '24px', 'font-weight': '700', color: '#1976d2' } }, { tagName: 'div', content: 'Users', style: { color: '#666' } }] },
                { tagName: 'div', style: { flex: '1', 'text-align': 'center', padding: '16px', background: '#e8f5e9', 'border-radius': '8px' }, components: [{ tagName: 'div', content: '94.2%', style: { 'font-size': '24px', 'font-weight': '700', color: '#4caf50' } }, { tagName: 'div', content: 'Uptime', style: { color: '#666' } }] },
                { tagName: 'div', style: { flex: '1', 'text-align': 'center', padding: '16px', background: '#fff3e0', 'border-radius': '8px' }, components: [{ tagName: 'div', content: '1.2s', style: { 'font-size': '24px', 'font-weight': '700', color: '#ff9800' } }, { tagName: 'div', content: 'Avg Load', style: { color: '#666' } }] }
            ]
        }
    });
    
    // Mini Sparkline
    bm.add('sparkline', {
        label: 'Sparkline',
        category,
        content: `<div class="atd-sparkline" style="display: inline-flex; align-items: center; gap: 8px;">
            <svg viewBox="0 0 80 24" style="width: 80px; height: 24px;">
                <polyline points="0,20 10,16 20,18 30,10 40,12 50,6 60,8 70,4 80,2" fill="none" stroke="#4caf50" stroke-width="2"/>
            </svg>
            <span style="color: #4caf50; font-weight: 600;">+23%</span>
        </div>`
    });
    
    // Progress Gauge
    bm.add('progress-gauge', {
        label: 'Progress Gauge',
        category,
        content: `<div class="atd-gauge" style="text-align: center;">
            <svg viewBox="0 0 100 60" style="width: 120px; height: 72px;">
                <path d="M10,50 A40,40 0 0,1 90,50" fill="none" stroke="#e0e0e0" stroke-width="8" stroke-linecap="round"/>
                <path d="M10,50 A40,40 0 0,1 90,50" fill="none" stroke="#1976d2" stroke-width="8" stroke-linecap="round" stroke-dasharray="100 126"/>
            </svg>
            <div style="margin-top: -10px; font-size: 20px; font-weight: 700;">79%</div>
        </div>`
    });
    
    // Comparison Bar
    bm.add('comparison-bar', {
        label: 'Comparison Bar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-comparison'],
            style: { padding: '16px', background: '#fff', 'border-radius': '8px' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '8px' }, components: [{ tagName: 'span', content: 'This Month' }, { tagName: 'span', content: '75%' }] },
                { tagName: 'div', style: { height: '8px', background: '#e0e0e0', 'border-radius': '4px', 'margin-bottom': '16px' }, components: [{ tagName: 'div', style: { width: '75%', height: '100%', background: '#1976d2', 'border-radius': '4px' } }] },
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', 'margin-bottom': '8px' }, components: [{ tagName: 'span', content: 'Last Month' }, { tagName: 'span', content: '60%' }] },
                { tagName: 'div', style: { height: '8px', background: '#e0e0e0', 'border-radius': '4px' }, components: [{ tagName: 'div', style: { width: '60%', height: '100%', background: '#90caf9', 'border-radius': '4px' } }] }
            ]
        }
    });
    
    // Data Table Header
    bm.add('data-table', {
        label: 'Data Table',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-data-table'],
            style: { background: '#fff', 'border-radius': '12px', overflow: 'hidden', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'justify-content': 'space-between', padding: '16px', 'border-bottom': '1px solid #e0e0e0' }, components: [
                    { tagName: 'h4', content: 'Data Table', style: { margin: '0' } },
                    { tagName: 'button', content: 'Export', style: { padding: '6px 12px', border: '1px solid #e0e0e0', 'border-radius': '4px', background: '#fff', cursor: 'pointer' } }
                ]},
                { tagName: 'table', style: { width: '100%', 'border-collapse': 'collapse' }, components: [
                    { tagName: 'thead', style: { background: '#f5f5f5' }, components: [{ tagName: 'tr', components: [
                        { tagName: 'th', content: 'Name', style: { padding: '12px 16px', 'text-align': 'left' } },
                        { tagName: 'th', content: 'Status', style: { padding: '12px 16px', 'text-align': 'left' } },
                        { tagName: 'th', content: 'Value', style: { padding: '12px 16px', 'text-align': 'right' } }
                    ]}]},
                    { tagName: 'tbody', components: [
                        { tagName: 'tr', components: [{ tagName: 'td', content: 'Item 1', style: { padding: '12px 16px' } }, { tagName: 'td', style: { padding: '12px 16px' }, components: [{ tagName: 'span', content: 'Active', style: { padding: '2px 8px', background: '#e8f5e9', color: '#2e7d32', 'border-radius': '4px', 'font-size': '12px' } }] }, { tagName: 'td', content: '$1,234', style: { padding: '12px 16px', 'text-align': 'right' } }] },
                        { tagName: 'tr', components: [{ tagName: 'td', content: 'Item 2', style: { padding: '12px 16px' } }, { tagName: 'td', style: { padding: '12px 16px' }, components: [{ tagName: 'span', content: 'Pending', style: { padding: '2px 8px', background: '#fff3e0', color: '#e65100', 'border-radius': '4px', 'font-size': '12px' } }] }, { tagName: 'td', content: '$567', style: { padding: '12px 16px', 'text-align': 'right' } }] }
                    ]}
                ]}
            ]
        }
    });
    
    // Legend
    bm.add('chart-legend', {
        label: 'Chart Legend',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-legend'],
            style: { display: 'flex', 'flex-wrap': 'wrap', gap: '16px' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'align-items': 'center', gap: '6px' }, components: [{ tagName: 'span', style: { width: '12px', height: '12px', 'border-radius': '2px', background: '#1976d2' } }, { tagName: 'span', content: 'Series A' }] },
                { tagName: 'div', style: { display: 'flex', 'align-items': 'center', gap: '6px' }, components: [{ tagName: 'span', style: { width: '12px', height: '12px', 'border-radius': '2px', background: '#42a5f5' } }, { tagName: 'span', content: 'Series B' }] },
                { tagName: 'div', style: { display: 'flex', 'align-items': 'center', gap: '6px' }, components: [{ tagName: 'span', style: { width: '12px', height: '12px', 'border-radius': '2px', background: '#90caf9' } }, { tagName: 'span', content: 'Series C' }] }
            ]
        }
    });
    
    // Timeline
    bm.add('timeline', {
        label: 'Timeline',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-timeline'],
            components: [
                { tagName: 'div', style: { display: 'flex', gap: '16px', 'padding-bottom': '24px' }, components: [
                    { tagName: 'div', style: { display: 'flex', 'flex-direction': 'column', 'align-items': 'center' }, components: [{ tagName: 'div', style: { width: '12px', height: '12px', 'border-radius': '50%', background: '#1976d2' } }, { tagName: 'div', style: { width: '2px', flex: '1', background: '#e0e0e0' } }] },
                    { tagName: 'div', components: [{ tagName: 'strong', content: 'Event 1', style: { display: 'block' } }, { tagName: 'span', content: 'Description of the first event', style: { color: '#666' } }] }
                ]},
                { tagName: 'div', style: { display: 'flex', gap: '16px', 'padding-bottom': '24px' }, components: [
                    { tagName: 'div', style: { display: 'flex', 'flex-direction': 'column', 'align-items': 'center' }, components: [{ tagName: 'div', style: { width: '12px', height: '12px', 'border-radius': '50%', background: '#42a5f5' } }, { tagName: 'div', style: { width: '2px', flex: '1', background: '#e0e0e0' } }] },
                    { tagName: 'div', components: [{ tagName: 'strong', content: 'Event 2', style: { display: 'block' } }, { tagName: 'span', content: 'Description of the second event', style: { color: '#666' } }] }
                ]},
                { tagName: 'div', style: { display: 'flex', gap: '16px' }, components: [
                    { tagName: 'div', style: { width: '12px', height: '12px', 'border-radius': '50%', background: '#90caf9' } },
                    { tagName: 'div', components: [{ tagName: 'strong', content: 'Event 3', style: { display: 'block' } }, { tagName: 'span', content: 'Description of the third event', style: { color: '#666' } }] }
                ]}
            ]
        }
    });
}
```

---

## Next Document

See [04f-COMPONENT-LIBRARY-ACCESSIBILITY-SYSTEM.md](04f-COMPONENT-LIBRARY-ACCESSIBILITY-SYSTEM.md) for Accessibility, System, Motion, and Advanced components.
