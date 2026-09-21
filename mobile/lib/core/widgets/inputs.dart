import 'package:flutter/material.dart';

import '../icons/idea_icons.dart';
import '../l10n/strings.dart';
import '../theme/theme.dart';
import '../theme/tokens.dart';
import 'basics.dart';

class IdeaSearchField extends StatelessWidget {
  const IdeaSearchField({super.key, required this.controller, required this.onChanged, required this.onFilter, this.filtersActive = false});
  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  final VoidCallback onFilter;
  final bool filtersActive;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Row(children: [
      Expanded(
        child: TextField(
          controller: controller,
          onChanged: onChanged,
          style: IdeaType.body(c.text, size: 16),
          decoration: InputDecoration(
            hintText: context.s.searchHint,
            prefixIcon: Padding(padding: const EdgeInsets.all(Gap.m), child: IdeaIcon(IdeaIcons.discover, size: 20, color: c.textMuted)),
          ),
        ),
      ),
      const SizedBox(width: Gap.s),
      Material(
        color: filtersActive ? c.filament : c.surface,
        shape: RoundedRectangleBorder(borderRadius: kBorder, side: BorderSide(color: filtersActive ? c.filament : c.line)),
        child: InkWell(
          onTap: onFilter,
          borderRadius: kBorder,
          child: SizedBox(width: 52, height: 52, child: Center(child: IdeaIcon(IdeaIcons.filter, size: 22, color: filtersActive ? c.onFilament : c.text))),
        ),
      ),
    ]);
  }
}

class DiscoverFilter {
  const DiscoverFilter({this.minScore = 0, this.source});
  final int minScore;
  final String? source;
  bool get active => minScore > 0 || source != null;
}

Future<DiscoverFilter?> showFilterSheet(BuildContext context, DiscoverFilter initial) {
  return showModalBottomSheet<DiscoverFilter>(
    context: context,
    isScrollControlled: true,
    builder: (_) => _FilterSheet(initial: initial),
  );
}

class _FilterSheet extends StatefulWidget {
  const _FilterSheet({required this.initial});
  final DiscoverFilter initial;
  @override
  State<_FilterSheet> createState() => _FilterSheetState();
}

class _FilterSheetState extends State<_FilterSheet> {
  late double _min = widget.initial.minScore.toDouble();
  late String? _source = widget.initial.source;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(Gap.xl),
        child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(s.filters, style: IdeaType.headline(c.text, size: 26)),
          const SizedBox(height: Gap.l),
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Text(s.minScore, style: IdeaType.body(c.text, size: 15, weight: FontWeight.w500)),
            Text('${_min.round()}', style: IdeaType.numeral(c.text, 22)),
          ]),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(activeTrackColor: c.filament, inactiveTrackColor: c.line, thumbColor: c.filament, overlayColor: Colors.transparent, trackHeight: 3),
            child: Slider(value: _min, min: 0, max: 100, divisions: 20, onChanged: (v) => setState(() => _min = v)),
          ),
          const SizedBox(height: Gap.m),
          Wrap(spacing: Gap.s, runSpacing: Gap.s, children: [
            for (final entry in const {null: 'All sources', 'youtube': 'YouTube', 'reddit': 'Reddit'}.entries)
              _Choice(label: entry.value, selected: _source == entry.key, onTap: () => setState(() => _source = entry.key)),
          ]),
          const SizedBox(height: Gap.xl),
          Row(children: [
            Expanded(child: IdeaButton(label: s.reset, primary: false, onPressed: () => Navigator.pop(context, const DiscoverFilter()))),
            const SizedBox(width: Gap.m),
            Expanded(child: IdeaButton(label: s.apply, onPressed: () => Navigator.pop(context, DiscoverFilter(minScore: _min.round(), source: _source)))),
          ]),
        ]),
      ),
    );
  }
}

class _Choice extends StatelessWidget {
  const _Choice({required this.label, required this.selected, required this.onTap});
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Material(
      color: selected ? c.text : Colors.transparent,
      shape: RoundedRectangleBorder(borderRadius: kBorder, side: BorderSide(color: selected ? c.text : c.line)),
      child: InkWell(
        onTap: onTap,
        borderRadius: kBorder,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: Gap.l, vertical: Gap.m),
          child: Text(label, style: IdeaType.body(selected ? c.ground : c.text, size: 14, weight: FontWeight.w600, height: 1.2)),
        ),
      ),
    );
  }
}

/// Single-choice row used by onboarding and pickers.
class ChoiceRow extends StatelessWidget {
  const ChoiceRow({super.key, required this.label, required this.selected, required this.onTap});
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: Gap.l),
        decoration: BoxDecoration(border: Border(bottom: BorderSide(color: c.line))),
        child: Row(children: [
          Expanded(child: Text(label, style: IdeaType.body(c.text, size: 17, weight: selected ? FontWeight.w600 : FontWeight.w400))),
          if (selected) IdeaIcon(IdeaIcons.check, size: 22, color: c.accentText),
        ]),
      ),
    );
  }
}
