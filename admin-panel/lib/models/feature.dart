class Feature {
  final String id;
  final String name;
  final String description;
  final String defaultEndpoint;
  final String category; // 'management', 'services', 'additional'

  Feature({
    required this.id,
    required this.name,
    required this.description,
    required this.defaultEndpoint,
    required this.category,
  });

  factory Feature.fromJson(Map<String, dynamic> json) {
    return Feature(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      defaultEndpoint: json['defaultEndpoint'] as String,
      category: json['category'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'defaultEndpoint': defaultEndpoint,
      'category': category,
    };
  }
}

