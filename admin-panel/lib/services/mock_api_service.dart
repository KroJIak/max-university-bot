import 'dart:async';
import '../models/user.dart';
import '../models/module.dart';
import '../models/endpoint.dart';
import '../models/api_settings.dart';

class MockApiService {
  // Имитация задержки сети
  Future<void> _delay() async {
    await Future.delayed(const Duration(milliseconds: 500));
  }

  // MOCK данные
  User? _currentUser;
  ApiSettings _apiSettings = ApiSettings(baseUrl: 'http://0.0.0.0:8001');
  List<Module> _modules = [];

  // Инициализация MOCK данных
  void _initializeMockData() {
    if (_modules.isEmpty) {
      _modules = [
        Module(
          id: 'students',
          name: 'Студенты',
          description: 'Управление студентами',
          icon: 'people',
          enabled: true,
          endpoints: [
            Endpoint(
              id: 'login',
              name: 'Логин студентов',
              path: '/students/login',
              description: 'Выполнить логин на сайте университета, вернуть cookies',
              method: 'POST',
              enabled: true,
            ),
            Endpoint(
              id: 'status',
              name: 'Статус студента',
              path: '/students/{user_id}/status',
              description: 'Получить статус студента',
              method: 'GET',
              enabled: false,
            ),
            Endpoint(
              id: 'get_all',
              name: 'Все студенты',
              path: '/students',
              description: 'Получить всех студентов',
              method: 'GET',
              enabled: false,
            ),
            Endpoint(
              id: 'get_credentials',
              name: 'Учетные данные студента',
              path: '/students/{user_id}',
              description: 'Получить учетные данные студента',
              method: 'GET',
              enabled: false,
            ),
            Endpoint(
              id: 'update_credentials',
              name: 'Обновить учетные данные',
              path: '/students/{user_id}',
              description: 'Обновить учетные данные студента',
              method: 'PUT',
              enabled: false,
            ),
            Endpoint(
              id: 'delete_credentials',
              name: 'Удалить учетные данные',
              path: '/students/{user_id}',
              description: 'Удалить учетные данные студента',
              method: 'DELETE',
              enabled: false,
            ),
            Endpoint(
              id: 'unlink',
              name: 'Отвязать студента',
              path: '/students/{user_id}/unlink',
              description: 'Отвязать студента',
              method: 'DELETE',
              enabled: false,
            ),
            Endpoint(
              id: 'tech',
              name: 'Техническая страница',
              path: '/students/{user_id}/tech',
              description: 'Получить tech страницу университета (требует cookies в запросе)',
              method: 'GET',
              enabled: false,
            ),
          ],
        ),
        Module(
          id: 'university_map',
          name: 'Карта вуза',
          description: 'Управление картой университета',
          icon: 'map',
          enabled: true,
          endpoints: [
            Endpoint(
              id: 'get_map',
              name: 'Получить карту',
              path: '/university/map',
              description: 'Получить карту университета',
              method: 'GET',
              enabled: true,
            ),
          ],
        ),
        Module(
          id: 'schedule',
          name: 'Расписание',
          description: 'Управление расписанием',
          icon: 'calendar_today',
          enabled: true,
          endpoints: [
            Endpoint(
              id: 'get_schedule',
              name: 'Получить расписание',
              path: '/schedule/{user_id}',
              description: 'Получить расписание студента',
              method: 'GET',
              enabled: true,
            ),
          ],
        ),
        Module(
          id: 'teachers',
          name: 'Преподаватели',
          description: 'Управление преподавателями',
          icon: 'school',
          enabled: true,
          endpoints: [
            Endpoint(
              id: 'get_teachers',
              name: 'Список преподавателей',
              path: '/students/teachers',
              description: 'Получить список всех преподавателей',
              method: 'GET',
              enabled: true,
            ),
          ],
        ),
        Module(
          id: 'news',
          name: 'Новости',
          description: 'Управление новостями',
          icon: 'article',
          enabled: true,
          endpoints: [
            Endpoint(
              id: 'get_news',
              name: 'Список новостей',
              path: '/students/news',
              description: 'Получить список новостей университета',
              method: 'GET',
              enabled: true,
            ),
          ],
        ),
      ];
    }
  }

  // Авторизация
  Future<Map<String, dynamic>> login(String username, String password) async {
    await _delay();

    // MOCK проверка логина/пароля
    if (username == 'admin' && password == 'admin') {
      _currentUser = User(
        id: '1',
        username: username,
        email: 'admin@university.ru',
      );
      return {
        'success': true,
        'user': _currentUser!.toJson(),
        'token': 'mock_token_${DateTime.now().millisecondsSinceEpoch}',
      };
    } else {
      return {
        'success': false,
        'error': 'Неверный логин или пароль',
      };
    }
  }

  // Получить текущего пользователя
  Future<User?> getCurrentUser() async {
    await _delay();
    return _currentUser;
  }

  // Выход
  Future<void> logout() async {
    await _delay();
    _currentUser = null;
  }

  // Получить настройки API
  Future<ApiSettings> getApiSettings() async {
    await _delay();
    _initializeMockData();
    return _apiSettings;
  }

  // Обновить настройки API
  Future<Map<String, dynamic>> updateApiSettings(String baseUrl) async {
    await _delay();
    _apiSettings = ApiSettings(
      baseUrl: baseUrl,
      lastUpdated: DateTime.now(),
    );
    return {
      'success': true,
      'message': 'Настройки API успешно обновлены',
      'settings': _apiSettings.toJson(),
    };
  }

  // Получить все модули
  Future<List<Module>> getModules() async {
    await _delay();
    _initializeMockData();
    return _modules;
  }

  // Получить модуль по ID
  Future<Module?> getModule(String moduleId) async {
    await _delay();
    _initializeMockData();
    try {
      return _modules.firstWhere((m) => m.id == moduleId);
    } catch (e) {
      return null;
    }
  }

  // Обновить модуль
  Future<Map<String, dynamic>> updateModule(Module module) async {
    await _delay();
    _initializeMockData();
    final index = _modules.indexWhere((m) => m.id == module.id);
    if (index != -1) {
      _modules[index] = module;
      return {
        'success': true,
        'message': 'Модуль успешно обновлен',
        'module': module.toJson(),
      };
    }
    return {
      'success': false,
      'error': 'Модуль не найден',
    };
  }

  // Обновить endpoint
  Future<Map<String, dynamic>> updateEndpoint(
    String moduleId,
    Endpoint endpoint,
  ) async {
    await _delay();
    _initializeMockData();
    final moduleIndex = _modules.indexWhere((m) => m.id == moduleId);
    if (moduleIndex != -1) {
      final endpointIndex = _modules[moduleIndex]
          .endpoints
          .indexWhere((e) => e.id == endpoint.id);
      if (endpointIndex != -1) {
        final updatedEndpoints = List<Endpoint>.from(_modules[moduleIndex].endpoints);
        updatedEndpoints[endpointIndex] = endpoint;
        _modules[moduleIndex] = _modules[moduleIndex].copyWith(
          endpoints: updatedEndpoints,
        );
        return {
          'success': true,
          'message': 'Endpoint успешно обновлен',
          'endpoint': endpoint.toJson(),
        };
      }
    }
    return {
      'success': false,
      'error': 'Endpoint не найден',
    };
  }

  // Синхронизировать все изменения с главным API
  Future<Map<String, dynamic>> syncAllChanges() async {
    await _delay();
    _initializeMockData();
    // Имитация отправки всех изменений на главный API
    return {
      'success': true,
      'message': 'Все изменения успешно синхронизированы с главным API',
      'modules': _modules.map((m) => m.toJson()).toList(),
      'apiSettings': _apiSettings.toJson(),
    };
  }
}

