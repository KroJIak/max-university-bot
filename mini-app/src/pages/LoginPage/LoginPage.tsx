import { useEffect, useMemo, useState } from 'react';

import { apiClient } from '@components/api/client';
import styles from './LoginPage.module.scss';

type UniversityOption = {
  id: string;
  title: string;
};

declare global {
  interface Window {
    WebApp?: {
      initDataUnsafe?: {
        user?: {
          id?: number;
          first_name?: string;
          last_name?: string;
          username?: string;
          language_code?: string;
          photo_url?: string;
        };
      };
      ready?: () => void;
    };
  }
}

const MAX_SUGGESTIONS = 3;
// Определяем, что приложение запущено через MAX (проверяем наличие WebApp объекта)
const isEmbedded = typeof window !== 'undefined' && !!window.WebApp;

type LoginPageProps = {
  onLogin: (payload: { universityId: number; email: string; userId: number; universityName?: string }) => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [universities, setUniversities] = useState<UniversityOption[]>([]);
  const [universitiesError, setUniversitiesError] = useState<string | null>(null);
  const [isUniversitiesLoading, setIsUniversitiesLoading] = useState(false);

  const [selectedUniversity, setSelectedUniversity] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [maxUserId, setMaxUserId] = useState<string>('123456789');

  // Получаем user ID из MAX WebApp
  useEffect(() => {
    const checkWebApp = () => {
      if (typeof window !== 'undefined' && window.WebApp) {
        const userId = window.WebApp.initDataUnsafe?.user?.id;
        if (userId) {
          console.log('[LoginPage] Got user ID from MAX WebApp:', userId);
          setMaxUserId(String(userId));
          return;
        }
        console.log('[LoginPage] WebApp available but user ID not found yet');
      }
      console.log('[LoginPage] WebApp not available, using dev user ID');
      setMaxUserId('123456789');
    };

    // Проверяем сразу
    checkWebApp();

    // Также проверяем после небольшой задержки на случай, если WebApp загружается асинхронно
    const timeoutId = setTimeout(checkWebApp, 100);

    // Подписываемся на событие готовности WebApp, если доступно
    if (typeof window !== 'undefined' && window.WebApp?.ready) {
      try {
        window.WebApp.ready();
      } catch (e) {
        console.warn('[LoginPage] Failed to call WebApp.ready()', e);
      }
    }

    return () => {
      clearTimeout(timeoutId);
    };
  }, []);

  const maxIdValue = maxUserId;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  const selectedOption = useMemo(() => {
    return universities.find((option) => option.id === selectedUniversity) ?? null;
  }, [universities, selectedUniversity]);

  const filteredOptions = useMemo(() => {
    const value = searchValue.trim().toLowerCase();
    if (!value) {
      return universities;
    }
    return universities.filter((option) => option.title.toLowerCase().includes(value));
  }, [searchValue, universities]);

  const isFormReady = Boolean(selectedUniversity && email.trim() && password.trim());

  useEffect(() => {
    let isMounted = true;
    async function loadUniversities() {
      try {
        setIsUniversitiesLoading(true);
        setUniversitiesError(null);
        const data = await apiClient.getUniversities();
        if (!isMounted) {
          return;
        }

        const mapped = data.map((item) => ({
          id: String(item.id),
          title: item.name,
        }));

        setUniversities(mapped);
        setSelectedUniversity(null);
        setSearchValue('');
        setShowSuggestions(false);
      } catch (error) {
        if (isMounted) {
          const message = error instanceof Error ? error.message : 'Не удалось получить список университетов.';
          setUniversitiesError(message);
        }
      } finally {
        if (isMounted) {
          setIsUniversitiesLoading(false);
        }
      }
    }

    loadUniversities();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedUniversity || !isFormReady) {
      return;
    }

                const userId = Number(maxIdValue || window.WebApp?.initDataUnsafe?.user?.id || 123456789);

    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    // Сначала убеждаемся, что пользователь существует в системе
    apiClient
      .ensureUserExists(userId, Number(selectedUniversity))
      .then(() => {
        // Затем выполняем логин студента
        return apiClient.loginStudent({
          userId,
          universityId: Number(selectedUniversity),
          student_email: email.trim(),
          password,
        });
      })
      .then(() => {
        setSubmitSuccess('Вход выполнен успешно');
        onLogin({
          universityId: Number(selectedUniversity),
          email: email.trim(),
          userId,
          universityName: selectedOption?.title,
        });
      })
      .catch((error) => {
        setSubmitError(error.message);
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  };

  const handleSelectUniversity = (option: UniversityOption) => {
    setSelectedUniversity(option.id);
    setSearchValue(option.title);
    setShowSuggestions(false);
  };

  const handleUniversityInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchValue(value);
    setShowSuggestions(true);
    if (!value.trim()) {
      setSelectedUniversity(null);
    }
  };

  const handleUniversityInputFocus = () => {
    setShowSuggestions(true);
    if (!searchValue && selectedOption) {
      setSearchValue(selectedOption.title);
    }
  };

  const handleUniversityInputBlur = () => {
    // Delay to allow click on suggestion
    setTimeout(() => {
      setShowSuggestions(false);
      if (selectedOption) {
        setSearchValue(selectedOption.title);
      }
    }, 100);
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.titleBlock}>
          <div className={styles.logo} aria-hidden="true">
            <svg viewBox="0 0 16 16">
              <path d="M16 6.28a1.23 1.23 0 0 0-.62-1.07l-6.74-4a1.27 1.27 0 0 0-1.28 0l-6.75 4a1.25 1.25 0 0 0 0 2.15l1.92 1.12v2.81a1.28 1.28 0 0 0 .62 1.09l4.25 2.45a1.28 1.28 0 0 0 1.24 0l4.25-2.45a1.28 1.28 0 0 0 .62-1.09V8.45l1.24-.73v2.72H16V6.28zm-3.73 5L8 13.74l-4.22-2.45V9.22l3.58 2.13a1.29 1.29 0 0 0 1.28 0l3.62-2.16zM8 10.27l-6.75-4L8 2.26l6.75 4z" />
            </svg>
          </div>
          <h1 className={styles.title}>Личный кабинет</h1>
          <p className={styles.subtitle}>для студентов</p>
        </div>

        <div className={styles.universitySelect}>
          <label className={styles.label} htmlFor="login-university">
            Университет
          </label>
          <div className={styles.universityControl}>
            <input
              id="login-university"
              type="text"
              className={styles.universityInput}
              placeholder="Начните вводить название"
              value={searchValue}
              onChange={handleUniversityInputChange}
              onFocus={handleUniversityInputFocus}
              onBlur={handleUniversityInputBlur}
              autoComplete="off"
            />
            {showSuggestions && filteredOptions.length > 0 ? (
              <ul className={styles.universitySuggestions}>
                {filteredOptions.slice(0, MAX_SUGGESTIONS).map((option) => {
                  const isActive = option.id === selectedUniversity;
                  return (
                    <li key={option.id}>
                      <button
                        type="button"
                        className={
                          isActive
                            ? `${styles.suggestionItem} ${styles.suggestionItemActive}`
                            : styles.suggestionItem
                        }
                        onMouseDown={(event) => event.preventDefault()}
                        onClick={() => handleSelectUniversity(option)}
                      >
                        {option.title}
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : null}
            {isUniversitiesLoading ? <p className={styles.helper}>Загрузка...</p> : null}
            {universitiesError ? <p className={styles.error}>{universitiesError}</p> : null}
          </div>
        </div>

        {selectedOption ? (
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.inputGroup}>
              <label className={styles.label} htmlFor="login-email">
                E-mail
              </label>
              <input
                id="login-email"
                className={styles.input}
                type="email"
                placeholder="student@example.ru"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label} htmlFor="login-password">
                Пароль
              </label>
              <input
                id="login-password"
                className={styles.input}
                type="password"
                placeholder="Введите пароль"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>

            <button className={styles.submit} type="submit" disabled={!isFormReady || isSubmitting}>
              Войти в аккаунт
            </button>
            {submitError ? <p className={styles.error}>{submitError}</p> : null}
            {submitSuccess ? <p className={styles.success}>{submitSuccess}</p> : null}
          </form>
        ) : (
          <p className={styles.footerText}>Выберите университет, чтобы продолжить авторизацию</p>
        )}
      </div>
    </div>
  );
}


