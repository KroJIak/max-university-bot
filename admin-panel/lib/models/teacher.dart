class Teacher {
  final String id;
  final String firstName;
  final String lastName;
  final String? middleName;
  final String? department; // Кафедра
  final String? position; // Должность
  final String? phoneNumber;
  final String? photoUrl;
  final String? photoBase64; // Фото в формате base64
  final Map<String, dynamic>? additionalData;

  Teacher({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.middleName,
    this.department,
    this.position,
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

  factory Teacher.fromJson(Map<String, dynamic> json) {
    return Teacher(
      id: json['id'] as String,
      firstName: json['first_name'] as String,
      lastName: json['last_name'] as String,
      middleName: json['middle_name'] as String?,
      department: json['department'] as String?,
      position: json['position'] as String?,
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
      'department': department,
      'position': position,
      'phone_number': phoneNumber,
      'photo_url': photoUrl,
      'photo_base64': photoBase64,
      'additional_data': additionalData,
    };
  }

  Teacher copyWith({
    String? id,
    String? firstName,
    String? lastName,
    String? middleName,
    String? department,
    String? position,
    String? phoneNumber,
    String? photoUrl,
    String? photoBase64,
    Map<String, dynamic>? additionalData,
  }) {
    return Teacher(
      id: id ?? this.id,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      middleName: middleName ?? this.middleName,
      department: department ?? this.department,
      position: position ?? this.position,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      photoUrl: photoUrl ?? this.photoUrl,
      photoBase64: photoBase64 ?? this.photoBase64,
      additionalData: additionalData ?? this.additionalData,
    );
  }
}

