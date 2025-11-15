import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/university_config.dart';
import '../services/api_service.dart';

class NewsItem {
  final String id;
  String title;
  String content;
  DateTime date;
  String author;
  String category;
  String? imageUrl;
  String? link;

  NewsItem({
    required this.id,
    required this.title,
    required this.content,
    required this.date,
    required this.author,
    required this.category,
    this.imageUrl,
    this.link,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'date': DateFormat('dd.MM.yyyy').format(date),
      'author': author,
      'category': category,
      'image_url': imageUrl,
      'link': link,
    };
  }

  static NewsItem fromJson(Map<String, dynamic> json) {
    return NewsItem(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      date: DateFormat('dd.MM.yyyy').parse(json['date'] as String),
      author: json['author'] as String,
      category: json['category'] as String,
      imageUrl: json['image_url'] as String?,
      link: json['link'] as String?,
    );
  }
}

class NewsScreen extends StatefulWidget {
  final int? universityId;
  final String? featureId;
  final VoidCallback? onCsvUploaded;
  final VoidCallback? onDataChanged;

  const NewsScreen({
    super.key,
    this.universityId,
    this.featureId,
    this.onCsvUploaded,
    this.onDataChanged,
  });

  @override
  State<NewsScreen> createState() => _NewsScreenState();
}

class _NewsScreenState extends State<NewsScreen> {
  final _apiService = ApiService();
  UniversityConfig? _universityConfig;
  bool _isLoading = true;

  // Фильтры
  final _searchController = TextEditingController();
  String _selectedCategory = 'Все категории';

  // Данные новостей
  List<NewsItem> _allNews = [];
  List<NewsItem> _filteredNews = [];
  final Set<String> _expandedNewsIds = {};

  // Публичный метод для получения данных для CSV
  List<Map<String, dynamic>> getNewsDataForCsv() {
    return _allNews.map((news) => {
      'id': news.id,
      'title': news.title,
      'content': news.content,
      'date': DateFormat('dd.MM.yyyy').format(news.date),
      'author': news.author,
      'category': news.category,
      'image_url': news.imageUrl ?? '',
      'link': news.link ?? '',
    }).toList();
  }

  @override
  void initState() {
    super.initState();
    _loadConfig();
    _loadMockNews();
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

  void _loadMockNews() {
    // Mock данные для демонстрации
    _allNews = [
      NewsItem(
        id: 'news_1',
        title: 'Открытие нового учебного корпуса',
        content: 'Университет рад сообщить об открытии нового современного учебного корпуса, оснащенного передовым оборудованием.',
        date: DateTime.now().subtract(const Duration(days: 1)),
        author: 'Администрация университета',
        category: 'Общие новости',
        link: 'https://www.chuvsu.ru/news/1',
      ),
      NewsItem(
        id: 'news_2',
        title: 'Студенческая конференция по информационным технологиям',
        content: 'Приглашаем всех желающих принять участие в студенческой конференции, посвященной актуальным вопросам IT-индустрии.',
        date: DateTime.now().subtract(const Duration(days: 2)),
        author: 'Администрация университета',
        category: 'Учеба',
        link: 'https://www.chuvsu.ru/news/2',
      ),
      NewsItem(
        id: 'news_3',
        title: 'Награждение лучших студентов семестра',
        content: 'Состоялась торжественная церемония награждения студентов, показавших отличные результаты в учебе.',
        date: DateTime.now().subtract(const Duration(days: 3)),
        author: 'Администрация университета',
        category: 'События',
        link: 'https://www.chuvsu.ru/news/3',
      ),
    ];
    _applyFilters();
  }

  void _applyFilters() {
    setState(() {
      _filteredNews = _allNews.where((news) {
        // Фильтр по названию
        final searchQuery = _searchController.text.toLowerCase();
        if (searchQuery.isNotEmpty) {
          final title = news.title.toLowerCase();
          final content = news.content.toLowerCase();
          if (!title.contains(searchQuery) && !content.contains(searchQuery)) {
            return false;
          }
        }

        // Фильтр по категории
        if (_selectedCategory != 'Все категории' && news.category != _selectedCategory) {
          return false;
        }

        return true;
      }).toList();
    });
  }

  List<String> get _availableCategories {
    final categories = _allNews.map((n) => n.category).toSet().toList()..sort();
    return ['Все категории', ...categories];
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

  void _toggleNewsExpansion(String newsId) {
    setState(() {
      if (_expandedNewsIds.contains(newsId)) {
        _expandedNewsIds.remove(newsId);
      } else {
        _expandedNewsIds.add(newsId);
      }
    });
  }

  void _addNews() {
    _showNewsDialog();
  }

  void _editNews(NewsItem news) {
    _showNewsDialog(news: news);
  }

  void _deleteNews(NewsItem news) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Удалить новость?'),
          content: Text('Вы уверены, что хотите удалить новость "${news.title}"?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Отмена'),
            ),
            TextButton(
              onPressed: () {
                setState(() {
                  _allNews.removeWhere((n) => n.id == news.id);
                  _expandedNewsIds.remove(news.id);
                  _applyFilters();
                });
                Navigator.of(context).pop();
                if (widget.onDataChanged != null) {
                  widget.onDataChanged!();
                }
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Новость удалена'),
                    backgroundColor: Colors.green,
                  ),
                );
              },
              child: const Text('Удалить', style: TextStyle(color: Colors.red)),
            ),
          ],
        );
      },
    );
  }

  void _showNewsDialog({NewsItem? news}) {
    final isEditing = news != null;
    final titleController = TextEditingController(text: news?.title ?? '');
    final contentController = TextEditingController(text: news?.content ?? '');
    final authorController = TextEditingController(text: news?.author ?? 'Администрация университета');
    final categoryController = TextEditingController(text: news?.category ?? 'Общие новости');
    final imageUrlController = TextEditingController(text: news?.imageUrl ?? '');
    final linkController = TextEditingController(text: news?.link ?? '');
    DateTime selectedDate = news?.date ?? DateTime.now();
    String selectedCategory = news?.category ?? 'Общие новости';

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: Text(isEditing ? 'Редактировать новость' : 'Добавить новость'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: 'Заголовок *',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: contentController,
                      decoration: const InputDecoration(
                        labelText: 'Содержание *',
                        border: OutlineInputBorder(),
                      ),
                      maxLines: 4,
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: authorController,
                      decoration: const InputDecoration(
                        labelText: 'Автор *',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      value: selectedCategory,
                      decoration: const InputDecoration(
                        labelText: 'Категория *',
                        border: OutlineInputBorder(),
                      ),
                      items: ['Общие новости', 'Учеба', 'События', 'Спорт', 'Культура']
                          .map((category) => DropdownMenuItem(
                                value: category,
                                child: Text(category),
                              ))
                          .toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setDialogState(() {
                            selectedCategory = value;
                            categoryController.text = value;
                          });
                        }
                      },
                    ),
                    const SizedBox(height: 16),
                    ListTile(
                      title: const Text('Дата публикации'),
                      subtitle: Text(DateFormat('dd.MM.yyyy').format(selectedDate)),
                      trailing: const Icon(Icons.calendar_today),
                      onTap: () async {
                        final picked = await showDatePicker(
                          context: context,
                          initialDate: selectedDate,
                          firstDate: DateTime(2020),
                          lastDate: DateTime(2030),
                        );
                        if (picked != null) {
                          setDialogState(() {
                            selectedDate = picked;
                          });
                        }
                      },
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: imageUrlController,
                      decoration: const InputDecoration(
                        labelText: 'URL изображения',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: linkController,
                      decoration: const InputDecoration(
                        labelText: 'Ссылка на полную новость',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Отмена'),
                ),
                ElevatedButton(
                  onPressed: () {
                    if (titleController.text.trim().isEmpty ||
                        contentController.text.trim().isEmpty ||
                        authorController.text.trim().isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Заполните все обязательные поля'),
                          backgroundColor: Colors.red,
                        ),
                      );
                      return;
                    }

                    setState(() {
                      if (isEditing) {
                        final index = _allNews.indexWhere((n) => n.id == news!.id);
                        if (index != -1) {
                          _allNews[index] = NewsItem(
                            id: news!.id,
                            title: titleController.text.trim(),
                            content: contentController.text.trim(),
                            date: selectedDate,
                            author: authorController.text.trim(),
                            category: selectedCategory,
                            imageUrl: imageUrlController.text.trim().isEmpty
                                ? null
                                : imageUrlController.text.trim(),
                            link: linkController.text.trim().isEmpty
                                ? null
                                : linkController.text.trim(),
                          );
                        }
                      } else {
                        final newId = 'news_${DateTime.now().millisecondsSinceEpoch}';
                        _allNews.add(NewsItem(
                          id: newId,
                          title: titleController.text.trim(),
                          content: contentController.text.trim(),
                          date: selectedDate,
                          author: authorController.text.trim(),
                          category: selectedCategory,
                          imageUrl: imageUrlController.text.trim().isEmpty
                              ? null
                              : imageUrlController.text.trim(),
                          link: linkController.text.trim().isEmpty
                              ? null
                              : linkController.text.trim(),
                        ));
                      }
                      _applyFilters();
                    });
                    Navigator.of(context).pop();
                    if (widget.onDataChanged != null) {
                      widget.onDataChanged!();
                    }
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(isEditing ? 'Новость обновлена' : 'Новость добавлена'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  },
                  child: Text(isEditing ? 'Сохранить' : 'Добавить'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    final isNewsEnabled = _isEndpointEnabled('students_news');
    final hasNewsEndpoint = _hasEndpointValue('students_news');

    // Если endpoint включен и настроен, показываем сообщение
    if (isNewsEnabled && hasNewsEndpoint) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.article, size: 64, color: Colors.grey.shade400),
              const SizedBox(height: 16),
              Text(
                'Эндпоинт новостей настроен',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                'Новости загружаются автоматически с University API',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey.shade600,
                    ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    // Если endpoint выключен, показываем сообщение
    if (!isNewsEnabled) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.article_outlined, size: 64, color: Colors.grey.shade400),
              const SizedBox(height: 16),
              Text(
                'Эндпоинт новостей отключен',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                'Включите эндпоинт новостей на главной странице для использования',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey.shade600,
                    ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    // Endpoint включен, но пустой - показываем таблицу для ручного ввода
    return Scaffold(
      body: Column(
        children: [
          // Панель фильтров и поиска
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.shade200,
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Поиск по новостям...',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      filled: true,
                      fillColor: Colors.grey.shade50,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                DropdownButton<String>(
                  value: _selectedCategory,
                  items: _availableCategories.map((category) {
                    return DropdownMenuItem(
                      value: category,
                      child: Text(category),
                    );
                  }).toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _selectedCategory = value;
                        _applyFilters();
                      });
                    }
                  },
                ),
                const SizedBox(width: 16),
                ElevatedButton.icon(
                  onPressed: _addNews,
                  icon: const Icon(Icons.add),
                  label: const Text('Добавить новость'),
                ),
              ],
            ),
          ),
          // Список новостей
          Expanded(
            child: _filteredNews.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.article_outlined, size: 64, color: Colors.grey.shade400),
                        const SizedBox(height: 16),
                        Text(
                          'Новостей не найдено',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                color: Colors.grey.shade600,
                              ),
                        ),
                        const SizedBox(height: 8),
                        ElevatedButton.icon(
                          onPressed: _addNews,
                          icon: const Icon(Icons.add),
                          label: const Text('Добавить первую новость'),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _filteredNews.length,
                    itemBuilder: (context, index) {
                      final news = _filteredNews[index];
                      final isExpanded = _expandedNewsIds.contains(news.id);

                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ExpansionTile(
                          leading: Icon(
                            Icons.article,
                            color: Colors.blue.shade700,
                          ),
                          title: Text(
                            news.title,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(height: 4),
                              Text(
                                '${DateFormat('dd.MM.yyyy').format(news.date)} • ${news.category}',
                                style: TextStyle(
                                  color: Colors.grey.shade600,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.edit, size: 20),
                                onPressed: () => _editNews(news),
                                tooltip: 'Редактировать',
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete, size: 20, color: Colors.red),
                                onPressed: () => _deleteNews(news),
                                tooltip: 'Удалить',
                              ),
                            ],
                          ),
                          initiallyExpanded: isExpanded,
                          onExpansionChanged: (expanded) {
                            _toggleNewsExpansion(news.id);
                          },
                          children: [
                            Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    news.content,
                                    style: Theme.of(context).textTheme.bodyMedium,
                                  ),
                                  const SizedBox(height: 12),
                                  if (news.author.isNotEmpty)
                                    Text(
                                      'Автор: ${news.author}',
                                      style: TextStyle(
                                        color: Colors.grey.shade600,
                                        fontSize: 12,
                                      ),
                                    ),
                                  if (news.link != null && news.link!.isNotEmpty) ...[
                                    const SizedBox(height: 8),
                                    InkWell(
                                      onTap: () {
                                        // Открыть ссылку
                                      },
                                      child: Text(
                                        'Ссылка: ${news.link}',
                                        style: TextStyle(
                                          color: Colors.blue.shade700,
                                          fontSize: 12,
                                          decoration: TextDecoration.underline,
                                        ),
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}


