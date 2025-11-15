class University {
  final int id;
  final String name;

  University({
    required this.id,
    required this.name,
  });

  factory University.fromJson(Map<String, dynamic> json) {
    return University(
      id: json['id'] as int,
      name: json['name'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
    };
  }
}

