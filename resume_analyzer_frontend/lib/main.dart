import 'package:flutter/material.dart';
import 'screens/resume_list_screen.dart';

void main() {
  runApp(const ResumeAnalyzerApp());
}

class ResumeAnalyzerApp extends StatelessWidget {
  const ResumeAnalyzerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Resume Analyzer',
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      home: const ResumeListScreen(),
    );
  }
}
