/**
 * Error Boundary Component
 * Catches React errors and displays user-friendly error messages
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-screen">
          <h1>⚠️ Component Error</h1>
          <div className="error-message">
            <pre>{this.state.error?.toString()}</pre>
          </div>
          {this.state.errorInfo && (
            <details className="debug-details">
              <summary>Component Stack Trace</summary>
              <div className="debug-log">
                <pre>{this.state.errorInfo.componentStack}</pre>
              </div>
            </details>
          )}
          {this.state.error?.stack && (
            <details className="debug-details">
              <summary>Error Stack Trace</summary>
              <div className="debug-log">
                <pre>{this.state.error.stack}</pre>
              </div>
            </details>
          )}
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null, errorInfo: null });
              window.location.reload();
            }}
            style={{ marginTop: '20px' }}
          >
            Reload Application
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
