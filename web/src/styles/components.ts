/**
 * Component Styling - All UI Components
 * Responsive, accessible, and themeable component styles
 */

export const componentStyles = {
  // ==================== PANELS ====================
  panel: `
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--spacing-md);
    transition: all var(--transition-base);

    &:hover {
      box-shadow: var(--shadow-lg);
    }

    @media (max-width: 768px) {
      border-radius: var(--radius-md);
      padding: var(--spacing-sm);
    }
  `,

  panelHeader: `
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
    gap: var(--spacing-md);

    h3 {
      margin: 0;
      font-size: 1.125rem;
      font-weight: 600;
      color: var(--color-text);
    }

    @media (max-width: 768px) {
      padding-bottom: var(--spacing-sm);
      margin-bottom: var(--spacing-sm);
      gap: var(--spacing-sm);

      h3 {
        font-size: 1rem;
      }
    }
  `,

  panelContent: `
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    max-height: calc(100vh - 200px);
    overflow-y: auto;

    @media (max-width: 768px) {
      gap: var(--spacing-sm);
      max-height: calc(100vh - 150px);
    }
  `,

  // ==================== BUTTONS ====================
  button: `
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: var(--radius-md);
    border: none;
    cursor: pointer;
    transition: all var(--transition-fast);
    white-space: nowrap;

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }

    &:active {
      transform: translateY(0);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    @media (max-width: 768px) {
      padding: var(--spacing-xs) var(--spacing-sm);
      font-size: 0.8125rem;
    }
  `,

  buttonPrimary: `
    background-color: var(--color-primary);
    color: #ffffff;

    &:hover {
      background-color: var(--color-primaryHover);
    }

    &:active {
      background-color: var(--color-primaryActive);
    }
  `,

  buttonSecondary: `
    background-color: transparent;
    color: var(--color-primary);
    border: 1px solid var(--color-primary);

    &:hover {
      background-color: rgba(59, 130, 246, 0.05);
      border-color: var(--color-primaryHover);
      color: var(--color-primaryHover);
    }
  `,

  buttonSmall: `
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.75rem;
  `,

  buttonLarge: `
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: 1rem;
  `,

  buttonIcon: `
    padding: var(--spacing-sm);
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);

    svg {
      width: 20px;
      height: 20px;
    }

    @media (max-width: 768px) {
      width: 36px;
      height: 36px;
    }
  `,

  // ==================== INPUTS ====================
  input: `
    width: 100%;
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: 0.875rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background-color: var(--color-surface);
    color: var(--color-text);
    transition: all var(--transition-fast);

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    &:disabled {
      background-color: var(--color-backgroundAlt);
      color: var(--color-textDisabled);
      cursor: not-allowed;
    }

    &::placeholder {
      color: var(--color-textSecondary);
    }

    @media (max-width: 768px) {
      padding: var(--spacing-xs) var(--spacing-sm);
      font-size: 0.8125rem;
    }
  `,

  select: `
    width: 100%;
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: 0.875rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background-color: var(--color-surface);
    color: var(--color-text);
    cursor: pointer;
    transition: all var(--transition-fast);

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    option {
      background-color: var(--color-surface);
      color: var(--color-text);
    }

    @media (max-width: 768px) {
      padding: var(--spacing-xs) var(--spacing-sm);
      font-size: 0.8125rem;
    }
  `,

  checkbox: `
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--color-primary);

    @media (max-width: 768px) {
      width: 16px;
      height: 16px;
    }
  `,

  // ==================== CARDS & CONTAINERS ====================
  card: `
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-md);
    transition: all var(--transition-base);

    &:hover {
      border-color: var(--color-borderLight);
      box-shadow: var(--shadow-md);
    }

    @media (max-width: 768px) {
      border-radius: var(--radius-md);
      padding: var(--spacing-sm);
    }
  `,

  cardGrid: `
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: var(--spacing-md);

    @media (max-width: 1024px) {
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    }

    @media (max-width: 768px) {
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: var(--spacing-sm);
    }

    @media (max-width: 480px) {
      grid-template-columns: 1fr;
      gap: var(--spacing-sm);
    }
  `,

  // ==================== LISTS & ITEMS ====================
  list: `
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  `,

  listItem: `
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    background-color: var(--color-surfaceHover);
    border: 1px solid var(--color-border);
    transition: all var(--transition-fast);
    cursor: pointer;

    &:hover {
      background-color: var(--color-borderLight);
      border-color: var(--color-primary);
    }

    &.selected {
      background-color: rgba(59, 130, 246, 0.1);
      border-color: var(--color-primary);
      color: var(--color-primary);
    }

    @media (max-width: 768px) {
      padding: var(--spacing-xs) var(--spacing-sm);
      font-size: 0.875rem;
    }
  `,

  // ==================== MODALS & DIALOGS ====================
  modalOverlay: `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn var(--transition-base);

    @media (max-width: 768px) {
      align-items: flex-end;
    }
  `,

  modal: `
    background-color: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    max-width: 500px;
    width: 90%;
    box-shadow: var(--shadow-xl);
    animation: slideUp var(--transition-base);

    @media (max-width: 768px) {
      border-radius: var(--radius-lg) var(--radius-lg) 0 0;
      padding: var(--spacing-md);
      width: 100%;
      max-width: none;
    }
  `,

  // ==================== DROPDOWNS ====================
  dropdown: `
    position: relative;
    display: inline-block;
  `,

  dropdownMenu: `
    position: absolute;
    top: 100%;
    left: 0;
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    z-index: 100;
    min-width: 150px;
    padding: var(--spacing-xs) 0;
    margin-top: var(--spacing-xs);
    animation: slideUp var(--transition-fast);
  `,

  dropdownItem: `
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--color-text);
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);

    &:hover {
      background-color: var(--color-surfaceHover);
      color: var(--color-primary);
    }

    &:active {
      background-color: rgba(59, 130, 246, 0.1);
    }
  `,

  // ==================== TABS ====================
  tabsContainer: `
    display: flex;
    gap: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
    padding: 0;
    margin-bottom: var(--spacing-md);
    overflow-x: auto;

    @media (max-width: 768px) {
      gap: var(--spacing-sm);
      margin-bottom: var(--spacing-sm);
    }
  `,

  tab: `
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--color-textSecondary);
    cursor: pointer;
    border: none;
    background: transparent;
    border-bottom: 2px solid transparent;
    transition: all var(--transition-fast);
    white-space: nowrap;

    &:hover {
      color: var(--color-text);
    }

    &.active {
      color: var(--color-primary);
      border-bottom-color: var(--color-primary);
    }

    @media (max-width: 768px) {
      padding: var(--spacing-xs) var(--spacing-sm);
      font-size: 0.875rem;
    }
  `,

  // ==================== BADGES & LABELS ====================
  badge: `
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: var(--radius-full);
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--color-primary);
  `,

  badgePrimary: `
    background-color: var(--color-primary);
    color: #ffffff;
  `,

  badgeSuccess: `
    background-color: var(--color-success);
    color: #ffffff;
  `,

  badgeWarning: `
    background-color: var(--color-warning);
    color: #ffffff;
  `,

  badgeError: `
    background-color: var(--color-error);
    color: #ffffff;
  `,

  // ==================== ALERTS ====================
  alert: `
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    border: 1px solid;
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-md);

    @media (max-width: 768px) {
      padding: var(--spacing-sm);
      gap: var(--spacing-sm);
    }
  `,

  alertInfo: `
    background-color: rgba(59, 130, 246, 0.1);
    border-color: var(--color-primary);
    color: var(--color-primary);
  `,

  alertSuccess: `
    background-color: rgba(16, 185, 129, 0.1);
    border-color: var(--color-success);
    color: var(--color-success);
  `,

  alertWarning: `
    background-color: rgba(245, 158, 11, 0.1);
    border-color: var(--color-warning);
    color: var(--color-warning);
  `,

  alertError: `
    background-color: rgba(239, 68, 68, 0.1);
    border-color: var(--color-error);
    color: var(--color-error);
  `,

  // ==================== LOADERS ====================
  spinner: `
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: var(--radius-full);
    animation: spin 1s linear infinite;
  `,

  skeletonLoader: `
    background: linear-gradient(
      90deg,
      var(--color-surfaceHover) 25%,
      var(--color-borderLight) 50%,
      var(--color-surfaceHover) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;

    @keyframes shimmer {
      0% {
        background-position: 200% 0;
      }
      100% {
        background-position: -200% 0;
      }
    }
  `,

  // ==================== UTILITIES ====================
  divider: `
    height: 1px;
    background-color: var(--color-border);
    margin: var(--spacing-md) 0;

    @media (max-width: 768px) {
      margin: var(--spacing-sm) 0;
    }
  `,

  shadow: {
    sm: `box-shadow: var(--shadow-sm);`,
    md: `box-shadow: var(--shadow-md);`,
    lg: `box-shadow: var(--shadow-lg);`,
    xl: `box-shadow: var(--shadow-xl);`,
  },
};

// Export component classes
export const componentClasses = {
  // Responsive grid
  responsiveGrid: `
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-md);

    @media (max-width: 1024px) {
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      gap: var(--spacing-sm);
    }
  `,

  // Flex utilities
  flexCenter: `
    display: flex;
    align-items: center;
    justify-content: center;
  `,

  flexBetween: `
    display: flex;
    align-items: center;
    justify-content: space-between;
  `,

  flexColumn: `
    display: flex;
    flex-direction: column;
  `,

  // Responsive typography
  headingResponsive: `
    @media (max-width: 768px) {
      font-size: 1.5rem;
    }

    @media (max-width: 480px) {
      font-size: 1.25rem;
    }
  `,
};
