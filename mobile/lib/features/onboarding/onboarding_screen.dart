import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/icons/idea_icons.dart';
import '../../core/l10n/strings.dart';
import '../../core/theme/theme.dart';
import '../../core/theme/tokens.dart';
import '../../core/widgets/basics.dart';
import '../../core/widgets/inputs.dart';
import '../../core/widgets/score.dart';
import '../../data/providers.dart';

const _platforms = ['YouTube', 'TikTok', 'Instagram', 'Blog', 'Newsletter', 'Podcast', 'Business', 'Nothing yet'];
const _notify = {'daily': 'Daily', 'three_weekly': '3 times weekly', 'weekly': 'Weekly', 'important': 'Important signals only'};

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});
  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  int _step = 0;
  final _picked = <String>{};
  bool? _hasNiche;
  final _niche = TextEditingController();
  final _audience = TextEditingController();
  String _notifyKey = 'daily';

  static const _last = 3;

  bool get _canContinue {
    switch (_step) {
      case 0:
        return _picked.isNotEmpty;
      case 1:
        return _hasNiche == false || (_hasNiche == true && _niche.text.trim().isNotEmpty);
      default:
        return true;
    }
  }

  Future<void> _next() async {
    if (_step < _last) {
      setState(() => _step++);
      return;
    }
    await ref.read(profileProvider.notifier).update((p) => p.copyWith(platforms: _picked.toList(), hasNiche: _hasNiche, niche: _niche.text.trim(), audience: _audience.text.trim(), notify: _notify[_notifyKey], done: true));
    if (!mounted) return;
    context.go(_hasNiche == false ? '/scan' : '/home');
  }

  @override
  void dispose() {
    _niche.dispose();
    _audience.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    final titles = [s.onbCreateQ, s.onbNicheQ, s.onbAudienceQ, s.onbNotifyQ];
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(Gap.xl),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              if (_step > 0)
                InkWell(onTap: () => setState(() => _step--), child: const Padding(padding: EdgeInsets.only(right: Gap.m), child: IdeaIcon(IdeaIcons.back)))
              else
                const SizedBox(width: 0),
              Expanded(child: SegmentBar(value: (_step + 1) / 4 * 100, height: 4)),
            ]),
            const SizedBox(height: Gap.xxl),
            Text(titles[_step], style: IdeaType.headline(c.text, size: 38)),
            const SizedBox(height: Gap.xl),
            Expanded(child: SingleChildScrollView(child: _body(context))),
            IdeaButton(label: _step == _last ? s.onbFinish : s.onbContinue, onPressed: _canContinue ? _next : null),
          ]),
        ),
      ),
    );
  }

  Widget _body(BuildContext context) {
    final s = context.s;
    switch (_step) {
      case 0:
        return Column(children: [
          for (final p in _platforms) ChoiceRow(label: p, selected: _picked.contains(p), onTap: () => setState(() => _picked.contains(p) ? _picked.remove(p) : _picked.add(p))),
        ]);
      case 1:
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          ChoiceRow(label: s.onbNicheYes, selected: _hasNiche == true, onTap: () => setState(() => _hasNiche = true)),
          ChoiceRow(label: s.onbNicheNo, selected: _hasNiche == false, onTap: () => setState(() => _hasNiche = false)),
          if (_hasNiche == true) ...[
            const SizedBox(height: Gap.xl),
            TextField(controller: _niche, onChanged: (_) => setState(() {}), decoration: InputDecoration(hintText: s.onbNicheField)),
          ],
        ]);
      case 2:
        return TextField(controller: _audience, minLines: 2, maxLines: 4, decoration: InputDecoration(hintText: s.onbAudienceHint));
      default:
        return Column(children: [
          for (final e in _notify.entries) ChoiceRow(label: e.value, selected: _notifyKey == e.key, onTap: () => setState(() => _notifyKey = e.key)),
        ]);
    }
  }
}
