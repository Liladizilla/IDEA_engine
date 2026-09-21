from app.intelligence.dissatisfaction import detect_dissatisfaction
from app.intelligence.questions import classify_signal, extract_questions, extract_signals
from app.intelligence.velocity import Velocity, classify_velocity, growth_ratio
from app.schemas.signals import SignalType
from tests.factories import post, video


def test_extracts_questions_and_ignores_statements():
    text = "I tried this yesterday. How do I deploy it? It was fun. Can I do this without a server?"
    assert extract_questions(text) == ["How do I deploy it?", "Can I do this without a server?"]


def test_spam_is_not_a_question():
    assert extract_questions("Check out my channel for free giveaways!!!") == []


def test_dissatisfaction_examples_from_spec():
    assert "every_tutorial" in detect_dissatisfaction("Every tutorial skips the deploy step")
    assert "nobody_explains" in detect_dissatisfaction("nobody explains how to host it")
    assert detect_dissatisfaction("Lovely video, thanks") == []


def test_complaint_without_question_mark_is_a_signal():
    item = post(1, "I've tried three AI automation tutorials and none actually show how to deploy the thing.", 1)
    signals = extract_signals(item)
    assert len(signals) == 1 and signals[0].dissatisfied and signals[0].signal_type == SignalType.COMPLAINT


def test_videos_are_answers_not_demand():
    assert extract_signals(video(1, "How do I build a website? Full tutorial")) == []


def test_classification():
    assert classify_signal("React vs Flutter for a first app?") == SignalType.COMPARISON
    assert classify_signal("Can someone recommend a good tutorial for this?") == SignalType.TUTORIAL_REQUEST
    assert classify_signal("How do I deploy this?") == SignalType.QUESTION


def test_velocity_spec_example_is_accelerating():
    assert classify_velocity([30, 42, 58, 91]) == Velocity.ACCELERATING


def test_velocity_states():
    assert classify_velocity([0, 0, 1, 0, 3, 6, 9, 12]) == Velocity.EMERGING
    assert classify_velocity([10, 11, 10, 11, 10, 11, 10, 11]) == Velocity.STABLE
    assert classify_velocity([40, 38, 30, 22, 15, 12, 9, 6]) == Velocity.DECLINING
    assert classify_velocity([1, 2]) == Velocity.UNKNOWN


def test_growth_ratio():
    assert growth_ratio([10, 10, 20, 20]) == 1.0
