class Student {
  final String id;
  final String firstName;
  final String lastName;
  final String? middleName;
  final int course;
  final String group;
  final String? phoneNumber;
  final String? photoUrl;
  final String? photoBase64; // Фото в формате base64
  final Map<String, dynamic>? additionalData;

  Student({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.middleName,
    required this.course,
    required this.group,
    this.phoneNumber,
    this.photoUrl,
    this.photoBase64,
    this.additionalData,
  });

  String get fullName {
    if (middleName != null && middleName!.isNotEmpty) {
      return '$lastName $firstName $middleName';
    }
    return '$lastName $firstName';
  }

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] as String,
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      middleName: json['middle_name'] as String?,
      course: json['course'] as int,
      group: json['group'] as String,
      phoneNumber: json['phone_number'] as String?,
      photoUrl: json['photo_url'] as String?,
      photoBase64: json['photo_base64'] as String?,
      additionalData: json['additional_data'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'first_name': firstName,
      'last_name': lastName,
      'middle_name': middleName,
      'course': course,
      'group': group,
      'phone_number': phoneNumber,
      'photo_url': photoUrl,
      'photo_base64': photoBase64,
      'additional_data': additionalData,
    };
  }

  Student copyWith({
    String? id,
    String? firstName,
    String? lastName,
    String? middleName,
    int? course,
    String? group,
    String? phoneNumber,
    String? photoUrl,
    String? photoBase64,
    Map<String, dynamic>? additionalData,
  }) {
    return Student(
      id: id ?? this.id,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      middleName: middleName ?? this.middleName,
      course: course ?? this.course,
      group: group ?? this.group,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      photoUrl: photoUrl ?? this.photoUrl,
      photoBase64: photoBase64 ?? this.photoBase64,
      additionalData: additionalData ?? this.additionalData,
    );
  }
}

