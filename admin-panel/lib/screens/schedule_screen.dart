import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:file_picker/file_picker.dart';
import 'package:csv/csv.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:convert';
import '../models/schedule_event.dart';
import '../services/api_service.dart';
import '../models/university_config.dart';
import 'event_dialog.dart';

// Условный импорт для веб-платформы
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html if (dart.library.html) 'dart:html';

String _formatDate(DateTime date) {
  return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year}';
}

enum CalendarViewMode { threeDays, week, month }

class ScheduleScreen extends StatefulWidget {
  final int? universityId;
  final String? featureId;
  final VoidCallback? onCsvUploaded;
  final VoidCallback? onDataChanged; // Callback при изменении данных
  
  const ScheduleScreen({
    super.key,
    this.universityId,
    this.featureId,
    this.onCsvUploaded,
    this.onDataChanged,
  });

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  final _apiService = ApiService();
  UniversityConfig? _universityConfig;
  bool _isLoading = true;
  
  CalendarViewMode _viewMode = CalendarViewMode.week;
  DateTime _focusedDay = DateTime.now();
  DateTime _selectedDay = DateTime.now();
  CalendarFormat _calendarFormat = CalendarFormat.week;
  
  List<ScheduleEvent> _allEvents = [];
  Map<DateTime, List<ScheduleEvent>> _eventsMap = {};
  
  // Публичный метод для получения данных для CSV
  List<Map<String, dynamic>> getScheduleDataForCsv() {
    return _allEvents.map((event) => {
      'title': event.title,
      'date': _formatDate(event.startTime),
      'startTime': '${event.startTime.hour.toString().padLeft(2, '0')}:${event.startTime.minute.toString().padLeft(2, '0')}',
      'endTime': '${event.endTime.hour.toString().padLeft(2, '0')}:${event.endTime.minute.toString().padLeft(2, '0')}',
      'description': event.description ?? '',
      'location': event.location ?? '',
      'subject': event.subject ?? '',
      'groupId': event.groupId ?? '',
    }).toList();
  }

  @override
  void initState() {
    super.initState();
    _loadConfig();
    _loadMockEvents();
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
      }
    }
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

  Widget _buildEndpointStatus(String endpointId, String endpointName) {
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
          Text(
            '$endpointName: $statusText',
            style: TextStyle(
              fontSize: 12,
              color: statusColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  void _loadMockEvents() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    
    _allEvents = [
      ScheduleEvent(
        id: '1',
        title: 'Математика',
        description: 'Лекция по математическому анализу',
        startTime: today.add(const Duration(hours: 9)),
        endTime: today.add(const Duration(hours: 10, minutes: 30)),
        location: 'Аудитория 101',
        subject: 'Математика',
        groupId: 'ИВТ-21',
      ),
      ScheduleEvent(
        id: '2',
        title: 'Программирование',
        description: 'Практическое занятие',
        startTime: today.add(const Duration(hours: 11)),
        endTime: today.add(const Duration(hours: 12, minutes: 30)),
        location: 'Аудитория 205',
        subject: 'Программирование',
        groupId: 'ИВТ-21',
      ),
      ScheduleEvent(
        id: '3',
        title: 'Физика',
        description: 'Лабораторная работа',
        startTime: today.add(const Duration(days: 1, hours: 10)),
        endTime: today.add(const Duration(days: 1, hours: 11, minutes: 30)),
        location: 'Лаборатория 301',
        subject: 'Физика',
        groupId: 'ИВТ-21',
      ),
      ScheduleEvent(
        id: '4',
        title: 'Английский язык',
        description: 'Практика разговорной речи',
        startTime: today.add(const Duration(days: 2, hours: 14)),
        endTime: today.add(const Duration(days: 2, hours: 15, minutes: 30)),
        location: 'Аудитория 402',
        subject: 'Английский язык',
        groupId: 'ИВТ-21',
      ),
    ];
    
    _updateEventsMap();
  }

  void _updateEventsMap() {
    _eventsMap = {};
    for (var event in _allEvents) {
      final date = DateTime(event.startTime.year, event.startTime.month, event.startTime.day);
      if (_eventsMap[date] == null) {
        _eventsMap[date] = [];
      }
      _eventsMap[date]!.add(event);
    }
  }

  List<ScheduleEvent> _getEventsForDay(DateTime day) {
    final date = DateTime(day.year, day.month, day.day);
    return _eventsMap[date] ?? [];
  }

  List<ScheduleEvent> _getEventsForRange(DateTime start, DateTime end) {
    final events = <ScheduleEvent>[];
    for (var event in _allEvents) {
      if (event.startTime.isAfter(start.subtract(const Duration(days: 1))) &&
          event.startTime.isBefore(end.add(const Duration(days: 1)))) {
        events.add(event);
      }
    }
    events.sort((a, b) => a.startTime.compareTo(b.startTime));
    return events;
  }

  void _onViewModeChanged(CalendarViewMode mode) {
    setState(() {
      _viewMode = mode;
      switch (mode) {
        case CalendarViewMode.threeDays:
          _calendarFormat = CalendarFormat.week;
          break;
        case CalendarViewMode.week:
          _calendarFormat = CalendarFormat.week;
          break;
        case CalendarViewMode.month:
          _calendarFormat = CalendarFormat.month;
          break;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // Проверяем состояние endpoint расписания
    final isScheduleEnabled = _isEndpointEnabled('students_schedule');
    final hasScheduleEndpoint = _hasEndpointValue('students_schedule');

    // Endpoint включен и настроен - показываем сообщение
    if (isScheduleEnabled && hasScheduleEndpoint) {
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
                      'Данные расписания',
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
                    _buildEndpointStatus('students_schedule', 'Расписание'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    // Endpoint выключен - показываем сообщение
    if (!isScheduleEnabled) {
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
                      Icons.calendar_today_outlined,
                      size: 64,
                      color: Colors.grey.shade400,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Функция расписания выключена',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Включите функцию расписания в настройках, чтобы управлять расписанием',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    _buildEndpointStatus('students_schedule', 'Расписание'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    // Endpoint включен, но пустой - показываем календарь для управления
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    return Column(
      children: [
        // Заголовок и переключатель режима
        Padding(
          padding: EdgeInsets.all(isMobile ? 12.0 : 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (isMobile) ...[
                // На мобильных - вертикальная компоновка
                Row(
                  children: [
                    Icon(Icons.calendar_today, size: 24, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Flexible(
                      child: Text(
                        'Расписание',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                // Переключатель режима просмотра
                SegmentedButton<CalendarViewMode>(
                  segments: const [
                    ButtonSegment<CalendarViewMode>(
                      value: CalendarViewMode.threeDays,
                      label: Text('3 дня'),
                      icon: Icon(Icons.view_day),
                    ),
                    ButtonSegment<CalendarViewMode>(
                      value: CalendarViewMode.week,
                      label: Text('Неделя'),
                      icon: Icon(Icons.view_week),
                    ),
                    ButtonSegment<CalendarViewMode>(
                      value: CalendarViewMode.month,
                      label: Text('Месяц'),
                      icon: Icon(Icons.view_module),
                    ),
                  ],
                  selected: {_viewMode},
                  onSelectionChanged: (Set<CalendarViewMode> newSelection) {
                    _onViewModeChanged(newSelection.first);
                  },
                ),
                const SizedBox(height: 12),
                // Кнопка добавления события
                Row(
                  children: [
                    Expanded(
                      child: FloatingActionButton.extended(
                        onPressed: () => _addEvent(),
                        icon: const Icon(Icons.add),
                        label: const Text('Добавить событие'),
                        backgroundColor: Colors.blue.shade700,
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Выпадающее меню для CSV операций
                    PopupMenuButton<String>(
                      icon: const Icon(Icons.more_vert),
                      onSelected: (value) {
                        if (value == 'upload') {
                          _showCsvUploadDialog();
                        } else if (value == 'export') {
                          _exportToCsv();
                        }
                      },
                      itemBuilder: (BuildContext context) => [
                        const PopupMenuItem<String>(
                          value: 'upload',
                          child: Row(
                            children: [
                              Icon(Icons.upload_file, size: 20),
                              SizedBox(width: 8),
                              Text('Загрузить CSV'),
                            ],
                          ),
                        ),
                        const PopupMenuItem<String>(
                          value: 'export',
                          child: Row(
                            children: [
                              Icon(Icons.download, size: 20),
                              SizedBox(width: 8),
                              Text('Экспорт CSV'),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ] else ...[
                // На десктопе - горизонтальная компоновка
                Row(
                  children: [
                    Icon(Icons.calendar_today, size: 32, color: Colors.blue.shade700),
                    const SizedBox(width: 12),
                    Text(
                      'Расписание',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const Spacer(),
                    // Переключатель режима просмотра
                    SegmentedButton<CalendarViewMode>(
                      segments: const [
                        ButtonSegment<CalendarViewMode>(
                          value: CalendarViewMode.threeDays,
                          label: Text('3 дня'),
                          icon: Icon(Icons.view_day),
                        ),
                        ButtonSegment<CalendarViewMode>(
                          value: CalendarViewMode.week,
                          label: Text('Неделя'),
                          icon: Icon(Icons.view_week),
                        ),
                        ButtonSegment<CalendarViewMode>(
                          value: CalendarViewMode.month,
                          label: Text('Месяц'),
                          icon: Icon(Icons.view_module),
                        ),
                      ],
                      selected: {_viewMode},
                      onSelectionChanged: (Set<CalendarViewMode> newSelection) {
                        _onViewModeChanged(newSelection.first);
                      },
                    ),
                    const SizedBox(width: 12),
                    // Кнопка добавления события
                    FloatingActionButton.extended(
                      onPressed: () => _addEvent(),
                      icon: const Icon(Icons.add),
                      label: const Text('Добавить событие'),
                      backgroundColor: Colors.blue.shade700,
                    ),
                    const SizedBox(width: 8),
                    // Выпадающее меню для CSV операций
                    PopupMenuButton<String>(
                      icon: const Icon(Icons.more_vert),
                      onSelected: (value) {
                        if (value == 'upload') {
                          _showCsvUploadDialog();
                        } else if (value == 'export') {
                          _exportToCsv();
                        }
                      },
                      itemBuilder: (BuildContext context) => [
                        const PopupMenuItem<String>(
                          value: 'upload',
                          child: Row(
                            children: [
                              Icon(Icons.upload_file, size: 20),
                              SizedBox(width: 8),
                              Text('Загрузить CSV'),
                            ],
                          ),
                        ),
                        const PopupMenuItem<String>(
                          value: 'export',
                          child: Row(
                            children: [
                              Icon(Icons.download, size: 20),
                              SizedBox(width: 8),
                              Text('Экспорт CSV'),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 12),
              // Статус endpoint
              _buildEndpointStatus('students_schedule', 'Расписание'),
            ],
          ),
        ),
        // Календарь и события
        Expanded(
          child: _viewMode == CalendarViewMode.month
              ? Row(
                  children: [
                    // Календарь
                    Expanded(
                      flex: 1,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24.0),
                        child: Card(
                      child: DragTarget<ScheduleEvent>(
                        onAccept: (event) {
                          _moveEventToDate(event, _selectedDay);
                        },
                        builder: (context, candidateData, rejectedData) {
                          return TableCalendar<ScheduleEvent>(
                            firstDay: DateTime.utc(2020, 1, 1),
                            lastDay: DateTime.utc(2030, 12, 31),
                            focusedDay: _focusedDay,
                            selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                            calendarFormat: _calendarFormat,
                            eventLoader: _getEventsForDay,
                            startingDayOfWeek: StartingDayOfWeek.monday,
                            calendarStyle: CalendarStyle(
                              outsideDaysVisible: false,
                              todayDecoration: BoxDecoration(
                                color: Colors.blue.shade200,
                                shape: BoxShape.circle,
                              ),
                              selectedDecoration: BoxDecoration(
                                color: Colors.blue.shade700,
                                shape: BoxShape.circle,
                              ),
                              markerDecoration: BoxDecoration(
                                color: Colors.blue.shade700,
                                shape: BoxShape.circle,
                              ),
                            ),
                            headerStyle: HeaderStyle(
                              formatButtonVisible: false,
                              titleCentered: true,
                            ),
                            onDaySelected: (selectedDay, focusedDay) {
                              setState(() {
                                _selectedDay = selectedDay;
                                _focusedDay = focusedDay;
                              });
                            },
                            onPageChanged: (focusedDay) {
                              setState(() {
                                _focusedDay = focusedDay;
                              });
                            },
                          );
                        },
                      ),
                        ),
                      ),
                    ),
                    // Список событий
                    Expanded(
                      flex: 1,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24.0),
                        child: _buildEventsList(),
                      ),
                    ),
                  ],
                )
              : Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  child: _buildEventsList(),
                ),
        ),
      ],
    );
  }

  Widget _buildEventsList() {
    List<ScheduleEvent> events;
    DateTime startDate;
    DateTime endDate;

    switch (_viewMode) {
      case CalendarViewMode.threeDays:
        startDate = _selectedDay;
        endDate = _selectedDay.add(const Duration(days: 3));
        events = _getEventsForRange(startDate, endDate);
        break;
      case CalendarViewMode.week:
        // Начало недели (понедельник)
        startDate = _selectedDay.subtract(Duration(days: _selectedDay.weekday - 1));
        endDate = startDate.add(const Duration(days: 7));
        events = _getEventsForRange(startDate, endDate);
        break;
      case CalendarViewMode.month:
        events = _getEventsForDay(_selectedDay);
        break;
    }

    if (events.isEmpty) {
      return Center(
        child: Text(
          'Нет событий в выбранном периоде',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Colors.grey,
              ),
        ),
      );
    }

    return ListView.builder(
      itemCount: events.length,
      itemBuilder: (context, index) {
        final event = events[index];
        return DragTarget<ScheduleEvent>(
          onAccept: (draggedEvent) {
            if (draggedEvent.id != event.id) {
              _moveEventToDate(draggedEvent, _selectedDay);
            }
          },
          builder: (context, candidateData, rejectedData) {
            return _buildEventCard(event);
          },
        );
      },
    );
  }

  void _moveEventToDate(ScheduleEvent event, DateTime newDate) {
    final timeDiff = event.endTime.difference(event.startTime);
    final newStartTime = DateTime(
      newDate.year,
      newDate.month,
      newDate.day,
      event.startTime.hour,
      event.startTime.minute,
    );
    final newEndTime = newStartTime.add(timeDiff);

    setState(() {
      final index = _allEvents.indexWhere((e) => e.id == event.id);
      if (index != -1) {
        _allEvents[index] = event.copyWith(
          startTime: newStartTime,
          endTime: newEndTime,
        );
        _updateEventsMap();
      }
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Событие "${event.title}" перенесено на ${_formatDate(newDate)}'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  Widget _buildEventCard(ScheduleEvent event) {
    return Draggable<ScheduleEvent>(
      data: event,
      feedback: Material(
        elevation: 6,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 300,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.blue.shade100,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            event.title,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
      ),
      childWhenDragging: Opacity(
        opacity: 0.3,
        child: Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${event.startTime.hour.toString().padLeft(2, '0')}:${event.startTime.minute.toString().padLeft(2, '0')}',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue.shade700,
                        ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    event.title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      child: Card(
        margin: const EdgeInsets.only(bottom: 12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Время
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Text(
                      '${event.startTime.hour.toString().padLeft(2, '0')}:${event.startTime.minute.toString().padLeft(2, '0')}',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue.shade700,
                          ),
                    ),
                    Text(
                      '${event.endTime.hour.toString().padLeft(2, '0')}:${event.endTime.minute.toString().padLeft(2, '0')}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.blue.shade600,
                          ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              // Информация о событии
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      event.title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    if (event.description != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        event.description!,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.grey.shade600,
                            ),
                      ),
                    ],
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 16,
                      runSpacing: 8,
                      children: [
                        if (event.location != null)
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.location_on, size: 16, color: Colors.grey.shade600),
                              const SizedBox(width: 4),
                              Text(
                                event.location!,
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Colors.grey.shade600,
                                    ),
                              ),
                            ],
                          ),
                        if (event.groupId != null)
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.group, size: 16, color: Colors.grey.shade600),
                              const SizedBox(width: 4),
                              Text(
                                event.groupId!,
                                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: Colors.grey.shade600,
                                    ),
                              ),
                            ],
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              // Кнопки действий
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit, color: Colors.blue),
                    onPressed: () => _editEvent(event),
                    tooltip: 'Редактировать',
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, color: Colors.red),
                    onPressed: () => _deleteEvent(event),
                    tooltip: 'Удалить',
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _addEvent() async {
    final result = await showDialog<ScheduleEvent>(
      context: context,
      builder: (context) => EventDialog(selectedDate: _selectedDay),
    );

    if (result != null) {
      setState(() {
        _allEvents.add(result);
        _updateEventsMap();
        // Уведомляем об изменениях данных, если endpoint пустой
        widget.onDataChanged?.call();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Событие "${result.title}" добавлено'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _editEvent(ScheduleEvent event) async {
    final result = await showDialog<ScheduleEvent>(
      context: context,
      builder: (context) => EventDialog(event: event),
    );

    if (result != null) {
      setState(() {
        final index = _allEvents.indexWhere((e) => e.id == event.id);
        if (index != -1) {
          _allEvents[index] = result;
          _updateEventsMap();
          // Уведомляем об изменениях данных, если endpoint пустой
          widget.onDataChanged?.call();
        }
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Событие "${result.title}" обновлено'),
            backgroundColor: Colors.blue,
          ),
        );
      }
    }
  }

  Future<void> _deleteEvent(ScheduleEvent event) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Удаление события'),
        content: Text('Вы уверены, что хотите удалить событие "${event.title}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Отмена'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Удалить'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      setState(() {
        _allEvents.removeWhere((e) => e.id == event.id);
        _updateEventsMap();
        // Уведомляем об изменениях данных, если endpoint пустой
        widget.onDataChanged?.call();
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Событие "${event.title}" удалено'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  void _showCsvUploadDialog() {
    showDialog(
      context: context,
      barrierColor: Colors.black54,
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
                  'Выберите CSV файл с расписанием',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                ),
                const SizedBox(height: 24),
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
                Text('Найдено событий: ${csvData.length - 1}'), // -1 для заголовка
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

        // Парсим события из CSV
        final events = _parseCsvToEvents(csvData);
        
        if (events.isEmpty) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Не удалось распарсить события из CSV файла'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        setState(() {
          if (action == 'replace') {
            _allEvents = events;
          } else {
            _allEvents.addAll(events);
          }
          _updateEventsMap();
          // Уведомляем об изменениях данных, если endpoint пустой
          widget.onDataChanged?.call();
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                action == 'replace'
                    ? 'Расписание заменено. Добавлено событий: ${events.length}'
                    : 'Добавлено событий: ${events.length}',
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

  List<ScheduleEvent> _parseCsvToEvents(List<List<dynamic>> csvData) {
    if (csvData.length < 2) return [];

    final events = <ScheduleEvent>[];
    
    // Пропускаем заголовок (первую строку)
    for (int i = 1; i < csvData.length; i++) {
      final row = csvData[i];
      if (row.length < 4) continue; // Минимум: Название, Дата, Время начала, Время окончания

      try {
        // Формат CSV: Название, Дата (dd.MM.yyyy), Время начала (HH:mm), Время окончания (HH:mm), Описание, Место, Предмет, Группа
        final title = row[0]?.toString().trim() ?? '';
        if (title.isEmpty) continue;

        // Парсим дату
        final dateStr = row[1]?.toString().trim() ?? '';
        final dateParts = dateStr.split('.');
        if (dateParts.length != 3) continue;
        final day = int.parse(dateParts[0]);
        final month = int.parse(dateParts[1]);
        final year = int.parse(dateParts[2]);

        // Парсим время начала
        final startTimeStr = row[2]?.toString().trim() ?? '09:00';
        final startTimeParts = startTimeStr.split(':');
        final startHour = int.parse(startTimeParts[0]);
        final startMinute = startTimeParts.length > 1 ? int.parse(startTimeParts[1]) : 0;

        // Парсим время окончания
        final endTimeStr = row[3]?.toString().trim() ?? '10:30';
        final endTimeParts = endTimeStr.split(':');
        final endHour = int.parse(endTimeParts[0]);
        final endMinute = endTimeParts.length > 1 ? int.parse(endTimeParts[1]) : 0;

        final startTime = DateTime(year, month, day, startHour, startMinute);
        final endTime = DateTime(year, month, day, endHour, endMinute);

        // Опциональные поля
        final description = row.length > 4 ? row[4]?.toString().trim() : null;
        final location = row.length > 5 ? row[5]?.toString().trim() : null;
        final subject = row.length > 6 ? row[6]?.toString().trim() : null;
        final groupId = row.length > 7 ? row[7]?.toString().trim() : null;

        final event = ScheduleEvent(
          id: DateTime.now().millisecondsSinceEpoch.toString() + '_$i',
          title: title,
          description: description?.isEmpty == true ? null : description,
          startTime: startTime,
          endTime: endTime,
          location: location?.isEmpty == true ? null : location,
          subject: subject?.isEmpty == true ? null : subject,
          groupId: groupId?.isEmpty == true ? null : groupId,
        );

        events.add(event);
      } catch (e) {
        // Пропускаем строки с ошибками
        continue;
      }
    }

    return events;
  }

  Future<void> _exportToCsv() async {
    if (_allEvents.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Нет событий для экспорта'),
            backgroundColor: Colors.orange,
          ),
        );
      }
      return;
    }

    try {
      // Создаем CSV данные
      final List<List<dynamic>> csvData = [];
      
      // Заголовки
      csvData.add([
        'Название',
        'Дата',
        'Время начала',
        'Время окончания',
        'Описание',
        'Место',
        'Предмет',
        'Группа',
      ]);

      // Данные событий
      for (var event in _allEvents) {
        csvData.add([
          event.title,
          _formatDate(event.startTime),
          '${event.startTime.hour.toString().padLeft(2, '0')}:${event.startTime.minute.toString().padLeft(2, '0')}',
          '${event.endTime.hour.toString().padLeft(2, '0')}:${event.endTime.minute.toString().padLeft(2, '0')}',
          event.description ?? '',
          event.location ?? '',
          event.subject ?? '',
          event.groupId ?? '',
        ]);
      }

      // Конвертируем в CSV строку
      final csvString = const ListToCsvConverter().convert(csvData);

      // Экспортируем файл для скачивания (отправка на ghost-api происходит при сохранении)
      if (kIsWeb) {
        await _downloadCsvWeb(csvString);
      } else {
        await _downloadCsvOther(csvString);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Экспортировано событий: ${_allEvents.length}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка экспорта CSV: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _downloadCsvWeb(String csvString) async {
    if (kIsWeb) {
      // ignore: undefined_prefixed_name, deprecated_member_use
      final bytes = utf8.encode(csvString);
      // ignore: undefined_prefixed_name, deprecated_member_use
      final blob = html.Blob([bytes], 'text/csv;charset=utf-8');
      // ignore: undefined_prefixed_name, deprecated_member_use
      final url = html.Url.createObjectUrlFromBlob(blob);
      // ignore: undefined_prefixed_name, deprecated_member_use
      html.AnchorElement(href: url)
        ..setAttribute('download', 'schedule_${DateTime.now().toIso8601String().split('T')[0]}.csv')
        ..click();
      // ignore: undefined_prefixed_name, deprecated_member_use
      html.Url.revokeObjectUrl(url);
    }
  }

  Future<void> _downloadCsvOther(String csvString) async {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Экспорт CSV доступен только в веб-версии'),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }
}

