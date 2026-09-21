import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/providers.dart';
import '../../domain/models.dart';
import '../l10n/strings.dart';
import '../theme/theme.dart';
import '../theme/tokens.dart';
import 'basics.dart';

/// Loads the bundle and handles the three states every screen shares:
/// loading (skeleton shaped like the content), failure (says what happened and what still works), and offline.
class BundleView extends ConsumerWidget {
  const BundleView({super.key, required this.builder});
  final Widget Function(BuildContext context, Bundle bundle) builder;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = context.s;
    return ref.watch(bundleProvider).when(
          loading: () => const _Skeleton(),
          error: (e, _) => Center(
            child: Padding(
              padding: const EdgeInsets.all(Gap.xl),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Text(s.errorLoad, textAlign: TextAlign.center, style: IdeaType.body(context.c.text, size: 16)),
                const SizedBox(height: Gap.l),
                IdeaButton(label: s.retry, expand: false, onPressed: () => ref.invalidate(bundleProvider)),
              ]),
            ),
          ),
          data: (b) => Column(children: [
            if (b.offline) SampleStrip(label: 'Offline', detail: s.offlineNotice),
            if (b.isSample && !b.offline) SampleStrip(label: s.sampleData, detail: 'Fixtures, not real evidence.'),
            Expanded(child: builder(context, b)),
          ]),
        );
  }
}

class _Skeleton extends StatelessWidget {
  const _Skeleton();
  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Padding(
      padding: const EdgeInsets.all(Gap.xl),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Container(width: 180, height: 36, color: c.raised),
        const SizedBox(height: Gap.xl),
        for (var i = 0; i < 4; i++) ...[
          Row(children: [
            Container(width: 48, height: 44, color: c.raised),
            const SizedBox(width: Gap.l),
            Expanded(child: Container(height: 44, color: c.raised)),
          ]),
          const SizedBox(height: Gap.xl),
        ],
      ]),
    );
  }
}
