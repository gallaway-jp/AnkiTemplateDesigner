/**
 * Root App Component
 * Sets up providers, initializes bridge, and renders main editor
 */

import React, { useEffect, useState } from 'react';
import { bridge } from '@services/pythonBridge';
import { useAnkiStore, useUiStore } from '@stores';
import { createLogger } from '@utils/logger';
import Editor from '@components/Editor';
import './App.css';

const logger = createLogger('App');

function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  
  const initializeAnkiStore = useAnkiStore((state) => state.initialize);
  const setTheme = useUiStore((state) => state.setTheme);

  /**
   * Initialize bridge and load Anki data
   */
  useEffect(() => {
    async function init() {
      try {
        logger.info('Initializing application...');

        // Initialize Python bridge
        await bridge.initialize();
        logger.info('Python bridge initialized');

        // Load Anki fields and behaviors
        const [fields, behaviors] = await Promise.all([
          bridge.getAnkiFields(),
          bridge.getAnkiBehaviors(),
        ]);

        // Initialize Anki store
        initializeAnkiStore(
          {
            ankiVersion: '2.1.45',
            notetypeId: 0,
            notetypeName: 'Default',
            isDroidCompatible: true,
          },
          fields,
          behaviors
        );

        logger.info('Anki data loaded', { fieldCount: fields.length, behaviorCount: behaviors.length });

        // Set up event listeners
        bridge.onFieldsUpdated((fields) => {
          logger.info('Fields updated from Python');
          useAnkiStore.setState({ fields });
        });

        // Apply theme
        setTheme('dark');

        setIsInitialized(true);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        logger.error('Initialization failed', { error: message });
        setInitError(message);
      }
    }

    init();
  }, [initializeAnkiStore, setTheme]);

  if (initError) {
    return (
      <div className="error-screen">
        <h1>Initialization Error</h1>
        <p>{initError}</p>
        <p className="hint">
          Check the browser console for more details. If running outside Anki,
          make sure the mock bridge is being used correctly.
        </p>
      </div>
    );
  }

  if (!isInitialized) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Initializing Anki Template Designer...</p>
      </div>
    );
  }

  return <Editor />;
}

export default App;
