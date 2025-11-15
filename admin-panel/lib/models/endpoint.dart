class Endpoint {
  final String id;
  final String name;
  final String path;
  final String description;
  final String method; // GET, POST, PUT, DELETE
  final bool enabled;

  Endpoint({
    required this.id,
    required this.name,
    required this.path,
    required this.description,
    required this.method,
    this.enabled = false,
  });

  factory Endpoint.fromJson(Map<String, dynamic> json) {
    return Endpoint(
      id: json['id'] as String,
      name: json['name'] as String,
      path: json['path'] as String,
      description: json['description'] as String,
      method: json['method'] as String,
      enabled: json['enabled'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'path': path,
      'description': description,
      'method': method,
      'enabled': enabled,
    };
  }

  Endpoint copyWith({
    String? id,
    String? name,
    String? path,
    String? description,
    String? method,
    bool? enabled,
  }) {
    return Endpoint(
      id: id ?? this.id,
      name: name ?? this.name,
      path: path ?? this.path,
      description: description ?? this.description,
      method: method ?? this.method,
      enabled: enabled ?? this.enabled,
    );
  }
}

