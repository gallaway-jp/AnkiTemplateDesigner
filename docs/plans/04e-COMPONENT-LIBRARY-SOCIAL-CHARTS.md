# 04e - Component Library: Social & Charts

> **Purpose**: Define GrapeJS blocks for Social Media and Data Visualization components.
> **Target Agent**: Claude Haiku 4.5 chat agent in VS Code
> **Date**: January 11, 2026

---

## 10. Social Components

### `web/blocks/social.js`

```javascript
/**
 * Social Component Blocks
 */

export function registerSocialBlocks(editor) {
    const bm = editor.BlockManager;
    const category = 'Social';
    
    // User Profile Card
    bm.add('profile-card', {
        label: 'Profile Card',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-profile-card'],
            style: { padding: '24px', background: '#fff', 'border-radius': '12px', 'text-align': 'center', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)' },
            components: [
                { tagName: 'div', content: 'JD', style: { width: '80px', height: '80px', margin: '0 auto 16px', 'border-radius': '50%', background: '#1976d2', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'font-size': '28px', 'font-weight': '600' } },
                { tagName: 'h3', content: 'John Doe', style: { margin: '0 0 4px' } },
                { tagName: 'p', content: '@johndoe', style: { margin: '0 0 12px', color: '#666' } },
                { tagName: 'p', content: 'Software developer passionate about creating great user experiences.', style: { margin: '0 0 16px', color: '#333', 'font-size': '14px' } },
                { tagName: 'button', content: 'Follow', style: { padding: '10px 32px', border: 'none', 'border-radius': '20px', background: '#1976d2', color: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Social Stats
    bm.add('social-stats', {
        label: 'Social Stats',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-social-stats'],
            style: { display: 'flex', 'justify-content': 'space-around', padding: '16px', background: '#f5f5f5', 'border-radius': '8px' },
            components: [
                { tagName: 'div', style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '1.2K', style: { 'font-size': '20px', 'font-weight': '700' } }, { tagName: 'div', content: 'Posts', style: { color: '#666', 'font-size': '14px' } }] },
                { tagName: 'div', style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '45.8K', style: { 'font-size': '20px', 'font-weight': '700' } }, { tagName: 'div', content: 'Followers', style: { color: '#666', 'font-size': '14px' } }] },
                { tagName: 'div', style: { 'text-align': 'center' }, components: [{ tagName: 'div', content: '892', style: { 'font-size': '20px', 'font-weight': '700' } }, { tagName: 'div', content: 'Following', style: { color: '#666', 'font-size': '14px' } }] }
            ]
        }
    });
    
    // Post Card
    bm.add('post-card', {
        label: 'Post Card',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-post'],
            style: { padding: '16px', background: '#fff', 'border-radius': '12px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)' },
            components: [
                { tagName: 'div', style: { display: 'flex', 'align-items': 'center', gap: '12px', 'margin-bottom': '12px' }, components: [
                    { tagName: 'div', content: 'JD', style: { width: '40px', height: '40px', 'border-radius': '50%', background: '#1976d2', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center' } },
                    { tagName: 'div', components: [{ tagName: 'strong', content: 'John Doe' }, { tagName: 'span', content: ' • 2h ago', style: { color: '#666' } }] }
                ]},
                { tagName: 'p', content: 'Just finished building something amazing! 🚀 #coding #webdev', style: { margin: '0 0 12px' } },
                { tagName: 'div', style: { display: 'flex', gap: '16px', 'padding-top': '12px', 'border-top': '1px solid #e0e0e0' }, components: [
                    { tagName: 'button', content: '❤️ 128', style: { border: 'none', background: 'none', cursor: 'pointer' } },
                    { tagName: 'button', content: '💬 24', style: { border: 'none', background: 'none', cursor: 'pointer' } },
                    { tagName: 'button', content: '🔄 8', style: { border: 'none', background: 'none', cursor: 'pointer' } }
                ]}
            ]
        }
    });
    
    // Comment
    bm.add('comment', {
        label: 'Comment',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-comment'],
            style: { display: 'flex', gap: '12px', padding: '12px 0' },
            components: [
                { tagName: 'div', content: 'AB', style: { width: '32px', height: '32px', 'flex-shrink': '0', 'border-radius': '50%', background: '#e91e63', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'font-size': '12px' } },
                { tagName: 'div', components: [
                    { tagName: 'div', components: [{ tagName: 'strong', content: 'Alice Brown' }, { tagName: 'span', content: ' • 1h', style: { color: '#666', 'font-size': '13px' } }] },
                    { tagName: 'p', content: 'This is amazing! Great work!', style: { margin: '4px 0 8px' } },
                    { tagName: 'div', style: { display: 'flex', gap: '16px', 'font-size': '13px', color: '#666' }, components: [
                        { tagName: 'button', content: 'Like', style: { border: 'none', background: 'none', cursor: 'pointer', color: '#666' } },
                        { tagName: 'button', content: 'Reply', style: { border: 'none', background: 'none', cursor: 'pointer', color: '#666' } }
                    ]}
                ]}
            ]
        }
    });
    
    // Comment Input
    bm.add('comment-input', {
        label: 'Comment Input',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-comment-input'],
            style: { display: 'flex', gap: '12px', padding: '12px', background: '#f5f5f5', 'border-radius': '8px' },
            components: [
                { tagName: 'div', content: 'ME', style: { width: '36px', height: '36px', 'flex-shrink': '0', 'border-radius': '50%', background: '#4caf50', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'font-size': '12px' } },
                { tagName: 'input', attributes: { type: 'text', placeholder: 'Write a comment...' }, style: { flex: '1', padding: '8px 12px', border: '1px solid #e0e0e0', 'border-radius': '20px', outline: 'none' } },
                { tagName: 'button', content: '📤', style: { border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } }
            ]
        }
    });
    
    // Share Buttons
    bm.add('share-buttons', {
        label: 'Share Buttons',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-share-buttons'],
            style: { display: 'flex', gap: '8px' },
            components: [
                { tagName: 'button', content: '𝕏', style: { width: '40px', height: '40px', 'border-radius': '50%', border: 'none', background: '#000', color: '#fff', cursor: 'pointer', 'font-size': '16px' } },
                { tagName: 'button', content: 'f', style: { width: '40px', height: '40px', 'border-radius': '50%', border: 'none', background: '#1877f2', color: '#fff', cursor: 'pointer', 'font-size': '18px', 'font-weight': '700' } },
                { tagName: 'button', content: 'in', style: { width: '40px', height: '40px', 'border-radius': '50%', border: 'none', background: '#0a66c2', color: '#fff', cursor: 'pointer', 'font-size': '14px', 'font-weight': '700' } },
                { tagName: 'button', content: '🔗', style: { width: '40px', height: '40px', 'border-radius': '50%', border: '1px solid #e0e0e0', background: '#fff', cursor: 'pointer' } }
            ]
        }
    });
    
    // Reaction Bar
    bm.add('reaction-bar', {
        label: 'Reaction Bar',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-reactions'],
            style: { display: 'flex', gap: '4px', padding: '8px', background: '#fff', 'border-radius': '24px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)' },
            components: [
                { tagName: 'button', content: '👍', style: { width: '36px', height: '36px', border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } },
                { tagName: 'button', content: '❤️', style: { width: '36px', height: '36px', border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } },
                { tagName: 'button', content: '😂', style: { width: '36px', height: '36px', border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } },
                { tagName: 'button', content: '😮', style: { width: '36px', height: '36px', border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } },
                { tagName: 'button', content: '😢', style: { width: '36px', height: '36px', border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } },
                { tagName: 'button', content: '😡', style: { width: '36px', height: '36px', border: 'none', background: 'none', 'font-size': '20px', cursor: 'pointer' } }
            ]
        }
    });
    
    // Follow Button
    bm.add('follow-button', {
        label: 'Follow Button',
        category,
        content: {
            tagName: 'button',
            classes: ['atd-follow-btn'],
            content: '+ Follow',
            style: { padding: '8px 20px', border: '2px solid #1976d2', 'border-radius': '20px', background: '#fff', color: '#1976d2', cursor: 'pointer', 'font-weight': '600' }
        }
    });
    
    // User List Item
    bm.add('user-list-item', {
        label: 'User List Item',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-user-item'],
            style: { display: 'flex', 'align-items': 'center', gap: '12px', padding: '12px' },
            components: [
                { tagName: 'div', content: 'JD', style: { width: '48px', height: '48px', 'border-radius': '50%', background: '#673ab7', color: '#fff', display: 'flex', 'align-items': 'center', 'justify-content': 'center', 'font-weight': '600' } },
                { tagName: 'div', style: { flex: '1' }, components: [{ tagName: 'strong', content: 'Jane Doe', style: { display: 'block' } }, { tagName: 'span', content: '@janedoe', style: { color: '#666', 'font-size': '14px' } }] },
                { tagName: 'button', content: 'Follow', style: { padding: '6px 16px', border: '1px solid #1976d2', 'border-radius': '20px', background: '#fff', color: '#1976d2', cursor: 'pointer' } }
            ]
        }
    });
    
    // Notification Item
    bm.add('notification-item', {
        label: 'Notification Item',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-notification'],
            style: { display: 'flex', gap: '12px', padding: '12px 16px', background: '#e3f2fd', 'border-radius': '8px' },
            components: [
                { tagName: 'div', content: '❤️', style: { 'font-size': '24px' } },
                { tagName: 'div', style: { flex: '1' }, components: [
                    { tagName: 'p', content: '<strong>John</strong> liked your post', style: { margin: '0 0 4px' } },
                    { tagName: 'span', content: '5 minutes ago', style: { color: '#666', 'font-size': '13px' } }
                ]},
                { tagName: 'div', style: { width: '8px', height: '8px', 'border-radius': '50%', background: '#1976d2' } }
            ]
        }
    });
    
    // Activity Feed Item
    bm.add('activity-item', {
        label: 'Activity Item',
        category,
        content: {
            tagName: 'div',
            classes: ['atd-activity'],
            style: { display: 'flex', gap: '12px', padding: '12px 0', 'border-bottom': '1px solid #e0e0e0' },
            components: [
                { tagName: 'div', style: { width: '32px', height: '32px', 'border-radius': '50%', background: '#4caf50', display: 'flex', 'align-items': 'center', 'justify-content': 'center' }, components: [{ tagName: 'span', content: '✓', style: { color: '#fff' } }] },
                { tagName: 'div', style: { flex: '1' }, components: [
                    { tagName: 'p', content: 'Completed task "Design homepage"', style: { margin: '0 0 4px' } },
                    { tagName: 'span', content: 'Today at 3:45 PM', style: { color: '#666', 'font-size': '13px' } }
                ]}
            ]
        }
    });
}
```

---

## 11. Charts & Data Visualization

### `web/blocks/charts.js`

```javascript
/**
 * Charts & Data Visualization Blocks
 * Note: These are visual representations. For interactive charts, 
 * users should integrate Chart.js or similar libraries.
 */

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
