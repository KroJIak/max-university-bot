class UniversityConfig {
  final String universityApiBaseUrl;
  final Map<String, String> endpoints;
  final int? universityId;

  UniversityConfig({
    required this.universityApiBaseUrl,
    required this.endpoints,
    this.universityId,
  });

  factory UniversityConfig.fromJson(Map<String, dynamic> json) {
    return UniversityConfig(
      universityApiBaseUrl: json['university_api_base_url'] as String? ?? '',
      endpoints: (json['endpoints'] as Map<String, dynamic>?)
              ?.map((key, value) => MapEntry(key, value.toString())) ??
          {},
      universityId: json['university_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'university_api_base_url': universityApiBaseUrl,
      'endpoints': endpoints,
      if (universityId != null) 'university_id': universityId,
    };
  }

  UniversityConfig copyWith({
    String? universityApiBaseUrl,
    Map<String, String>? endpoints,
    int? universityId,
  }) {
    return UniversityConfig(
      universityApiBaseUrl: universityApiBaseUrl ?? this.universityApiBaseUrl,
      endpoints: endpoints ?? this.endpoints,
      universityId: universityId ?? this.universityId,
    );
  }
}

class Feature {
  final String id;
  final String name;
  final String description;
  final String defaultEndpoint;
  final String category;

  Feature({
    required this.id,
    required this.name,
    required this.description,
    required this.defaultEndpoint,
    required this.category,
  });
}
