class JobSkill {
  final String skill;
  final String importance;
  final int minYears;
  final String experienceType;

  JobSkill({
    required this.skill,
    required this.importance,
    required this.minYears,
    required this.experienceType,
  });

  factory JobSkill.fromJson(Map<String, dynamic> json) {
    return JobSkill(
      skill: json['skill'] as String,
      importance: json['importance'] as String,
      minYears: json['min_years'] as int,
      experienceType: json['experience_type'] as String,
    );
  }
}

class SkillMatch {
  final JobSkill jobSkill;
  final String? resumeSkill;
  final double matchingScore;
  final String category;
  final int experienceMonths;
  final String requirementSatisfaction;

  SkillMatch({
    required this.jobSkill,
    required this.resumeSkill,
    required this.matchingScore,
    required this.category,
    required this.experienceMonths,
    required this.requirementSatisfaction,
  });

  factory SkillMatch.fromJson(Map<String, dynamic> json) {
    return SkillMatch(
      jobSkill: JobSkill.fromJson(json['job_skill'] as Map<String, dynamic>),
      resumeSkill: json['resume_skill'] as String?,
      matchingScore: (json['matching_score'] as num).toDouble(),
      category: json['category'] as String,
      experienceMonths: json['experience_months'] as int,
      requirementSatisfaction: json['requirement_satisfaction'] as String,
    );
  }
}

class SkillBreakdownCategory {
  final int total;
  final int matched;
  final int missing;

  SkillBreakdownCategory({
    required this.total,
    required this.matched,
    required this.missing,
  });

  factory SkillBreakdownCategory.fromJson(Map<String, dynamic> json) {
    return SkillBreakdownCategory(
      total: json['total'] as int,
      matched: json['matched'] as int,
      missing: json['missing'] as int,
    );
  }
}

class SkillBreakdown {
  final SkillBreakdownCategory requiredSkills;
  final SkillBreakdownCategory preferredSkills;
  final SkillBreakdownCategory unspecifiedSkills;

  SkillBreakdown({
    required this.requiredSkills,
    required this.preferredSkills,
    required this.unspecifiedSkills,
  });

  factory SkillBreakdown.fromJson(Map<String, dynamic> json) {
    return SkillBreakdown(
      requiredSkills:
          SkillBreakdownCategory.fromJson(json['required_skills'] as Map<String, dynamic>),
      preferredSkills:
          SkillBreakdownCategory.fromJson(json['preferred_skills'] as Map<String, dynamic>),
      unspecifiedSkills:
          SkillBreakdownCategory.fromJson(json['unspecified_skills'] as Map<String, dynamic>),
    );
  }
}

class AnalyzeSummary {
  final List<SkillMatch> matchedSkills;
  final List<SkillMatch> requiredMissingSkills;
  final List<SkillMatch> preferredMissingSkills;
  final List<SkillMatch> missingSkills;
  final List<SkillMatch> relatedSkills;

  AnalyzeSummary({
    required this.matchedSkills,
    required this.requiredMissingSkills,
    required this.preferredMissingSkills,
    required this.missingSkills,
    required this.relatedSkills,
  });

  factory AnalyzeSummary.fromJson(Map<String, dynamic> json) {
    List<SkillMatch> parseList(String key) {
      return (json[key] as List<dynamic>)
          .map((e) => SkillMatch.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    return AnalyzeSummary(
      matchedSkills: parseList('matched_skills'),
      requiredMissingSkills: parseList('required_missing_skills'),
      preferredMissingSkills: parseList('preferred_missing_skills'),
      missingSkills: parseList('missing_skills'),
      relatedSkills: parseList('related_skills'),
    );
  }
}

class AnalyzeResult {
  final List<SkillMatch> analysis;
  final AnalyzeSummary summary;
  final SkillBreakdown skillBreakdown;
  final double? overallScore;

  AnalyzeResult({
    required this.analysis,
    required this.summary,
    required this.skillBreakdown,
    required this.overallScore,
  });

  factory AnalyzeResult.fromJson(Map<String, dynamic> json) {
    return AnalyzeResult(
      analysis: (json['analysis'] as List<dynamic>)
          .map((e) => SkillMatch.fromJson(e as Map<String, dynamic>))
          .toList(),
      summary: AnalyzeSummary.fromJson(json['summary'] as Map<String, dynamic>),
      skillBreakdown:
          SkillBreakdown.fromJson(json['skill_breakdown'] as Map<String, dynamic>),
      overallScore:
          json['overall_score'] == null ? null : (json['overall_score'] as num).toDouble(),
    );
  }
}
