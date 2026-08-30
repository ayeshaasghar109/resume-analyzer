import 'package:flutter/material.dart';
import '../models/analyze_result.dart';

class AnalyzeResultScreen extends StatelessWidget {
  final AnalyzeResult result;
  const AnalyzeResultScreen({super.key, required this.result});

  Color _categoryColor(String category) {
    switch (category) {
      case 'Very Strong':
        return Colors.green.shade700;
      case 'Strong':
        return Colors.green.shade400;
      case 'Partial':
        return Colors.orange.shade600;
      case 'Somewhat Related':
        return Colors.orange.shade300;
      case 'Missing':
        return Colors.red.shade400;
      default:
        return Colors.grey;
    }
  }

  Widget _breakdownRow(String label, SkillBreakdownCategory c) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text('${c.matched} / ${c.total} matched'),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final score = result.overallScore;
    return Scaffold(
      appBar: AppBar(title: const Text('Analysis Result')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    score == null
                        ? 'Overall score: n/a'
                        : 'Overall score: ${score.toStringAsFixed(1)}%',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const Divider(height: 24),
                  _breakdownRow('Required', result.skillBreakdown.requiredSkills),
                  _breakdownRow('Preferred', result.skillBreakdown.preferredSkills),
                  _breakdownRow('Unspecified', result.skillBreakdown.unspecifiedSkills),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text('Skill-by-skill breakdown', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          ...result.analysis.map(
            (m) => Card(
              child: ListTile(
                title: Text(m.jobSkill.skill),
                subtitle: Text(
                  m.resumeSkill == null
                      ? 'No match found'
                      : 'Matched: ${m.resumeSkill} · ${m.experienceMonths} mo experience · needs met: ${m.requirementSatisfaction}',
                ),
                trailing: Chip(
                  label: Text(m.category),
                  backgroundColor: _categoryColor(m.category).withOpacity(0.15),
                  labelStyle: TextStyle(color: _categoryColor(m.category)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
