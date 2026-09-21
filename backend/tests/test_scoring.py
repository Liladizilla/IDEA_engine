import pytest

from app.intelligence.scoring import (
    INVERTED, WEIGHTS, ClusterStats, EvidenceStats, InsufficientSignal, ScoreInputs, derive_inputs, scale_log, score_opportunity,
)

GOOD = dict(demand=90, question_density=90, growth=80, dissatisfaction=90, engagement=70, audience_value=70, recency=90, competition=30, answer_saturation=30)
ENOUGH = EvidenceStats(question_count=40, source_count=2)


def test_weights_sum_to_one():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)


def test_score_is_sum_of_factor_points():
    r = score_opportunity(ScoreInputs(**GOOD), ENOUGH)
    assert abs(sum(f.points for f in r.factors) - r.score) <= 0.5 + 0.01 * len(r.factors)


def test_bounds():
    worst = {k: (100 if k in INVERTED else 0) for k in WEIGHTS}
    best = {k: (0 if k in INVERTED else 100) for k in WEIGHTS}
    assert score_opportunity(ScoreInputs(**worst), ENOUGH).score == 0
    assert score_opportunity(ScoreInputs(**best), ENOUGH).score == 100


def test_more_competition_lowers_score():
    lo = score_opportunity(ScoreInputs(**{**GOOD, "competition": 10}), ENOUGH).score
    hi = score_opportunity(ScoreInputs(**{**GOOD, "competition": 90}), ENOUGH).score
    assert hi < lo


def test_more_demand_raises_score():
    lo = score_opportunity(ScoreInputs(**{**GOOD, "demand": 20}), ENOUGH).score
    hi = score_opportunity(ScoreInputs(**{**GOOD, "demand": 95}), ENOUGH).score
    assert hi > lo


def test_insufficient_signal_instead_of_fake_confidence():
    r = score_opportunity(ScoreInputs(**GOOD), EvidenceStats(question_count=5, source_count=1))
    assert isinstance(r, InsufficientSignal)
    assert r.questions_needed == 12 and r.sources_needed == 2


def test_single_source_is_not_enough_even_with_volume():
    assert isinstance(score_opportunity(ScoreInputs(**GOOD), EvidenceStats(500, 1)), InsufficientSignal)


def test_invalid_input_rejected():
    with pytest.raises(ValueError):
        ScoreInputs(**{**GOOD, "demand": 140})


def test_scale_log_shape():
    assert scale_log(0, 100) == 0
    assert scale_log(100, 100) == pytest.approx(100)
    assert scale_log(500, 100) == 100
    assert scale_log(10, 100) > 10  # early counts matter most


def test_derive_inputs_saturation_needs_quality():
    s = ClusterStats(50, 60, 0.4, 0.3, 20, 0.9, competing_videos=30, answer_count=30, answer_quality=0)
    assert derive_inputs(s).answer_saturation == 0
