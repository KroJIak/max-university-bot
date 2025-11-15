import 'dart:convert';
import 'dart:html' as html if (dart.library.html) 'dart:html';
import 'dart:js' as js if (dart.library.html) 'dart:js';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/university.dart';
import '../models/user.dart';
import '../models/university_config.dart';

class ApiService {
  String? _baseUrl;
  String? _fallbackUrl;
  String? _token;
  
  // Получить конфигурацию из window.APP_CONFIG
  Map<String, String>? _getAppConfig() {
    try {
      // ignore: undefined_prefixed_name
      final window = js.context['window'];
      if (window != null) {
        // ignore: undefined_prefixed_name
        final appConfig = window['APP_CONFIG'];
        if (appConfig != null) {
          return {
            'MAX_API_DOMAIN_URL': appConfig['MAX_API_DOMAIN_URL']?.toString() ?? '',
            'MAX_API_HOST': appConfig['MAX_API_HOST']?.toString() ?? '',
            'MAX_API_PORT': appConfig['MAX_API_PORT']?.toString() ?? '',
            'GHOST_API_DOMAIN_URL': appConfig['GHOST_API_DOMAIN_URL']?.toString() ?? '',
            'GHOST_API_HOST': appConfig['GHOST_API_HOST']?.toString() ?? '',
            'GHOST_API_PORT': appConfig['GHOST_API_PORT']?.toString() ?? '',
          };
        }
      }
    } catch (e) {
      // Игнорируем ошибки доступа к JS объектам
    }
    return null;
  }
  
  // Получить Ghost API URL с fallback логикой
  String get ghostApiUrl {
    final config = _getAppConfig();
    String? domainUrl;
    String? host;
    String? port;
    
    if (config != null) {
      domainUrl = config['GHOST_API_DOMAIN_URL']?.trim();
      final rawHost = config['GHOST_API_HOST']?.trim() ?? 'localhost';
      host = (rawHost == '0.0.0.0') ? 'localhost' : rawHost;
      port = config['GHOST_API_PORT']?.trim() ?? '8004';
    } else {
      domainUrl = 'https://max-ghost-api.cloudpub.ru';
      host = 'localhost';
      port = '8004';
    }
    
    return (domainUrl != null && domainUrl.isNotEmpty) 
        ? domainUrl 
        : 'http://$host:$port';
  }
  
  // Получить base URL с fallback логикой
  String get baseUrl {
    if (_baseUrl != null) {
      return _baseUrl!;
    }
    
    // Пытаемся получить из config.js (window.APP_CONFIG)
    final config = _getAppConfig();
    String? domainUrl;
    String? host;
    String? port;
    
    if (config != null) {
      domainUrl = config['MAX_API_DOMAIN_URL']?.trim();
      // Для браузера 0.0.0.0 не работает, используем localhost
      final rawHost = config['MAX_API_HOST']?.trim() ?? 'localhost';
      host = (rawHost == '0.0.0.0') ? 'localhost' : rawHost;
      port = config['MAX_API_PORT']?.trim() ?? '8003';
    } else {
      // Fallback: используем значения по умолчанию
      domainUrl = 'https://max-api.cloudpub.ru';
      host = 'localhost';
      port = '8003';
    }
    
    // Приоритет: сначала domain URL, потом host:port
    _baseUrl = (domainUrl != null && domainUrl.isNotEmpty) 
        ? domainUrl 
        : 'http://$host:$port';
    
    // Сохраняем fallback URL (всегда localhost для браузера)
    _fallbackUrl = 'http://localhost:$port';
    
    return _baseUrl!;
  }
  
  // Получить fallback URL (localhost)
  String get fallbackUrl {
    if (_fallbackUrl != null) {
      return _fallbackUrl!;
    }
    
    final config = _getAppConfig();
    // Для браузера 0.0.0.0 не работает, используем localhost
    final rawHost = config?['MAX_API_HOST']?.trim() ?? 'localhost';
    final host = (rawHost == '0.0.0.0') ? 'localhost' : rawHost;
    final port = config?['MAX_API_PORT']?.trim() ?? '8003';
    _fallbackUrl = 'http://$host:$port';
    return _fallbackUrl!;
  }
  
  // Выполнить запрос с автоматическим fallback
  Future<http.Response> _requestWithFallback(
    Future<http.Response> Function(String url) requestFn,
  ) async {
    final primaryUrl = baseUrl;
    
    try {
      final response = await requestFn(primaryUrl)
          .timeout(const Duration(seconds: 10));
      return response;
    } catch (e) {
      // Если primary URL не работает, пробуем fallback
      final fallback = fallbackUrl;
      if (fallback != primaryUrl) {
        try {
          return await requestFn(fallback)
              .timeout(const Duration(seconds: 10));
        } catch (e2) {
          // Если и fallback не работает, выбрасываем оригинальную ошибку
          throw e;
        }
      }
      throw e;
    }
  }

  // Получить сохраненный токен
  Future<String?> getToken() async {
    if (_token != null) return _token;
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('jwt_token');
    return _token;
  }

  // Сохранить токен
  Future<void> _saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
  }

  // Удалить токен
  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
  }

  // Получить список университетов
  Future<List<University>> getUniversities({int skip = 0, int limit = 100}) async {
    try {
      final response = await _requestWithFallback((url) async {
        return await http.get(
          Uri.parse('$url/api/v1/universities?skip=$skip&limit=$limit'),
          headers: {
            'accept': 'application/json',
          },
        );
      });

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => University.fromJson(json)).toList();
      } else {
        throw Exception('Ошибка загрузки университетов: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Ошибка при получении университетов: $e');
    }
  }

  // Вход в систему
  Future<Map<String, dynamic>> login({
    required String login,
    required String password,
    required int universityId,
  }) async {
    try {
      final response = await _requestWithFallback((url) async {
        return await http.post(
          Uri.parse('$url/api/v1/universities/login'),
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: json.encode({
            'login': login,
            'password': password,
            'university_id': universityId,
          }),
        ).timeout(
          const Duration(seconds: 30),
          onTimeout: () {
            throw Exception('Превышено время ожидания ответа от сервера');
          },
        );
      });

      if (response.statusCode == 200) {
        try {
          final Map<String, dynamic> data = json.decode(response.body);
          
          // Извлекаем токен из ответа
          // Предполагаем, что токен приходит в поле 'access_token' или 'token'
          final String? token = data['access_token'] ?? data['token'];
          
          if (token != null) {
            await _saveToken(token);
          }

          // Создаем объект пользователя из ответа
          final user = User(
            id: data['user_id']?.toString() ?? data['id']?.toString() ?? '0',
            username: login,
            email: data['email'] ?? '$login@university.ru',
          );

          // Сохраняем ID университета
          await saveUniversityId(universityId);

          return {
            'success': true,
            'user': user.toJson(),
            'token': token,
          };
        } catch (e) {
          return {
            'success': false,
            'error': 'Ошибка обработки ответа сервера: $e',
          };
        }
      } else {
        String errorMessage = 'Ошибка входа (код: ${response.statusCode})';
        try {
          if (response.body.isNotEmpty) {
            final errorData = json.decode(response.body);
            errorMessage = errorData['detail'] ?? 
                          errorData['message'] ?? 
                          errorData['error'] ?? 
                          errorMessage;
          }
        } catch (e) {
          // Если не удалось декодировать JSON, используем текст ответа
          if (response.body.isNotEmpty) {
            errorMessage = 'Ошибка сервера: ${response.body.substring(0, response.body.length > 200 ? 200 : response.body.length)}';
          }
        }
        return {
          'success': false,
          'error': errorMessage,
        };
      }
    } on http.ClientException catch (e) {
      // Ошибки клиента (сеть, CORS и т.д.)
      String errorMessage = 'Ошибка подключения к серверу';
      if (e.message.contains('Failed host lookup') || e.message.contains('Failed to fetch')) {
        errorMessage = 'Не удалось подключиться к серверу. Проверьте подключение к интернету и доступность сервера $baseUrl';
      } else if (e.message.contains('CORS')) {
        errorMessage = 'Ошибка CORS. Сервер не разрешает запросы с этого домена';
      } else {
        errorMessage = 'Ошибка сети: ${e.message}';
      }
      return {
        'success': false,
        'error': errorMessage,
      };
    } on FormatException catch (e) {
      return {
        'success': false,
        'error': 'Ошибка формата данных: $e',
      };
    } catch (e) {
      String errorMessage = 'Неизвестная ошибка: $e';
      if (e.toString().contains('Failed to fetch') || e.toString().contains('ClientException')) {
        errorMessage = 'Не удалось подключиться к серверу $baseUrl. Возможные причины:\n'
                      '• Сервер недоступен\n'
                      '• Проблемы с сетью\n'
                      '• Блокировка CORS\n'
                      '• Неверный URL сервера';
      }
      return {
        'success': false,
        'error': errorMessage,
      };
    }
  }

  // Получить текущего пользователя (если API поддерживает)
  Future<User?> getCurrentUser() async {
    final token = await getToken();
    if (token == null) return null;

    try {
      final response = await _requestWithFallback((url) async {
        return await http.get(
          Uri.parse('$url/api/v1/users/me'),
          headers: {
            'accept': 'application/json',
            'Authorization': 'Bearer $token',
          },
        );
      });

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return User.fromJson(data);
      }
    } catch (e) {
      // Игнорируем ошибку, если endpoint не существует
    }
    return null;
  }

  // Создать новый университет
  Future<Map<String, dynamic>> createUniversity(String name) async {
    try {
      final response = await _requestWithFallback((url) async {
        return await http.post(
          Uri.parse('$url/api/v1/universities'),
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: json.encode({
            'name': name,
          }),
        );
      });

      if (response.statusCode == 200 || response.statusCode == 201) {
        final Map<String, dynamic> data = json.decode(response.body);
        final university = University.fromJson(data);
        return {
          'success': true,
          'university': university,
        };
      } else {
        final errorData = json.decode(response.body);
        return {
          'success': false,
          'error': errorData['detail'] ?? errorData['message'] ?? 'Ошибка создания университета',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Ошибка подключения: $e',
      };
    }
  }

  // Получить ID университета
  Future<int?> getUniversityId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('university_id');
  }

  // Сохранить ID университета
  Future<void> saveUniversityId(int universityId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('university_id', universityId);
  }

  // Удалить ID университета
  Future<void> clearUniversityId() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('university_id');
  }

  // Получить конфигурацию университета
  Future<UniversityConfig?> getUniversityConfig(int universityId) async {
    try {
      final token = await getToken();
      final response = await _requestWithFallback((url) async {
        return await http.get(
          Uri.parse('$url/api/v1/config/university/$universityId'),
          headers: {
            'accept': 'application/json',
            if (token != null) 'Authorization': 'Bearer $token',
          },
        );
      });

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return UniversityConfig.fromJson(data);
      } else if (response.statusCode == 404) {
        // Конфигурации еще нет
        return null;
      } else {
        throw Exception('Ошибка загрузки конфигурации: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Ошибка при получении конфигурации: $e');
    }
  }

  // Сохранить конфигурацию университета
  Future<Map<String, dynamic>> saveUniversityConfig(UniversityConfig config) async {
    try {
      final token = await getToken();
      if (token == null) {
        return {
          'success': false,
          'error': 'Требуется авторизация',
        };
      }

      if (config.universityId == null) {
        return {
          'success': false,
          'error': 'Не указан ID университета',
        };
      }

      final response = await _requestWithFallback((url) async {
        return await http.put(
          Uri.parse('$url/api/v1/config/university'),
          headers: {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
          body: json.encode(config.toJson()),
        );
      });

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          'success': true,
          'message': 'Конфигурация успешно сохранена',
        };
      } else {
        final errorData = json.decode(response.body);
        return {
          'success': false,
          'error': errorData['detail'] ?? errorData['message'] ?? 'Ошибка сохранения конфигурации',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Ошибка подключения: $e',
      };
    }
  }

  // Выход из системы
  Future<void> logout() async {
    await clearToken();
    await clearUniversityId();
  }
  
  // Отправить CSV файл на Ghost API
  Future<Map<String, dynamic>> uploadCsvToGhostApi({
    required int universityId,
    required List<int> csvBytes,
    required String filename,
  }) async {
    try {
      final url = ghostApiUrl;
      final uri = Uri.parse('$url/upload');
      
      // Создаем multipart request
      final request = http.MultipartRequest('POST', uri);
      
      // Добавляем university_id как form field
      request.fields['university_id'] = universityId.toString();
      
      // Добавляем CSV файл
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          csvBytes,
          filename: filename,
        ),
      );
      
      // Отправляем запрос
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return {
          'success': true,
          'message': data['message'] ?? 'CSV файл успешно загружен',
          'imported': data['imported'],
          'rows_count': data['rows_count'],
        };
      } else {
        final errorData = json.decode(response.body);
        return {
          'success': false,
          'error': errorData['detail'] ?? errorData['error'] ?? 'Ошибка загрузки CSV файла',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Ошибка подключения к Ghost API: $e',
      };
    }
  }
  
  // Проверить, используется ли endpoint (не пустой и feature включена)
  bool isEndpointUsed(UniversityConfig? config, String featureId) {
    if (config == null) return false;
    final endpoint = config.endpoints[featureId];
    return endpoint != null && endpoint.trim().isNotEmpty;
  }
}

