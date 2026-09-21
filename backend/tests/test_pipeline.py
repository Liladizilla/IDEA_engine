from app.ai.embeddings import HashingEmbedder
from app.intelligence.pipeline import run_pipeline
from app.intelligence.velocity import Velocity
from tests.factories import NOW, noisy_dataset, post, strong_cluster_items


async def test_finds_the_real_opportunity_in_noise():
    out = await run_pipeline(noisy_dataset(), HashingEmbedder(), now=NOW)
    assert out.candidates, "expected at least one opportunity"
    top = out.candidates[0]
    assert "website" in top.cluster.representative.question.lower()
    assert len(top.cluster.sources) == 2
    assert top.velocity in (Velocity.ACCELERATING, Velocity.EMERGING)
    assert top.result.score > 0


async def test_unrelated_singles_never_become_opportunities():
    out = await run_pipeline(noisy_dataset(), HashingEmbedder(), now=NOW)
    for c in out.candidates:
        text = c.cluster.representative.question.lower()
        assert "bicycle" not in text and "violin" not in text and "moon" not in text


async def test_one_person_repeating_does_not_inflate_demand():
    repeats = [post(i, "Why does my sourdough starter smell like acetone?", 1, author="same_person") for i in range(30)]
    out = await run_pipeline(repeats, HashingEmbedder(), now=NOW)
    assert out.candidates == []


async def test_insufficient_evidence_yields_no_fake_opportunity():
    few = strong_cluster_items()[:5]
    out = await run_pipeline(few, HashingEmbedder(), now=NOW)
    assert out.candidates == []


async def test_competition_comes_from_real_videos_in_the_data():
    out = await run_pipeline(noisy_dataset(), HashingEmbedder(), now=NOW)
    assert out.candidates[0].stats.competing_videos >= 1
