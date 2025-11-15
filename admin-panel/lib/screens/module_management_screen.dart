import 'package:flutter/material.dart';
import '../models/module.dart';
import '../models/endpoint.dart';
import '../services/mock_api_service.dart';

class ModuleManagementScreen extends StatefulWidget {
  final Module module;

  const ModuleManagementScreen({
    super.key,
    required this.module,
  });

  @override
  State<ModuleManagementScreen> createState() => _ModuleManagementScreenState();
}

class _ModuleManagementScreenState extends State<ModuleManagementScreen> {
  late Module _module;
  final _apiService = MockApiService();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _module = widget.module;
  }

  Future<void> _updateEndpoint(Endpoint endpoint) async {
    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _apiService.updateEndpoint(_module.id, endpoint);
      if (mounted) {
        if (result['success'] == true) {
          setState(() {
            final index = _module.endpoints.indexWhere((e) => e.id == endpoint.id);
            if (index != -1) {
              final updatedEndpoints = List<Endpoint>.from(_module.endpoints);
              updatedEndpoints[index] = endpoint;
              _module = _module.copyWith(endpoints: updatedEndpoints);
            }
          });
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Endpoint успешно обновлен'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Ошибка обновления'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка: $e'),
            backgroundColor: Colors.red,
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

  Future<void> _updateModule() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final result = await _apiService.updateModule(_module);
      if (mounted) {
        if (result['success'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Модуль успешно обновлен'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['error'] ?? 'Ошибка обновления'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка: $e'),
            backgroundColor: Colors.red,
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

  Color _getMethodColor(String method) {
    switch (method.toUpperCase()) {
      case 'GET':
        return Colors.blue;
      case 'POST':
        return Colors.green;
      case 'PUT':
        return Colors.orange;
      case 'DELETE':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Widget _buildEndpointCard(Endpoint endpoint) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getMethodColor(endpoint.method),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    endpoint.method,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    endpoint.name,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
                Switch(
                  value: endpoint.enabled,
                  onChanged: (value) {
                    _updateEndpoint(endpoint.copyWith(enabled: value));
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              endpoint.description,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.code, size: 16, color: Colors.grey.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      endpoint.path,
                      style: TextStyle(
                        fontFamily: 'monospace',
                        color: Colors.grey.shade800,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  endpoint.enabled ? Icons.check_circle : Icons.cancel,
                  size: 16,
                  color: endpoint.enabled ? Colors.green : Colors.grey,
                ),
                const SizedBox(width: 4),
                Text(
                  endpoint.enabled ? 'Включено' : 'Выключено',
                  style: TextStyle(
                    color: endpoint.enabled ? Colors.green : Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_module.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _updateModule,
            tooltip: 'Сохранить модуль',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1000),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                _getIconData(_module.icon),
                                color: Colors.blue.shade700,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  _module.name,
                                  style: Theme.of(context)
                                      .textTheme
                                      .headlineSmall
                                      ?.copyWith(
                                        fontWeight: FontWeight.bold,
                                      ),
                                ),
                              ),
                              Switch(
                                value: _module.enabled,
                                onChanged: (value) {
                                  setState(() {
                                    _module = _module.copyWith(enabled: value);
                                  });
                                  _updateModule();
                                },
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _module.description,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Colors.grey.shade600,
                                ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'Endpoints',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 16),
                  ..._module.endpoints.map((endpoint) => _buildEndpointCard(endpoint)),
                    ],
                  ),
                ),
              ),
            ),
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
      case 'link':
        return Icons.link;
      case 'settings':
        return Icons.settings;
      default:
        return Icons.widgets;
    }
  }
}

