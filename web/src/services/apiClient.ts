/**
 * API Client - Transport-agnostic API abstraction layer
 * Supports HTTP, WebSocket, and custom transports
 */

/**
 * HTTP request/response types
 */
export interface ApiRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  body?: any;
  headers?: Record<string, string>;
  timeout?: number;
  query?: Record<string, string | number | boolean>;
}

export interface ApiResponse<T> {
  status: number;
  data: T;
  headers: Record<string, string>;
}

/**
 * Transport interface
 * Implement this to support different transports
 */
export interface ApiTransport {
  send<T>(request: ApiRequest): Promise<ApiResponse<T>>;
}

/**
 * HTTP transport implementation
 * Uses Fetch API for HTTP requests
 */
export class HttpTransport implements ApiTransport {
  constructor(
    private baseUrl: string,
    private defaultHeaders: Record<string, string> = {}
  ) {}

  async send<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    const url = this.buildUrl(request);

    const fetchInit: RequestInit = {
      method: request.method,
      headers: { ...this.defaultHeaders, ...request.headers },
    };

    if (request.body) {
      fetchInit.body = JSON.stringify(request.body);
    }

    if (request.timeout) {
      fetchInit.signal = AbortSignal.timeout(request.timeout);
    }

    try {
      const response = await fetch(url, fetchInit);
      const contentType = response.headers.get('content-type');
      let data: T;

      if (contentType?.includes('application/json')) {
        data = (await response.json()) as T;
      } else {
        data = (await response.text()) as T;
      }

      return {
        status: response.status,
        data,
        headers: Object.fromEntries(response.headers),
      };
    } catch (error) {
      throw new Error(
        `HTTP request failed: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private buildUrl(request: ApiRequest): string {
    let url = `${this.baseUrl}${request.path}`;

    if (request.query) {
      const params = new URLSearchParams();
      Object.entries(request.query).forEach(([key, value]) => {
        params.append(key, String(value));
      });
      url += `?${params.toString()}`;
    }

    return url;
  }
}

/**
 * WebSocket transport implementation
 * For real-time bidirectional communication
 */
export class WebSocketTransport implements ApiTransport {
  private ws: WebSocket | null = null;
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  private requestId = 0;

  constructor(
    private baseUrl: string,
    private onError?: (error: Error) => void
  ) {}

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.baseUrl);

        this.ws.onopen = () => {
          resolve();
        };

        this.ws.onerror = (event) => {
          const error = new Error('WebSocket connection error');
          this.onError?.(error);
          reject(error);
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            const { id, data, error } = message;

            if (id) {
              const handler = this.messageHandlers.get(id);
              if (handler) {
                handler({ error, data });
                this.messageHandlers.delete(id);
              }
            }
          } catch (e) {
            this.onError?.(e as Error);
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  async send<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket not connected'));
        return;
      }

      const id = String(++this.requestId);

      const timeout = setTimeout(() => {
        this.messageHandlers.delete(id);
        reject(new Error('WebSocket request timeout'));
      }, request.timeout || 30000);

      this.messageHandlers.set(id, (response: any) => {
        clearTimeout(timeout);

        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve({
            status: 200,
            data: response.data,
            headers: {},
          });
        }
      });

      try {
        this.ws!.send(
          JSON.stringify({
            id,
            method: request.method,
            path: request.path,
            body: request.body,
            query: request.query,
          })
        );
      } catch (error) {
        this.messageHandlers.delete(id);
        clearTimeout(timeout);
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandlers.clear();
  }

  isConnected(): boolean {
    return this.ws ? this.ws.readyState === WebSocket.OPEN : false;
  }
}

/**
 * API Client
 * Abstracts transport details, provides high-level API
 */
export class ApiClient {
  constructor(
    private transport: ApiTransport,
    private defaultHeaders: Record<string, string> = {}
  ) {}

  /**
   * GET request
   */
  async get<T>(path: string, headers?: Record<string, string>): Promise<T> {
    const response = await this.transport.send<T>({
      method: 'GET',
      path,
      headers: { ...this.defaultHeaders, ...headers },
    });
    this.validateStatus(response.status);
    return response.data;
  }

  /**
   * POST request
   */
  async post<T>(
    path: string,
    body?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    const response = await this.transport.send<T>({
      method: 'POST',
      path,
      body,
      headers: { ...this.defaultHeaders, ...headers },
    });
    this.validateStatus(response.status);
    return response.data;
  }

  /**
   * PUT request
   */
  async put<T>(
    path: string,
    body?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    const response = await this.transport.send<T>({
      method: 'PUT',
      path,
      body,
      headers: { ...this.defaultHeaders, ...headers },
    });
    this.validateStatus(response.status);
    return response.data;
  }

  /**
   * DELETE request
   */
  async delete<T>(path: string, headers?: Record<string, string>): Promise<T> {
    const response = await this.transport.send<T>({
      method: 'DELETE',
      path,
      headers: { ...this.defaultHeaders, ...headers },
    });
    this.validateStatus(response.status);
    return response.data;
  }

  /**
   * PATCH request
   */
  async patch<T>(
    path: string,
    body?: any,
    headers?: Record<string, string>
  ): Promise<T> {
    const response = await this.transport.send<T>({
      method: 'PATCH',
      path,
      body,
      headers: { ...this.defaultHeaders, ...headers },
    });
    this.validateStatus(response.status);
    return response.data;
  }

  /**
   * Low-level request
   */
  async request<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    return this.transport.send<T>({
      ...request,
      headers: { ...this.defaultHeaders, ...request.headers },
    });
  }

  /**
   * Set default headers
   */
  setDefaultHeaders(headers: Record<string, string>): void {
    Object.assign(this.defaultHeaders, headers);
  }

  /**
   * Get default headers
   */
  getDefaultHeaders(): Record<string, string> {
    return { ...this.defaultHeaders };
  }

  /**
   * Validate HTTP status
   */
  private validateStatus(status: number): void {
    if (status >= 400) {
      throw new Error(`HTTP ${status}`);
    }
  }
}

/**
 * Custom error for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
