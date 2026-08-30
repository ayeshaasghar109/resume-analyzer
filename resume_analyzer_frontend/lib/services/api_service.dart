import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/resume.dart';
import '../models/analyze_result.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  // Point this at your running FastAPI server.
  // 127.0.0.1 works for `flutter run -d chrome` against a local uvicorn.
  // Change this before deploying either side anywhere else.
  static const String baseUrl = 'http://127.0.0.1:8000';

  Future<List<Resume>> getResumes() async {
    final res = await http.get(Uri.parse('$baseUrl/resumes'));
    if (res.statusCode != 200) {
      throw ApiException('Failed to load resumes (${res.statusCode})');
    }
    final data = jsonDecode(res.body) as List<dynamic>;
    return data.map((row) => Resume.fromRow(row as List<dynamic>)).toList();
  }

  Future<void> createResume(Resume resume) async {
    final res = await http.post(
      Uri.parse('$baseUrl/resumes'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(resume.toJson()),
    );
    if (res.statusCode != 200) {
      throw ApiException('Failed to create resume (${res.statusCode})');
    }
    // The backend only returns {"message": "success"} here, not the new
    // row or its id, so the caller should refetch the list afterward.
  }

  Future<void> updateResume(int id, Resume resume) async {
    final res = await http.put(
      Uri.parse('$baseUrl/resumes/$id'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(resume.toJson()),
    );
    if (res.statusCode != 200) {
      throw ApiException('Failed to update resume (${res.statusCode})');
    }
  }

  Future<void> deleteResume(int id) async {
    final res = await http.delete(Uri.parse('$baseUrl/resumes/$id'));
    if (res.statusCode != 200) {
      throw ApiException('Failed to delete resume (${res.statusCode})');
    }
  }

  Future<AnalyzeResult> analyze({
    required List<int> fileBytes,
    required String fileName,
    required String jobDescription,
  }) async {
    final uri = Uri.parse('$baseUrl/analyze');
    final request = http.MultipartRequest('POST', uri)
      ..fields['job_description'] = jobDescription
      ..files.add(http.MultipartFile.fromBytes(
        'file',
        fileBytes,
        filename: fileName,
      ));

    final streamed = await request.send();
    final res = await http.Response.fromStream(streamed);

    if (res.statusCode != 200) {
      throw ApiException('Analysis failed (${res.statusCode}): ${res.body}');
    }
    return AnalyzeResult.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
  }
}
