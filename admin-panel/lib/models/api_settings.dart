class ApiSettings {
  final String baseUrl;
  final DateTime? lastUpdated;

  ApiSettings({
    required this.baseUrl,
    this.lastUpdated,
  });

  factory ApiSettings.fromJson(Map<String, dynamic> json) {
    return ApiSettings(
      baseUrl: json['baseUrl'] as String,
      lastUpdated: json['lastUpdated'] != null
          ? DateTime.parse(json['lastUpdated'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'baseUrl': baseUrl,
      'lastUpdated': lastUpdated?.toIso8601String(),
    };
  }

  ApiSettings copyWith({
    String? baseUrl,
    DateTime? lastUpdated,
  }) {
    return ApiSettings(
      baseUrl: baseUrl ?? this.baseUrl,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }
}

