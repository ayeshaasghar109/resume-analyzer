import 'package:flutter/material.dart';
import '../models/resume.dart';
import '../services/api_service.dart';

class ResumeFormScreen extends StatefulWidget {
  final Resume? resume;
  const ResumeFormScreen({super.key, this.resume});

  @override
  State<ResumeFormScreen> createState() => _ResumeFormScreenState();
}

class _ResumeFormScreenState extends State<ResumeFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _api = ApiService();
  late final TextEditingController _nameController;
  late final TextEditingController _emailController;
  bool _saving = false;

  bool get _isEditing => widget.resume != null;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.resume?.name ?? '');
    _emailController = TextEditingController(text: widget.resume?.email ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    final resume = Resume(
      id: widget.resume?.id,
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
    );
    try {
      if (_isEditing) {
        await _api.updateResume(resume.id!, resume);
      } else {
        await _api.createResume(resume);
      }
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_isEditing ? 'Edit Resume' : 'Add Resume')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Name is required' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Email is required' : null,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _saving ? null : _save,
                child: _saving
                    ? const SizedBox(
                        height: 18,
                        width: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Save'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
