"""Builds app/sample/data.json: sample fixtures for the API, the Flutter mock repository and the design preview.

Scores come from the real scoring engine, so the numbers on screen are the numbers the engine produces.
Everything here is FIXTURE data (is_sample = true). It is never presented as real evidence.
Run from backend/:  PYTHONPATH=. python scripts/generate_sample.py
"""
import json
import shutil
from pathlib import Path

from app.intelligence.scoring import EvidenceStats, ScoreInputs, score_opportunity
from app.intelligence.velocity import classify_velocity

OPPS = [
    dict(
        id="opp-ai-support-smb",
        title="Affordable AI automation for small businesses",
        core_question="How can a small business automate customer replies without paying an agency?",
        audience="Small business owners",
        why="People keep asking how to set this up cheaply, and the tutorials they find stop before anything is deployed.",
        inputs=dict(demand=92, question_density=94, growth=88, dissatisfaction=94, engagement=78, audience_value=82, recency=95, competition=40, answer_saturation=30),
        notes=dict(
            demand="118 different people asked, across 4 communities.",
            dissatisfaction="Over a third of the questions say a tutorial did not work or stopped short.",
            competition="18 creators cover the general topic; few cover the small-business case.",
            answer_saturation="Existing videos are mostly concept demos. Answer quality not yet assessed by AI.",
        ),
        counts=[4, 5, 4, 6, 7, 8, 9, 9, 11, 12, 14, 15, 18, 20],
        sources=dict(youtube=61, reddit=81), communities=4, askers=118,
        competition=dict(level="medium", creators=18, note="Many videos explain the concept. Few show a working setup for a shop with one employee."),
        answer_gap=dict(level="high", note="Most answers demonstrate a tool, then stop before deployment and cost."),
        evidence=[
            ("reddit", "post", "r/smallbusiness", "I've tried three AI automation tutorials and none actually show how to deploy the thing.", "212 upvotes, 64 comments", 2),
            ("youtube", "comment", "Comment on a 24 min tutorial", "Great demo, but where does this run once my laptop is closed? Nobody explains that part.", "88 likes", 4),
            ("reddit", "post", "r/Entrepreneur", "Quoted 3,000 a month by an agency for what looks like a simple auto-reply setup. Is there a cheaper way?", "141 upvotes, 52 comments", 6),
            ("youtube", "comment", "Comment on a 12 min walkthrough", "Still confused about how to connect this to my actual inbox. Every tutorial uses a fake one.", "47 likes", 9),
        ],
        related=["Can I automate replies to customers with a free tool?", "How much does it cost to run an AI assistant for a small shop?", "Do I need a developer to set up an AI receptionist?", "What happens to the automation when my computer is off?", "Is an AI auto-reply safe to use with real customers?"],
        ideas=[
            ("Why most AI automation tutorials never reach a real customer", "You followed the tutorial. It worked on video. Here is why it will not work on Monday morning.", "youtube_long", "medium", "Question volume roughly doubled over two weeks."),
            ("I automated a small shop's replies for the cost of a coffee a month", "A full build, deployed, with the monthly bill on screen.", "youtube_long", "hard", "People compare agency quotes with DIY cost."),
            ("The three things AI tutorials skip: hosting, cost, failure", "A short checklist for anyone about to build.", "youtube_short", "easy", "Repeated complaints about missing deployment steps."),
        ],
    ),
    dict(
        id="opp-deploy-agents-cheap",
        title="Deploying AI agents without a big cloud bill",
        core_question="How do I deploy an AI agent cheaply once it works on my laptop?",
        audience="Beginner and self-taught developers",
        why="The agent works locally, then the questions turn to hosting, secrets and cost. Existing answers assume a team and a budget.",
        inputs=dict(demand=88, question_density=86, growth=84, dissatisfaction=92, engagement=70, audience_value=76, recency=90, competition=42, answer_saturation=36),
        notes=dict(
            dissatisfaction="Many questions mention outdated or incomplete deployment guides.",
            competition="Deployment content exists but targets enterprise setups.",
            answer_saturation="Answer quality not yet assessed by AI.",
        ),
        counts=[3, 3, 4, 4, 5, 5, 6, 6, 7, 8, 9, 10, 12, 14],
        sources=dict(youtube=34, reddit=62), communities=3, askers=79,
        competition=dict(level="medium", creators=14, note="Deployment tutorials are common. Budget-first ones are rare."),
        answer_gap=dict(level="high", note="Guides skip secrets handling and the monthly cost."),
        evidence=[
            ("reddit", "post", "r/LocalLLaMA", "Agent runs fine locally. What is the cheapest sane way to keep it running 24/7?", "176 upvotes, 71 comments", 1),
            ("youtube", "comment", "Comment on a 31 min agent build", "Can someone actually show the deploy step without a 200 dollar cloud setup?", "63 likes", 3),
            ("reddit", "post", "r/webdev", "Every guide I find is outdated. Half the commands do not work anymore.", "98 upvotes, 40 comments", 7),
        ],
        related=["Where can I host a Python AI agent for free or nearly free?", "How do I keep API keys safe when I deploy an agent?", "Is a small VPS enough to run an agent all day?", "How do I stop my agent from running up a huge API bill?"],
        ideas=[
            ("Deploy an AI agent for under 5 dollars a month", "Real bill on screen from day one.", "youtube_long", "medium", "Cost is the most repeated worry in the questions."),
            ("Your agent's API key is probably leaking. Check in 2 minutes", "A quick audit walkthrough.", "youtube_short", "easy", "Secrets handling is asked about and rarely answered."),
        ],
    ),
    dict(
        id="opp-mpesa-small-site",
        title="Accepting M-Pesa payments on a small website",
        core_question="How do I add M-Pesa checkout to a site I built myself?",
        audience="Kenyan small sellers and self-taught developers",
        why="Sellers who built their own site cannot find a walkthrough that goes from sandbox credentials to a live payment.",
        inputs=dict(demand=70, question_density=68, growth=76, dissatisfaction=78, engagement=60, audience_value=80, recency=85, competition=22, answer_saturation=30),
        notes=dict(
            competition="Few creators cover this end to end.",
            audience_value="Set by the creator profile, not by the data.",
            answer_saturation="Answer quality not yet assessed by AI.",
        ),
        counts=[1, 2, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 6, 6],
        sources=dict(youtube=19, reddit=28), communities=3, askers=39,
        competition=dict(level="low", creators=5, note="A handful of tutorials, most of them a few years old."),
        answer_gap=dict(level="high", note="Sandbox is covered. Going live and handling failed payments is not."),
        evidence=[
            ("reddit", "post", "r/Kenya", "Got the Daraja sandbox working. Going to production is where every tutorial ends. Anyone done this?", "58 upvotes, 23 comments", 3),
            ("youtube", "comment", "Comment on an 18 min integration video", "This is from 2021, the callback part does not work anymore. Is there an updated one?", "34 likes", 5),
        ],
        related=["How do I get M-Pesa Daraja production credentials?", "How do I confirm a payment actually went through?", "What do I do when the callback never arrives?"],
        ideas=[
            ("M-Pesa checkout from sandbox to live, nothing skipped", "Every step tutorials leave out, on a real small shop.", "youtube_long", "hard", "Multiple questions stop at the production step."),
        ],
    ),
    dict(
        id="opp-whatsapp-support",
        title="WhatsApp customer support with AI",
        core_question="How can I answer WhatsApp customer messages automatically with AI?",
        audience="Shop owners and freelancers",
        why="Steady demand, but the topic is crowded. A narrower angle is needed to stand out.",
        inputs=dict(demand=74, question_density=72, growth=8, dissatisfaction=55, engagement=64, audience_value=76, recency=90, competition=68, answer_saturation=58),
        notes=dict(
            growth="Volume is flat over the last two weeks.",
            competition="Many creators already cover this in general terms.",
            answer_saturation="Answer quality not yet assessed by AI.",
        ),
        counts=[4, 5, 4, 5, 4, 5, 5, 4, 5, 5, 4, 5, 4, 5],
        sources=dict(youtube=38, reddit=26), communities=5, askers=52,
        competition=dict(level="high", creators=41, note="Well covered. A specific niche angle would matter more than the topic."),
        answer_gap=dict(level="medium", note="Setup is covered. Handling approvals and templates is thin."),
        evidence=[
            ("reddit", "post", "r/smallbusiness", "Anyone using an AI bot on WhatsApp Business? Worried about it saying something wrong.", "77 upvotes, 31 comments", 2),
            ("youtube", "comment", "Comment on a 15 min setup video", "Works in the demo, but Meta keeps rejecting my message templates.", "29 likes", 8),
        ],
        related=["Is it allowed to use a bot on WhatsApp Business?", "Why does WhatsApp reject my message templates?", "How much does the WhatsApp Business API cost per message?"],
        ideas=[
            ("Why WhatsApp keeps rejecting your bot's message templates", "A narrow fix for a problem the general tutorials skip.", "youtube_short", "easy", "Template rejections show up repeatedly in comments."),
        ],
    ),
]

RADAR = [
    ("How do I keep an AI agent running 24/7 without a big bill?", "opp-deploy-agents-cheap", ["youtube", "reddit"], 0.31, "high", 12),
    ("Where does the automation run when my laptop is off?", "opp-ai-support-smb", ["reddit", "youtube"], 0.38, "high", 27),
    ("Can someone show M-Pesa checkout going live, not sandbox?", "opp-mpesa-small-site", ["reddit"], 0.22, "high", 54),
    ("Why does WhatsApp keep rejecting my message templates?", "opp-whatsapp-support", ["youtube", "reddit"], 0.04, "medium", 96),
    ("Is an AI reply bot safe to use with real customers?", "opp-ai-support-smb", ["reddit"], 0.19, "medium", 141),
    ("How do I self-host a small language model on a cheap VPS?", None, ["reddit"], 0.15, "unknown", 188),
]

NEW_QUESTIONS = [
    ("How do I keep an AI agent running 24/7 without a big bill?", "reddit", 12),
    ("Where does the automation run when my laptop is off?", "youtube", 27),
    ("How do I confirm an M-Pesa payment actually went through?", "reddit", 54),
    ("Do I need a developer to set up an AI receptionist?", "youtube", 71),
]

NICHES = [
    dict(id="niche-ai-smb", title="Affordable AI automation for small businesses", audience="Small business owners",
         why=["Question volume rose 38% in 7 days", "Discussed in 4 communities", "Repeated complaints that tutorials stop before deployment", "Few detailed answers for a one-person shop"],
         opportunity_ids=["opp-ai-support-smb", "opp-deploy-agents-cheap", "opp-whatsapp-support"]),
    dict(id="niche-ke-commerce", title="Selling online in Kenya", audience="Small sellers and self-taught developers",
         why=["Growing question volume about payments and hosting", "Only a handful of recent tutorials", "Existing walkthroughs stop at sandbox"],
         opportunity_ids=["opp-mpesa-small-site"]),
]

INSUFFICIENT = [dict(scope="Gaming", reason="IDEA needs more evidence before identifying a reliable content opportunity.",
                     questions_found=9, questions_needed=12, sources_found=1, sources_needed=2)]


def growth_7d(counts):
    a, b = sum(counts[:7]), sum(counts[7:])
    return round((b - a) / max(a, 1), 2)


def build():
    opps = []
    for o in OPPS:
        total = sum(o["counts"])
        o["inputs"]["growth"] = max(0.0, min(100.0, growth_7d(o["counts"]) * 100))  # same rule as derive_inputs
        res = score_opportunity(ScoreInputs(**o["inputs"]), EvidenceStats(total, len(o["sources"])), o["notes"])
        assert not hasattr(res, "reason"), o["id"]
        opps.append(dict(
            id=o["id"], title=o["title"], core_question=o["core_question"], audience=o["audience"], why_detected=o["why"],
            score=res.score, band=res.band, confidence=res.confidence,
            factors=[f.model_dump() for f in res.factors],
            stats=dict(related_questions=total, askers=o["askers"], sources=o["sources"], communities=o["communities"],
                       growth_7d=growth_7d(o["counts"]), velocity=classify_velocity(o["counts"]).value),
            trend=o["counts"], competition=o["competition"], answer_gap=o["answer_gap"],
            evidence=[dict(source=s, kind=k, where=w, excerpt=x, engagement=e, days_ago=d, url="sample://" + s) for s, k, w, x, e, d in o["evidence"]],
            related_questions=o["related"],
            ideas=[dict(title=t, hook=h, format=f, difficulty=d, why_now=w) for t, h, f, d, w in o["ideas"]],
        ))
    opps.sort(key=lambda x: -x["score"])
    NICHES[0]["why"][0] = f"Question volume rose {round(opps[0]['stats']['growth_7d'] * 100)}% week over week"
    return dict(
        is_sample=True,
        note="Fixture data for design and development. Not real evidence.",
        opportunities=opps,
        radar=[dict(question=q, opportunity_id=i, sources=s, momentum=m, answer_gap=g, minutes_ago=t) for q, i, s, m, g, t in RADAR],
        new_questions=[dict(question=q, source=s, minutes_ago=t) for q, s, t in NEW_QUESTIONS],
        niches=NICHES,
        insufficient=INSUFFICIENT,
        categories=["AI", "Technology", "Business", "Finance", "Programming", "Gaming", "Education", "Fitness", "Food", "Travel", "Career", "Music", "Science", "History", "Productivity", "Entrepreneurship", "DIY", "Fashion", "Software", "Local business", "African technology", "Kenya"],
    )


if __name__ == "__main__":
    data = build()
    out = Path(__file__).resolve().parents[1] / "app" / "sample" / "data.json"
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    for o in data["opportunities"]:
        print(o["score"], o["band"], o["confidence"], o["stats"]["velocity"], o["title"])
    mobile = Path(__file__).resolve().parents[2] / "mobile" / "assets" / "mock"
    mobile.mkdir(parents=True, exist_ok=True)
    shutil.copy(out, mobile / "data.json")
