/**
 * Root App Component
 * Sets up providers, initializes bridge, and renders main editor
 */

import React, { useEffect, useState } from 'react';
import { bridge } from '@services/pythonBridge';
import { useAnkiStore, useUiStore } from '@stores';
import { createLogger } from '@utils/logger';
import Editor from '@components/Editor';
import LanguageSwitcher from '@components/LanguageSwitcher';
import ErrorBoundary from '@components/ErrorBoundary';
import type { AnkiField, AnkiBehavior } from '@/types';
import { appStyle, containerStyle, mainContentStyle } from './App.styles';

const logger = createLogger('App');

function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string[]>([]);
  const debugLogRef = React.useRef<HTMLDivElement>(null);
  
  const initializeAnkiStore = useAnkiStore((state) => state.initialize);
  const setTheme = useUiStore((state) => state.setTheme);

  // Auto-scroll debug log to bottom
  useEffect(() => {
    if (debugLogRef.current) {
      debugLogRef.current.scrollTop = debugLogRef.current.scrollHeight;
    }
  }, [debugInfo]);

  const addDebugInfo = (msg: string) => {
    setDebugInfo(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
    console.log(msg);
  };

  /**
   * Initialize bridge and load Anki data
   */
  useEffect(() => {
    async function init() {
      try {
        addDebugInfo('Step 1: Starting initialization...');
        logger.info('Initializing application...');

        // Initialize Python bridge
        addDebugInfo('Step 2: Initializing Python bridge...');
        console.log('Step 2: About to call bridge.initialize()');
        console.time('bridge.initialize');
        try {
          await bridge.initialize();
          console.timeEnd('bridge.initialize');
        } catch (initError) {
          console.timeEnd('bridge.initialize');
          console.error('Bridge initialization error:', initError);
          addDebugInfo(`Step 2 FAILED: Bridge init error: ${initError instanceof Error ? initError.message : String(initError)}`);
          throw initError;
        }
        addDebugInfo('Step 3: Python bridge initialized successfully');
        logger.info('Python bridge initialized');
        console.log('Step 3: Bridge initialized successfully');

        // Load Anki fields and behaviors
        addDebugInfo('Step 4: Loading Anki fields and behaviors...');
        let fields: AnkiField[] = [];
        let behaviors: AnkiBehavior[] = [];
        
        try {
          addDebugInfo('Step 4a: Calling bridge.getAnkiFields()...');
          fields = await Promise.race([
            bridge.getAnkiFields(),
            new Promise((_, reject) => 
              setTimeout(() => reject(new Error('getAnkiFields timeout after 10s')), 10000)
            )
          ]);
          addDebugInfo(`Step 4b: Loaded ${fields.length} fields successfully`);
        } catch (error) {
          const msg = error instanceof Error ? error.message : String(error);
          addDebugInfo(`Step 4b ERROR (fields): ${msg}`);
          throw error;
        }
        
        try {
          addDebugInfo('Step 4c: Calling bridge.getAnkiBehaviors()...');
          console.log('About to call bridge.getAnkiBehaviors()');
          
          // Check if bridge method exists
          if (!bridge || typeof bridge.getAnkiBehaviors !== 'function') {
            throw new Error('bridge.getAnkiBehaviors is not a function');
          }
          
          const behaviorPromise = bridge.getAnkiBehaviors();
          console.log('Promise created:', behaviorPromise);
          
          if (!behaviorPromise) {
            throw new Error('bridge.getAnkiBehaviors returned null/undefined');
          }
          
          behaviors = await Promise.race([
            behaviorPromise,
            new Promise((_, reject) => 
              setTimeout(() => {
                console.log('Timeout firing for getAnkiBehaviors');
                reject(new Error('getAnkiBehaviors timeout after 10s'));
              }, 10000)
            )
          ]);
          
          if (!Array.isArray(behaviors)) {
            console.warn('behaviors is not an array:', behaviors);
            behaviors = behaviors ? Object.values(behaviors) : [];
          }
          
          addDebugInfo(`Step 4d: Loaded ${behaviors.length} behaviors successfully`);
        } catch (error) {
          const msg = error instanceof Error ? error.message : String(error);
          addDebugInfo(`Step 4d ERROR (behaviors): ${msg}`);
          console.error('Behaviors error:', error);
          console.error('Error type:', typeof error, 'constructor:', error?.constructor?.name);
          // Don't throw - use empty array as fallback
          behaviors = [];
          addDebugInfo(`Step 4d FALLBACK: Using empty behaviors array`);
        }

        // Initialize Anki store
        addDebugInfo('Step 5: Initializing Anki store...');
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
        addDebugInfo('Step 6: Setting up event listeners...');
        bridge.onFieldsUpdated((fields) => {
          logger.info('Fields updated from Python');
          useAnkiStore.setState({ fields });
        });

        // Apply theme
        addDebugInfo('Step 7: Applying theme...');
        setTheme('dark');

        addDebugInfo('Step 8: Initialization complete! Rendering editor...');
        setIsInitialized(true);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        const stack = error instanceof Error ? error.stack : '';
        logger.error('Initialization failed', { error: message, stack });
        addDebugInfo(`FATAL ERROR: ${message}`);
        addDebugInfo(`Stack: ${stack}`);
        console.error('Full error object:', error);
        // Ensure error is preserved in state
        const errorMessage = `${message}\n\n${stack}`;
        setInitError(errorMessage);
        console.error('Init error set to:', errorMessage);
      }
    }

    init();
  }, [initializeAnkiStore, setTheme]);

  if (initError) {
    return (
      <div className="error-screen">
        <h1>⚠️ Initialization Error</h1>
        <div className="error-message">
          <pre>{initError}</pre>
        </div>
        <details className="debug-details" open>
          <summary>Debug Information (click to hide)</summary>
          <div className="debug-log" ref={debugLogRef}>
            {debugInfo.map((info, i) => (
              <div key={i}>{info}</div>
            ))}
          </div>
        </details>
        <p className="hint">
          Check the browser console (F12) for more details. If running in Anki,
          make sure the Python bridge is properly configured.
        </p>
      </div>
    );
  }

  if (!isInitialized) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Initializing Anki Template Designer...</p>
        <details className="debug-details" style={{ marginTop: '20px' }} open>
          <summary>Initialization Progress (click to hide)</summary>
          <div className="debug-log" ref={debugLogRef}>
            {debugInfo.length === 0 ? (
              <div>Waiting for initialization to start...</div>
            ) : (
              debugInfo.map((info, i) => (
                <div key={i}>{info}</div>
              ))
            )}
          </div>
        </details>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="app-container">
        <header className="app-header">
          <h1>Anki Template Designer</h1>
          <LanguageSwitcher />
        </header>
        <main className="app-main">
          <Editor />
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
