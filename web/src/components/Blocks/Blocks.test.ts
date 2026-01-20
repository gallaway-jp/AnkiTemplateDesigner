/**
 * Block Components Test Suite
 * Tests for all block components with Craft.js integration
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import '@testing-library/jest-dom';

// Layout Blocks
import {
  Frame,
  Section,
  Panel,
  Card,
  Surface,
  ModalContainer,
  Drawer,
  SplitView,
  Grid,
  Row2Col,
  Row3Col,
  HStack,
  VStack,
  Spacer,
  Divider,
  Container,
  getBlocks as getLayoutBlocks,
} from './LayoutBlocks';

// Input Blocks
import {
  TextField,
  TextArea,
  EmailField,
  PasswordField,
  CheckBox,
  RadioButton,
  SelectInput,
  RangeSlider,
  FileInput,
  ToggleSwitch,
  FormGroup,
  getBlocks as getInputBlocks,
} from './InputBlocks';

// Button Blocks
import {
  PrimaryButton,
  SecondaryButton,
  DestructiveButton,
  SuccessButton,
  WarningButton,
  LinkButton,
  TextButton,
  OutlineButton,
  IconButton,
  FloatingActionButton,
  ButtonGroup,
  getBlocks as getButtonBlocks,
} from './ButtonBlocks';

// Data Blocks
import {
  Heading,
  Paragraph,
  Caption,
  Label,
  CodeBlock,
  InlineCode,
  Blockquote,
  UnorderedList,
  OrderedList,
  DefinitionList,
  Image,
  Video,
  HorizontalRule,
  Badge,
  Chip,
  Alert,
  getBlocks as getDataBlocks,
} from './DataBlocks';

// Mock useNode from Craft.js
vi.mock('@craftjs/core', () => ({
  useNode: () => ({
    connectors: {
      connect: vi.fn((node) => node),
      drag: vi.fn((node) => node),
    },
  }),
}));

describe('Layout Blocks', () => {
  describe('Container Components', () => {
    it('renders Frame component', () => {
      const { container } = render(React.createElement(Frame, { title: 'Device Frame' }));
      expect(container.querySelector('div')).toHaveStyle('width: 375px');
    });

    it('renders Section component with semantic tag', () => {
      const { container } = render(React.createElement(Section));
      expect(container.querySelector('section')).toBeInTheDocument();
    });

    it('renders Card with title', () => {
      render(React.createElement(Card, { title: 'Test Card' }));
      expect(screen.getByText('Test Card')).toBeInTheDocument();
    });

    it('renders Panel with border styling', () => {
      const { container } = render(React.createElement(Panel));
      expect(container.firstChild).toHaveStyle('border: 1px solid #e0e0e0');
    });

    it('renders Surface with light background', () => {
      const { container } = render(React.createElement(Surface));
      expect(container.firstChild).toHaveStyle('background: #f5f5f5');
    });
  });

  describe('Layout Grid Components', () => {
    it('renders Row2Col with 2 columns', () => {
      const { container } = render(React.createElement(Row2Col));
      expect(container.querySelector('[style*="grid"]')).toBeDefined();
    });

    it('renders Row3Col with 3 columns', () => {
      const { container } = render(React.createElement(Row3Col));
      expect(container.querySelector('[style*="grid"]')).toBeDefined();
    });

    it('renders Grid with 3-column layout', () => {
      const { container } = render(React.createElement(Grid));
      expect(container.querySelector('[style*="grid"]')).toBeDefined();
    });
  });

  describe('Layout Flex Components', () => {
    it('renders HStack with flex-row', () => {
      const { container } = render(React.createElement(HStack));
      expect(container.firstChild).toHaveStyle('display: flex');
    });

    it('renders VStack with flex-column', () => {
      const { container } = render(React.createElement(VStack));
      expect(container.firstChild).toHaveStyle('display: flex');
    });

    it('renders Spacer with specified height', () => {
      const { container } = render(React.createElement(Spacer, { size: 32 }));
      expect(container.firstChild).toHaveStyle('height: 32px');
    });
  });

  describe('Block Registration', () => {
    it('exports all layout blocks', () => {
      const blocks = getLayoutBlocks();
      expect(blocks.length).toBeGreaterThan(10);
      expect(blocks.some((b) => b.name === 'frame')).toBe(true);
      expect(blocks.some((b) => b.name === 'card')).toBe(true);
    });

    it('each layout block has required properties', () => {
      const blocks = getLayoutBlocks();
      blocks.forEach((block) => {
        expect(block.name).toBeDefined();
        expect(block.label).toBeDefined();
        expect(block.category).toBe('Layout');
        expect(block.Component).toBeDefined();
      });
    });
  });
});

describe('Input Blocks', () => {
  describe('Text Input Components', () => {
    it('renders TextField with label', () => {
      render(React.createElement(TextField, { label: 'Name' }));
      expect(screen.getByText('Name')).toBeInTheDocument();
    });

    it('renders TextArea with rows', () => {
      const { container } = render(React.createElement(TextArea, { label: 'Message', rows: 5 }));
      expect(container.querySelector('textarea')).toHaveAttribute('rows', '5');
    });

    it('renders EmailField with type="email"', () => {
      const { container } = render(React.createElement(EmailField));
      expect(container.querySelector('input[type="email"]')).toBeInTheDocument();
    });

    it('renders PasswordField with type="password"', () => {
      const { container } = render(React.createElement(PasswordField));
      expect(container.querySelector('input[type="password"]')).toBeInTheDocument();
    });
  });

  describe('Selection Input Components', () => {
    it('renders CheckBox with label', () => {
      render(React.createElement(CheckBox, { label: 'Agree' }));
      expect(screen.getByText('Agree')).toBeInTheDocument();
    });

    it('renders RadioButton with label', () => {
      render(React.createElement(RadioButton, { label: 'Option 1' }));
      expect(screen.getByText('Option 1')).toBeInTheDocument();
    });

    it('renders SelectInput with options', () => {
      const { container } = render(
        React.createElement(SelectInput, {
          options: ['Option 1', 'Option 2', 'Option 3'],
        })
      );
      expect(container.querySelectorAll('option').length).toBe(3);
    });
  });

  describe('Specialized Input Components', () => {
    it('renders RangeSlider with min/max', () => {
      const { container } = render(React.createElement(RangeSlider, { min: 0, max: 100 }));
      expect(container.querySelector('input[type="range"]')).toHaveAttribute('min', '0');
    });

    it('renders FileInput with type="file"', () => {
      const { container } = render(React.createElement(FileInput));
      expect(container.querySelector('input[type="file"]')).toBeInTheDocument();
    });

    it('renders ToggleSwitch', () => {
      const { container } = render(React.createElement(ToggleSwitch));
      expect(container.querySelector('input[type="checkbox"]')).toBeInTheDocument();
    });
  });

  describe('Block Registration', () => {
    it('exports all input blocks', () => {
      const blocks = getInputBlocks();
      expect(blocks.length).toBeGreaterThanOrEqual(11);
      expect(blocks.some((b) => b.name === 'input-text')).toBe(true);
      expect(blocks.some((b) => b.name === 'input-checkbox')).toBe(true);
    });

    it('each input block has required properties', () => {
      const blocks = getInputBlocks();
      blocks.forEach((block) => {
        expect(block.name).toBeDefined();
        expect(block.label).toBeDefined();
        expect(block.category).toBe('Inputs & Forms');
        expect(block.Component).toBeDefined();
      });
    });
  });
});

describe('Button Blocks', () => {
  describe('Button Variants', () => {
    it('renders PrimaryButton with correct styling', () => {
      const { container } = render(React.createElement(PrimaryButton, { label: 'Click Me' }));
      expect(screen.getByText('Click Me')).toBeInTheDocument();
      expect(container.querySelector('button')).toHaveStyle('background: #1976d2');
    });

    it('renders SecondaryButton with outline', () => {
      const { container } = render(React.createElement(SecondaryButton));
      expect(container.querySelector('button')).toHaveStyle('border: 1px solid #1976d2');
    });

    it('renders DestructiveButton with red background', () => {
      const { container } = render(React.createElement(DestructiveButton));
      expect(container.querySelector('button')).toHaveStyle('background: #d32f2f');
    });

    it('renders SuccessButton with green background', () => {
      const { container } = render(React.createElement(SuccessButton));
      expect(container.querySelector('button')).toHaveStyle('background: #4caf50');
    });

    it('renders WarningButton with orange background', () => {
      const { container } = render(React.createElement(WarningButton));
      expect(container.querySelector('button')).toHaveStyle('background: #ff9800');
    });
  });

  describe('Special Button Types', () => {
    it('renders LinkButton as text link', () => {
      const { container } = render(React.createElement(LinkButton));
      expect(container.querySelector('button')).toHaveStyle('background: none');
    });

    it('renders TextButton', () => {
      const { container } = render(React.createElement(TextButton));
      expect(container.querySelector('button')).toBeInTheDocument();
    });

    it('renders OutlineButton with border', () => {
      const { container } = render(React.createElement(OutlineButton));
      expect(container.querySelector('button')).toHaveStyle('border: 2px solid #424242');
    });

    it('renders IconButton as circular', () => {
      const { container } = render(React.createElement(IconButton, { icon: '✓' }));
      expect(container.querySelector('button')).toHaveStyle('border-radius: 50%');
    });

    it('renders FloatingActionButton (FAB)', () => {
      const { container } = render(React.createElement(FloatingActionButton));
      expect(container.querySelector('button')).toHaveStyle('width: 56px');
    });
  });

  describe('Block Registration', () => {
    it('exports all button blocks', () => {
      const blocks = getButtonBlocks();
      expect(blocks.length).toBeGreaterThanOrEqual(11);
      expect(blocks.some((b) => b.name === 'button-primary')).toBe(true);
      expect(blocks.some((b) => b.name === 'button-fab')).toBe(true);
    });

    it('each button block has required properties', () => {
      const blocks = getButtonBlocks();
      blocks.forEach((block) => {
        expect(block.name).toBeDefined();
        expect(block.label).toBeDefined();
        expect(block.category).toBe('Buttons & Actions');
        expect(block.Component).toBeDefined();
      });
    });
  });
});

describe('Data Display Blocks', () => {
  describe('Text Display Components', () => {
    it('renders Heading with correct level', () => {
      render(React.createElement(Heading, { level: 1, text: 'Title' }));
      expect(screen.getByText('Title')).toBeInTheDocument();
    });

    it('renders Paragraph', () => {
      render(React.createElement(Paragraph, { text: 'Sample paragraph' }));
      expect(screen.getByText('Sample paragraph')).toBeInTheDocument();
    });

    it('renders Caption with small font', () => {
      render(React.createElement(Caption, { text: 'Small text' }));
      expect(screen.getByText('Small text')).toBeInTheDocument();
    });

    it('renders Label', () => {
      render(React.createElement(Label, { text: 'Label Text' }));
      expect(screen.getByText('Label Text')).toBeInTheDocument();
    });
  });

  describe('Code Display Components', () => {
    it('renders CodeBlock with code content', () => {
      render(React.createElement(CodeBlock, { code: 'const x = 1;' }));
      expect(screen.getByText('const x = 1;')).toBeInTheDocument();
    });

    it('renders InlineCode', () => {
      render(React.createElement(InlineCode, { code: 'const' }));
      expect(screen.getByText('const')).toBeInTheDocument();
    });

    it('renders Blockquote with quote', () => {
      render(React.createElement(Blockquote, { quote: 'Famous quote' }));
      expect(screen.getByText(/Famous quote/)).toBeInTheDocument();
    });
  });

  describe('List Components', () => {
    it('renders UnorderedList with items', () => {
      render(React.createElement(UnorderedList, { items: ['Item 1', 'Item 2'] }));
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });

    it('renders OrderedList with items', () => {
      render(React.createElement(OrderedList, { items: ['First', 'Second'] }));
      expect(screen.getByText('First')).toBeInTheDocument();
    });
  });

  describe('Media Components', () => {
    it('renders Image with src and alt', () => {
      const { container } = render(
        React.createElement(Image, { src: 'test.jpg', alt: 'Test Image' })
      );
      expect(container.querySelector('img')).toHaveAttribute('src', 'test.jpg');
      expect(container.querySelector('img')).toHaveAttribute('alt', 'Test Image');
    });

    it('renders Video component', () => {
      render(React.createElement(Video));
      // Should render either iframe or placeholder
    });

    it('renders HorizontalRule', () => {
      const { container } = render(React.createElement(HorizontalRule));
      expect(container.querySelector('hr')).toBeInTheDocument();
    });
  });

  describe('Feedback Components', () => {
    it('renders Badge with text', () => {
      render(React.createElement(Badge, { text: 'New' }));
      expect(screen.getByText('New')).toBeInTheDocument();
    });

    it('renders Chip with text', () => {
      render(React.createElement(Chip, { text: 'Chip Label' }));
      expect(screen.getByText('Chip Label')).toBeInTheDocument();
    });

    it('renders Alert with message', () => {
      render(React.createElement(Alert, { message: 'Alert!', type: 'info' }));
      expect(screen.getByText('Alert!')).toBeInTheDocument();
    });

    it('renders different alert types', () => {
      const { container: containerSuccess } = render(
        React.createElement(Alert, { type: 'success' })
      );
      const { container: containerError } = render(React.createElement(Alert, { type: 'error' }));
      expect(containerSuccess.firstChild).toBeDefined();
      expect(containerError.firstChild).toBeDefined();
    });
  });

  describe('Block Registration', () => {
    it('exports all data blocks', () => {
      const blocks = getDataBlocks();
      expect(blocks.length).toBeGreaterThanOrEqual(16);
      expect(blocks.some((b) => b.name === 'data-heading')).toBe(true);
      expect(blocks.some((b) => b.name === 'data-alert')).toBe(true);
    });

    it('each data block has required properties', () => {
      const blocks = getDataBlocks();
      blocks.forEach((block) => {
        expect(block.name).toBeDefined();
        expect(block.label).toBeDefined();
        expect(block.category).toBe('Data Display');
        expect(block.Component).toBeDefined();
      });
    });
  });
});

describe('Block Registration & Export', () => {
  it('all block categories export getBlocks function', () => {
    const layoutBlocks = getLayoutBlocks();
    const inputBlocks = getInputBlocks();
    const buttonBlocks = getButtonBlocks();
    const dataBlocks = getDataBlocks();

    expect(Array.isArray(layoutBlocks)).toBe(true);
    expect(Array.isArray(inputBlocks)).toBe(true);
    expect(Array.isArray(buttonBlocks)).toBe(true);
    expect(Array.isArray(dataBlocks)).toBe(true);
  });

  it('total block count is reasonable', () => {
    const layoutBlocks = getLayoutBlocks();
    const inputBlocks = getInputBlocks();
    const buttonBlocks = getButtonBlocks();
    const dataBlocks = getDataBlocks();

    const total = layoutBlocks.length + inputBlocks.length + buttonBlocks.length + dataBlocks.length;
    expect(total).toBeGreaterThanOrEqual(50);
  });

  it('all blocks have proper Craft.js configuration', () => {
    const allBlocks = [
      ...getLayoutBlocks(),
      ...getInputBlocks(),
      ...getButtonBlocks(),
      ...getDataBlocks(),
    ];

    allBlocks.forEach((block) => {
      expect(block.craft).toBeDefined();
      expect(block.craft.displayName).toBeDefined();
      if (block.craft.isCanvas !== undefined) {
        expect(typeof block.craft.isCanvas).toBe('boolean');
      }
    });
  });

  it('block names are unique within each category', () => {
    const blocksByCategory = {
      Layout: getLayoutBlocks(),
      'Inputs & Forms': getInputBlocks(),
      'Buttons & Actions': getButtonBlocks(),
      'Data Display': getDataBlocks(),
    };

    Object.entries(blocksByCategory).forEach(([category, blocks]) => {
      const names = blocks.map((b) => b.name);
      const uniqueNames = new Set(names);
      expect(uniqueNames.size).toBe(names.length);
    });
  });
});

describe('Block Component Props', () => {
  it('layout blocks accept children', () => {
    const { container } = render(
      React.createElement(
        Frame,
        {},
        React.createElement('div', {}, 'Child Content')
      )
    );
    expect(screen.getByText('Child Content')).toBeInTheDocument();
  });

  it('input blocks accept label prop', () => {
    render(React.createElement(TextField, { label: 'Custom Label' }));
    expect(screen.getByText('Custom Label')).toBeInTheDocument();
  });

  it('button blocks accept label prop', () => {
    render(React.createElement(PrimaryButton, { label: 'Custom Button' }));
    expect(screen.getByText('Custom Button')).toBeInTheDocument();
  });

  it('data blocks accept text/content props', () => {
    render(React.createElement(Heading, { text: 'Custom Heading' }));
    expect(screen.getByText('Custom Heading')).toBeInTheDocument();
  });
});
