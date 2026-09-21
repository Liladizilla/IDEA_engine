import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/config.dart';
import '../domain/models.dart';
import 'repository.dart';

final repositoryProvider = Provider<IdeaRepository>((ref) => AppConfig.useMock ? MockRepository() : ApiRepository());

final bundleProvider = FutureProvider<Bundle>((ref) => ref.watch(repositoryProvider).loadBundle());

/// Saved opportunity ids, persisted on device.
class SavedNotifier extends Notifier<Set<String>> {
  static const _key = 'saved_ids';

  @override
  Set<String> build() {
    _load();
    return <String>{};
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    state = (prefs.getStringList(_key) ?? const []).toSet();
  }

  Future<void> toggle(String id) async {
    final next = {...state};
    next.contains(id) ? next.remove(id) : next.add(id);
    state = next;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_key, next.toList());
  }
}

final savedProvider = NotifierProvider<SavedNotifier, Set<String>>(SavedNotifier.new);

class ProfileNotifier extends Notifier<CreatorProfile> {
  static const _key = 'creator_profile';

  @override
  CreatorProfile build() {
    _load();
    return const CreatorProfile();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw != null) state = CreatorProfile.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    ref.read(profileLoadedProvider.notifier).state = true;
  }

  Future<void> update(CreatorProfile Function(CreatorProfile) change) async {
    state = change(state);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, jsonEncode(state.toJson()));
  }
}

final profileProvider = NotifierProvider<ProfileNotifier, CreatorProfile>(ProfileNotifier.new);

/// Flips to true once the stored profile has been read, so the router never guesses.
final profileLoadedProvider = StateProvider<bool>((ref) => false);
