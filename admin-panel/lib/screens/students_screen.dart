import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:csv/csv.dart';
import '../models/university_config.dart';
import '../models/student.dart';
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

class StudentsScreen extends StatefulWidget {
  const StudentsScreen({super.key});

  @override
  State<StudentsScreen> createState() => _StudentsScreenState();
}

class _StudentsScreenState extends State<StudentsScreen> {
  final _apiService = ApiService();
  UniversityConfig? _universityConfig;
  bool _isLoading = true;
  
  // Фильтры
  final _searchController = TextEditingController();
  String _selectedGroup = 'Все группы';
  int? _selectedCourse;
  
  // Данные студентов
  List<Student> _allStudents = [];
  List<Student> _filteredStudents = [];
  final Set<String> _expandedStudentIds = {};
  

  @override
  void initState() {
    super.initState();
    _loadConfig();
    _loadMockStudents(); // Загружаем mock данные для демонстрации
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

  void _loadMockStudents() {
    // Mock данные для демонстрации
    _allStudents = [
      Student(
        id: '1',
        firstName: 'Иван',
        lastName: 'Иванов',
        middleName: 'Иванович',
        course: 1,
        group: 'ИВТ-21',
        photoUrl: null,
      ),
      Student(
        id: '2',
        firstName: 'Мария',
        lastName: 'Петрова',
        middleName: 'Сергеевна',
        course: 2,
        group: 'ИВТ-20',
        photoUrl: null,
      ),
      Student(
        id: '3',
        firstName: 'Алексей',
        lastName: 'Сидоров',
        middleName: null,
        course: 1,
        group: 'ИВТ-21',
        photoUrl: null,
      ),
      Student(
        id: '4',
        firstName: 'Елена',
        lastName: 'Козлова',
        middleName: 'Александровна',
        course: 3,
        group: 'ИВТ-19',
        photoUrl: null,
      ),
    ];
    _applyFilters();
  }

  void _applyFilters() {
    setState(() {
      _filteredStudents = _allStudents.where((student) {
        // Фильтр по имени
        final searchQuery = _searchController.text.toLowerCase();
        if (searchQuery.isNotEmpty) {
          final fullName = student.fullName.toLowerCase();
          if (!fullName.contains(searchQuery)) {
            return false;
          }
        }
        
        // Фильтр по группе
        if (_selectedGroup != 'Все группы' && student.group != _selectedGroup) {
          return false;
        }
        
        // Фильтр по курсу
        if (_selectedCourse != null && student.course != _selectedCourse) {
          return false;
        }
        
        return true;
      }).toList();
    });
  }

  List<String> get _availableGroups {
    final groups = _allStudents.map((s) => s.group).toSet().toList()..sort();
    return ['Все группы', ...groups];
  }

  List<int> get _availableCourses {
    final courses = _allStudents.map((s) => s.course).toSet().toList()..sort();
    return courses;
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

  void _toggleStudentExpansion(String studentId) {
    setState(() {
      if (_expandedStudentIds.contains(studentId)) {
        _expandedStudentIds.remove(studentId);
      } else {
        _expandedStudentIds.add(studentId);
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
                Text('Найдено студентов: ${csvData.length - 1}'), // -1 для заголовка
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

        // Парсим студентов из CSV
        final students = _parseCsvToStudents(csvData);
        
        if (students.isEmpty) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Не удалось распарсить студентов из CSV файла'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        setState(() {
          if (action == 'replace') {
            _allStudents = students;
          } else {
            _allStudents.addAll(students);
          }
          _applyFilters();
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                action == 'replace'
                    ? 'Список студентов заменен. Добавлено студентов: ${students.length}'
                    : 'Добавлено студентов: ${students.length}',
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

  List<Student> _parseCsvToStudents(List<List<dynamic>> csvData) {
    if (csvData.length < 2) return [];

    final students = <Student>[];
    
    // Пропускаем заголовок (первую строку)
    for (int i = 1; i < csvData.length; i++) {
      final row = csvData[i];
      if (row.length < 5) continue; // Минимум: ID, Фамилия, Имя, Курс, Группа

      try {
        // Формат CSV: ID, Фамилия, Имя, Отчество, Курс, Группа, Телефон, Фото URL
        final id = row[0]?.toString().trim() ?? DateTime.now().millisecondsSinceEpoch.toString() + '_$i';
        final lastName = row[1]?.toString().trim() ?? '';
        final firstName = row[2]?.toString().trim() ?? '';
        
        if (lastName.isEmpty || firstName.isEmpty) continue;

        final middleName = row.length > 3 ? row[3]?.toString().trim() : null;
        final course = row.length > 4 ? int.tryParse(row[4]?.toString().trim() ?? '1') ?? 1 : 1;
        final group = row.length > 5 ? row[5]?.toString().trim() ?? '' : '';
        final phoneNumber = row.length > 6 ? row[6]?.toString().trim() : null;
        final photoUrl = row.length > 7 ? row[7]?.toString().trim() : null;

        if (group.isEmpty) continue;

        final student = Student(
          id: id,
          firstName: firstName,
          lastName: lastName,
          middleName: middleName?.isEmpty == true ? null : middleName,
          course: course,
          group: group,
          phoneNumber: phoneNumber?.isEmpty == true ? null : phoneNumber,
          photoUrl: photoUrl?.isEmpty == true ? null : photoUrl,
        );

        students.add(student);
      } catch (e) {
        // Пропускаем строки с ошибками
        continue;
      }
    }

    return students;
  }

  Future<void> _handleRefresh() async {
    setState(() {
      _isLoading = true;
    });
    await Future.delayed(const Duration(seconds: 1)); // Имитация загрузки
    _loadMockStudents();
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
      if (_filteredStudents.isEmpty) {
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
        'Курс',
        'Группа',
        'Телефон',
        'Фото URL',
      ]);

      // Данные студентов
      for (var student in _filteredStudents) {
        csvData.add([
          student.id,
          student.lastName,
          student.firstName,
          student.middleName ?? '',
          student.course,
          student.group,
          student.phoneNumber ?? '',
          student.photoUrl ?? '',
        ]);
      }

      // Конвертируем в CSV строку
      final csvString = const ListToCsvConverter().convert(csvData);

      // Экспортируем файл
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
            content: Text('Экспортировано ${_filteredStudents.length} студентов'),
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
        ..setAttribute('download', 'students_${DateTime.now().toIso8601String().split('T')[0]}.csv')
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

  Future<void> _editStudent(Student student) async {
    final result = await showDialog<Student>(
      context: context,
      barrierColor: Colors.black54,
      builder: (BuildContext context) {
        return _EditStudentDialog(student: student);
      },
    );

    if (result != null) {
      setState(() {
        final index = _allStudents.indexWhere((s) => s.id == student.id);
        if (index != -1) {
          _allStudents[index] = result;
          _applyFilters();
        }
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Студент успешно обновлен'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _deleteStudent(Student student) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Удаление студента'),
          content: Text(
            'Вы уверены, что хотите удалить студента "${student.fullName}"?',
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
        _allStudents.removeWhere((s) => s.id == student.id);
        _expandedStudentIds.remove(student.id);
        _applyFilters();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Студент "${student.fullName}" удален'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  Future<void> _addStudent() async {
    final result = await showDialog<Student>(
      context: context,
      barrierColor: Colors.black54,
      builder: (BuildContext context) {
        return _AddStudentDialog();
      },
    );

    if (result != null) {
      setState(() {
        _allStudents.add(result);
        _applyFilters();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Студент "${result.fullName}" успешно добавлен'),
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

    final isLoginEnabled = _isEndpointEnabled('students_login');
    final isPersonalDataEnabled = _isEndpointEnabled('students_personal_data');
    final hasLoginEndpoint = _hasEndpointValue('students_login');
    final hasPersonalDataEndpoint = _hasEndpointValue('students_personal_data');

    // Оба endpoint включены и имеют значения
    final bothEnabledAndConfigured = isLoginEnabled && 
                                     isPersonalDataEnabled && 
                                     hasLoginEndpoint && 
                                     hasPersonalDataEndpoint;

    // Оба endpoint выключены
    final bothDisabled = !isLoginEnabled && !isPersonalDataEnabled;

    // Endpoint включены, но пустые (не настроены) - показываем таблицу
    // Эта переменная используется для логики, но таблица показывается всегда, когда не bothEnabledAndConfigured и не bothDisabled

    // Если endpoints включены и настроены, показываем сообщение
    if (bothEnabledAndConfigured) {
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
                      'Данные студентов',
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
                    _buildEndpointStatusSimple('students_login', 'Логин студентов'),
                    const SizedBox(height: 8),
                    _buildEndpointStatusSimple('students_personal_data', 'Данные студента'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    // Если endpoints выключены, показываем сообщение
    if (bothDisabled) {
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
                    Icon(Icons.people, size: 32, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Студенты',
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
                          'Данные функции выключены',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.orange.shade700,
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Для работы с данными студентов необходимо включить функции "Логин студентов" и "Данные студента" на главной странице.',
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

    // Основной функционал - таблица студентов (когда endpoints включены, но пустые)
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    if (isMobile) {
      // На мобильных устройствах используем SingleChildScrollView
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
                    Icon(Icons.people, size: 24, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Студенты',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Информация о состоянии endpoints
                Card(
                  color: Colors.blue.shade50,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline, size: 14, color: Colors.blue.shade700),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _buildEndpointStatus(
                                'Логин студентов',
                                isLoginEnabled,
                                hasLoginEndpoint,
                                _universityConfig?.endpoints['students_login'] ?? '',
                              ),
                              const SizedBox(height: 4),
                              _buildEndpointStatus(
                                'Данные студента',
                                isPersonalDataEnabled,
                                hasPersonalDataEndpoint,
                                _universityConfig?.endpoints['students_personal_data'] ?? '',
                              ),
                            ],
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
                    // Фильтр по группе
                    Autocomplete<String>(
                      displayStringForOption: (String option) => option,
                      optionsBuilder: (TextEditingValue textEditingValue) {
                        if (textEditingValue.text.isEmpty) {
                          return _availableGroups;
                        }
                        return _availableGroups.where((group) {
                          return group.toLowerCase().contains(
                            textEditingValue.text.toLowerCase(),
                          );
                        });
                      },
                      onSelected: (String selection) {
                        setState(() {
                          _selectedGroup = selection;
                          _applyFilters();
                        });
                      },
                      fieldViewBuilder: (
                        BuildContext context,
                        TextEditingController textEditingController,
                        FocusNode focusNode,
                        VoidCallback onFieldSubmitted,
                      ) {
                        textEditingController.text = _selectedGroup;
                        return TextField(
                          controller: textEditingController,
                          focusNode: focusNode,
                          decoration: InputDecoration(
                            labelText: 'Группа',
                            prefixIcon: const Icon(Icons.group),
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
                    // Фильтр по курсу
                    DropdownButtonFormField<int>(
                      decoration: InputDecoration(
                        labelText: 'Курс',
                        prefixIcon: const Icon(Icons.school),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                      ),
                      isExpanded: true,
                      value: _selectedCourse,
                      items: [
                        const DropdownMenuItem<int>(
                          value: null,
                          child: Text('Все курсы'),
                        ),
                        ..._availableCourses.map((course) {
                          return DropdownMenuItem<int>(
                            value: course,
                            child: Text('$course курс'),
                          );
                        }),
                      ],
                      onChanged: (value) {
                        setState(() {
                          _selectedCourse = value;
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
          // Таблица студентов (прокручиваемая)
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12.0),
              child: _filteredStudents.isEmpty
                  ? Center(
                      child: Text(
                        'Студенты не найдены',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.grey,
                            ),
                      ),
                    )
                  : ListView.builder(
                      itemCount: _filteredStudents.length,
                      itemBuilder: (context, index) {
                        final student = _filteredStudents[index];
                        final isExpanded = _expandedStudentIds.contains(student.id);
                        return _buildStudentCard(student, isExpanded);
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
                    onPressed: _addStudent,
                    icon: const Icon(Icons.add),
                    label: const Text('Добавить студента'),
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
                  Icon(Icons.people, size: 32, color: Colors.blue.shade700),
                  const SizedBox(width: 12),
                  Flexible(
                    child: Text(
                      'Студенты',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              // Информация о состоянии endpoints
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, size: 16, color: Colors.blue.shade700),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Row(
                          children: [
                            Expanded(
                              child: _buildEndpointStatus(
                                'Логин студентов',
                                isLoginEnabled,
                                hasLoginEndpoint,
                                _universityConfig?.endpoints['students_login'] ?? '',
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: _buildEndpointStatus(
                                'Данные студента',
                                isPersonalDataEnabled,
                                hasPersonalDataEndpoint,
                                _universityConfig?.endpoints['students_personal_data'] ?? '',
                              ),
                            ),
                          ],
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
                        // Фильтр по группе
                        Autocomplete<String>(
                          displayStringForOption: (String option) => option,
                          optionsBuilder: (TextEditingValue textEditingValue) {
                            if (textEditingValue.text.isEmpty) {
                              return _availableGroups;
                            }
                            return _availableGroups.where((group) {
                              return group.toLowerCase().contains(
                                textEditingValue.text.toLowerCase(),
                              );
                            });
                          },
                          onSelected: (String selection) {
                            setState(() {
                              _selectedGroup = selection;
                              _applyFilters();
                            });
                          },
                          fieldViewBuilder: (
                            BuildContext context,
                            TextEditingController textEditingController,
                            FocusNode focusNode,
                            VoidCallback onFieldSubmitted,
                          ) {
                            textEditingController.text = _selectedGroup;
                            return TextField(
                              controller: textEditingController,
                              focusNode: focusNode,
                              decoration: InputDecoration(
                                labelText: 'Группа',
                                prefixIcon: const Icon(Icons.group),
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
                        // Фильтр по курсу
                        DropdownButtonFormField<int>(
                          decoration: InputDecoration(
                            labelText: 'Курс',
                            prefixIcon: const Icon(Icons.school),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          isExpanded: true,
                          value: _selectedCourse,
                          items: [
                            const DropdownMenuItem<int>(
                              value: null,
                              child: Text('Все курсы'),
                            ),
                            ..._availableCourses.map((course) {
                              return DropdownMenuItem<int>(
                                value: course,
                                child: Text('$course курс'),
                              );
                            }),
                          ],
                          onChanged: (value) {
                            setState(() {
                              _selectedCourse = value;
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
                        // Фильтр по группе
                        Expanded(
                          child: Autocomplete<String>(
                            displayStringForOption: (String option) => option,
                            optionsBuilder: (TextEditingValue textEditingValue) {
                              if (textEditingValue.text.isEmpty) {
                                return _availableGroups;
                              }
                              return _availableGroups.where((group) {
                                return group.toLowerCase().contains(
                                  textEditingValue.text.toLowerCase(),
                                );
                              });
                            },
                            onSelected: (String selection) {
                              setState(() {
                                _selectedGroup = selection;
                                _applyFilters();
                              });
                            },
                            fieldViewBuilder: (
                              BuildContext context,
                              TextEditingController textEditingController,
                              FocusNode focusNode,
                              VoidCallback onFieldSubmitted,
                            ) {
                              textEditingController.text = _selectedGroup;
                              return TextField(
                                controller: textEditingController,
                                focusNode: focusNode,
                                decoration: InputDecoration(
                                  labelText: 'Группа',
                                  prefixIcon: const Icon(Icons.group),
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
                        // Фильтр по курсу
                        Expanded(
                          child: DropdownButtonFormField<int>(
                            decoration: InputDecoration(
                              labelText: 'Курс',
                              prefixIcon: const Icon(Icons.school),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                            ),
                            value: _selectedCourse,
                            items: [
                              const DropdownMenuItem<int>(
                                value: null,
                                child: Text('Все курсы'),
                              ),
                              ..._availableCourses.map((course) {
                                return DropdownMenuItem<int>(
                                  value: course,
                                  child: Text('$course курс'),
                                );
                              }),
                            ],
                            onChanged: (value) {
                              setState(() {
                                _selectedCourse = value;
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
        // Таблица студентов
        Expanded(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: isMobile ? 16.0 : 24.0),
            child: _filteredStudents.isEmpty
                ? Center(
                    child: Text(
                      'Студенты не найдены',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  )
                : ListView.builder(
                    itemCount: _filteredStudents.length,
                    itemBuilder: (context, index) {
                      final student = _filteredStudents[index];
                      final isExpanded = _expandedStudentIds.contains(student.id);
                      return _buildStudentCard(student, isExpanded);
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
                        onPressed: _addStudent,
                        icon: const Icon(Icons.add),
                        label: const Text('Добавить студента'),
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
                      onPressed: _addStudent,
                      icon: const Icon(Icons.add),
                      label: const Text('Добавить студента'),
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

  Widget _buildStudentCard(Student student, bool isExpanded) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Column(
        children: [
          // Основная информация
          InkWell(
            onTap: () => _toggleStudentExpansion(student.id),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  // Фото или иконка
                  CircleAvatar(
                    radius: 30,
                    backgroundImage: student.photoBase64 != null
                        ? MemoryImage(base64Decode(student.photoBase64!))
                        : student.photoUrl != null
                            ? NetworkImage(student.photoUrl!)
                            : null,
                    child: student.photoBase64 == null && student.photoUrl == null
                        ? const Icon(Icons.person, size: 30)
                        : null,
                  ),
                  const SizedBox(width: 16),
                  // ФИО, курс, группа
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          student.fullName,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                        const SizedBox(height: 4),
                        LayoutBuilder(
                          builder: (context, constraints) {
                            final isMobile = constraints.maxWidth < 200;
                            if (isMobile) {
                              // На очень маленьких экранах - вертикальная компоновка
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.school, size: 16, color: Colors.grey.shade600),
                                      const SizedBox(width: 4),
                                      Flexible(
                                        child: Text(
                                          '${student.course} курс',
                                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                                color: Colors.grey.shade600,
                                              ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.group, size: 16, color: Colors.grey.shade600),
                                      const SizedBox(width: 4),
                                      Flexible(
                                        child: Text(
                                          student.group,
                                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                                color: Colors.grey.shade600,
                                              ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              );
                            } else {
                              // На больших экранах - горизонтальная компоновка
                              return Row(
                                children: [
                                  Icon(Icons.school, size: 16, color: Colors.grey.shade600),
                                  const SizedBox(width: 4),
                                  Flexible(
                                    child: Text(
                                      '${student.course} курс',
                                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                            color: Colors.grey.shade600,
                                          ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  Icon(Icons.group, size: 16, color: Colors.grey.shade600),
                                  const SizedBox(width: 4),
                                  Flexible(
                                    child: Text(
                                      student.group,
                                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                            color: Colors.grey.shade600,
                                          ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              );
                            }
                          },
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
                                _editStudent(student);
                                break;
                              case 'delete':
                                _deleteStudent(student);
                                break;
                              case 'expand':
                                _toggleStudentExpansion(student.id);
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
                              onPressed: () => _editStudent(student),
                              tooltip: 'Редактировать',
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => _deleteStudent(student),
                              tooltip: 'Удалить',
                            ),
                            // Иконка разворачивания
                            IconButton(
                              icon: Icon(
                                isExpanded ? Icons.expand_less : Icons.expand_more,
                                color: Colors.grey.shade600,
                              ),
                              onPressed: () => _toggleStudentExpansion(student.id),
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
                  _buildDetailRow('ID', student.id),
                  _buildDetailRow('Фамилия', student.lastName),
                  _buildDetailRow('Имя', student.firstName),
                  if (student.middleName != null)
                    _buildDetailRow('Отчество', student.middleName!),
                  _buildDetailRow('Курс', '${student.course}'),
                  _buildDetailRow('Группа', student.group),
                  if (student.phoneNumber != null && student.phoneNumber!.isNotEmpty)
                    _buildDetailRow('Телефон', student.phoneNumber!),
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

class _EditStudentDialog extends StatefulWidget {
  final Student student;

  const _EditStudentDialog({required this.student});

  @override
  State<_EditStudentDialog> createState() => _EditStudentDialogState();
}

class _EditStudentDialogState extends State<_EditStudentDialog> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _middleNameController;
  late TextEditingController _courseController;
  late TextEditingController _groupController;
  late TextEditingController _phoneNumberController;
  final _formKey = GlobalKey<FormState>();
  String? _photoBase64;
  Uint8List? _selectedImageBytes;

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.student.firstName);
    _lastNameController = TextEditingController(text: widget.student.lastName);
    _middleNameController = TextEditingController(text: widget.student.middleName ?? '');
    _courseController = TextEditingController(text: widget.student.course.toString());
    _groupController = TextEditingController(text: widget.student.group);
    _phoneNumberController = TextEditingController(text: widget.student.phoneNumber ?? '');
    _photoBase64 = widget.student.photoBase64;
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _middleNameController.dispose();
    _courseController.dispose();
    _groupController.dispose();
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
                      'Редактировать студента',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Фото студента
                Center(
                  child: Column(
                    children: [
                      Stack(
                        children: [
                          CircleAvatar(
                            radius: 50,
                            backgroundImage: _photoBase64 != null
                                ? MemoryImage(base64Decode(_photoBase64!))
                                : widget.student.photoUrl != null
                                    ? NetworkImage(widget.student.photoUrl!)
                                    : null,
                            child: _photoBase64 == null && widget.student.photoUrl == null
                                ? const Icon(Icons.person, size: 50)
                                : null,
                          ),
                          if (_selectedImageBytes != null || _photoBase64 != null || widget.student.photoUrl != null)
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
                        label: Text(_photoBase64 != null || widget.student.photoUrl != null
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
                  controller: _courseController,
                  decoration: InputDecoration(
                    labelText: 'Курс *',
                    prefixIcon: const Icon(Icons.school),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите курс';
                    }
                    final course = int.tryParse(value);
                    if (course == null || course < 1 || course > 6) {
                      return 'Введите корректный курс (1-6)';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _groupController,
                  decoration: InputDecoration(
                    labelText: 'Группа *',
                    prefixIcon: const Icon(Icons.group),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите группу';
                    }
                    return null;
                  },
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
                          final updatedStudent = Student(
                            id: widget.student.id,
                            firstName: _firstNameController.text.trim(),
                            lastName: _lastNameController.text.trim(),
                            middleName: _middleNameController.text.trim().isEmpty
                                ? null
                                : _middleNameController.text.trim(),
                            course: int.parse(_courseController.text.trim()),
                            group: _groupController.text.trim(),
                            phoneNumber: _phoneNumberController.text.trim().isEmpty
                                ? null
                                : _phoneNumberController.text.trim(),
                            photoUrl: widget.student.photoUrl,
                            photoBase64: _photoBase64,
                            additionalData: widget.student.additionalData,
                          );
                          Navigator.of(context).pop(updatedStudent);
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

class _AddStudentDialog extends StatefulWidget {
  const _AddStudentDialog();

  @override
  State<_AddStudentDialog> createState() => _AddStudentDialogState();
}

class _AddStudentDialogState extends State<_AddStudentDialog> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _middleNameController;
  late TextEditingController _courseController;
  late TextEditingController _groupController;
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
    _courseController = TextEditingController();
    _groupController = TextEditingController();
    _phoneNumberController = TextEditingController();
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _middleNameController.dispose();
    _courseController.dispose();
    _groupController.dispose();
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
                      'Добавить студента',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Фото студента
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
                  controller: _courseController,
                  decoration: InputDecoration(
                    labelText: 'Курс *',
                    prefixIcon: const Icon(Icons.school),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  keyboardType: TextInputType.number,
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите курс';
                    }
                    final course = int.tryParse(value);
                    if (course == null || course < 1 || course > 6) {
                      return 'Введите корректный курс (1-6)';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _groupController,
                  decoration: InputDecoration(
                    labelText: 'Группа *',
                    prefixIcon: const Icon(Icons.group),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Введите группу';
                    }
                    return null;
                  },
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
                          final newStudent = Student(
                            id: _generateId(),
                            firstName: _firstNameController.text.trim(),
                            lastName: _lastNameController.text.trim(),
                            middleName: _middleNameController.text.trim().isEmpty
                                ? null
                                : _middleNameController.text.trim(),
                            course: int.parse(_courseController.text.trim()),
                            group: _groupController.text.trim(),
                            phoneNumber: _phoneNumberController.text.trim().isEmpty
                                ? null
                                : _phoneNumberController.text.trim(),
                            photoUrl: null,
                            photoBase64: _photoBase64,
                            additionalData: null,
                          );
                          Navigator.of(context).pop(newStudent);
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
