import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:idea_app/domain/models.dart';

void main() {
  test('sample bundle parses and scores are consistent with their factors', () {
    final raw = File('assets/mock/data.json').readAsStringSync();
    final bundle = Bundle.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    expect(bundle.isSample, isTrue);
    expect(bundle.opportunities, isNotEmpty);
    for (final o in bundle.opportunities) {
      final sum = o.factors.fold<double>(0, (a, f) => a + f.points);
      expect((sum - o.score).abs() <= 1.0, isTrue, reason: o.title);
      expect(o.evidence.every((e) => e.isSample), isTrue, reason: 'fixtures must never look like live sources');
    }
  });
}
