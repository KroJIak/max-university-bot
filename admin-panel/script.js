// Получаем базовый URL для MAX API с fallback на CLOUDPUB_URL
function getMaxApiUrl() {
    // Локальный URL
    const localUrl = window.location.origin.replace(':8080', ':8000') + '/api/v1';
    return localUrl;
}

const API_BASE_URL = getMaxApiUrl();

// Функция для выполнения запросов
// Fallback на CLOUDPUB_URL обрабатывается на стороне MAX API сервера
async function fetchWithFallback(url, options = {}) {
    return await fetch(url, options);
}

// Список функций с их описаниями и endpoints для University API
const FEATURES = [
    {
        id: 'students_login',
        name: 'Логин студентов',
        description: 'Выполнить логин на сайте университета, вернуть cookies',
        defaultEndpoint: '/students/login'
    },
    {
        id: 'students_tech',
        name: 'Список преподавателей',
        description: 'Получить список всех преподавателей (требует cookies в запросе)',
        defaultEndpoint: '/students/teachers'
    },
    {
        id: 'students_personal_data',
        name: 'Данные студента',
        description: 'Получить данные студента с lk.chuvsu.ru (пробует cookies от tt, если не работает - логин)',
        defaultEndpoint: '/students/personal_data'
    },
    {
        id: 'students_teacher_info',
        name: 'Информация о преподавателе',
        description: 'Получить информацию о конкретном преподавателе (кафедры, фото)',
        defaultEndpoint: '/students/teacher_info'
    },
    {
        id: 'students_schedule',
        name: 'Расписание',
        description: 'Получить расписание занятий (текущая или следующая неделя)',
        defaultEndpoint: '/students/schedule'
    },
    {
        id: 'students_contacts',
        name: 'Контакты',
        description: 'Получить контакты деканатов и кафедр',
        defaultEndpoint: '/students/contacts'
    },
    {
        id: 'students_platforms',
        name: 'Веб-платформы',
        description: 'Получить список полезных веб-платформ',
        defaultEndpoint: '/students/platforms'
    }
];

let currentConfig = {
    university_api_base_url: '',
    endpoints: {}
};

// Инициализация
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    renderFeatures();
    setupEventListeners();
});

// Загрузка конфигурации
async function loadConfig() {
    try {
        const response = await fetchWithFallback(`${API_BASE_URL}/config/university`);
        if (response.ok) {
            const data = await response.json();
            currentConfig = {
                university_api_base_url: data.university_api_base_url || '',
                endpoints: data.endpoints || {}
            };
            document.getElementById('university-api-url').value = currentConfig.university_api_base_url;
        } else if (response.status === 404) {
            // Конфигурации еще нет, используем значения по умолчанию
            currentConfig = {
                university_api_base_url: '',
                endpoints: {}
            };
        }
    } catch (error) {
        console.error('Ошибка загрузки конфигурации:', error);
        showStatus('Ошибка загрузки конфигурации', 'error');
    }
}

// Сохранение конфигурации
async function saveConfig() {
    const apiUrl = document.getElementById('university-api-url').value.trim();
    
    if (!apiUrl) {
        showStatus('Укажите Base URL University API', 'error');
        return;
    }

    try {
        const response = await fetchWithFallback(`${API_BASE_URL}/config/university`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                university_api_base_url: apiUrl,
                endpoints: currentConfig.endpoints
            })
        });

        if (response.ok) {
            currentConfig.university_api_base_url = apiUrl;
            showStatus('Конфигурация успешно сохранена', 'success');
        } else {
            const error = await response.json();
            showStatus(`Ошибка сохранения: ${error.detail || 'Неизвестная ошибка'}`, 'error');
        }
    } catch (error) {
        console.error('Ошибка сохранения конфигурации:', error);
        showStatus('Ошибка сохранения конфигурации', 'error');
    }
}

// Рендеринг списка функций
function renderFeatures() {
    const featuresList = document.getElementById('features-list');
    featuresList.innerHTML = '';

    FEATURES.forEach(feature => {
        const isEnabled = currentConfig.endpoints[feature.id] !== undefined;
        const endpoint = currentConfig.endpoints[feature.id] || feature.defaultEndpoint;

        const featureItem = document.createElement('div');
        featureItem.className = 'feature-item';
        featureItem.innerHTML = `
            <div class="feature-header">
                <div class="feature-title">
                    <span>${feature.name}</span>
                </div>
                <div class="switch-container">
                    <span style="font-size: 14px; color: #666;">${isEnabled ? 'Включено' : 'Выключено'}</span>
                    <div class="switch ${isEnabled ? 'active' : ''}" data-feature-id="${feature.id}"></div>
                </div>
            </div>
            <div class="feature-description">${feature.description}</div>
            <input 
                type="text" 
                class="endpoint-input" 
                data-feature-id="${feature.id}"
                value="${endpoint}"
                placeholder="Endpoint для ${feature.name}"
                ${!isEnabled ? 'disabled' : ''}
            />
        `;

        featuresList.appendChild(featureItem);
    });

    // Добавляем обработчики событий для переключателей
    document.querySelectorAll('.switch').forEach(switchEl => {
        switchEl.addEventListener('click', toggleFeature);
    });

    // Добавляем обработчики для полей endpoint
    document.querySelectorAll('.endpoint-input').forEach(input => {
        input.addEventListener('blur', updateEndpoint);
    });
}

// Переключение функции
async function toggleFeature(event) {
    const switchEl = event.currentTarget;
    const featureId = switchEl.getAttribute('data-feature-id');
    const isEnabled = switchEl.classList.contains('active');
    const endpointInput = document.querySelector(`.endpoint-input[data-feature-id="${featureId}"]`);

    if (isEnabled) {
        // Выключаем
        switchEl.classList.remove('active');
        endpointInput.disabled = true;
        delete currentConfig.endpoints[featureId];
    } else {
        // Включаем
        switchEl.classList.add('active');
        endpointInput.disabled = false;
        const feature = FEATURES.find(f => f.id === featureId);
        if (!currentConfig.endpoints[featureId]) {
            currentConfig.endpoints[featureId] = feature.defaultEndpoint;
            endpointInput.value = feature.defaultEndpoint;
        }
    }

    // Обновляем текст статуса
    const switchContainer = switchEl.closest('.switch-container');
    const statusText = switchContainer.querySelector('span');
    statusText.textContent = !isEnabled ? 'Включено' : 'Выключено';

    // Сохраняем конфигурацию
    await saveConfig();
}

// Обновление endpoint
async function updateEndpoint(event) {
    const input = event.currentTarget;
    const featureId = input.getAttribute('data-feature-id');
    const endpoint = input.value.trim();

    if (endpoint) {
        currentConfig.endpoints[featureId] = endpoint;
        await saveConfig();
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    document.getElementById('save-api-url').addEventListener('click', saveConfig);
    
    // Сохранение по Enter
    document.getElementById('university-api-url').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            saveConfig();
        }
    });
}

// Показать статус
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    
    setTimeout(() => {
        statusEl.className = 'status-message';
    }, 5000);
}

