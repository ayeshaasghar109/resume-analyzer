import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'analyze_result_screen.dart';

class AnalyzeScreen extends StatefulWidget {
  const AnalyzeScreen({super.key});

  @override
  State<AnalyzeScreen> createState() => _AnalyzeScreenState();
}

class _AnalyzeScreenState extends State<AnalyzeScreen> {
  final ApiService _api = ApiService();
  final TextEditingController _jobDescController = TextEditingController();
  PlatformFile? _pickedFile;
  bool _loading = false;

  @override
  void dispose() {
    _jobDescController.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
      withData: true, // required on web to get raw bytes instead of a path
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() => _pickedFile = result.files.first);
    }
  }

  Future<void> _analyze() async {
    if (_pickedFile == null || _pickedFile!.bytes == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Pick a PDF resume first')));
      return;
    }
    if (_jobDescController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Paste a job description first')));
      return;
    }

    setState(() => _loading = true);
    try {
      final result = await _api.analyze(
        fileBytes: _pickedFile!.bytes!,
        fileName: _pickedFile!.name,
        jobDescription: _jobDescController.text.trim(),
      );
      if (mounted) {
        Navigator.of(context)
            .push(MaterialPageRoute(builder: (_) => AnalyzeResultScreen(result: result)));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analyze Resume')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            OutlinedButton.icon(
              onPressed: _pickFile,
              icon: const Icon(Icons.upload_file),
              label: Text(_pickedFile == null ? 'Choose PDF resume' : _pickedFile!.name),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: TextField(
                controller: _jobDescController,
                maxLines: null,
                expands: true,
                textAlignVertical: TextAlignVertical.top,
                decoration: const InputDecoration(
                  labelText: 'Job description',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loading ? null : _analyze,
              child: _loading
                  ? const SizedBox(
                      height: 18,
                      width: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Analyze'),
            ),
          ],
        ),
      ),
    );
  }
}
