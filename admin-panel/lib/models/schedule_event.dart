class ScheduleEvent {
  final String id;
  final String title;
  final String? description;
  final DateTime startTime;
  final DateTime endTime;
  final String? location;
  final String? buildingId;
  final String? teacherId;
  final String? groupId;
  final String? subject;
  final Map<String, dynamic>? additionalData;

  ScheduleEvent({
    required this.id,
    required this.title,
    this.description,
    required this.startTime,
    required this.endTime,
    this.location,
    this.buildingId,
    this.teacherId,
    this.groupId,
    this.subject,
    this.additionalData,
  });

  factory ScheduleEvent.fromJson(Map<String, dynamic> json) {
    return ScheduleEvent(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: DateTime.parse(json['end_time'] as String),
      location: json['location'] as String?,
      buildingId: json['building_id'] as String?,
      teacherId: json['teacher_id'] as String?,
      groupId: json['group_id'] as String?,
      subject: json['subject'] as String?,
      additionalData: json['additional_data'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'location': location,
      'building_id': buildingId,
      'teacher_id': teacherId,
      'group_id': groupId,
      'subject': subject,
      'additional_data': additionalData,
    };
  }

  ScheduleEvent copyWith({
    String? id,
    String? title,
    String? description,
    DateTime? startTime,
    DateTime? endTime,
    String? location,
    String? buildingId,
    String? teacherId,
    String? groupId,
    String? subject,
    Map<String, dynamic>? additionalData,
  }) {
    return ScheduleEvent(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      location: location ?? this.location,
      buildingId: buildingId ?? this.buildingId,
      teacherId: teacherId ?? this.teacherId,
      groupId: groupId ?? this.groupId,
      subject: subject ?? this.subject,
      additionalData: additionalData ?? this.additionalData,
    );
  }

  Duration get duration => endTime.difference(startTime);
  bool isOnDate(DateTime date) {
    return startTime.year == date.year &&
           startTime.month == date.month &&
           startTime.day == date.day;
  }
}

