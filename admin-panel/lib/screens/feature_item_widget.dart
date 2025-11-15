import 'package:flutter/material.dart';
import '../models/university_config.dart';

class FeatureItemWidget extends StatefulWidget {
  final Feature feature;
  final bool isEnabled;
  final String endpoint;
  final List<String> availableEndpoints;
  final Function(bool) onToggle;
  final Function(String) onEndpointChanged;
  final Function(Feature)? onManualSetup; // Callback для ручной настройки

  const FeatureItemWidget({
    super.key,
    required this.feature,
    required this.isEnabled,
    required this.endpoint,
    required this.availableEndpoints,
    required this.onToggle,
    required this.onEndpointChanged,
    this.onManualSetup,
  });

  @override
  State<FeatureItemWidget> createState() => _FeatureItemWidgetState();
}

class _FeatureItemWidgetState extends State<FeatureItemWidget> {
  TextEditingController? _endpointController;
  FocusNode? _focusNode;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    // Создаем контроллер только если нет доступных endpoints (будет использоваться TextField)
    if (widget.availableEndpoints.isEmpty) {
      _endpointController = TextEditingController(text: widget.endpoint);
      _focusNode = FocusNode();
      _focusNode?.addListener(_onFocusChange);
    }
  }

  void _onFocusChange() {
    if (_focusNode != null && !_focusNode!.hasFocus && _isEditing) {
      // Поле потеряло фокус, сохраняем изменения
      _isEditing = false;
      // Передаем значение - функция включится автоматически, если endpoint не пустой
      widget.onEndpointChanged(_endpointController?.text.trim() ?? '');
    }
  }

  @override
  void didUpdateWidget(FeatureItemWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // Если появились доступные endpoints, создаем контроллер для TextField
    if (oldWidget.availableEndpoints.isEmpty && widget.availableEndpoints.isNotEmpty) {
      // Переключаемся на DropdownButton - контроллер не нужен
      _endpointController?.dispose();
      _focusNode?.dispose();
      _endpointController = null;
      _focusNode = null;
    } else if (oldWidget.availableEndpoints.isNotEmpty && widget.availableEndpoints.isEmpty) {
      // Переключаемся на TextField - создаем контроллер
      _endpointController = TextEditingController(text: widget.endpoint);
      _focusNode = FocusNode();
      _focusNode?.addListener(_onFocusChange);
    }
    
    // Обновляем контроллер только если пользователь не редактирует поле и используется TextField
    if (_endpointController != null && !_isEditing && oldWidget.endpoint != widget.endpoint) {
      // Если endpoint пустой, показываем пустую строку (не дефолтное значение)
      _endpointController!.text = widget.endpoint.isEmpty ? '' : widget.endpoint;
    }
    if (_endpointController != null && oldWidget.isEnabled != widget.isEnabled) {
      // При изменении состояния включенности обновляем endpoint
      _endpointController!.text = widget.endpoint.isEmpty ? '' : widget.endpoint;
    }
  }

  @override
  void dispose() {
    _focusNode?.removeListener(_onFocusChange);
    _focusNode?.dispose();
    _focusNode = null;
    _endpointController?.dispose();
    _endpointController = null;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.feature.name,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        widget.feature.description,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey.shade600,
                            ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Column(
                  children: [
                    Text(
                      widget.isEnabled ? 'Включено' : 'Выключено',
                      style: TextStyle(
                        fontSize: 12,
                        color: widget.isEnabled ? Colors.green : Colors.grey,
                      ),
                    ),
                    Switch(
                      value: widget.isEnabled,
                      onChanged: (value) {
                        widget.onToggle(value);
                      },
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Если есть доступные endpoints из OpenAPI, показываем выпадающий список
            // Иначе показываем обычное текстовое поле
            widget.availableEndpoints.isNotEmpty
                ? DropdownButtonFormField<String>(
                    value: widget.endpoint.isEmpty ? null : widget.endpoint,
                    decoration: InputDecoration(
                      labelText: 'Endpoint',
                      hintText: widget.feature.defaultEndpoint,
                      prefixIcon: const Icon(Icons.code),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      helperText: widget.isEnabled 
                          ? null 
                          : 'Выберите endpoint, чтобы включить функцию',
                    ),
                    items: [
                      // Первый элемент - пустой (чтобы можно было не выбирать endpoint)
                      const DropdownMenuItem<String>(
                        value: null,
                        child: Text('(Не выбран)'),
                      ),
                      // Остальные endpoints из OpenAPI
                      ...widget.availableEndpoints.map((endpoint) {
                        return DropdownMenuItem<String>(
                          value: endpoint,
                          child: Text(
                            endpoint,
                            overflow: TextOverflow.ellipsis,
                          ),
                        );
                      }),
                    ],
                    onChanged: (value) {
                      // Передаем значение (может быть null, если выбран пустой элемент)
                      widget.onEndpointChanged(value ?? '');
                    },
                  )
                : Builder(
                    builder: (context) {
                      // Создаем контроллер, если его еще нет
                      if (_endpointController == null) {
                        _endpointController = TextEditingController(text: widget.endpoint);
                        _focusNode = FocusNode();
                        _focusNode?.addListener(_onFocusChange);
                      }
                      return TextField(
                        controller: _endpointController!,
                        focusNode: _focusNode,
                        decoration: InputDecoration(
                          labelText: 'Endpoint',
                          hintText: widget.feature.defaultEndpoint,
                          prefixIcon: const Icon(Icons.code),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          // Показываем подсказку, если функция выключена
                          helperText: widget.isEnabled 
                              ? null 
                              : 'Введите endpoint, чтобы включить функцию',
                        ),
                        // Поле всегда доступно для редактирования
                        enabled: true,
                        onTap: () {
                          _isEditing = true;
                        },
                        onChanged: (value) {
                          // Отмечаем, что пользователь редактирует поле
                          _isEditing = true;
                        },
                        onSubmitted: (value) {
                          // При нажатии Enter сохраняем изменения
                          _isEditing = false;
                          // Передаем значение - функция включится автоматически, если endpoint не пустой
                          widget.onEndpointChanged(value.trim());
                        },
                      );
                    },
                  ),
            // Показываем кнопку "Настроить вручную" только если endpoint не используется
            if (!widget.isEnabled || widget.endpoint.trim().isEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: widget.onManualSetup != null
                        ? () => widget.onManualSetup!(widget.feature)
                        : null,
                    icon: const Icon(Icons.edit_note),
                    label: const Text('Настроить вручную (CSV)'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

