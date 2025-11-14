const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

type RequestOptions = RequestInit & {
  parseResponse?: boolean;
};

async function request<TResponse>(path: string, options: RequestOptions = {}): Promise<TResponse> {
  const { parseResponse = true, headers, ...rest } = options;
  const fullUrl = `${API_BASE_URL}${path}`;
  console.log('[API Client] Making request:', { method: options.method || 'GET', url: fullUrl, path, API_BASE_URL });
  const response = await fetch(fullUrl, {
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    ...rest,
  });

  const contentType = response.headers.get('content-type') ?? '';
  const isJsonResponse = contentType.includes('application/json');
  let payload: unknown = null;

  if (parseResponse && isJsonResponse) {
    const raw = await response.text();
    if (raw) {
      try {
        payload = JSON.parse(raw);
      } catch (error) {
        throw new Error('Не удалось обработать ответ сервера. Попробуйте позже.');
      }
    }
  } else if (parseResponse && !isJsonResponse) {
    payload = await response.text();
  }

  if (!response.ok) {
    if (
      payload &&
      typeof payload === 'object' &&
      payload !== null &&
      'detail' in payload &&
      typeof (payload as Record<string, unknown>).detail === 'string'
    ) {
      const detail = (payload as Record<string, unknown>).detail;
      if (typeof detail === 'string') {
        throw new Error(detail);
      }
    }
    if (
      payload &&
      typeof payload === 'object' &&
      payload !== null &&
      'message' in payload &&
      typeof (payload as Record<string, unknown>).message === 'string'
    ) {
      const message = (payload as Record<string, unknown>).message;
      if (typeof message === 'string') {
        throw new Error(message);
      }
    }
    if (typeof payload === 'string' && payload.trim()) {
      throw new Error(payload);
    }
    throw new Error('Запрос завершился с ошибкой. Попробуйте ещё раз позже.');
  }

  if (!parseResponse || !isJsonResponse) {
    return undefined as TResponse;
  }

  return payload as TResponse;
}

type UniversityDto = {
  id: number;
  name: string;
};

type StudentLoginPayload = {
  userId: number;
  universityId: number;
  student_email: string;
  password: string;
};

type StudentStatusDto = {
  is_linked: boolean;
  student_email: string | null;
  linked_at: string | null;
};

export const apiClient = {
  async getUniversities(): Promise<UniversityDto[]> {
    const data = await request<unknown>('/api/v1/universities?limit=200');
    if (Array.isArray(data)) {
      return data.filter((item): item is UniversityDto => typeof item?.id === 'number' && typeof item?.name === 'string');
    }
    return [];
  },

  async loginStudent({ userId, universityId, student_email, password }: StudentLoginPayload): Promise<void> {
    const url = '/api/v1/students/login';
    const fullUrl = `${API_BASE_URL}${url}`;
    console.log('[API_CLIENT] Login request:', { url, fullUrl, API_BASE_URL, userId, universityId, student_email });
    
    await request(url, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        university_id: universityId,
        student_email,
        password,
      }),
    });
  },

  async getStudentStatus(userId: number): Promise<StudentStatusDto> {
    return request<StudentStatusDto>(`/api/v1/students/${userId}/status`);
  },

  async unlinkStudent(userId: number): Promise<void> {
    await request<{ success: boolean; message: string }>(`/api/v1/students/${userId}/unlink`, {
      method: 'DELETE',
    });
  },
};


