const API_BASE_URL =
  typeof window === 'undefined'
    ? process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL
    : process.env.NEXT_PUBLIC_API_BASE_URL;

const TIMEOUT_MS = 30 * 1000;

const parseResponseBody = <T>(text: string): T | null => {
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
};

const request = async <T>(
  endpoint: string,
  options: RequestInit,
): Promise<T> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const res = await fetch(`${API_BASE_URL ?? ''}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
      signal: controller.signal,
    });

    const text = await res.text();
    const data = parseResponseBody<T>(text);

    if (!res.ok) {
      throw new Error('요청 처리 중 오류가 발생했습니다.');
    }

    return data as T;
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('요청 시간이 초과되었습니다.');
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
};

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { method: 'GET', ...options }),
  post: <T>(endpoint: string, body: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
      ...options,
    }),
};
