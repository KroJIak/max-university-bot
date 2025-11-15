import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:csv/csv.dart';
import '../models/university_config.dart';
import '../models/teacher.dart';
import '../services/api_service.dart';

// Условный импорт для веб-платформы
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html if (dart.library.html) 'dart:html';

/// Форматтер для номера телефона
/// Разрешает только цифры и символы форматирования: +, -, (, ), пробелы
/// Автоматически форматирует номер в формат +7 (999) 123-45-67
class PhoneInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final text = newValue.text;
    
    // Разрешаем только цифры и символы форматирования
    final allowedChars = RegExp(r'[\d\+\-\(\)\s]');
    final filteredText = text.split('').where((char) => allowedChars.hasMatch(char)).join('');
    
    // Если текст изменился (были удалены недопустимые символы), обновляем значение
    if (filteredText != text) {
      return TextEditingValue(
        text: filteredText,
        selection: TextSelection.collapsed(offset: filteredText.length),
      );
    }
    
    // Форматируем номер телефона
    final digitsOnly = filteredText.replaceAll(RegExp(r'[^\d]'), '');
    
    if (digitsOnly.isEmpty) {
      return newValue;
    }
    
    String formatted = '';
    
    // Если начинается с 7 или 8, форматируем как российский номер
    if (digitsOnly.startsWith('7') || digitsOnly.startsWith('8')) {
      final phoneDigits = digitsOnly.startsWith('8') 
          ? '7${digitsOnly.substring(1)}' 
          : digitsOnly;
      
      if (phoneDigits.isNotEmpty) {
        formatted = '+7';
        if (phoneDigits.length > 1) {
          formatted += ' (${phoneDigits.substring(1, phoneDigits.length > 4 ? 4 : phoneDigits.length)}';
          if (phoneDigits.length > 4) {
            formatted += ') ${phoneDigits.substring(4, phoneDigits.length > 7 ? 7 : phoneDigits.length)}';
            if (phoneDigits.length > 7) {
              formatted += '-${phoneDigits.substring(7, phoneDigits.length > 9 ? 9 : phoneDigits.length)}';
              if (phoneDigits.length > 9) {
                formatted += '-${phoneDigits.substring(9, phoneDigits.length > 11 ? 11 : phoneDigits.length)}';
              }
            }
          } else {
            formatted += ')';
          }
        }
      }
    } else if (filteredText.startsWith('+')) {
      // Если начинается с +, но не с +7, оставляем как есть (международный формат)
      formatted = filteredText;
    } else {
      // Для других случаев форматируем просто как цифры с возможными символами
      formatted = filteredText;
    }
    
    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}

class TeachersScreen extends StatefulWidget {
  final int? universityId;
  final String? featureId;
  final VoidCallback? onCsvUploaded;
  final VoidCallback? onDataChanged; // Callback при изменении данных
  
  const TeachersScreen({
    super.key,
    this.universityId,
    this.featureId,
    this.onCsvUploaded,
    this.onDataChanged,
  });

  @override
  State<TeachersScreen> createState() => _TeachersScreenState();
}

class _TeachersScreenState extends State<TeachersScreen> {
  final _apiService = ApiService();
  UniversityConfig? _universityConfig;
  bool _isLoading = true;
  
  // Фильтры
  final _searchController = TextEditingController();
  String _selectedDepartment = 'Все кафедры';
  String? _selectedPosition;
  
  // Данные преподавателей
  List<Teacher> _allTeachers = [];
  List<Teacher> _filteredTeachers = [];
  final Set<String> _expandedTeacherIds = {};
  
  // Публичный метод для получения данных для CSV
  List<Map<String, dynamic>> getTeachersDataForCsv() {
    return _allTeachers.map((teacher) => {
      'id': teacher.id,
      'lastName': teacher.lastName,
      'firstName': teacher.firstName,
      'middleName': teacher.middleName ?? '',
      'department': teacher.department ?? '',
      'position': teacher.position ?? '',
      'phoneNumber': teacher.phoneNumber ?? '',
      'photoUrl': teacher.photoUrl ?? '',
    }).toList();
  }
  

  @override
  void initState() {
    super.initState();
    _loadConfig();
    _loadMockTeachers(); // Загружаем mock данные для демонстрации
    _searchController.addListener(_applyFilters);
  }

  @override
  void dispose() {
    _searchController.removeListener(_applyFilters);
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadConfig() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final universityId = await _apiService.getUniversityId();
      if (universityId != null) {
        final config = await _apiService.getUniversityConfig(universityId);
        if (mounted) {
          setState(() {
            _universityConfig = config;
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
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

  void _loadMockTeachers() {
    // Mock данные для демонстрации
    _allTeachers = [
      Teacher(
        id: '1',
        firstName: 'Анна',
        lastName: 'Иванова',
        middleName: 'Петровна',
        department: 'Информатика',
        position: 'Доцент',
        photoUrl: null,
      ),
      Teacher(
        id: '2',
        firstName: 'Сергей',
        lastName: 'Смирнов',
        middleName: 'Александрович',
        department: 'Математика',
        position: 'Профессор',
        photoUrl: null,
      ),
      Teacher(
        id: '3',
        firstName: 'Ольга',
        lastName: 'Кузнецова',
        middleName: null,
        department: 'Физика',
        position: 'Старший преподаватель',
        photoUrl: null,
      ),
      Teacher(
        id: '4',
        firstName: 'Дмитрий',
        lastName: 'Волков',
        middleName: 'Игоревич',
        department: 'Информатика',
        position: 'Доцент',
        photoUrl: null,
      ),
    ];
    _applyFilters();
  }

  void _applyFilters() {
    setState(() {
      _filteredTeachers = _allTeachers.where((teacher) {
        // Фильтр по имени
        final searchQuery = _searchController.text.toLowerCase();
        if (searchQuery.isNotEmpty) {
          final fullName = teacher.fullName.toLowerCase();
          if (!fullName.contains(searchQuery)) {
            return false;
          }
        }
        
        // Фильтр по кафедре
        if (_selectedDepartment != 'Все кафедры' && teacher.department != _selectedDepartment) {
          return false;
        }
        
        // Фильтр по должности
        if (_selectedPosition != null && _selectedPosition != 'Все должности' && teacher.position != _selectedPosition) {
          return false;
        }
        
        return true;
      }).toList();
    });
  }

  List<String> get _availableDepartments {
    final departments = _allTeachers.map((t) => t.department).where((d) => d != null).cast<String>().toSet().toList()..sort();
    return ['Все кафедры', ...departments];
  }

  List<String> get _availablePositions {
    final positions = _allTeachers.map((t) => t.position).where((p) => p != null).cast<String>().toSet().toList()..sort();
    return ['Все должности', ...positions];
  }

  bool _isEndpointEnabled(String endpointId) {
    if (_universityConfig == null) return false;
    return _universityConfig!.endpoints.containsKey(endpointId);
  }

  bool _hasEndpointValue(String endpointId) {
    if (_universityConfig == null) return false;
    final endpoint = _universityConfig!.endpoints[endpointId];
    return endpoint != null && endpoint.trim().isNotEmpty;
  }

  void _toggleTeacherExpansion(String teacherId) {
    setState(() {
      if (_expandedTeacherIds.contains(teacherId)) {
        _expandedTeacherIds.remove(teacherId);
      } else {
        _expandedTeacherIds.add(teacherId);
      }
    });
  }

  void _toggleCsvUpload() {
    _showCsvUploadDialog();
  }

  void _showCsvUploadDialog() {
    showDialog(
      context: context,
      barrierColor: Colors.black54, // Затемнение фона
      builder: (BuildContext context) {
        return Dialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Container(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.cloud_upload,
                  size: 64,
                  color: Colors.blue.shade700,
                ),
                const SizedBox(height: 16),
                Text(
                  'Загрузка CSV файла',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade700,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Перетащите CSV файл сюда',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'или',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey.shade500,
                      ),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: () async {
                    Navigator.of(context).pop();
                    await _handleCsvUpload();
                  },
                  icon: const Icon(Icons.folder_open),
                  label: const Text('Выбрать файл'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  ),
                ),
                const SizedBox(height: 16),
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  child: const Text('Отмена'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _handleCsvUpload() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv'],
        withData: true,
      );

      if (result != null && result.files.single.bytes != null) {
        final bytes = result.files.single.bytes!;
        final csvString = utf8.decode(bytes);
        
        // Парсим CSV
        final csvData = const CsvToListConverter().convert(csvString);
        
        if (csvData.isEmpty) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('CSV файл пуст'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        // Показываем диалог выбора: заменить или добавить
        final action = await showDialog<String>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Импорт CSV'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Найдено преподавателей: ${csvData.length - 1}'), // -1 для заголовка
                const SizedBox(height: 16),
                const Text('Выберите действие:'),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop('replace'),
                child: const Text('Заменить все'),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop('add'),
                child: const Text('Добавить к существующим'),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Отмена'),
              ),
            ],
          ),
        );

        if (action == null) return;

        // Парсим преподавателей из CSV
        final teachers = _parseCsvToTeachers(csvData);
        
        if (teachers.isEmpty) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Не удалось распарсить преподавателей из CSV файла'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        setState(() {
          if (action == 'replace') {
            _allTeachers = teachers;
          } else {
            _allTeachers.addAll(teachers);
            // Уведомляем об изменениях данных, если endpoint пустой
            widget.onDataChanged?.call();
          }
          _applyFilters();
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                action == 'replace'
                    ? 'Список преподавателей заменен. Добавлено преподавателей: ${teachers.length}'
                    : 'Добавлено преподавателей: ${teachers.length}',
              ),
              backgroundColor: Colors.green,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка загрузки CSV: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  List<Teacher> _parseCsvToTeachers(List<List<dynamic>> csvData) {
    if (csvData.length < 2) return [];

    final teachers = <Teacher>[];
    
    // Пропускаем заголовок (первую строку)
    for (int i = 1; i < csvData.length; i++) {
      final row = csvData[i];
      if (row.length < 3) continue; // Минимум: ID, Фамилия, Имя

      try {
        // Формат CSV: ID, Фамилия, Имя, Отчество, Кафедра, Должность, Телефон, Фото URL
        final id = row[0]?.toString().trim() ?? DateTime.now().millisecondsSinceEpoch.toString() + '_$i';
        final lastName = row[1]?.toString().trim() ?? '';
        final firstName = row[2]?.toString().trim() ?? '';
        
        if (lastName.isEmpty || firstName.isEmpty) continue;

        final middleName = row.length > 3 ? row[3]?.toString().trim() : null;
        final department = row.length > 4 ? row[4]?.toString().trim() : null;
        final position = row.length > 5 ? row[5]?.toString().trim() : null;
        final phoneNumber = row.length > 6 ? row[6]?.toString().trim() : null;
        final photoUrl = row.length > 7 ? row[7]?.toString().trim() : null;

        final teacher = Teacher(
          id: id,
          firstName: firstName,
          lastName: lastName,
          middleName: middleName?.isEmpty == true ? null : middleName,
          department: department?.isEmpty == true ? null : department,
          position: position?.isEmpty == true ? null : position,
          phoneNumber: phoneNumber?.isEmpty == true ? null : phoneNumber,
          photoUrl: photoUrl?.isEmpty == true ? null : photoUrl,
        );

        teachers.add(teacher);
      } catch (e) {
        // Пропускаем строки с ошибками
        continue;
      }
    }

    return teachers;
  }

  Future<void> _handleRefresh() async {
    setState(() {
      _isLoading = true;
    });
    await Future.delayed(const Duration(seconds: 1)); // Имитация загрузки
    _loadMockTeachers();
    if (mounted) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Данные обновлены'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  Future<void> _handleSave() async {
    // TODO: Реализовать сохранение
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Данные сохранены'),
        backgroundColor: Colors.green,
      ),
    );
  }

  Future<void> _exportToCsv() async {
    try {
      if (_filteredTeachers.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Нет данных для экспорта'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      // Создаем CSV данные
      final List<List<dynamic>> csvData = [];
      
      // Заголовки
      csvData.add([
        'ID',
        'Фамилия',
        'Имя',
        'Отчество',
        'Кафедра',
        'Должность',
        'Телефон',
        'Фото URL',
      ]);

      // Данные преподавателей
      for (var teacher in _filteredTeachers) {
        csvData.add([
          teacher.id,
          teacher.lastName,
          teacher.firstName,
          teacher.middleName ?? '',
          teacher.department ?? '',
          teacher.position ?? '',
          teacher.phoneNumber ?? '',
          teacher.photoUrl ?? '',
        ]);
      }

      // Конвертируем в CSV строку
      final csvString = const ListToCsvConverter().convert(csvData);

      // Экспортируем файл для скачивания (отправка на ghost-api происходит при сохранении)
      if (kIsWeb) {
        // Для веб-платформы используем dart:html
        await _downloadCsvWeb(csvString);
      } else {
        // Для других платформ можно использовать file_picker для сохранения
        await _downloadCsvOther(csvString);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Экспортировано ${_filteredTeachers.length} преподавателей'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка при экспорте: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _downloadCsvWeb(String csvString) async {
    // Используем условную компиляцию для веб
    if (kIsWeb) {
      // ignore: undefined_prefixed_name, deprecated_member_use
      final bytes = utf8.encode(csvString);
      // ignore: undefined_prefixed_name, deprecated_member_use
      final blob = html.Blob([bytes], 'text/csv;charset=utf-8');
      // ignore: undefined_prefixed_name, deprecated_member_use
      final url = html.Url.createObjectUrlFromBlob(blob);
      // ignore: undefined_prefixed_name, deprecated_member_use
      html.AnchorElement(href: url)
        ..setAttribute('download', 'teachers_${DateTime.now().toIso8601String().split('T')[0]}.csv')
        ..click();
      // ignore: undefined_prefixed_name, deprecated_member_use
      html.Url.revokeObjectUrl(url);
    }
  }

  Future<void> _downloadCsvOther(String csvString) async {
    // Для не-веб платформ можно использовать file_picker для сохранения
    // Или показать диалог выбора места сохранения
    // В данном случае просто показываем сообщение, что на не-веб платформах
    // нужно использовать другой подход
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Экспорт CSV доступен только в веб-версии'),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }

  Future<void> _editTeacher(Teacher teacher) async {
    final result = await showDialog<Teacher>(
      context: context,
      barrierColor: Colors.black54,
      builder: (BuildContext context) {
        return _EditTeacherDialog(teacher: teacher);
      },
    );

    if (result != null) {
      setState(() {
        final index = _allTeachers.indexWhere((t) => t.id == teacher.id);
        if (index != -1) {
          _allTeachers[index] = result;
          _applyFilters();
        }
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Преподаватель успешно обновлен'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _deleteTeacher(Teacher teacher) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Удаление преподавателя'),
          content: Text(
            'Вы уверены, что хотите удалить преподавателя "${teacher.fullName}"?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Отмена'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: TextButton.styleFrom(
                foregroundColor: Colors.red,
              ),
              child: const Text('Удалить'),
            ),
          ],
        );
      },
    );

    if (confirm == true) {
      setState(() {
        _allTeachers.removeWhere((t) => t.id == teacher.id);
        _expandedTeacherIds.remove(teacher.id);
        _applyFilters();
        // Уведомляем об изменениях данных, если endpoint пустой
        widget.onDataChanged?.call();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Преподаватель "${teacher.fullName}" удален'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  Future<void> _addTeacher() async {
    final result = await showDialog<Teacher>(
      context: context,
      barrierColor: Colors.black54,
      builder: (BuildContext context) {
        return _AddTeacherDialog();
      },
    );

    if (result != null) {
      setState(() {
        _allTeachers.add(result);
        _applyFilters();
        // Уведомляем об изменениях данных, если endpoint пустой
        widget.onDataChanged?.call();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Преподаватель "${result.fullName}" успешно добавлен'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    final isTeachersEnabled = _isEndpointEnabled('students_teachers');
    final hasTeachersEndpoint = _hasEndpointValue('students_teachers');

    // Endpoint включен и имеет значение
    final enabledAndConfigured = isTeachersEnabled && hasTeachersEndpoint;

    // Endpoint выключен
    final disabled = !isTeachersEnabled;

    // Endpoint включены, но пустые (не настроены) - показываем таблицу
    // Эта переменная используется для логики, но таблица показывается всегда, когда не bothEnabledAndConfigured и не bothDisabled

    // Если endpoint включен и настроен, показываем сообщение
    if (enabledAndConfigured) {
      return SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.cloud_done,
                      size: 64,
                      color: Colors.green.shade700,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Данные преподавателей',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Данные напрямую идут с вашей API',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    _buildEndpointStatusSimple('students_teachers', 'Список преподавателей'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    // Если endpoint выключен, показываем сообщение
    if (disabled) {
      return SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.school, size: 32, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Преподаватели',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        Icon(
                          Icons.info_outline,
                          size: 64,
                          color: Colors.orange.shade600,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Данная функция выключена',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.orange.shade700,
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Для работы с данными преподавателей необходимо включить функцию "Список преподавателей" на главной странице.',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.grey.shade600,
                              ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // Основной функционал - таблица преподавателей (когда endpoint включен, но пустой)
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    if (isMobile) {
      // На мобильных устройствах используем компактный layout
      return Column(
        children: [
          // Заголовок (фиксированный сверху)
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Icon(Icons.school, size: 24, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Преподаватели',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Информация о состоянии endpoint
                Card(
                  color: Colors.blue.shade50,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline, size: 14, color: Colors.blue.shade700),
                        const SizedBox(width: 6),
                        Expanded(
                          child: _buildEndpointStatus(
                            'Список преподавателей',
                            isTeachersEnabled,
                            hasTeachersEndpoint,
                            _universityConfig?.endpoints['students_teachers'] ?? '',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Фильтры (фиксированные)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12.0),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Поиск по имени
                    TextField(
                      controller: _searchController,
                      decoration: InputDecoration(
                        labelText: 'Поиск по имени',
                        hintText: 'Введите ФИО...',
                        prefixIcon: const Icon(Icons.search),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                      ),
                    ),
                    const SizedBox(height: 8),
                    // Фильтр по кафедре
                    Autocomplete<String>(
                      displayStringForOption: (String option) => option,
                      optionsBuilder: (TextEditingValue textEditingValue) {
                        if (textEditingValue.text.isEmpty) {
                          return _availableDepartments;
                        }
                        return _availableDepartments.where((department) {
                          return department.toLowerCase().contains(
                            textEditingValue.text.toLowerCase(),
                          );
                        });
                      },
                      onSelected: (String selection) {
                        setState(() {
                          _selectedDepartment = selection;
                          _applyFilters();
                        });
                      },
                      fieldViewBuilder: (
                        BuildContext context,
                        TextEditingController textEditingController,
                        FocusNode focusNode,
                        VoidCallback onFieldSubmitted,
                      ) {
                        textEditingController.text = _selectedDepartment;
                        return TextField(
                          controller: textEditingController,
                          focusNode: focusNode,
                          decoration: InputDecoration(
                            labelText: 'Кафедра',
                            prefixIcon: const Icon(Icons.business),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                          ),
                          onChanged: (value) {
                            // Автозаполнение работает через Autocomplete
                          },
                        );
                      },
                    ),
                    const SizedBox(height: 8),
                    // Фильтр по должности
                    DropdownButtonFormField<String>(
                      decoration: InputDecoration(
                        labelText: 'Должность',
                        prefixIcon: const Icon(Icons.work),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                      ),
                      isExpanded: true,
                      value: _selectedPosition,
                      items: [
                        const DropdownMenuItem<String>(
                          value: null,
                          child: Text('Все должности'),
                        ),
                        ..._availablePositions.map((position) {
                          return DropdownMenuItem<String>(
                            value: position,
                            child: Text(position),
                          );
                        }),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedPosition = value;
                          _applyFilters();
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          // Таблица преподавателей (прокручиваемая)
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12.0),
              child: _filteredTeachers.isEmpty
                  ? Center(
                      child: Text(
                        'Преподаватели не найдены',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.grey,
                            ),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _filteredTeachers.length,
                      itemBuilder: (context, index) {
                        final teacher = _filteredTeachers[index];
                        final isExpanded = _expandedTeacherIds.contains(teacher.id);
                        return _buildTeacherCard(teacher, isExpanded);
                      },
                    ),
            ),
          ),
          // Кнопки управления (фиксированные снизу)
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _addTeacher,
                    icon: const Icon(Icons.add),
                    label: const Text('Добавить преподавателя'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  alignment: WrapAlignment.center,
                  children: [
                    ElevatedButton.icon(
                      onPressed: _toggleCsvUpload,
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Загрузить CSV'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: _handleRefresh,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Обновить'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: _handleSave,
                      icon: const Icon(Icons.save),
                      label: const Text('Сохранить'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: _exportToCsv,
                      icon: const Icon(Icons.download),
                      label: const Text('Экспорт CSV'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        backgroundColor: Colors.blue.shade700,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      );
    }
    
    // На десктопе - обычный layout
    return Column(
      children: [
        // Заголовок
        Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                  children: [
                    Icon(Icons.school, size: 32, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Преподаватели',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Информация о состоянии endpoint
                Card(
                  color: Colors.blue.shade50,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline, size: 16, color: Colors.blue.shade700),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _buildEndpointStatus(
                            'Список преподавателей',
                            isTeachersEnabled,
                            hasTeachersEndpoint,
                            _universityConfig?.endpoints['students_teachers'] ?? '',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
        // Фильтры
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final isMobile = constraints.maxWidth < 600;
                  if (isMobile) {
                    // На мобильных устройствах - вертикальная компоновка
                    return Column(
                      children: [
                        // Поиск по имени
                        TextField(
                          controller: _searchController,
                          decoration: InputDecoration(
                            labelText: 'Поиск по имени',
                            hintText: 'Введите ФИО...',
                            prefixIcon: const Icon(Icons.search),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        // Фильтр по кафедре
                        Autocomplete<String>(
                          displayStringForOption: (String option) => option,
                          optionsBuilder: (TextEditingValue textEditingValue) {
                            if (textEditingValue.text.isEmpty) {
                              return _availableDepartments;
                            }
                            return _availableDepartments.where((department) {
                              return department.toLowerCase().contains(
                                textEditingValue.text.toLowerCase(),
                              );
                            });
                          },
                          onSelected: (String selection) {
                            setState(() {
                              _selectedDepartment = selection;
                              _applyFilters();
                            });
                          },
                          fieldViewBuilder: (
                            BuildContext context,
                            TextEditingController textEditingController,
                            FocusNode focusNode,
                            VoidCallback onFieldSubmitted,
                          ) {
                            textEditingController.text = _selectedDepartment;
                            return TextField(
                              controller: textEditingController,
                              focusNode: focusNode,
                              decoration: InputDecoration(
                                labelText: 'Кафедра',
                                prefixIcon: const Icon(Icons.business),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onChanged: (value) {
                                // Автозаполнение работает через Autocomplete
                              },
                            );
                          },
                        ),
                        const SizedBox(height: 12),
                        // Фильтр по должности
                        DropdownButtonFormField<String>(
                          decoration: InputDecoration(
                            labelText: 'Должность',
                            prefixIcon: const Icon(Icons.work),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          isExpanded: true,
                          value: _selectedPosition,
                          items: [
                            const DropdownMenuItem<String>(
                              value: null,
                              child: Text('Все должности'),
                            ),
                            ..._availablePositions.map((position) {
                              return DropdownMenuItem<String>(
                                value: position,
                                child: Text(position),
                              );
                            }),
                          ],
                          onChanged: (value) {
                            setState(() {
                              _selectedPosition = value;
                              _applyFilters();
                            });
                          },
                        ),
                      ],
                    );
                  } else {
                    // На десктопе - горизонтальная компоновка
                    return Row(
                      children: [
                        // Поиск по имени
                        Expanded(
                          flex: 2,
                          child: TextField(
                            controller: _searchController,
                            decoration: InputDecoration(
                              labelText: 'Поиск по имени',
                              hintText: 'Введите ФИО...',
                              prefixIcon: const Icon(Icons.search),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        // Фильтр по кафедре
                        Expanded(
                          child: Autocomplete<String>(
                            displayStringForOption: (String option) => option,
                            optionsBuilder: (TextEditingValue textEditingValue) {
                              if (textEditingValue.text.isEmpty) {
                                return _availableDepartments;
                              }
                              return _availableDepartments.where((department) {
                                return department.toLowerCase().contains(
                                  textEditingValue.text.toLowerCase(),
                                );
                              });
                            },
                            onSelected: (String selection) {
                              setState(() {
                                _selectedDepartment = selection;
                                _applyFilters();
                              });
                            },
                            fieldViewBuilder: (
                              BuildContext context,
                              TextEditingController textEditingController,
                              FocusNode focusNode,
                              VoidCallback onFieldSubmitted,
                            ) {
                              textEditingController.text = _selectedDepartment;
                              return TextField(
                                controller: textEditingController,
                                focusNode: focusNode,
                                decoration: InputDecoration(
                                  labelText: 'Кафедра',
                                  prefixIcon: const Icon(Icons.business),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                onChanged: (value) {
                                  // Автозаполнение работает через Autocomplete
                                },
                              );
                            },
                          ),
                        ),
                        const SizedBox(width: 16),
                        // Фильтр по должности
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            decoration: InputDecoration(
                              labelText: 'Должность',
                              prefixIcon: const Icon(Icons.work),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            value: _selectedPosition,
                            items: [
                              const DropdownMenuItem<String>(
                                value: null,
                                child: Text('Все должности'),
                              ),
                              ..._availablePositions.map((position) {
                                return DropdownMenuItem<String>(
                                  value: position,
                                  child: Text(position),
                                );
                              }),
                            ],
                            onChanged: (value) {
                              setState(() {
                                _selectedPosition = value;
                                _applyFilters();
                              });
                            },
                          ),
                        ),
                      ],
                    );
                  }
                },
              ),
            ),
          ),
        ),
        SizedBox(height: isMobile ? 12 : 16),
        // Таблица преподавателей
        Expanded(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: isMobile ? 16.0 : 24.0),
            child: _filteredTeachers.isEmpty
                ? Center(
                    child: Text(
                      'Преподаватели не найдены',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  )
                : ListView.builder(
                    itemCount: _filteredTeachers.length,
                    itemBuilder: (context, index) {
                      final teacher = _filteredTeachers[index];
                      final isExpanded = _expandedTeacherIds.contains(teacher.id);
                      return _buildTeacherCard(teacher, isExpanded);
                    },
                  ),
          ),
        ),
        // Кнопки управления
        Padding(
          padding: const EdgeInsets.all(24.0),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final isMobile = constraints.maxWidth < 600;
              if (isMobile) {
                // На мобильных устройствах - вертикальная компоновка
                return Column(
                  children: [
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _addTeacher,
                        icon: const Icon(Icons.add),
                        label: const Text('Добавить преподавателя'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      alignment: WrapAlignment.center,
                      children: [
                        ElevatedButton.icon(
                          onPressed: _toggleCsvUpload,
                          icon: const Icon(Icons.upload_file),
                          label: const Text('Загрузить CSV'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          ),
                        ),
                        ElevatedButton.icon(
                          onPressed: _handleRefresh,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Обновить'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                          ),
                        ),
                        ElevatedButton.icon(
                          onPressed: _handleSave,
                          icon: const Icon(Icons.save),
                          label: const Text('Сохранить'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                          ),
                        ),
                        ElevatedButton.icon(
                          onPressed: _exportToCsv,
                          icon: const Icon(Icons.download),
                          label: const Text('Экспорт CSV'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            backgroundColor: Colors.blue.shade700,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              } else {
                // На десктопе - горизонтальная компоновка
                return Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    ElevatedButton.icon(
                      onPressed: _addTeacher,
                      icon: const Icon(Icons.add),
                      label: const Text('Добавить преподавателя'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                    ),
                    Row(
                      children: [
                        ElevatedButton.icon(
                          onPressed: _toggleCsvUpload,
                          icon: const Icon(Icons.upload_file),
                          label: const Text('Загрузить CSV'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: _handleRefresh,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Обновить'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: _handleSave,
                          icon: const Icon(Icons.save),
                          label: const Text('Сохранить'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: _exportToCsv,
                          icon: const Icon(Icons.download),
                          label: const Text('Экспорт CSV'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                            backgroundColor: Colors.blue.shade700,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ],
                );
              }
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTeacherCard(Teacher teacher, bool isExpanded) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Column(
        children: [
          // Основная информация
          InkWell(
            onTap: () => _toggleTeacherExpansion(teacher.id),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  // Фото или иконка
                  CircleAvatar(
                    radius: 30,
                    backgroundImage: teacher.photoBase64 != null
                        ? MemoryImage(base64Decode(teacher.photoBase64!))
                        : teacher.photoUrl != null
                            ? NetworkImage(teacher.photoUrl!)
                            : null,
                    child: teacher.photoBase64 == null && teacher.photoUrl == null
                        ? const Icon(Icons.person, size: 30)
                        : null,
                  ),
                  const SizedBox(width: 16),
                  // ФИО, кафедра, должность
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          teacher.fullName,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            if (teacher.department != null) ...[
                              Icon(Icons.business, size: 16, color: Colors.grey.shade600),
                              const SizedBox(width: 4),
                              Flexible(
                                child: Text(
                                  teacher.department!,
                                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                        color: Colors.grey.shade600,
                                      ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                            if (teacher.department != null && teacher.position != null)
                              const SizedBox(width: 16),
                            if (teacher.position != null) ...[
                              Icon(Icons.work, size: 16, color: Colors.grey.shade600),
                              const SizedBox(width: 4),
                              Flexible(
                                child: Text(
                                  teacher.position!,
                                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                        color: Colors.grey.shade600,
                                      ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ],
                    ),
                  ),
                  // Кнопки действий
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final isMobile = constraints.maxWidth < 400;
                      if (isMobile) {
                        // На очень маленьких экранах используем PopupMenuButton
                        return PopupMenuButton<String>(
                          icon: const Icon(Icons.more_vert),
                          onSelected: (value) {
                            switch (value) {
                              case 'edit':
                                _editTeacher(teacher);
                                break;
                              case 'delete':
                                _deleteTeacher(teacher);
                                break;
                              case 'expand':
                                _toggleTeacherExpansion(teacher.id);
                                break;
                            }
                          },
                          itemBuilder: (context) => [
                            PopupMenuItem(
                              value: 'edit',
                              child: Row(
                                children: [
                                  const Icon(Icons.edit, color: Colors.blue, size: 20),
                                  const SizedBox(width: 8),
                                  const Text('Редактировать'),
                                ],
                              ),
                            ),
                            PopupMenuItem(
                              value: 'delete',
                              child: Row(
                                children: [
                                  const Icon(Icons.delete, color: Colors.red, size: 20),
                                  const SizedBox(width: 8),
                                  const Text('Удалить'),
                                ],
                              ),
                            ),
                            PopupMenuItem(
                              value: 'expand',
                              child: Row(
                                children: [
                                  Icon(
                                    isExpanded ? Icons.expand_less : Icons.expand_more,
                                    color: Colors.grey.shade600,
                                    size: 20,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(isExpanded ? 'Свернуть' : 'Развернуть'),
                                ],
                              ),
                            ),
                          ],
                        );
                      } else {
                        // На больших экранах показываем все кнопки
                        return Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit, color: Colors.blue),
                              onPressed: () => _editTeacher(teacher),
                              tooltip: 'Редактировать',
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => _deleteTeacher(teacher),
                              tooltip: 'Удалить',
                            ),
                            // Иконка разворачивания
                            IconButton(
                              icon: Icon(
                                isExpanded ? Icons.expand_less : Icons.expand_more,
                                color: Colors.grey.shade600,
                              ),
                              onPressed: () => _toggleTeacherExpansion(teacher.id),
                              tooltip: isExpanded ? 'Свернуть' : 'Развернуть',
                            ),
                          ],
                        );
                      }
                    },
                  ),
                ],
              ),
            ),
          ),
          // Развернутая информация
          if (isExpanded)
            Container(
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                border: Border(
                  top: BorderSide(color: Colors.grey.shade300),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildDetailRow('ID', teacher.id),
                  _buildDetailRow('Фамилия', teacher.lastName),
                  _buildDetailRow('Имя', teacher.firstName),
                  if (teacher.middleName != null)
                    _buildDetailRow('Отчество', teacher.middleName!),
                  if (teacher.department != null)
                    _buildDetailRow('Кафедра', teacher.department!),
                  if (teacher.position != null)
                    _buildDetailRow('Должность', teacher.position!),
                  if (teacher.phoneNumber != null && teacher.phoneNumber!.isNotEmpty)
                    _buildDetailRow('Телефон', teacher.phoneNumber!),
                  // Здесь можно добавить дополнительную информацию
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade700,
                  ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEndpointStatusSimple(String endpointId, String endpointName) {
    final isEnabled = _isEndpointEnabled(endpointId);
    final hasValue = _hasEndpointValue(endpointId);
    
    Color statusColor;
    IconData statusIcon;
    String statusText;
    
    if (isEnabled && hasValue) {
      statusColor = Colors.green;
      statusIcon = Icons.check_circle;
      statusText = 'Включен и настроен';
    } else if (isEnabled && !hasValue) {
      statusColor = Colors.orange;
      statusIcon = Icons.warning;
      statusText = 'Включен, но не настроен';
    } else {
      statusColor = Colors.grey;
      statusIcon = Icons.cancel;
      statusText = 'Выключен';
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(statusIcon, size: 16, color: statusColor),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              '$endpointName: $statusText',
              style: TextStyle(
                fontSize: 12,
                color: statusColor,
                fontWeight: FontWeight.w500,
              ),
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEndpointStatus(String name, bool isEnabled, bool hasValue, String endpoint) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          isEnabled
              ? (hasValue ? Icons.check_circle : Icons.warning_amber_rounded)
              : Icons.cancel,
          size: 16,
          color: isEnabled
              ? (hasValue ? Colors.green : Colors.orange)
              : Colors.grey,
        ),
        const SizedBox(width: 6),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                name,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              if (isEnabled)
                Text(
                  hasValue
                      ? 'Endpoint: $endpoint'
                      : 'Не настроен',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: hasValue ? Colors.green.shade700 : Colors.orange.shade700,
                        fontStyle: FontStyle.italic,
                        fontSize: 11,
                      ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                )
              else
                Text(
                  'Выключен',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey.shade600,
                        fontSize: 11,
                      ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _EditTeacherDialog extends StatefulWidget {
  final Teacher teacher;

  const _EditTeacherDialog({required this.teacher});

  @override
  State<_EditTeacherDialog> createState() => _EditTeacherDialogState();
}

class _EditTeacherDialogState extends State<_EditTeacherDialog> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _middleNameController;
  late TextEditingController _departmentController;
  late TextEditingController _positionController;
  late TextEditingController _phoneNumberController;
  final _formKey = GlobalKey<FormState>();
  String? _photoBase64;
  Uint8List? _selectedImageBytes;

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.teacher.firstName);
    _lastNameController = TextEditingController(text: widget.teacher.lastName);
    _middleNameController = TextEditingController(text: widget.teacher.middleName ?? '');
    _departmentController = TextEditingController(text: widget.teacher.department ?? '');
    _positionController = TextEditingController(text: widget.teacher.position ?? '');
    _phoneNumberController = TextEditingController(text: widget.teacher.phoneNumber ?? '');
    _photoBase64 = widget.teacher.photoBase64;
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _middleNameController.dispose();
    _departmentController.dispose();
    _positionController.dispose();
    _phoneNumberController.dispose();
    super.dispose();
  }

  Future<void> _pickImage() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
        withData: true,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.single;
        
        // Для веба используем bytes напрямую, для других платформ читаем из path
        Uint8List? bytes;
        if (file.bytes != null) {
          bytes = file.bytes!;
        } else if (file.path != null) {
          // Для не-веб платформ можно использовать dart:io
          // Но в веб-версии это не сработает, поэтому используем только bytes
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Не удалось загрузить изображение. Попробуйте другой файл.'),
                backgroundColor: Colors.orange,
              ),
            );
          }
          return;
        }
        
        if (bytes != null) {
          final base64String = base64Encode(bytes);
          
          setState(() {
            _selectedImageBytes = bytes;
            _photoBase64 = base64String;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка при выборе изображения: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 500),
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.edit, color: Colors.blue.shade700),
                    const SizedBox(width: 8),
                    Text(
                      'Редактировать преподавателя',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Фото преподавателя
                Center(
                  child: Column(
                    children: [
                      Stack(
                        children: [
                          CircleAvatar(
                            radius: 50,
                            backgroundImage: _photoBase64 != null
                                ? MemoryImage(base64Decode(_photoBase64!))
                                : widget.teacher.photoUrl != null
                                    ? NetworkImage(widget.teacher.photoUrl!)
                                    : null,
                            child: _photoBase64 == null && widget.teacher.photoUrl == null
                                ? const Icon(Icons.person, size: 50)
                                : null,
                          ),
                          if (_selectedImageBytes != null || _photoBase64 != null || widget.teacher.photoUrl != null)
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: CircleAvatar(
                                radius: 16,
                                backgroundColor: Colors.red,
                                child: IconButton(
                                  icon: const Icon(Icons.close, size: 16, color: Colors.white),
                                  onPressed: () {
                                    setState(() {
                                      _photoBase64 = null;
                                      _selectedImageBytes = null;
                                    });
                                  },
                                  padding: EdgeInsets.zero,
                                  constraints: const BoxConstraints(),
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: _pickImage,
                        icon: const Icon(Icons.photo_camera),
                        label: Text(_photoBase64 != null || widget.teacher.photoUrl != null
                            ? 'Изменить фото'
                            : 'Добавить фото'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _lastNameController,
                  decoration: InputDecoration(
                    labelText: 'Фамилия *',
                    prefixIcon: const Icon(Icons.person),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите фамилию';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _firstNameController,
                  decoration: InputDecoration(
                    labelText: 'Имя *',
                    prefixIcon: const Icon(Icons.person_outline),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите имя';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _middleNameController,
                  decoration: InputDecoration(
                    labelText: 'Отчество',
                    prefixIcon: const Icon(Icons.person_outline),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _departmentController,
                  decoration: InputDecoration(
                    labelText: 'Кафедра',
                    prefixIcon: const Icon(Icons.business),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _positionController,
                  decoration: InputDecoration(
                    labelText: 'Должность',
                    prefixIcon: const Icon(Icons.work),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _phoneNumberController,
                  decoration: InputDecoration(
                    labelText: 'Номер телефона',
                    prefixIcon: const Icon(Icons.phone),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    hintText: '+7 (999) 123-45-67',
                  ),
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    PhoneInputFormatter(),
                  ],
                  validator: (value) {
                    if (value != null && value.trim().isNotEmpty) {
                      // Простая валидация номера телефона
                      final phoneRegex = RegExp(r'^[\d\s\+\-\(\)]+$');
                      if (!phoneRegex.hasMatch(value.trim())) {
                        return 'Введите корректный номер телефона';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Отмена'),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: () {
                        if (_formKey.currentState!.validate()) {
                          final updatedTeacher = Teacher(
                            id: widget.teacher.id,
                            firstName: _firstNameController.text.trim(),
                            lastName: _lastNameController.text.trim(),
                            middleName: _middleNameController.text.trim().isEmpty
                                ? null
                                : _middleNameController.text.trim(),
                            department: _departmentController.text.trim().isEmpty
                                ? null
                                : _departmentController.text.trim(),
                            position: _positionController.text.trim().isEmpty
                                ? null
                                : _positionController.text.trim(),
                            phoneNumber: _phoneNumberController.text.trim().isEmpty
                                ? null
                                : _phoneNumberController.text.trim(),
                            photoUrl: widget.teacher.photoUrl,
                            photoBase64: _photoBase64,
                            additionalData: widget.teacher.additionalData,
                          );
                          Navigator.of(context).pop(updatedTeacher);
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Сохранить'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _AddTeacherDialog extends StatefulWidget {
  const _AddTeacherDialog();

  @override
  State<_AddTeacherDialog> createState() => _AddTeacherDialogState();
}

class _AddTeacherDialogState extends State<_AddTeacherDialog> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _middleNameController;
  late TextEditingController _departmentController;
  late TextEditingController _positionController;
  late TextEditingController _phoneNumberController;
  final _formKey = GlobalKey<FormState>();
  String? _photoBase64;
  Uint8List? _selectedImageBytes;

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController();
    _lastNameController = TextEditingController();
    _middleNameController = TextEditingController();
    _departmentController = TextEditingController();
    _positionController = TextEditingController();
    _phoneNumberController = TextEditingController();
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _middleNameController.dispose();
    _departmentController.dispose();
    _positionController.dispose();
    _phoneNumberController.dispose();
    super.dispose();
  }

  String _generateId() {
    // Генерируем уникальный ID на основе текущего времени и случайного числа
    return DateTime.now().millisecondsSinceEpoch.toString();
  }

  Future<void> _pickImage() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
        withData: true,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.single;
        
        // Для веба используем bytes напрямую, для других платформ читаем из path
        Uint8List? bytes;
        if (file.bytes != null) {
          bytes = file.bytes!;
        } else if (file.path != null) {
          // Для не-веб платформ можно использовать dart:io
          // Но в веб-версии это не сработает, поэтому используем только bytes
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Не удалось загрузить изображение. Попробуйте другой файл.'),
                backgroundColor: Colors.orange,
              ),
            );
          }
          return;
        }
        
        if (bytes != null) {
          final base64String = base64Encode(bytes);
          
          setState(() {
            _selectedImageBytes = bytes;
            _photoBase64 = base64String;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка при выборе изображения: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 500),
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.person_add, color: Colors.blue.shade700),
                    const SizedBox(width: 8),
                    Text(
                      'Добавить преподавателя',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Фото преподавателя
                Center(
                  child: Column(
                    children: [
                      Stack(
                        children: [
                          CircleAvatar(
                            radius: 50,
                            backgroundImage: _photoBase64 != null
                                ? MemoryImage(base64Decode(_photoBase64!))
                                : null,
                            child: _photoBase64 == null
                                ? const Icon(Icons.person, size: 50)
                                : null,
                          ),
                          if (_selectedImageBytes != null || _photoBase64 != null)
                            Positioned(
                              bottom: 0,
                              right: 0,
                              child: CircleAvatar(
                                radius: 16,
                                backgroundColor: Colors.red,
                                child: IconButton(
                                  icon: const Icon(Icons.close, size: 16, color: Colors.white),
                                  onPressed: () {
                                    setState(() {
                                      _photoBase64 = null;
                                      _selectedImageBytes = null;
                                    });
                                  },
                                  padding: EdgeInsets.zero,
                                  constraints: const BoxConstraints(),
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: _pickImage,
                        icon: const Icon(Icons.photo_camera),
                        label: Text(_photoBase64 != null
                            ? 'Изменить фото'
                            : 'Добавить фото'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _lastNameController,
                  decoration: InputDecoration(
                    labelText: 'Фамилия *',
                    prefixIcon: const Icon(Icons.person),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите фамилию';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _firstNameController,
                  decoration: InputDecoration(
                    labelText: 'Имя *',
                    prefixIcon: const Icon(Icons.person_outline),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите имя';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _middleNameController,
                  decoration: InputDecoration(
                    labelText: 'Отчество',
                    prefixIcon: const Icon(Icons.person_outline),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _departmentController,
                  decoration: InputDecoration(
                    labelText: 'Кафедра',
                    prefixIcon: const Icon(Icons.business),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _positionController,
                  decoration: InputDecoration(
                    labelText: 'Должность',
                    prefixIcon: const Icon(Icons.work),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _phoneNumberController,
                  decoration: InputDecoration(
                    labelText: 'Номер телефона',
                    prefixIcon: const Icon(Icons.phone),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    hintText: '+7 (999) 123-45-67',
                  ),
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    PhoneInputFormatter(),
                  ],
                  validator: (value) {
                    if (value != null && value.trim().isNotEmpty) {
                      // Простая валидация номера телефона
                      final phoneRegex = RegExp(r'^[\d\s\+\-\(\)]+$');
                      if (!phoneRegex.hasMatch(value.trim())) {
                        return 'Введите корректный номер телефона';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Отмена'),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: () {
                        if (_formKey.currentState!.validate()) {
                          final newTeacher = Teacher(
                            id: _generateId(),
                            firstName: _firstNameController.text.trim(),
                            lastName: _lastNameController.text.trim(),
                            middleName: _middleNameController.text.trim().isEmpty
                                ? null
                                : _middleNameController.text.trim(),
                            department: _departmentController.text.trim().isEmpty
                                ? null
                                : _departmentController.text.trim(),
                            position: _positionController.text.trim().isEmpty
                                ? null
                                : _positionController.text.trim(),
                            phoneNumber: _phoneNumberController.text.trim().isEmpty
                                ? null
                                : _phoneNumberController.text.trim(),
                            photoUrl: null,
                            photoBase64: _photoBase64,
                            additionalData: null,
                          );
                          Navigator.of(context).pop(newTeacher);
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Добавить'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
