import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:file_picker/file_picker.dart';
import 'package:csv/csv.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import '../models/building.dart';
import '../services/api_service.dart';
import '../models/university_config.dart';

// Условный импорт для веб-платформы
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html if (dart.library.html) 'dart:html';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _apiService = ApiService();
  UniversityConfig? _universityConfig;
  bool _isLoading = true;
  
  List<Building> _buildings = [];
  Building? _selectedBuilding;
  
  // Контроллер карты для управления масштабом и позицией
  final MapController _mapController = MapController();

  @override
  void initState() {
    super.initState();
    _loadConfig();
    _loadMockBuildings();
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

  void _loadMockBuildings() {
    _buildings = [
      Building(
        id: '1',
        name: 'Главный корпус',
        description: 'Основной учебный корпус университета',
        latitude: 56.1436,
        longitude: 47.2525,
        address: 'Московский проспект, 15',
      ),
      Building(
        id: '2',
        name: 'Корпус №2',
        description: 'Корпус технических факультетов',
        latitude: 56.1440,
        longitude: 47.2530,
        address: 'Московский проспект, 17',
      ),
      Building(
        id: '3',
        name: 'Спортивный комплекс',
        description: 'Спортивный зал и бассейн',
        latitude: 56.1430,
        longitude: 47.2520,
        address: 'Московский проспект, 13',
      ),
    ];
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
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(statusIcon, color: statusColor, size: 20),
          const SizedBox(width: 8),
          Text(
            '$endpointName: $statusText',
            style: TextStyle(
              color: statusColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // Проверяем состояние endpoint карт
    final isMapsEnabled = _isEndpointEnabled('students_maps');
    final hasMapsEndpoint = _hasEndpointValue('students_maps');

    // Endpoint включен и настроен - показываем сообщение
    if (isMapsEnabled && hasMapsEndpoint) {
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
                      'Данные карт корпусов',
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
                    _buildEndpointStatus('students_maps', 'Карты корпусов'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    // Endpoint выключен - показываем сообщение
    if (!isMapsEnabled) {
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
                      Icons.map_outlined,
                      size: 64,
                      color: Colors.grey.shade400,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Функция карт выключена',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Включите функцию карт в настройках, чтобы использовать эту функцию',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    _buildEndpointStatus('students_maps', 'Карты корпусов'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    }

    // Endpoint включен, но пустой - показываем интерфейс управления картами
    final isMobile = MediaQuery.of(context).size.width < 600;
    
    if (isMobile) {
      // На мобильных устройствах - вертикальный layout
      return Column(
        children: [
          // Статус endpoint в заголовке
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: _buildEndpointStatus('students_maps', 'Карты корпусов'),
          ),
          // Заголовок и кнопки
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              children: [
                Icon(Icons.map, size: 24, color: Colors.blue.shade700),
                const SizedBox(width: 12),
                Flexible(
                  child: Text(
                    'Карта корпусов',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const Spacer(),
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
                const SizedBox(width: 8),
                FloatingActionButton.small(
                  onPressed: _addBuilding,
                  backgroundColor: Colors.blue.shade700,
                  tooltip: 'Добавить корпус',
                  child: const Icon(Icons.add),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Карта (на мобильных показываем карту сверху)
          SizedBox(
            height: 300,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Card(
                clipBehavior: Clip.antiAlias,
                child: Stack(
                  children: [
                    _buildMap(),
                    // Кнопки масштабирования
                    Positioned(
                      bottom: 16,
                      right: 16,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          FloatingActionButton.small(
                            heroTag: 'zoom_in_map_mobile',
                            onPressed: () {
                              final currentZoom = _mapController.camera.zoom;
                              if (currentZoom < 18.0) {
                                _mapController.move(_mapController.camera.center, currentZoom + 1);
                              }
                            },
                            backgroundColor: Colors.white,
                            child: const Icon(Icons.add, color: Colors.black87),
                          ),
                          const SizedBox(height: 8),
                          FloatingActionButton.small(
                            heroTag: 'zoom_out_map_mobile',
                            onPressed: () {
                              final currentZoom = _mapController.camera.zoom;
                              if (currentZoom > 10.0) {
                                _mapController.move(_mapController.camera.center, currentZoom - 1);
                              }
                            },
                            backgroundColor: Colors.white,
                            child: const Icon(Icons.remove, color: Colors.black87),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Список корпусов
          Expanded(
            child: _buildings.isEmpty
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        'Нет корпусов. Добавьте первый корпус.',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.grey,
                            ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    itemCount: _buildings.length,
                    itemBuilder: (context, index) {
                      final building = _buildings[index];
                      return _buildBuildingCard(building);
                    },
                  ),
          ),
        ],
      );
    } else {
      // На десктопе - горизонтальный layout
      return Column(
        children: [
          // Статус endpoint в заголовке
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: _buildEndpointStatus('students_maps', 'Карты корпусов'),
          ),
          // Основной интерфейс карты
          Expanded(
            child: Row(
              children: [
                // Список корпусов
                Expanded(
                  flex: 1,
                  child: Column(
                    children: [
                      // Заголовок и кнопка добавления
                      Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: Row(
                          children: [
                            Icon(Icons.map, size: 32, color: Colors.blue.shade700),
                            const SizedBox(width: 12),
                            Flexible(
                              child: Text(
                                'Карта корпусов',
                                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                      fontWeight: FontWeight.bold,
                                    ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            const Spacer(),
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
                            const SizedBox(width: 8),
                            FloatingActionButton(
                              onPressed: _addBuilding,
                              backgroundColor: Colors.blue.shade700,
                              tooltip: 'Добавить корпус',
                              child: const Icon(Icons.add),
                            ),
                          ],
                        ),
                      ),
                      // Список корпусов
                      Expanded(
                        child: _buildings.isEmpty
                            ? Center(
                                child: Text(
                                  'Нет корпусов. Добавьте первый корпус.',
                                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                        color: Colors.grey,
                                      ),
                                ),
                              )
                            : ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                                itemCount: _buildings.length,
                                itemBuilder: (context, index) {
                                  final building = _buildings[index];
                                  return _buildBuildingCard(building);
                                },
                              ),
                      ),
                    ],
                  ),
                ),
                const VerticalDivider(thickness: 1, width: 1),
                // Карта
                Expanded(
                  flex: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Stack(
                      children: [
                        Card(
                          clipBehavior: Clip.antiAlias,
                          child: _buildMap(),
                        ),
                        // Кнопки масштабирования поверх карты
                        Positioned(
                          bottom: 32,
                          right: 32,
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              FloatingActionButton.small(
                                heroTag: 'zoom_in_map',
                                onPressed: () {
                                  final currentZoom = _mapController.camera.zoom;
                                  if (currentZoom < 18.0) {
                                    _mapController.move(_mapController.camera.center, currentZoom + 1);
                                  }
                                },
                                backgroundColor: Colors.white,
                                child: const Icon(Icons.add, color: Colors.black87),
                              ),
                              const SizedBox(height: 8),
                              FloatingActionButton.small(
                                heroTag: 'zoom_out_map',
                                onPressed: () {
                                  final currentZoom = _mapController.camera.zoom;
                                  if (currentZoom > 10.0) {
                                    _mapController.move(_mapController.camera.center, currentZoom - 1);
                                  }
                                },
                                backgroundColor: Colors.white,
                                child: const Icon(Icons.remove, color: Colors.black87),
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
        ],
      );
    }
  }

  Widget _buildBuildingCard(Building building) {
    final isSelected = _selectedBuilding?.id == building.id;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: isSelected ? Colors.blue.shade50 : null,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.blue.shade700,
          child: const Icon(Icons.business, color: Colors.white),
        ),
        title: Text(
          building.name,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (building.description != null) ...[
              const SizedBox(height: 4),
              Text(building.description!),
            ],
            const SizedBox(height: 4),
            Text(
              '${building.latitude.toStringAsFixed(6)}, ${building.longitude.toStringAsFixed(6)}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
            if (building.address != null) ...[
              const SizedBox(height: 2),
              Row(
                children: [
                  Icon(Icons.location_on, size: 14, color: Colors.grey.shade600),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      building.address!,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.edit, color: Colors.blue),
              onPressed: () => _editBuilding(building),
              tooltip: 'Редактировать',
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () => _deleteBuilding(building),
              tooltip: 'Удалить',
            ),
          ],
        ),
        onTap: () {
          setState(() {
            _selectedBuilding = building;
          });
          _focusOnBuilding(building);
        },
      ),
    );
  }

  Widget _buildMap() {
    if (_buildings.isEmpty) {
      return Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(
          color: Colors.grey.shade200,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.map, size: 64, color: Colors.grey.shade400),
              const SizedBox(height: 16),
              Text(
                'Добавьте корпуса для отображения на карте',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Colors.grey.shade600,
                    ),
              ),
            ],
          ),
        ),
      );
    }

    // Вычисляем центр карты
    final centerLat = _buildings.map((b) => b.latitude).reduce((a, b) => a + b) / _buildings.length;
    final centerLng = _buildings.map((b) => b.longitude).reduce((a, b) => a + b) / _buildings.length;
    final center = LatLng(centerLat, centerLng);

    return Container(
      width: double.infinity,
      height: double.infinity,
      decoration: BoxDecoration(
        color: Colors.grey.shade200,
        borderRadius: BorderRadius.circular(12),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          // Реальная карта с OpenStreetMap
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: center,
              initialZoom: _buildings.length == 1 ? 15.0 : 14.0,
              minZoom: 10.0,
              maxZoom: 18.0,
              interactionOptions: const InteractionOptions(
                flags: InteractiveFlag.all,
              ),
              onTap: (tapPosition, point) {
                // Можно добавить обработку клика на карте для добавления нового корпуса
              },
            ),
            children: [
              // Слой карты OpenStreetMap
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.example.adminpanel',
                maxZoom: 19,
              ),
              // Маркеры корпусов
              MarkerLayer(
                markers: _buildings.map((building) {
                  final isSelected = _selectedBuilding?.id == building.id;
                  return Marker(
                    point: LatLng(building.latitude, building.longitude),
                    width: isSelected ? 50 : 40,
                    height: isSelected ? 50 : 40,
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedBuilding = building;
                        });
                      },
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // Тень
                          Positioned(
                            bottom: 0,
                            child: Container(
                              width: isSelected ? 50 : 40,
                              height: isSelected ? 50 : 40,
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.2),
                                shape: BoxShape.circle,
                              ),
                            ),
                          ),
                          // Маркер
                          Container(
                            width: isSelected ? 45 : 35,
                            height: isSelected ? 45 : 35,
                            decoration: BoxDecoration(
                              color: isSelected ? Colors.blue.shade700 : Colors.blue.shade400,
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: Colors.white,
                                width: 3,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.3),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Icon(
                              Icons.business,
                              color: Colors.white,
                              size: isSelected ? 24 : 20,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
          // Легенда с корпусами
          Positioned(
            top: 16,
            right: 16,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Корпуса',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    ..._buildings.map((building) {
                      final isSelected = _selectedBuilding?.id == building.id;
                      return InkWell(
                        onTap: () {
                          setState(() {
                            _selectedBuilding = building;
                          });
                        },
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4.0),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 16,
                                height: 16,
                                decoration: BoxDecoration(
                                  color: isSelected ? Colors.blue.shade700 : Colors.blue.shade300,
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: Colors.white,
                                    width: 2,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                building.name,
                                style: TextStyle(
                                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                  color: isSelected ? Colors.blue.shade700 : Colors.black87,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _focusOnBuilding(Building building) {
    setState(() {
      _selectedBuilding = building;
    });
  }


  Future<void> _addBuilding() async {
    final result = await showDialog<Building>(
      context: context,
      builder: (context) => _BuildingDialog(),
    );

    if (result != null) {
      setState(() {
        _buildings.add(result);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Корпус "${result.name}" добавлен'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _editBuilding(Building building) async {
    final result = await showDialog<Building>(
      context: context,
      builder: (context) => _BuildingDialog(building: building),
    );

    if (result != null) {
      setState(() {
        final index = _buildings.indexWhere((b) => b.id == building.id);
        if (index != -1) {
          _buildings[index] = result;
          if (_selectedBuilding?.id == building.id) {
            _selectedBuilding = result;
          }
        }
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Корпус "${result.name}" обновлен'),
            backgroundColor: Colors.blue,
          ),
        );
      }
    }
  }

  Future<void> _deleteBuilding(Building building) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Удаление корпуса'),
        content: Text('Вы уверены, что хотите удалить корпус "${building.name}"?'),
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
        _buildings.removeWhere((b) => b.id == building.id);
        if (_selectedBuilding?.id == building.id) {
          _selectedBuilding = null;
        }
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Корпус "${building.name}" удален'),
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
                Text('Найдено корпусов: ${csvData.length - 1}'), // -1 для заголовка
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

        // Парсим корпуса из CSV
        final buildings = _parseCsvToBuildings(csvData);
        
        if (buildings.isEmpty) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Не удалось распарсить корпуса из CSV файла'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        setState(() {
          if (action == 'replace') {
            _buildings = buildings;
          } else {
            _buildings.addAll(buildings);
          }
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                action == 'replace'
                    ? 'Список корпусов заменен. Добавлено корпусов: ${buildings.length}'
                    : 'Добавлено корпусов: ${buildings.length}',
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

  List<Building> _parseCsvToBuildings(List<List<dynamic>> csvData) {
    if (csvData.length < 2) return [];

    final buildings = <Building>[];
    
    // Пропускаем заголовок (первую строку)
    for (int i = 1; i < csvData.length; i++) {
      final row = csvData[i];
      if (row.length < 4) continue; // Минимум: ID, Название, Широта, Долгота

      try {
        // Формат CSV: ID, Название, Описание, Широта, Долгота, Адрес
        final id = row[0]?.toString().trim() ?? DateTime.now().millisecondsSinceEpoch.toString() + '_$i';
        final name = row[1]?.toString().trim() ?? '';
        
        if (name.isEmpty) continue;

        final description = row.length > 2 ? row[2]?.toString().trim() : null;
        final latitude = row.length > 3 ? double.tryParse(row[3]?.toString().trim() ?? '0') ?? 0.0 : 0.0;
        final longitude = row.length > 4 ? double.tryParse(row[4]?.toString().trim() ?? '0') ?? 0.0 : 0.0;
        final address = row.length > 5 ? row[5]?.toString().trim() : null;

        if (latitude == 0.0 && longitude == 0.0) continue;

        final building = Building(
          id: id,
          name: name,
          description: description?.isEmpty == true ? null : description,
          latitude: latitude,
          longitude: longitude,
          address: address?.isEmpty == true ? null : address,
        );

        buildings.add(building);
      } catch (e) {
        // Пропускаем строки с ошибками
        continue;
      }
    }

    return buildings;
  }

  Future<void> _exportToCsv() async {
    try {
      if (_buildings.isEmpty) {
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
        'Название',
        'Описание',
        'Широта',
        'Долгота',
        'Адрес',
      ]);

      // Данные корпусов
      for (var building in _buildings) {
        csvData.add([
          building.id,
          building.name,
          building.description ?? '',
          building.latitude,
          building.longitude,
          building.address ?? '',
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
            content: Text('Экспортировано ${_buildings.length} корпусов'),
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
    // ignore: avoid_web_libraries_in_flutter
    if (kIsWeb) {
      final blob = html.Blob([csvString], 'text/csv', 'native');
      final url = html.Url.createObjectUrlFromBlob(blob);
      final anchor = html.AnchorElement(href: url)
        ..setAttribute('download', 'buildings_${DateTime.now().millisecondsSinceEpoch}.csv')
        ..click();
      html.Url.revokeObjectUrl(url);
    }
  }

  Future<void> _downloadCsvOther(String csvString) async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Экспорт CSV доступен только в веб-версии'),
        backgroundColor: Colors.orange,
      ),
    );
  }
}

class _BuildingDialog extends StatefulWidget {
  final Building? building;

  const _BuildingDialog({this.building});

  @override
  State<_BuildingDialog> createState() => _BuildingDialogState();
}

class _BuildingDialogState extends State<_BuildingDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _latitudeController = TextEditingController();
  final _longitudeController = TextEditingController();
  final _addressController = TextEditingController();

  @override
  void initState() {
    super.initState();
    if (widget.building != null) {
      _nameController.text = widget.building!.name;
      _descriptionController.text = widget.building!.description ?? '';
      _latitudeController.text = widget.building!.latitude.toString();
      _longitudeController.text = widget.building!.longitude.toString();
      _addressController.text = widget.building!.address ?? '';
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _latitudeController.dispose();
    _longitudeController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.building == null ? 'Добавить корпус' : 'Редактировать корпус'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Название корпуса *',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Введите название корпуса';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Описание',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _latitudeController,
                      decoration: const InputDecoration(
                        labelText: 'Широта *',
                        border: OutlineInputBorder(),
                        hintText: '56.1436',
                      ),
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Введите широту';
                        }
                        final lat = double.tryParse(value);
                        if (lat == null || lat < -90 || lat > 90) {
                          return 'Широта должна быть от -90 до 90';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: TextFormField(
                      controller: _longitudeController,
                      decoration: const InputDecoration(
                        labelText: 'Долгота *',
                        border: OutlineInputBorder(),
                        hintText: '47.2525',
                      ),
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Введите долготу';
                        }
                        final lng = double.tryParse(value);
                        if (lng == null || lng < -180 || lng > 180) {
                          return 'Долгота должна быть от -180 до 180';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _addressController,
                decoration: const InputDecoration(
                  labelText: 'Адрес',
                  border: OutlineInputBorder(),
                  hintText: 'Московский проспект, 15',
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Отмена'),
        ),
        ElevatedButton(
          onPressed: _save,
          child: const Text('Сохранить'),
        ),
      ],
    );
  }

  void _save() {
    if (_formKey.currentState!.validate()) {
      final building = Building(
        id: widget.building?.id ?? DateTime.now().millisecondsSinceEpoch.toString(),
        name: _nameController.text.trim(),
        description: _descriptionController.text.trim().isEmpty
            ? null
            : _descriptionController.text.trim(),
        latitude: double.parse(_latitudeController.text.trim()),
        longitude: double.parse(_longitudeController.text.trim()),
        address: _addressController.text.trim().isEmpty
            ? null
            : _addressController.text.trim(),
      );
      Navigator.of(context).pop(building);
    }
  }
}

