class Resume {
  final int? id;
  final String name;
  final String email;

  Resume({this.id, required this.name, required this.email});

  /// The backend's GET /resumes and GET /resumes/{id} return raw SQLite
  /// rows serialized as JSON arrays, e.g. [1, "Ayesha", "a@b.com"], not
  /// objects with keys. This parses that array by position: id, name, email.
  factory Resume.fromRow(List<dynamic> row) {
    return Resume(
      id: row[0] as int,
      name: row[1] as String,
      email: row[2] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
      };
}
