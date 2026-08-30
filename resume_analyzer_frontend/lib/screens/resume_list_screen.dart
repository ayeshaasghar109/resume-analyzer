import 'package:flutter/material.dart';
import '../models/resume.dart';
import '../services/api_service.dart';
import 'resume_form_screen.dart';
import 'analyze_screen.dart';

class ResumeListScreen extends StatefulWidget {
  const ResumeListScreen({super.key});

  @override
  State<ResumeListScreen> createState() => _ResumeListScreenState();
}

class _ResumeListScreenState extends State<ResumeListScreen> {
  final ApiService _api = ApiService();
  late Future<List<Resume>> _resumesFuture;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _resumesFuture = _api.getResumes();
    });
  }

  Future<void> _delete(Resume resume) async {
    try {
      await _api.deleteResume(resume.id!);
      _refresh();
    } catch (e) {
      _showError(e.toString());
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _openForm({Resume? resume}) async {
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => ResumeFormScreen(resume: resume)),
    );
    if (saved == true) _refresh();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Resumes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.analytics_outlined),
            tooltip: 'Analyze a resume',
            onPressed: () {
              Navigator.of(context)
                  .push(MaterialPageRoute(builder: (_) => const AnalyzeScreen()));
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refresh(),
        child: FutureBuilder<List<Resume>>(
          future: _resumesFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(child: Text('Error: ${snapshot.error}'));
            }
            final resumes = snapshot.data ?? [];
            if (resumes.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 120),
                  Center(child: Text('No resumes yet. Tap + to add one.')),
                ],
              );
            }
            return ListView.builder(
              itemCount: resumes.length,
              itemBuilder: (context, index) {
                final r = resumes[index];
                return ListTile(
                  title: Text(r.name),
                  subtitle: Text(r.email),
                  onTap: () => _openForm(resume: r),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline),
                    onPressed: () => _delete(r),
                  ),
                );
              },
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _openForm(),
        child: const Icon(Icons.add),
      ),
    );
  }
}
