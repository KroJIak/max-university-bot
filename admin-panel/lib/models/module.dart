import 'endpoint.dart';

class Module {
  final String id;
  final String name;
  final String description;
  final String icon;
  final List<Endpoint> endpoints;
  final bool enabled;

  Module({
    required this.id,
    required this.name,
    required this.description,
    required this.icon,
    required this.endpoints,
    this.enabled = true,
  });

  factory Module.fromJson(Map<String, dynamic> json) {
    return Module(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      icon: json['icon'] as String,
      endpoints: (json['endpoints'] as List<dynamic>?)
              ?.map((e) => Endpoint.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      enabled: json['enabled'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'icon': icon,
      'endpoints': endpoints.map((e) => e.toJson()).toList(),
      'enabled': enabled,
    };
  }

  Module copyWith({
    String? id,
    String? name,
    String? description,
    String? icon,
    List<Endpoint>? endpoints,
    bool? enabled,
  }) {
    return Module(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      icon: icon ?? this.icon,
      endpoints: endpoints ?? this.endpoints,
      enabled: enabled ?? this.enabled,
    );
  }
}

