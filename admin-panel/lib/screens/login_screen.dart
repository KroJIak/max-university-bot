import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/university.dart';
import 'main_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _universityController = TextEditingController();
  final _apiService = ApiService();
  
  List<University> _universities = [];
  University? _selectedUniversity;
  bool _isLoading = false;
  bool _isLoadingUniversities = false;
  bool _obscurePassword = true;
  
  // Заглушка для отображения подсказки
  static final University _placeholderUniversity = University(id: -1, name: '_placeholder_');

  @override
  void initState() {
    super.initState();
    _loadUniversities();
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _universityController.dispose();
    super.dispose();
  }

  Future<void> _loadUniversities() async {
    setState(() {
      _isLoadingUniversities = true;
    });

    try {
      final universities = await _apiService.getUniversities();
      if (mounted) {
        setState(() {
          _universities = universities;
          _isLoadingUniversities = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingUniversities = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка загрузки университетов: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }


  Future<void> _showAddUniversityDialog(BuildContext parentContext) async {
    final nameController = TextEditingController();
    final formKey = GlobalKey<FormState>();
    bool isSaving = false;

    await showDialog(
      context: parentContext,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Добавить университет'),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: nameController,
                    decoration: InputDecoration(
                      labelText: 'Название университета',
                      hintText: 'Введите название',
                      prefixIcon: const Icon(Icons.school),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Введите название университета';
                      }
                      return null;
                    },
                    autofocus: true,
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: isSaving
                  ? null
                  : () {
                      Navigator.of(dialogContext).pop();
                    },
              child: const Text('Отмена'),
            ),
            ElevatedButton(
              onPressed: isSaving
                  ? null
                  : () async {
                      if (formKey.currentState!.validate()) {
                        setDialogState(() {
                          isSaving = true;
                        });

                        try {
                          final result = await _apiService.createUniversity(
                            nameController.text.trim(),
                          );

                          if (result['success'] == true) {
                            final newUniversity = result['university'] as University;
                            
                            // Обновляем список университетов
                            await _loadUniversities();
                            
                            // Выбираем новый университет
                            if (mounted) {
                              setState(() {
                                _selectedUniversity = newUniversity;
                              });
                            }

                            if (dialogContext.mounted) {
                              Navigator.of(dialogContext).pop();
                            }
                            
                            // Используем контекст из параметра метода
                            if (mounted && parentContext.mounted) {
                              ScaffoldMessenger.of(parentContext).showSnackBar(
                                SnackBar(
                                  content: Text('Университет "${newUniversity.name}" успешно добавлен'),
                                  backgroundColor: Colors.green,
                                ),
                              );
                            }
                          } else {
                            if (dialogContext.mounted) {
                              ScaffoldMessenger.of(dialogContext).showSnackBar(
                                SnackBar(
                                  content: Text(result['error'] ?? 'Ошибка создания университета'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          }
                        } catch (e) {
                          if (dialogContext.mounted) {
                            ScaffoldMessenger.of(dialogContext).showSnackBar(
                              SnackBar(
                                content: Text('Ошибка: $e'),
                                backgroundColor: Colors.red,
                              ),
                            );
                          }
                        } finally {
                          if (dialogContext.mounted) {
                            setDialogState(() {
                              isSaving = false;
                            });
                          }
                        }
                      }
                    },
              child: isSaving
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                  : const Text('Добавить'),
            ),
          ],
        ),
      ),
    );

    nameController.dispose();
  }

  Future<void> _handleLogin() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
      });

      try {
        University? universityToUse = _selectedUniversity;
        
        // Если университет не выбран, но есть текст в поле, создаем новый университет
        if (universityToUse == null && _universityController.text.trim().isNotEmpty) {
          final createResult = await _apiService.createUniversity(
            _universityController.text.trim(),
          );
          
          if (createResult['success'] == true) {
            universityToUse = createResult['university'] as University;
            // Обновляем список и выбираем новый университет
            await _loadUniversities();
            setState(() {
              _selectedUniversity = universityToUse;
            });
          } else {
            if (mounted) {
              setState(() {
                _isLoading = false;
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(createResult['error'] ?? 'Ошибка создания университета'),
                  backgroundColor: Colors.red,
                ),
              );
            }
            return;
          }
        }
        
        if (universityToUse == null) {
          if (mounted) {
            setState(() {
              _isLoading = false;
            });
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Выберите или введите название университета'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        final result = await _apiService.login(
          login: _usernameController.text.trim(),
          password: _passwordController.text,
          universityId: universityToUse.id,
        );

        if (result['success'] == true && mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(
              builder: (context) => const MainScreen(),
            ),
          );
        } else if (mounted) {
          final errorMessage = result['error'] ?? 'Ошибка входа';
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                errorMessage,
                style: const TextStyle(fontSize: 14),
              ),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
              action: SnackBarAction(
                label: 'OK',
                textColor: Colors.white,
                onPressed: () {},
              ),
            ),
          );
        }
      } catch (e) {
        if (mounted) {
          String errorMessage = 'Ошибка подключения';
          if (e.toString().contains('Failed to fetch') || 
              e.toString().contains('ClientException') ||
              e.toString().contains('Failed host lookup')) {
            errorMessage = 'Не удалось подключиться к серверу.\nПроверьте подключение к интернету.';
          } else {
            errorMessage = 'Ошибка: $e';
          }
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(errorMessage),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      } finally {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.blue.shade700,
              Colors.blue.shade400,
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 500),
                  child: Card(
                    elevation: 8,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(32.0),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.admin_panel_settings,
                              size: 64,
                              color: Colors.blue.shade700,
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'Админ панель университета',
                              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.grey.shade800,
                                  ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Управление функционалом бота и API',
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: Colors.grey.shade600,
                                  ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 32),
                            // Поиск и выбор университета
                            Autocomplete<University>(
                              displayStringForOption: (University option) => option.name,
                              optionsBuilder: (TextEditingValue textEditingValue) {
                                // Синхронизируем контроллер
                                _universityController.text = textEditingValue.text;
                                
                                if (textEditingValue.text.isEmpty) {
                                  return _universities;
                                }
                                final filtered = _universities.where((University university) {
                                  return university.name
                                      .toLowerCase()
                                      .contains(textEditingValue.text.toLowerCase());
                                }).toList();
                                // Если результатов нет, возвращаем заглушку, чтобы список всегда показывался
                                // В optionsViewBuilder мы отфильтруем её и покажем только подсказку
                                if (filtered.isEmpty) {
                                  return [_placeholderUniversity];
                                }
                                return filtered;
                              },
                              optionsViewOpenDirection: OptionsViewOpenDirection.down,
                              optionsMaxHeight: 300,
                              onSelected: (University selection) {
                                setState(() {
                                  _selectedUniversity = selection;
                                });
                              },
                              fieldViewBuilder: (
                                BuildContext context,
                                TextEditingController textEditingController,
                                FocusNode focusNode,
                                VoidCallback onFieldSubmitted,
                              ) {
                                // Синхронизируем контроллеры при изменении
                                textEditingController.addListener(() {
                                  if (_universityController.text != textEditingController.text) {
                                    _universityController.text = textEditingController.text;
                                  }
                                });
                                
                                return TextFormField(
                                  controller: textEditingController,
                                  focusNode: focusNode,
                                  decoration: InputDecoration(
                                    labelText: 'Университет',
                                    hintText: 'Введите название для поиска...',
                                    prefixIcon: const Icon(Icons.school),
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    suffixIcon: _isLoadingUniversities
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
                                        : textEditingController.text.isNotEmpty
                                            ? IconButton(
                                                icon: const Icon(Icons.clear),
                                                onPressed: () {
                                                  textEditingController.clear();
                                                  _universityController.clear();
                                                  setState(() {
                                                    _selectedUniversity = null;
                                                  });
                                                },
                                              )
                                            : null,
                                  ),
                                  onChanged: (String value) {
                                    _universityController.text = value;
                                    setState(() {
                                      if (_selectedUniversity != null &&
                                          value != _selectedUniversity!.name) {
                                        _selectedUniversity = null;
                                      }
                                    });
                                  },
                                  validator: (String? value) {
                                    if (value == null || value.trim().isEmpty) {
                                      return 'Введите название университета';
                                    }
                                    return null;
                                  },
                                );
                              },
                              optionsViewBuilder: (
                                BuildContext context,
                                AutocompleteOnSelected<University> onSelected,
                                Iterable<University> options,
                              ) {
                                // Фильтруем заглушку из списка
                                final realOptions = options.where((u) => u.id != -1).toList();
                                final hasResults = realOptions.isNotEmpty;
                                final hasText = _universityController.text.trim().isNotEmpty;
                                
                                // Всегда показываем подсказку
                                return Align(
                                  alignment: Alignment.topLeft,
                                  child: Material(
                                    elevation: 4.0,
                                    borderRadius: BorderRadius.circular(12),
                                    child: ConstrainedBox(
                                      constraints: const BoxConstraints(maxHeight: 300),
                                      child: ListView(
                                        padding: EdgeInsets.zero,
                                        shrinkWrap: true,
                                        children: [
                                          // Подсказка всегда наверху - всегда видна
                                          Container(
                                            padding: const EdgeInsets.all(16.0),
                                            decoration: BoxDecoration(
                                              color: Colors.blue.shade50,
                                              border: Border(
                                                bottom: BorderSide(
                                                  color: Colors.grey.shade300,
                                                  width: 1,
                                                ),
                                              ),
                                            ),
                                            child: Row(
                                              children: [
                                                Icon(
                                                  Icons.info_outline,
                                                  color: Colors.blue.shade700,
                                                  size: 20,
                                                ),
                                                const SizedBox(width: 12),
                                                Expanded(
                                                  child: Text(
                                                    'Нет названия? Напишите его полностью!',
                                                    style: TextStyle(
                                                      fontSize: 14,
                                                      color: Colors.blue.shade700,
                                                      fontStyle: FontStyle.italic,
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                          // Список университетов
                                          if (hasResults)
                                            ...realOptions.map((option) => InkWell(
                                                  onTap: () {
                                                    onSelected(option);
                                                  },
                                                  child: Padding(
                                                    padding: const EdgeInsets.all(16.0),
                                                    child: Text(
                                                      option.name,
                                                      style: const TextStyle(fontSize: 16),
                                                    ),
                                                  ),
                                                )),
                                          // Информация о добавлении, если есть текст, но нет результатов
                                          if (!hasResults && hasText)
                                            Padding(
                                              padding: const EdgeInsets.all(16.0),
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                                  Text(
                                                    '"${_universityController.text}"',
                                                    style: TextStyle(
                                                      fontSize: 16,
                                                      color: Colors.grey.shade700,
                                                      fontWeight: FontWeight.w500,
                                                    ),
                                                  ),
                                                  const SizedBox(height: 4),
                                                  Text(
                                                    'Университет будет создан при входе',
                                                    style: TextStyle(
                                                      fontSize: 12,
                                                      color: Colors.grey.shade600,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                        ],
                                      ),
                                    ),
                                  ),
                                );
                              },
                            ),
                            const SizedBox(height: 16),
                            TextFormField(
                              controller: _usernameController,
                              decoration: InputDecoration(
                                labelText: 'Логин',
                                prefixIcon: const Icon(Icons.person),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Введите логин';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            TextFormField(
                              controller: _passwordController,
                              obscureText: _obscurePassword,
                              decoration: InputDecoration(
                                labelText: 'Пароль',
                                prefixIcon: const Icon(Icons.lock),
                                suffixIcon: IconButton(
                                  icon: Icon(
                                    _obscurePassword
                                        ? Icons.visibility
                                        : Icons.visibility_off,
                                  ),
                                  onPressed: () {
                                    setState(() {
                                      _obscurePassword = !_obscurePassword;
                                    });
                                  },
                                ),
                                border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'Введите пароль';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 24),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: _isLoading ? null : _handleLogin,
                                style: ElevatedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                child: _isLoading
                                    ? const SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          valueColor:
                                              AlwaysStoppedAnimation<Color>(Colors.white),
                                        ),
                                      )
                                    : const Text(
                                        'Войти',
                                        style: TextStyle(fontSize: 16),
                                      ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
