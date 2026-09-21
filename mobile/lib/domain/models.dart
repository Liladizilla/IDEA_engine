// coverage:ignore-file

double _d(Object? v) => (v as num?)?.toDouble() ?? 0;
int _i(Object? v) => (v as num?)?.toInt() ?? 0;
List<T> _list<T>(Object? v, T Function(Map<String, dynamic>) f) =>
    ((v as List?) ?? const []).map((e) => f(e as Map<String, dynamic>)).toList();

class Factor {
  const Factor({required this.key, required this.label, required this.value, required this.weight, required this.inverted, required this.points, required this.maxPoints, required this.note});

  final String key;
  final String label;
  final double value;
  final double weight;
  final bool inverted;
  final double points;
  final double maxPoints;
  final String note;

  factory Factor.fromJson(Map<String, dynamic> j) => Factor(
        key: j['key'] as String,
        label: j['label'] as String,
        value: _d(j['value']),
        weight: _d(j['weight']),
        inverted: j['inverted'] as bool? ?? false,
        points: _d(j['points']),
        maxPoints: _d(j['max_points']),
        note: j['note'] as String? ?? '',
      );
}

class Evidence {
  const Evidence({required this.source, required this.kind, required this.where, required this.excerpt, required this.engagement, required this.daysAgo, required this.url});

  final String source;
  final String kind;
  final String where;
  final String excerpt;
  final String engagement;
  final int daysAgo;
  final String url;

  /// Fixture evidence uses sample:// URLs and must never be opened or presented as real.
  bool get isSample => url.startsWith('sample://');

  factory Evidence.fromJson(Map<String, dynamic> j) => Evidence(
        source: j['source'] as String,
        kind: j['kind'] as String,
        where: j['where'] as String? ?? '',
        excerpt: j['excerpt'] as String,
        engagement: j['engagement'] as String? ?? '',
        daysAgo: _i(j['days_ago']),
        url: j['url'] as String? ?? '',
      );
}

class IdeaConcept {
  const IdeaConcept({required this.title, required this.hook, required this.format, required this.difficulty, required this.whyNow});

  final String title;
  final String hook;
  final String format;
  final String difficulty;
  final String whyNow;

  factory IdeaConcept.fromJson(Map<String, dynamic> j) => IdeaConcept(
        title: j['title'] as String,
        hook: j['hook'] as String,
        format: j['format'] as String,
        difficulty: j['difficulty'] as String,
        whyNow: j['why_now'] as String,
      );
}

class OppStats {
  const OppStats({required this.relatedQuestions, required this.askers, required this.communities, required this.growth7d, required this.velocity, required this.sources});

  final int relatedQuestions;
  final int askers;
  final int communities;
  final double growth7d;
  final String velocity;
  final Map<String, int> sources;

  factory OppStats.fromJson(Map<String, dynamic> j) => OppStats(
        relatedQuestions: _i(j['related_questions']),
        askers: _i(j['askers']),
        communities: _i(j['communities']),
        growth7d: _d(j['growth_7d']),
        velocity: j['velocity'] as String? ?? 'unknown',
        sources: ((j['sources'] as Map?) ?? const {}).map((k, v) => MapEntry(k as String, _i(v))),
      );
}

class Opportunity {
  const Opportunity({
    required this.id,
    required this.title,
    required this.coreQuestion,
    required this.audience,
    required this.whyDetected,
    required this.score,
    required this.band,
    required this.confidence,
    required this.factors,
    required this.stats,
    required this.trend,
    required this.competitionLevel,
    required this.competitionNote,
    required this.creators,
    required this.answerGapLevel,
    required this.answerGapNote,
    required this.evidence,
    required this.relatedQuestions,
    required this.ideas,
  });

  final String id;
  final String title;
  final String coreQuestion;
  final String audience;
  final String whyDetected;
  final int score;
  final String band;
  final String confidence;
  final List<Factor> factors;
  final OppStats stats;
  final List<int> trend;
  final String competitionLevel;
  final String competitionNote;
  final int creators;
  final String answerGapLevel;
  final String answerGapNote;
  final List<Evidence> evidence;
  final List<String> relatedQuestions;
  final List<IdeaConcept> ideas;

  factory Opportunity.fromJson(Map<String, dynamic> j) {
    final comp = j['competition'] as Map<String, dynamic>;
    final gap = j['answer_gap'] as Map<String, dynamic>;
    return Opportunity(
      id: j['id'] as String,
      title: j['title'] as String,
      coreQuestion: j['core_question'] as String,
      audience: j['audience'] as String,
      whyDetected: j['why_detected'] as String,
      score: _i(j['score']),
      band: j['band'] as String,
      confidence: j['confidence'] as String,
      factors: _list(j['factors'], Factor.fromJson),
      stats: OppStats.fromJson(j['stats'] as Map<String, dynamic>),
      trend: ((j['trend'] as List?) ?? const []).map(_i).toList(),
      competitionLevel: comp['level'] as String,
      competitionNote: comp['note'] as String,
      creators: _i(comp['creators']),
      answerGapLevel: gap['level'] as String,
      answerGapNote: gap['note'] as String,
      evidence: _list(j['evidence'], Evidence.fromJson),
      relatedQuestions: ((j['related_questions'] as List?) ?? const []).cast<String>(),
      ideas: _list(j['ideas'], IdeaConcept.fromJson),
    );
  }
}

class RadarSignal {
  const RadarSignal({required this.question, required this.opportunityId, required this.sources, required this.momentum, required this.answerGap, required this.minutesAgo});

  final String question;
  final String? opportunityId;
  final List<String> sources;
  final double momentum;
  final String answerGap;
  final int minutesAgo;

  factory RadarSignal.fromJson(Map<String, dynamic> j) => RadarSignal(
        question: j['question'] as String,
        opportunityId: j['opportunity_id'] as String?,
        sources: ((j['sources'] as List?) ?? const []).cast<String>(),
        momentum: _d(j['momentum']),
        answerGap: j['answer_gap'] as String? ?? 'unknown',
        minutesAgo: _i(j['minutes_ago']),
      );
}

class NewQuestion {
  const NewQuestion({required this.question, required this.source, required this.minutesAgo});

  final String question;
  final String source;
  final int minutesAgo;

  factory NewQuestion.fromJson(Map<String, dynamic> j) =>
      NewQuestion(question: j['question'] as String, source: j['source'] as String, minutesAgo: _i(j['minutes_ago']));
}

class Niche {
  const Niche({required this.id, required this.title, required this.audience, required this.why, required this.opportunityIds});

  final String id;
  final String title;
  final String audience;
  final List<String> why;
  final List<String> opportunityIds;

  factory Niche.fromJson(Map<String, dynamic> j) => Niche(
        id: j['id'] as String,
        title: j['title'] as String,
        audience: j['audience'] as String,
        why: ((j['why'] as List?) ?? const []).cast<String>(),
        opportunityIds: ((j['opportunity_ids'] as List?) ?? const []).cast<String>(),
      );
}

class InsufficientScope {
  const InsufficientScope({required this.scope, required this.reason, required this.questionsFound, required this.questionsNeeded, required this.sourcesFound, required this.sourcesNeeded});

  final String scope;
  final String reason;
  final int questionsFound;
  final int questionsNeeded;
  final int sourcesFound;
  final int sourcesNeeded;

  factory InsufficientScope.fromJson(Map<String, dynamic> j) => InsufficientScope(
        scope: j['scope'] as String,
        reason: j['reason'] as String,
        questionsFound: _i(j['questions_found']),
        questionsNeeded: _i(j['questions_needed']),
        sourcesFound: _i(j['sources_found']),
        sourcesNeeded: _i(j['sources_needed']),
      );
}

class Bundle {
  const Bundle({
    required this.isSample,
    required this.opportunities,
    required this.radar,
    required this.newQuestions,
    required this.niches,
    required this.insufficient,
    required this.categories,
    this.offline = false,
  });

  final bool isSample;
  final List<Opportunity> opportunities;
  final List<RadarSignal> radar;
  final List<NewQuestion> newQuestions;
  final List<Niche> niches;
  final List<InsufficientScope> insufficient;
  final List<String> categories;

  /// True when the network failed and this came from the on-device cache.
  final bool offline;

  Opportunity? opportunity(String id) {
    for (final o in opportunities) {
      if (o.id == id) return o;
    }
    return null;
  }

  Bundle asOffline() => Bundle(
        isSample: isSample,
        opportunities: opportunities,
        radar: radar,
        newQuestions: newQuestions,
        niches: niches,
        insufficient: insufficient,
        categories: categories,
        offline: true,
      );

  factory Bundle.fromJson(Map<String, dynamic> j) => Bundle(
        isSample: j['is_sample'] as bool? ?? false,
        opportunities: _list(j['opportunities'], Opportunity.fromJson),
        radar: _list(j['radar'], RadarSignal.fromJson),
        newQuestions: _list(j['new_questions'], NewQuestion.fromJson),
        niches: _list(j['niches'], Niche.fromJson),
        insufficient: _list(j['insufficient'], InsufficientScope.fromJson),
        categories: ((j['categories'] as List?) ?? const []).cast<String>(),
      );
}

/// What the person told us during onboarding. Persisted on device; synced to the backend later.
class CreatorProfile {
  const CreatorProfile({this.platforms = const [], this.hasNiche, this.niche = '', this.audience = '', this.notify = 'daily', this.done = false});

  final List<String> platforms;
  final bool? hasNiche;
  final String niche;
  final String audience;
  final String notify;
  final bool done;

  CreatorProfile copyWith({List<String>? platforms, bool? hasNiche, String? niche, String? audience, String? notify, bool? done}) => CreatorProfile(
        platforms: platforms ?? this.platforms,
        hasNiche: hasNiche ?? this.hasNiche,
        niche: niche ?? this.niche,
        audience: audience ?? this.audience,
        notify: notify ?? this.notify,
        done: done ?? this.done,
      );

  Map<String, dynamic> toJson() => {'platforms': platforms, 'hasNiche': hasNiche, 'niche': niche, 'audience': audience, 'notify': notify, 'done': done};

  factory CreatorProfile.fromJson(Map<String, dynamic> j) => CreatorProfile(
        platforms: ((j['platforms'] as List?) ?? const []).cast<String>(),
        hasNiche: j['hasNiche'] as bool?,
        niche: j['niche'] as String? ?? '',
        audience: j['audience'] as String? ?? '',
        notify: j['notify'] as String? ?? 'daily',
        done: j['done'] as bool? ?? false,
      );
}
