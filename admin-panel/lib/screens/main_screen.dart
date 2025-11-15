import 'package:flutter/material.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:csv/csv.dart';
import '../services/api_service.dart';
import '../services/mock_api_service.dart';
import '../models/module.dart';
import '../models/university_config.dart';
import 'login_screen.dart';
import 'feature_item_widget.dart';
import 'students_screen.dart';
import 'teachers_screen.dart';
import 'schedule_screen.dart';
import 'map_screen.dart';
import 'news_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  final _apiService = ApiService();
  final _mockApiService = MockApiService();
  List<Module> _modules = [];
  bool _isLoading = true;
  int _selectedIndex = 0;
  
  // Конфигурация университета
  UniversityConfig? _universityConfig;
  UniversityConfig? _savedConfig; // Сохраненная версия для сравнения
  bool _isLoadingConfig = false;
  final _universityApiUrlController = TextEditingController();
  
  // Отслеживание изменений
  bool _hasUnsavedChanges = false;
  bool _hasDataChanges = false; // Изменения в данных (преподаватели, расписание и т.д.)
  
  // Список endpoints из OpenAPI
  List<String> _availableEndpoints = [];
  bool _isLoadingEndpoints = false;
  
  // GlobalKeys для доступа к экранам (используем публичные типы)
  final GlobalKey _teachersScreenKey = GlobalKey();
  final GlobalKey _scheduleScreenKey = GlobalKey();
  final GlobalKey _newsScreenKey = GlobalKey();
  
  // Список функций (features)
  static final List<Feature> _features = [
    // Управление
    Feature(
      id: 'students_login',
      name: 'Логин студентов',
      description: 'Выполняет логин на обоих сайтах университета и сохраняет cookies сессии в БД. Cookies не возвращаются в ответе - они используются только внутри University API для последующих запросов. При успешном логине возвращает только success=true, при ошибке - HTTP 401.',
      defaultEndpoint: '/students/login',
      category: 'management',
    ),
    Feature(
      id: 'students_personal_data',
      name: 'Данные студента',
      description: 'Получает структурированные данные студента с личного кабинета университета (ФИО, группа, курс, фото и т.д.). Использует сохраненные cookies сессии из БД.',
      defaultEndpoint: '/students/personal_data',
      category: 'management',
    ),
    // Сервисы
    Feature(
      id: 'students_teachers',
      name: 'Список преподавателей',
      description: 'Получает список всех преподавателей университета для студента. Использует сохраненные cookies сессии из БД.',
      defaultEndpoint: '/students/teachers',
      category: 'services',
    ),
    Feature(
      id: 'students_schedule',
      name: 'Расписание',
      description: 'Получает расписание занятий студента за указанный период. Использует сохраненные cookies сессии из БД.',
      defaultEndpoint: '/students/schedule',
      category: 'services',
    ),
    Feature(
      id: 'students_contacts',
      name: 'Контакты',
      description: 'Получает контактную информацию деканатов факультетов и кафедр. Использует сохраненные cookies сессии из БД.',
      defaultEndpoint: '/students/contacts',
      category: 'services',
    ),
    Feature(
      id: 'students_platforms',
      name: 'Веб-платформы',
      description: 'Получает список полезных веб-платформ университета для студентов. Возвращает статический список платформ.',
      defaultEndpoint: '/students/platforms',
      category: 'services',
    ),
    Feature(
      id: 'students_maps',
      name: 'Карты корпусов',
      description: 'Получает список всех корпусов университета с их координатами и ссылками на карты (Яндекс, 2ГИС, Google). Не требует аутентификации.',
      defaultEndpoint: '/students/maps',
      category: 'services',
    ),
    Feature(
      id: 'students_news',
      name: 'Новости',
      description: 'Получает список новостей университета. Использует тестовые данные из JSON файла. Не требует аутентификации.',
      defaultEndpoint: '/students/news',
      category: 'services',
    ),
    Feature(
      id: 'students_services',
      name: 'Сервисы',
      description: 'Получает список сервисов университета для студентов (не веб-платформы). Возвращает статический список сервисов с названиями и эмодзи.',
      defaultEndpoint: '/students/services',
      category: 'services',
    ),
    // Дополнительный функционал
    Feature(
      id: 'students_teacher_info',
      name: 'Информация о преподавателе',
      description: 'Получает информацию о конкретном преподавателе (кафедры, фото). Использует сохраненные cookies сессии из БД.',
      defaultEndpoint: '/students/teacher_info',
      category: 'additional',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _loadModules();
    _loadConfig();
    _universityApiUrlController.addListener(_checkForChanges);
  }

  @override
  void dispose() {
    _universityApiUrlController.removeListener(_checkForChanges);
    _universityApiUrlController.dispose();
    super.dispose();
  }
  
  void _checkForChanges() {
    if (_universityConfig == null || _savedConfig == null) {
      setState(() {
        _hasUnsavedChanges = false;
      });
      return;
    }
    
    // Проверяем изменения в Base URL
    final urlChanged = _universityApiUrlController.text.trim() != _savedConfig!.universityApiBaseUrl;
    
    // Проверяем изменения в endpoints
    final endpointsChanged = !_mapsEqual(_universityConfig!.endpoints, _savedConfig!.endpoints);
    
    final hasChanges = urlChanged || endpointsChanged;
    
    if (_hasUnsavedChanges != hasChanges) {
      setState(() {
        _hasUnsavedChanges = hasChanges;
      });
    }
  }
  
  bool _mapsEqual(Map<String, String> map1, Map<String, String> map2) {
    if (map1.length != map2.length) return false;
    for (var key in map1.keys) {
      if (map1[key] != map2[key]) return false;
    }
    return true;
  }

  Future<void> _loadModules() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final modules = await _mockApiService.getModules();
      if (mounted) {
        setState(() {
          _modules = modules;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка загрузки модулей: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _loadConfig() async {
    setState(() {
      _isLoadingConfig = true;
    });

    try {
      final universityId = await _apiService.getUniversityId();
      if (universityId != null) {
        final config = await _apiService.getUniversityConfig(universityId);
        if (mounted) {
          setState(() {
            if (config != null) {
              _universityConfig = config;
              _savedConfig = UniversityConfig(
                universityApiBaseUrl: config.universityApiBaseUrl,
                endpoints: Map<String, String>.from(config.endpoints),
                universityId: config.universityId,
              );
              _universityApiUrlController.text = config.universityApiBaseUrl;
            } else {
              // Создаем пустую конфигурацию
              _universityConfig = UniversityConfig(
                universityApiBaseUrl: '',
                endpoints: {},
                universityId: universityId,
              );
              _savedConfig = UniversityConfig(
                universityApiBaseUrl: '',
                endpoints: {},
                universityId: universityId,
              );
            }
            _hasUnsavedChanges = false;
            _isLoadingConfig = false;
          });
          
          // Загружаем endpoints из OpenAPI, если base URL есть
          if (_universityConfig?.universityApiBaseUrl.isNotEmpty == true) {
            await _loadOpenApiEndpoints(_universityConfig!.universityApiBaseUrl);
          }
        }
      } else {
        if (mounted) {
          setState(() {
            _isLoadingConfig = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingConfig = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка загрузки конфигурации: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _loadOpenApiEndpoints(String baseUrl) async {
    setState(() {
      _isLoadingEndpoints = true;
    });

    try {
      // Добавляем /openapi.json к base URL
      final openApiUrl = baseUrl.endsWith('/') 
          ? '${baseUrl}openapi.json' 
          : '$baseUrl/openapi.json';
      
      final response = await http.get(
        Uri.parse(openApiUrl),
        headers: {'accept': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final Map<String, dynamic> openApiJson = json.decode(response.body);
        final List<String> endpoints = _parseOpenApiEndpoints(openApiJson);
        
        if (mounted) {
          setState(() {
            _availableEndpoints = endpoints;
            _isLoadingEndpoints = false;
          });
        }
      } else {
        throw Exception('Ошибка загрузки OpenAPI: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingEndpoints = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Не удалось загрузить OpenAPI: $e'),
            backgroundColor: Colors.orange,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  List<String> _parseOpenApiEndpoints(Map<String, dynamic> openApiJson) {
    final List<String> endpoints = [];
    
    try {
      final paths = openApiJson['paths'] as Map<String, dynamic>?;
      if (paths != null) {
        paths.forEach((path, methods) {
          if (methods is Map<String, dynamic>) {
            methods.forEach((method, details) {
              // Добавляем путь как endpoint
              if (!endpoints.contains(path)) {
                endpoints.add(path);
              }
            });
          }
        });
      }
      
      // Сортируем endpoints
      endpoints.sort();
    } catch (e) {
      // Если парсинг не удался, возвращаем пустой список
      print('Ошибка парсинга OpenAPI: $e');
    }
    
    return endpoints;
  }

  Future<void> _saveConfig() async {
    if (_universityConfig == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Конфигурация не загружена'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // Загружаем endpoints из OpenAPI перед сохранением
    final baseUrl = _universityApiUrlController.text.trim();
    if (baseUrl.isNotEmpty) {
      await _loadOpenApiEndpoints(baseUrl);
    }

    if (!_hasUnsavedChanges && !_hasDataChanges) {
      // Нет изменений для сохранения
      print('Нет изменений для сохранения. _hasUnsavedChanges: $_hasUnsavedChanges, _hasDataChanges: $_hasDataChanges');
      return;
    }

    setState(() {
      _isLoadingConfig = true;
    });

    final updatedConfig = _universityConfig!.copyWith(
      universityApiBaseUrl: baseUrl,
    );

    try {
      // Если есть изменения данных, отправляем общий CSV на ghost-api ПЕРЕД сохранением конфигурации
      if (_hasDataChanges && _universityConfig?.universityId != null) {
        print('Отправка CSV в Ghost API перед сохранением конфигурации...');
        await _saveAllDataToGhostApi();
      }
      
      // Сохраняем конфигурацию endpoints
      final result = await _apiService.saveUniversityConfig(updatedConfig);
      
      if (mounted) {
        setState(() {
          _isLoadingConfig = false;
        });
        if (result['success'] == true) {
          setState(() {
            _universityConfig = updatedConfig;
            _savedConfig = UniversityConfig(
              universityApiBaseUrl: updatedConfig.universityApiBaseUrl,
              endpoints: Map<String, String>.from(updatedConfig.endpoints),
              universityId: updatedConfig.universityId,
            );
            _hasUnsavedChanges = false;
            _hasDataChanges = false; // Сбрасываем флаг изменений данных
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Конфигурация успешно сохранена'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Ошибка сохранения'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingConfig = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _toggleFeature(Feature feature, bool enabled) {
    if (_universityConfig == null) return;

    final updatedEndpoints = Map<String, String>.from(_universityConfig!.endpoints);
    
    if (enabled) {
      // Включаем - добавляем endpoint, если его еще нет, используем дефолтное значение
      // Если endpoint уже есть (даже пустой), оставляем его как есть
      if (!updatedEndpoints.containsKey(feature.id)) {
        updatedEndpoints[feature.id] = feature.defaultEndpoint;
      }
    } else {
      // Выключаем - удаляем endpoint
      updatedEndpoints.remove(feature.id);
    }

    final updatedConfig = _universityConfig!.copyWith(endpoints: updatedEndpoints);
    
    setState(() {
      _universityConfig = updatedConfig;
      _checkForChanges();
    });
  }

  void _updateEndpoint(Feature feature, String endpoint) {
    if (_universityConfig == null) return;

    final updatedEndpoints = Map<String, String>.from(_universityConfig!.endpoints);
    
    // Если функция включена (есть в endpoints), обновляем или удаляем endpoint
    // Если endpoint пустой, оставляем пустую строку (функция остается включенной)
    if (updatedEndpoints.containsKey(feature.id)) {
      if (endpoint.trim().isEmpty) {
        // Оставляем пустую строку, функция остается включенной
        updatedEndpoints[feature.id] = '';
      } else {
        updatedEndpoints[feature.id] = endpoint;
      }
    } else {
      // Если функция выключена, но пользователь вводит endpoint, включаем функцию
      if (endpoint.trim().isNotEmpty) {
        updatedEndpoints[feature.id] = endpoint;
      }
    }

    final updatedConfig = _universityConfig!.copyWith(endpoints: updatedEndpoints);
    
    // Обновляем состояние и проверяем изменения
    setState(() {
      _universityConfig = updatedConfig;
    });
    
    // Вызываем проверку изменений после обновления состояния
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkForChanges();
    });
  }

  // Обработка ручной настройки (CSV)
  Future<void> _handleManualSetup(Feature feature) async {
    final universityId = await _apiService.getUniversityId();
    if (universityId == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Необходимо выбрать университет'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }
    
    // Проверяем, что endpoint действительно не используется
    final isUsed = _apiService.isEndpointUsed(_universityConfig, feature.id);
    if (isUsed) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Endpoint уже настроен. Отключите его для ручной настройки.'),
            backgroundColor: Colors.orange,
          ),
        );
      }
      return;
    }
    
    // Переключаемся на соответствующую вкладку слева вместо открытия нового экрана
    if (mounted) {
      String? moduleId;
      switch (feature.id) {
        case 'students_teachers':
          moduleId = 'teachers';
          break;
        case 'students_schedule':
          moduleId = 'schedule';
          break;
        case 'students_maps':
          moduleId = 'university_map';
          break;
        case 'students_personal_data':
          // Для данных студента используем модуль students
          moduleId = 'students';
          break;
        case 'students_news':
          moduleId = 'news';
          break;
        case 'students_contacts':
          // TODO: Создать экран для контактов
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Ручная настройка контактов будет доступна позже'),
              backgroundColor: Colors.orange,
            ),
          );
          return;
        default:
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Ручная настройка для "${feature.name}" будет доступна позже'),
              backgroundColor: Colors.orange,
            ),
          );
          return;
      }
      
      // Находим индекс модуля
      final moduleIndex = _modules.indexWhere((module) => module.id == moduleId);
      if (moduleIndex != -1) {
        // Переключаемся на нужную вкладку (индекс + 1, так как 0 - это главная страница)
        setState(() {
          _selectedIndex = moduleIndex + 1;
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Модуль "$moduleId" не найден'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  // Собрать все данные и отправить общий CSV на ghost-api
  Future<void> _saveAllDataToGhostApi() async {
    if (_universityConfig == null || _universityConfig!.universityId == null) {
      return;
    }

    try {
      final List<List<dynamic>> csvData = [];
      
      // Заголовок CSV с указанием типа данных
      csvData.add(['Type', 'Data']);
      
      // Собираем данные преподавателей, если endpoint пустой
      final teachersEndpointEmpty = !_apiService.isEndpointUsed(_universityConfig, 'students_teachers');
      if (teachersEndpointEmpty) {
        try {
          // Проверяем, что экран преподавателей открыт (вкладка выбрана)
          final teachersModuleIndex = _modules.indexWhere((m) => m.id == 'teachers');
          final isTeachersScreenOpen = teachersModuleIndex != -1 && _selectedIndex == teachersModuleIndex + 1;
          
          if (isTeachersScreenOpen) {
            final teachersState = _teachersScreenKey.currentState;
            if (teachersState != null) {
              // Используем динамический вызов метода (приватный тип недоступен из другого файла)
              final dynamic state = teachersState;
              try {
                final teachersData = state.getTeachersDataForCsv() as List<Map<String, dynamic>>?;
                if (teachersData != null && teachersData.isNotEmpty) {
                  print('Найдено ${teachersData.length} преподавателей для отправки в Ghost API');
                  csvData.add(['TEACHERS_HEADER', 'ID', 'Фамилия', 'Имя', 'Отчество', 'Кафедра', 'Должность', 'Телефон', 'Фото URL']);
                  for (var teacher in teachersData) {
                    csvData.add([
                      'TEACHER',
                      teacher['id']?.toString() ?? '',
                      teacher['lastName']?.toString() ?? '',
                      teacher['firstName']?.toString() ?? '',
                      teacher['middleName']?.toString() ?? '',
                      teacher['department']?.toString() ?? '',
                      teacher['position']?.toString() ?? '',
                      teacher['phoneNumber']?.toString() ?? '',
                      teacher['photoUrl']?.toString() ?? '',
                    ]);
                  }
                } else {
                  print('Данные преподавателей пусты');
                }
              } catch (e) {
                // Метод не найден или ошибка вызова
                print('Ошибка вызова getTeachersDataForCsv: $e');
              }
            } else {
              print('TeachersScreen state не найден (GlobalKey не работает)');
            }
          } else {
            print('Экран преподавателей не открыт. Текущий индекс: $_selectedIndex, нужный: ${teachersModuleIndex + 1}');
          }
        } catch (e) {
          // Игнорируем ошибки доступа к данным преподавателей
          print('Ошибка получения данных преподавателей: $e');
        }
      }
      
      // Собираем данные расписания, если endpoint пустой
      final scheduleEndpointEmpty = !_apiService.isEndpointUsed(_universityConfig, 'students_schedule');
      if (scheduleEndpointEmpty) {
        try {
          // Проверяем, что экран расписания открыт (вкладка выбрана)
          final scheduleModuleIndex = _modules.indexWhere((m) => m.id == 'schedule');
          final isScheduleScreenOpen = scheduleModuleIndex != -1 && _selectedIndex == scheduleModuleIndex + 1;
          
          if (isScheduleScreenOpen) {
            final scheduleState = _scheduleScreenKey.currentState;
            if (scheduleState != null) {
              // Используем динамический вызов метода (приватный тип недоступен из другого файла)
              final dynamic state = scheduleState;
              try {
                final scheduleData = state.getScheduleDataForCsv() as List<Map<String, dynamic>>?;
                if (scheduleData != null && scheduleData.isNotEmpty) {
                  print('Найдено ${scheduleData.length} событий расписания для отправки в Ghost API');
                  csvData.add(['SCHEDULE_HEADER', 'Название', 'Дата', 'Время начала', 'Время окончания', 'Описание', 'Место', 'Предмет', 'Группа']);
                  for (var event in scheduleData) {
                    csvData.add([
                      'SCHEDULE_EVENT',
                      event['title']?.toString() ?? '',
                      event['date']?.toString() ?? '',
                      event['startTime']?.toString() ?? '',
                      event['endTime']?.toString() ?? '',
                      event['description']?.toString() ?? '',
                      event['location']?.toString() ?? '',
                      event['subject']?.toString() ?? '',
                      event['groupId']?.toString() ?? '',
                    ]);
                  }
                } else {
                  print('Данные расписания пусты');
                }
              } catch (e) {
                // Метод не найден или ошибка вызова
                print('Ошибка вызова getScheduleDataForCsv: $e');
              }
            } else {
              print('ScheduleScreen state не найден (GlobalKey не работает)');
            }
          } else {
            print('Экран расписания не открыт. Текущий индекс: $_selectedIndex, нужный: ${scheduleModuleIndex + 1}');
          }
        } catch (e) {
          // Игнорируем ошибки доступа к данным расписания
          print('Ошибка получения данных расписания: $e');
        }
      }
      
      // Собираем данные новостей, если endpoint пустой
      final newsEndpointEmpty = !_apiService.isEndpointUsed(_universityConfig, 'students_news');
      if (newsEndpointEmpty) {
        try {
          // Проверяем, что экран новостей открыт (вкладка выбрана)
          final newsModuleIndex = _modules.indexWhere((m) => m.id == 'news');
          final isNewsScreenOpen = newsModuleIndex != -1 && _selectedIndex == newsModuleIndex + 1;
          
          if (isNewsScreenOpen) {
            final newsState = _newsScreenKey.currentState;
            if (newsState != null) {
              // Используем динамический вызов метода (приватный тип недоступен из другого файла)
              final dynamic state = newsState;
              try {
                final newsData = state.getNewsDataForCsv() as List<Map<String, dynamic>>?;
                if (newsData != null && newsData.isNotEmpty) {
                  print('Найдено ${newsData.length} новостей для отправки в Ghost API');
                  csvData.add(['NEWS_HEADER', 'ID', 'Заголовок', 'Содержание', 'Дата', 'Автор', 'Категория', 'URL изображения', 'Ссылка']);
                  for (var news in newsData) {
                    csvData.add([
                      'NEWS',
                      news['id']?.toString() ?? '',
                      news['title']?.toString() ?? '',
                      news['content']?.toString() ?? '',
                      news['date']?.toString() ?? '',
                      news['author']?.toString() ?? '',
                      news['category']?.toString() ?? '',
                      news['image_url']?.toString() ?? '',
                      news['link']?.toString() ?? '',
                    ]);
                  }
                } else {
                  print('Данные новостей пусты');
                }
              } catch (e) {
                // Метод не найден или ошибка вызова
                print('Ошибка вызова getNewsDataForCsv: $e');
              }
            } else {
              print('NewsScreen state не найден (GlobalKey не работает)');
            }
          } else {
            print('Экран новостей не открыт. Текущий индекс: $_selectedIndex, нужный: ${newsModuleIndex + 1}');
          }
        } catch (e) {
          // Игнорируем ошибки доступа к данным новостей
          print('Ошибка получения данных новостей: $e');
        }
      }
      
      // Если нет данных для отправки, выходим
      if (csvData.length <= 1) {
        print('Нет данных для отправки в Ghost API');
        return;
      }
      
      print('Отправка CSV в Ghost API. Количество строк: ${csvData.length}');
      
      // Конвертируем в CSV строку
      final csvString = const ListToCsvConverter().convert(csvData);
      final csvBytes = utf8.encode(csvString);
      
      // Отправляем на ghost-api
      final filename = 'all_data_${DateTime.now().toIso8601String().split('T')[0]}.csv';
      final result = await _apiService.uploadCsvToGhostApi(
        universityId: _universityConfig!.universityId!,
        csvBytes: csvBytes,
        filename: filename,
      );
      
      if (mounted) {
        if (result['success'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Все данные успешно отправлены на Ghost API'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Ошибка отправки данных на Ghost API'),
              backgroundColor: Colors.orange,
              duration: const Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка при отправке данных: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Выход'),
        content: const Text('Вы уверены, что хотите выйти?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Выйти'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _apiService.logout();
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (context) => const LoginScreen()),
          (route) => false,
        );
      }
    }
  }

  Future<void> _syncChanges() async {
    // Синхронизация теперь происходит автоматически при сохранении конфигурации
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Изменения сохраняются автоматически'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  Widget _buildContent() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_selectedIndex == 0) {
      // Главная страница
      if (_isLoadingConfig) {
        return const Center(
          child: CircularProgressIndicator(),
        );
      }

      final isMobile = MediaQuery.of(context).size.width < 600;
      
      return SingleChildScrollView(
        padding: EdgeInsets.all(isMobile ? 16.0 : 24.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.dashboard, size: isMobile ? 24 : 32, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Главная страница',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              fontSize: isMobile ? 20 : null,
                            ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: isMobile ? 16 : 24),
                // Настройки University API
                Card(
                  child: Padding(
                    padding: EdgeInsets.all(isMobile ? 12.0 : 16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.link, color: Colors.blue.shade700, size: isMobile ? 20 : 24),
                            const SizedBox(width: 8),
                            Flexible(
                              child: Text(
                                'Настройки University API',
                                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                      fontWeight: FontWeight.bold,
                                      fontSize: isMobile ? 18 : null,
                                    ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        TextField(
                          controller: _universityApiUrlController,
                          decoration: InputDecoration(
                            labelText: 'Base URL University API',
                            hintText: 'http://university-api:8002',
                            prefixIcon: const Icon(Icons.link),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            suffixIcon: _isLoadingConfig || _isLoadingEndpoints
                                ? const Padding(
                                    padding: EdgeInsets.all(12.0),
                                    child: SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    ),
                                  )
                                : IconButton(
                                    icon: const Icon(Icons.save),
                                    onPressed: _saveConfig,
                                    tooltip: 'Сохранить и загрузить endpoints',
                                  ),
                          ),
                          onSubmitted: (_) => _saveConfig(),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Управление функционалом
                ..._buildFeatureCategories(),
                // Добавляем отступ снизу для плавающей кнопки
                const SizedBox(height: 100),
              ],
            ),
          ),
        ),
      );
    }

    // Проверяем, выбран ли модуль "Студенты", "Преподаватели", "Расписание" или "Карта"
    if (_selectedIndex > 0 && _selectedIndex <= _modules.length) {
      final selectedModule = _modules[_selectedIndex - 1];
      final universityId = _universityConfig?.universityId;
      
      if (selectedModule.id == 'students') {
        return StudentsScreen(key: ValueKey(_universityConfig?.endpoints.toString()));
      }
      if (selectedModule.id == 'teachers') {
        final isEndpointEmpty = !_apiService.isEndpointUsed(_universityConfig, 'students_teachers');
        return TeachersScreen(
          key: _teachersScreenKey,
          universityId: universityId,
          featureId: 'students_teachers',
          onCsvUploaded: () {
            // Callback после загрузки CSV (не используется здесь)
          },
          onDataChanged: isEndpointEmpty ? () {
            // Отслеживаем изменения данных, если endpoint пустой
            setState(() {
              _hasDataChanges = true;
            });
          } : null,
        );
      }
      if (selectedModule.id == 'schedule') {
        final isEndpointEmpty = !_apiService.isEndpointUsed(_universityConfig, 'students_schedule');
        return ScheduleScreen(
          key: _scheduleScreenKey,
          universityId: universityId,
          featureId: 'students_schedule',
          onCsvUploaded: () {
            // Callback после загрузки CSV (не используется здесь)
          },
          onDataChanged: isEndpointEmpty ? () {
            // Отслеживаем изменения данных, если endpoint пустой
            setState(() {
              _hasDataChanges = true;
            });
          } : null,
        );
      }
      if (selectedModule.id == 'university_map') {
        return const MapScreen();
      }
      if (selectedModule.id == 'news') {
        final isEndpointEmpty = !_apiService.isEndpointUsed(_universityConfig, 'students_news');
        return NewsScreen(
          key: _newsScreenKey,
          universityId: universityId,
          featureId: 'students_news',
          onCsvUploaded: () {
            // Callback после загрузки CSV (не используется здесь)
          },
          onDataChanged: isEndpointEmpty ? () {
            // Отслеживаем изменения данных, если endpoint пустой
            setState(() {
              _hasDataChanges = true;
            });
          } : null,
        );
      }
    }

    return const Center(
      child: Text('Выберите модуль из меню'),
    );
  }

  List<Widget> _buildFeatureCategories() {
    final categories = {
      'management': 'Управление',
      'services': 'Сервисы',
      'additional': 'Дополнительный функционал',
    };

    return categories.entries.map((categoryEntry) {
      final categoryId = categoryEntry.key;
      final categoryName = categoryEntry.value;
      final categoryFeatures = _features.where((f) => f.category == categoryId).toList();

      if (categoryFeatures.isEmpty) return const SizedBox.shrink();

      final isMobile = MediaQuery.of(context).size.width < 600;
      
      return Card(
        margin: EdgeInsets.only(bottom: isMobile ? 16 : 24),
        child: Padding(
          padding: EdgeInsets.all(isMobile ? 12.0 : 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.widgets, color: Colors.blue.shade700, size: isMobile ? 20 : 24),
                  const SizedBox(width: 8),
                  Flexible(
                    child: Text(
                      categoryName,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            fontSize: isMobile ? 18 : null,
                          ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...categoryFeatures.map((feature) => _buildFeatureItem(feature)),
            ],
          ),
        ),
      );
    }).toList();
  }

  Widget _buildFeatureItem(Feature feature) {
    // Функция включена, если она есть в endpoints (даже с пустым значением)
    final isEnabled = _universityConfig?.endpoints.containsKey(feature.id) ?? false;
    // Если endpoint есть в конфигурации, используем его (даже если пустой)
    // Если нет, используем дефолтное значение для отображения
    // Но важно: если endpoint не включен, показываем дефолтное значение,
    // но при редактировании оно будет включено автоматически
    String endpoint;
    if (_universityConfig?.endpoints.containsKey(feature.id) == true) {
      // Endpoint существует в конфигурации - используем его значение
      endpoint = _universityConfig!.endpoints[feature.id] ?? '';
    } else {
      // Endpoint не существует - используем дефолтное значение для отображения
      endpoint = feature.defaultEndpoint;
    }

    return FeatureItemWidget(
      key: ValueKey(feature.id),
      feature: feature,
      isEnabled: isEnabled,
      endpoint: endpoint,
      availableEndpoints: _availableEndpoints,
      onToggle: (value) => _toggleFeature(feature, value),
      onEndpointChanged: (value) => _updateEndpoint(feature, value),
      onManualSetup: (feature) => _handleManualSetup(feature),
    );
  }

  IconData _getIconData(String icon) {
    switch (icon) {
      case 'people':
        return Icons.people;
      case 'map':
        return Icons.map;
      case 'calendar_today':
        return Icons.calendar_today;
      case 'school':
        return Icons.school;
      case 'article':
        return Icons.article;
      case 'link':
        return Icons.link;
      case 'settings':
        return Icons.settings;
      default:
        return Icons.widgets;
    }
  }

  @override
  Widget build(BuildContext context) {
    // Определяем, является ли экран мобильным
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Админ панель университета'),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: _syncChanges,
            tooltip: 'Синхронизировать',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _handleLogout,
            tooltip: 'Выйти',
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: (_isLoadingConfig || (!_hasUnsavedChanges && !_hasDataChanges)) ? null : _saveConfig,
        backgroundColor: (_hasUnsavedChanges || _hasDataChanges) ? Colors.green : Colors.grey,
        foregroundColor: Colors.white,
        icon: _isLoadingConfig
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : const Icon(Icons.save),
        label: Text(
          isMobile ? 'Сохранить' : 'Сохранить изменения',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      body: isMobile ? _buildMobileLayout() : _buildDesktopLayout(),
      bottomNavigationBar: isMobile ? _buildBottomNavigationBar() : null,
    );
  }

  Widget _buildDesktopLayout() {
    return Row(
      children: [
        NavigationRail(
          selectedIndex: _selectedIndex,
          onDestinationSelected: (index) {
            setState(() {
              _selectedIndex = index;
            });
          },
          labelType: NavigationRailLabelType.all,
          destinations: [
            const NavigationRailDestination(
              icon: Icon(Icons.dashboard),
              selectedIcon: Icon(Icons.dashboard),
              label: Text('Главная'),
            ),
            ..._modules.asMap().entries.map((entry) {
              final module = entry.value;
              return NavigationRailDestination(
                icon: Icon(_getIconData(module.icon)),
                selectedIcon: Icon(_getIconData(module.icon)),
                label: Text(module.name),
              );
            }),
          ],
        ),
        const VerticalDivider(thickness: 1, width: 1),
        Expanded(
          child: _buildContent(),
        ),
      ],
    );
  }

  Widget _buildMobileLayout() {
    return _buildContent();
  }

  Widget _buildBottomNavigationBar() {
    // NavigationBar требует минимум 2 пункта назначения
    // Если модули еще не загружены или их недостаточно, не показываем навигацию
    if (_modules.isEmpty) {
      return const SizedBox.shrink();
    }

    final destinations = [
      const NavigationDestination(
        icon: Icon(Icons.dashboard_outlined),
        selectedIcon: Icon(Icons.dashboard),
        label: 'Главная',
      ),
      ..._modules.map((module) {
        return NavigationDestination(
          icon: Icon(_getIconData(module.icon)),
          selectedIcon: Icon(_getIconData(module.icon)),
          label: module.name,
        );
      }),
    ];

    // Проверяем, что есть минимум 2 пункта (Главная + хотя бы один модуль)
    if (destinations.length < 2) {
      return const SizedBox.shrink();
    }

    return NavigationBar(
      selectedIndex: _selectedIndex.clamp(0, destinations.length - 1),
      onDestinationSelected: (index) {
        setState(() {
          _selectedIndex = index;
        });
      },
      destinations: destinations,
    );
  }
}

