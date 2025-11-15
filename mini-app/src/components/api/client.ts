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

type PersonalDataDto = {
  success: boolean;
  data: {
    fam?: string;
    name?: string;
    patronymic?: string;
    sex?: string;
    birthday?: string;
    zachetka?: string;
    faculty?: string;
    spec?: string;
    profile?: string;
    group?: string;
    course?: string;
    phone?: string;
    photo?: string;
  } | null;
  error: string | null;
};

type UserDto = {
  id: number;
  user_id: number;
  university_id: number;
  first_name: string;
  last_name: string | null;
  username: string | null;
};

type CreateUserPayload = {
  user_id: number;
  university_id: number;
  first_name: string;
  last_name?: string;
  username?: string;
};

type PlatformItem = {
  emoji: string;
  key: string;
  name: string;
  url: string;
};

type ServiceItem = {
  emoji: string;
  key: string;
  name: string;
};

type PlatformsResponse = {
  success: boolean;
  platforms: PlatformItem[] | null;
  error: string | null;
};

type ServicesResponse = {
  success: boolean;
  services: ServiceItem[] | null;
  error: string | null;
};

type TeacherListItem = {
  id: string;
  name: string;
};

type TeachersResponse = {
  success: boolean;
  teachers: TeacherListItem[] | null;
  error: string | null;
};

type TeacherInfoResponse = {
  success: boolean;
  departments: string[] | null;
  photo: string | null;
  error: string | null;
};

type DeanContact = {
  email: string;
  faculty: string;
  phone: string;
};

type DepartmentContact = {
  department: string;
  email: string;
  faculty: string;
  phones: string;
};

type ContactsResponse = {
  success: boolean;
  deans: DeanContact[] | null;
  departments: DepartmentContact[] | null;
  error: string | null;
};

type BuildingMap = {
  name: string;
  latitude: number;
  longitude: number;
  yandex_map_url: string;
  gis2_map_url: string;
  google_map_url: string;
};

type MapsResponse = {
  buildings: BuildingMap[];
};

export type ScheduleItemDto = {
  id: string;
  start: string;
  end: string;
  title: string;
  type: 'lecture' | 'practice' | 'lab';
  room: string;
  note: string;
  audience?: 'full' | 'subgroup1' | 'subgroup2';
  date?: string;
  teacher?: string;
  additional_info?: string | null;
  undergruop?: string | null;
};

export type ScheduleResponse = {
  success: boolean;
  schedule: ScheduleItemDto[];
  error: string | null;
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

  async getPersonalData(userId: number): Promise<PersonalDataDto> {
    return request<PersonalDataDto>(`/api/v1/students/${userId}/personal_data`);
  },

  async getUser(userId: number): Promise<UserDto | null> {
    try {
      return await request<UserDto>(`/api/v1/users/${userId}`);
    } catch (error) {
      // Если пользователь не найден (404 или сообщение об ошибке), возвращаем null
      if (error instanceof Error) {
        const message = error.message.toLowerCase();
        if (message.includes('404') || message.includes('не найден') || message.includes('not found')) {
          return null;
        }
      }
      throw error;
    }
  },

  async createUser(payload: CreateUserPayload): Promise<UserDto> {
    return request<UserDto>('/api/v1/users', {
      method: 'POST',
      body: JSON.stringify({
        user_id: payload.user_id,
        university_id: payload.university_id,
        first_name: payload.first_name,
        last_name: payload.last_name || null,
        username: payload.username || null,
      }),
    });
  },

  async ensureUserExists(userId: number, universityId: number): Promise<UserDto> {
    // Проверяем, существует ли пользователь
    let user = await this.getUser(userId);
    
    if (user) {
      return user;
    }

    // Если пользователя нет, пытаемся создать его с данными из MAX WebApp
    let firstName = 'Пользователь';
    let lastName: string | null = null;
    let username: string | null = null;

    if (typeof window !== 'undefined' && window.WebApp?.initDataUnsafe?.user) {
      const userData = window.WebApp.initDataUnsafe.user;
      firstName = userData.first_name || firstName;
      lastName = userData.last_name || null;
      username = userData.username || null;
    }

    // Создаём пользователя
    try {
      user = await this.createUser({
        user_id: userId,
        university_id: universityId,
        first_name: firstName,
        last_name: lastName || undefined,
        username: username || undefined,
      });
      return user;
    } catch (error) {
      // Если пользователь уже существует (возможно, создался параллельно), получаем его
      if (error instanceof Error) {
        const message = error.message.toLowerCase();
        if (message.includes('уже существует') || message.includes('already exists') || message.includes('400')) {
          user = await this.getUser(userId);
          if (user) {
            return user;
          }
        }
      }
      throw error;
    }
  },

  async getPlatforms(userId: number): Promise<PlatformsResponse> {
    return request<PlatformsResponse>(`/api/v1/students/${userId}/platforms`);
  },

  async getServices(userId: number): Promise<ServicesResponse> {
    return request<ServicesResponse>(`/api/v1/students/${userId}/services`);
  },

  async getTeachers(userId: number): Promise<TeachersResponse> {
    return request<TeachersResponse>(`/api/v1/students/${userId}/teachers`);
  },

  async getTeacherInfo(userId: number, teacherId: string): Promise<TeacherInfoResponse> {
    return request<TeacherInfoResponse>(`/api/v1/students/${userId}/teacher/${teacherId}`);
  },

  async getContacts(userId: number): Promise<ContactsResponse> {
    return request<ContactsResponse>(`/api/v1/students/${userId}/contacts`);
  },

  async getMaps(userId: number): Promise<MapsResponse> {
    return request<MapsResponse>(`/api/v1/students/${userId}/maps`);
  },

  async getSchedule(userId: number, dateRange: string): Promise<ScheduleResponse> {
    const url = `/api/v1/students/${userId}/schedule?date_range=${encodeURIComponent(dateRange)}`;
    return request<ScheduleResponse>(url);
  },
};


