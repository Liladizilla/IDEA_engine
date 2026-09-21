import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'icons/idea_icons.dart';
import 'l10n/strings.dart';
import 'theme/theme.dart';
import 'theme/tokens.dart';
import 'widgets/idea_logo.dart';

class Shell extends StatelessWidget {
  const Shell({super.key, required this.shell});
  final StatefulNavigationShell shell;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final s = context.s;
    final items = <(String, Widget Function(bool, Color))>[
      (s.navHome, (sel, col) => BulbMark(size: 26, color: col, lit: sel ? 1 : 0)),
      (s.navDiscover, (sel, col) => IdeaIcon(IdeaIcons.discover, color: col, size: 26)),
      (s.navRadar, (sel, col) => IdeaIcon(IdeaIcons.radar, color: col, size: 26)),
      (s.navSaved, (sel, col) => IdeaIcon(IdeaIcons.saved, color: col, size: 26, filled: sel)),
      (s.navProfile, (sel, col) => IdeaIcon(IdeaIcons.profile, color: col, size: 26)),
    ];
    return Scaffold(
      body: SafeArea(bottom: false, child: shell),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(color: c.ground, border: Border(top: BorderSide(color: c.line))),
        child: SafeArea(
          top: false,
          child: Row(children: [
            for (var i = 0; i < items.length; i++)
              Expanded(
                child: InkWell(
                  onTap: () => shell.goBranch(i, initialLocation: i == shell.currentIndex),
                  child: _NavItem(label: items[i].$1, selected: i == shell.currentIndex, icon: items[i].$2),
                ),
              ),
          ]),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({required this.label, required this.selected, required this.icon});
  final String label;
  final bool selected;
  final Widget Function(bool selected, Color color) icon;

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final color = selected ? c.text : c.textMuted;
    return Semantics(
      selected: selected,
      label: label,
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        Container(height: 2, width: 24, color: selected ? c.filament : Colors.transparent),
        const SizedBox(height: 10),
        icon(selected, color),
        const SizedBox(height: 4),
        Text(label, style: IdeaType.body(color, size: 12, weight: selected ? FontWeight.w600 : FontWeight.w400, height: 1.2)),
        const SizedBox(height: 10),
      ]),
    );
  }
}
