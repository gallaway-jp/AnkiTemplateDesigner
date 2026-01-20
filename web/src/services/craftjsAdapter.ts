/**
 * Craft.js Adapter Utilities
 * Helper functions for integrating Craft.js with Zustand stores
 */

import { Template, CraftComponent } from '@/types';

/**
 * Convert GrapeJS data format to Craft.js format
 * This maintains compatibility with existing template data
 */
export function convertGrapeJSToXraftJS(grapeJsData: any): any {
  // For now, keep Craft.js data similar to GrapeJS
  // In production, you might need more sophisticated conversion
  return {
    ROOT: {
      type: 'Container',
      props: {
        width: '100%',
        height: '100%',
      },
      children: grapeJsData?.components || [],
    },
  };
}

/**
 * Convert Craft.js serialized data to HTML
 */
export function craftDataToHtml(craftData: any): string {
  // This would use Craft.js serialization
  // For now, a placeholder
  return '<div>Converted from Craft.js</div>';
}

/**
 * Flatten Craft.js component tree to get all components
 */
export function flattenCraftComponents(craftData: any): CraftComponent[] {
  const components: CraftComponent[] = [];

  function traverse(nodeId: string, node: any, path: string[] = []) {
    const component: CraftComponent = {
      id: nodeId,
      type: node.type,
      displayName: node.displayName || node.type,
      props: node.props || {},
      parent: path[path.length - 1],
      children: node.children || [],
    };

    components.push(component);

    if (node.children) {
      node.children.forEach((childId: string, index: number) => {
        traverse(childId, craftData[childId], [...path, nodeId]);
      });
    }
  }

  if (craftData?.ROOT) {
    traverse('ROOT', craftData.ROOT);
  }

  return components;
}

/**
 * Get component by ID from Craft.js data
 */
export function getCraftComponent(craftData: any, componentId: string): CraftComponent | null {
  const node = craftData[componentId];
  if (!node) return null;

  return {
    id: componentId,
    type: node.type,
    displayName: node.displayName || node.type,
    props: node.props || {},
    children: node.children || [],
  };
}

/**
 * Update component properties in Craft.js data
 */
export function updateCraftComponent(
  craftData: any,
  componentId: string,
  updates: Partial<CraftComponent>
): any {
  return {
    ...craftData,
    [componentId]: {
      ...craftData[componentId],
      ...updates,
    },
  };
}

/**
 * Validate Craft.js data structure
 */
export function validateCraftData(craftData: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!craftData) {
    errors.push('Craft data is null or undefined');
  } else if (!craftData.ROOT) {
    errors.push('Craft data missing ROOT component');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}
