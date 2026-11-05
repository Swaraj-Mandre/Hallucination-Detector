"""Builds the HTML for the results, and holds the page's look."""

from html import escape

import config

CSS = """
:root {
  --paper: #F6F2E9; --card: #FFFDF8; --ink: #1E2320; --muted: #5C625D;
  --rule: #DDD6C6; --blue: #24476B; --good: #1E7A57; --warn: #B7791F; --bad: #B3372F;
}
body, .gradio-container { background: var(--paper) !important; color: var(--ink); }
.gradio-container { max-width: 860px !important; margin: 0 auto !important;
  font-family: 'IBM Plex Sans', system-ui, sans-serif !important; }
footer { display: none !important; }
.gradio-container { --color-accent: #24476B; --color-accent-soft: #E4E9EE; }
.gradio-container button[role="tab"] { font-size: 15px; color: var(--muted); }
.gradio-container button[role="tab"][aria-selected="true"] { color: var(--ink); font-weight: 600; }
.gradio-container button.secondary { border: 1px solid #CFC7B5 !important; }
.block.gradio-html, .gradio-html, .html-container { padding-left: 0 !important; padding-right: 0 !important; }

.masthead { padding: 34px 0 20px; border-bottom: 2px solid var(--ink); margin-bottom: 8px; }
.masthead .kicker { font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.masthead h1 { font-family: 'Source Serif 4', Georgia, serif; font-size: 46px; font-weight: 600;
  line-height: 1.05; margin: 8px 0 10px; color: var(--ink); letter-spacing: -.01em; }
.masthead p { font-size: 17px; line-height: 1.5; color: var(--muted); margin: 0; max-width: 600px; }

.starter { padding: 22px 0 4px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.starter div { border-top: 1px solid var(--rule); padding-top: 10px; }
.starter b { display: block; font-family: 'Source Serif 4', Georgia, serif; font-size: 18px; font-weight: 600; color: var(--ink); }
.starter span { font-size: 14px; line-height: 1.45; color: var(--muted); }

.verdict { background: var(--card); border: 1px solid var(--rule); border-top: 6px solid var(--tone);
  padding: 22px 24px 20px; margin-top: 6px; }
.verdict .asked { font-size: 14px; color: var(--muted); margin-bottom: 12px; }
.verdict .head { display: flex; align-items: center; gap: 12px; }
.verdict svg { flex: none; }
.verdict h2 { font-family: 'Source Serif 4', Georgia, serif; font-size: 34px; font-weight: 600;
  line-height: 1.1; margin: 0; color: var(--ink); }
.verdict .advice { font-size: 16px; line-height: 1.5; margin: 8px 0 18px; color: var(--ink); }
.meter { position: relative; height: 10px; background: #ECE6D8; border-radius: 5px; margin-top: 6px; }
.meter i { position: absolute; left: 0; top: 0; bottom: 0; background: var(--tone); border-radius: 5px; }
.meter u { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--ink); }
.meter-line { display: flex; justify-content: space-between; font-size: 14px; color: var(--muted); }
.meter-line b { color: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }
.meter-note { font-size: 12px; color: var(--muted); margin-top: 7px; }

.lead { padding: 18px 2px 4px; }
.label { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.lead q { display: block; quotes: none; font-family: 'Source Serif 4', Georgia, serif; font-size: 22px;
  line-height: 1.35; color: var(--ink); }
.lead.doubtful q { color: var(--muted); }

.attempts { margin-top: 18px; }
.attempt { display: grid; grid-template-columns: 76px 1fr 150px; gap: 14px; align-items: center;
  padding: 11px 2px; border-top: 1px solid var(--rule); }
.attempt .claim { font-size: 12px; font-weight: 600; color: var(--ink); }
.attempt .claim small { display: block; font-weight: 400; color: var(--muted); font-size: 12px; }
.attempt .text { font-size: 15px; line-height: 1.4; color: var(--ink); overflow-wrap: anywhere; }
.bar { height: 8px; background: #ECE6D8; border-radius: 4px; position: relative; }
.bar i { position: absolute; left: 0; top: 0; bottom: 0; background: var(--blue); border-radius: 4px; min-width: 2px; }
.bar u { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--ink); opacity: .55; }
.score { font-size: 13px; color: var(--ink); text-align: right; margin-bottom: 4px; font-variant-numeric: tabular-nums; }

details.more { border-top: 1px solid var(--rule); padding: 12px 2px; }
details.more:last-of-type { border-bottom: 1px solid var(--rule); }
details.more summary { cursor: pointer; font-size: 15px; font-weight: 600; color: var(--ink); }
details.more p { font-size: 14px; line-height: 1.5; color: var(--muted); margin: 10px 0; }
.matrix { border-collapse: separate !important; border-spacing: 2px; margin: 10px 0 6px; width: auto !important; border: 0 !important; }
.matrix th, .matrix td, .matrix tr { border: 0 !important; }
.matrix th { font-size: 12px; font-weight: 500; color: var(--muted); padding: 4px 8px; background: transparent !important; }
.matrix td { width: 54px; height: 38px; text-align: center; font-size: 13px; font-variant-numeric: tabular-nums; border-radius: 3px; padding: 0 !important; }
.chip { display: inline-block; padding: 3px 5px; margin: 2px 1px; border-radius: 3px; font-size: 14px; color: var(--ink); }
.chip.hot { color: #fff; }
.pair { font-size: 14px; color: var(--ink); margin: 2px 0; }

.howto h3 { font-family: 'Source Serif 4', Georgia, serif; font-size: 24px; font-weight: 600; margin: 26px 0 8px; color: var(--ink); }
.howto p, .howto li { font-size: 15px; line-height: 1.55; color: var(--ink); }
.steps { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; margin: 12px 0; }
.steps div { background: var(--card); border: 1px solid var(--rule); padding: 12px 10px; font-size: 13px; line-height: 1.35; color: var(--muted); }
.steps b { display: block; color: var(--ink); font-size: 14px; margin-bottom: 4px; }
.versus { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.versus div { border-top: 3px solid var(--blue); background: var(--card); padding: 12px 14px; font-size: 14px; line-height: 1.5; color: var(--ink); }

.credit { margin-top: 30px; padding-top: 12px; border-top: 1px solid var(--rule); font-size: 13px; color: var(--muted); }

@media (max-width: 640px) {
  .masthead h1 { font-size: 36px; }
  .starter, .versus { grid-template-columns: 1fr; }
  .steps { grid-template-columns: 1fr; }
  .attempt { grid-template-columns: 1fr; gap: 6px; }
  .matrix td { width: 42px; }
}
"""

HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">
"""

# The page has one look, so it stays in light mode on every device.
FORCE_LIGHT = """
() => {
  const url = new URL(window.location);
  if (url.searchParams.get('__theme') !== 'light') {
    url.searchParams.set('__theme', 'light');
    window.location.replace(url);
  }
}
"""

MASTHEAD = """
<div class="masthead">
  <div class="kicker">Self-consistency hallucination detector</div>
  <h1>Ask it five times.</h1>
  <p>A language model that knows a fact repeats it. A model that is guessing changes
  its story. Crosscheck asks your question five times and tells you whether the
  answers hold together.</p>
</div>
"""

STARTER = """
<div class="starter">
  <div><b>1. Ask</b><span>Type a factual question, or ask about an image.</span></div>
  <div><b>2. Compare</b><span>Five answers are compared with each other, in both directions.</span></div>
  <div><b>3. Decide</b><span>You get a verdict, and the evidence behind it.</span></div>
</div>
"""

CREDIT = """
<div class="credit">Swaraj Mandre, Roll No. 52. Generative AI mini project P52.
Built with Qwen2.5-3B-Instruct, RoBERTa-MNLI, BLIP and SD-Turbo.</div>
"""

HOW_IT_WORKS = """
<div class="howto">
  <h3>From question to verdict</h3>
  <div class="steps">
    <div><b>Prompt</b>Your question goes to the model with a fixed instruction.</div>
    <div><b>Sample</b>Five answers are drawn at a set temperature.</div>
    <div><b>Compare</b>RoBERTa-MNLI checks every pair in both directions.</div>
    <div><b>Score</b>Pair results become one agreement score.</div>
    <div><b>Warn</b>A low score raises a warning before the answer.</div>
  </div>

  <h3>Two kinds of model working together</h3>
  <div class="versus">
    <div><b>Generative: Qwen2.5-3B, BLIP, SD-Turbo.</b><br>These create new content. Qwen picks
    each next word from a probability distribution, which is why repeated answers can differ.</div>
    <div><b>Discriminative: RoBERTa-MNLI.</b><br>This one creates nothing. It reads two sentences
    and sorts the pair into entailment, neutral or contradiction.</div>
  </div>

  <h3>Why the score works</h3>
  <p>When a model has learned a fact, most of its probability sits on one answer, so samples
  repeat it. When it has not, the probability is spread thin and samples drift apart. Agreement
  is therefore a stand-in for how much the model really knows.</p>

  <h3>What it cannot do</h3>
  <p>It measures consistency, not truth. If the model holds a firm wrong belief, all five answers
  agree and the detector stays quiet. Treat "Consistent" as a good sign, never as proof. The app
  also sends nothing to outside services and stores no questions.</p>
</div>
"""

MARKS = {
    "high": ("var(--good)", '<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><circle cx="15" cy="15" r="14" fill="#1E7A57"/><path d="M8.5 15.5l4.5 4.5 8.5-9.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'),
    "mixed": ("var(--warn)", '<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><path d="M15 2l14 25H1z" fill="#B7791F"/><path d="M15 11v8" stroke="#fff" stroke-width="3" stroke-linecap="round"/><circle cx="15" cy="23" r="1.8" fill="#fff"/></svg>'),
    "low": ("var(--bad)", '<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true"><rect x="1" y="1" width="28" height="28" rx="3" fill="#B3372F"/><path d="M9.5 9.5l11 11M20.5 9.5l-11 11" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>'),
}


def blue_shade(value):
    """Sequential scale for the matrix: one hue, pale to dark."""
    low, high = (236, 230, 216), (36, 71, 107)
    mixed = [round(a + (b - a) * value) for a, b in zip(low, high)]
    return "rgb(%d,%d,%d)" % tuple(mixed)


def verdict_block(result):
    verdict = result["verdict"]
    tone, mark = MARKS[verdict["level"]]
    agreeing = len(result["groups"][0])
    total = len(result["answers"])
    percent = round(result["agreement"] * 100)
    low_mark = config.AGREEMENT_THRESHOLD * 100
    if agreeing == 1:
        summary = f"No two of the {total} answers make the same claim"
    elif agreeing == total:
        summary = f"All {total} answers make the same claim"
    else:
        summary = f"{agreeing} of {total} answers make the same claim"
    return f"""
    <div class="verdict" style="--tone:{tone}">
      <div class="asked">You asked: {escape(result['question'])}</div>
      <div class="head">{mark}<h2>{verdict['title']}</h2></div>
      <div class="advice">{verdict['advice']}</div>
      <div class="meter-line"><span>{summary}</span><span>Agreement <b>{percent}%</b></span></div>
      <div class="meter"><i style="width:{percent}%"></i><u style="left:{low_mark:.0f}%"></u></div>
      <div class="meter-note">The tick marks the {low_mark:.0f}% warning line.</div>
    </div>"""


def lead_block(result):
    answer = escape(result["answers"][result["best"]])
    if result["verdict"]["level"] == "high":
        return f'<div class="lead"><div class="label">Answer</div><q>{answer}</q></div>'
    return (f'<div class="lead doubtful"><div class="label">Best supported answer, not verified</div>'
            f'<q>{answer}</q></div>')


def attempts_block(result):
    claim_of = {}
    for number, group in enumerate(result["groups"]):
        for index in group:
            claim_of[index] = (chr(65 + number), len(group))

    rows = []
    limit = config.AGREEMENT_THRESHOLD * 100
    for index, answer in enumerate(result["answers"]):
        percent = round(result["confidence"][index] * 100)
        letter, size = claim_of[index]
        note = "alone" if size == 1 else "%d answers" % size
        rows.append(f"""
        <div class="attempt">
          <div class="claim">Claim {letter}<small>{note}</small></div>
          <div class="text">{escape(answer)}</div>
          <div title="Attempt {index + 1}: {percent}% supported by the other answers">
            <div class="score">{percent}%</div>
            <div class="bar"><i style="width:{percent}%"></i><u style="left:{limit:.0f}%"></u></div>
          </div>
        </div>""")
    return ('<div class="attempts"><div class="label">The five attempts, and how far '
            'the others support each one</div>' + "".join(rows) + "</div>")


def matrix_block(result):
    labels = ["A%d" % (i + 1) for i in range(len(result["matrix"]))]
    head = "<tr><th></th>" + "".join(f"<th>{label}</th>" for label in labels) + "</tr>"
    rows = []
    for i, row in enumerate(result["matrix"]):
        cells = []
        for j, value in enumerate(row):
            if i == j:
                cells.append('<td style="background:transparent;color:var(--muted)">&middot;</td>')
                continue
            ink = "#fff" if value > 0.55 else "var(--ink)"
            cells.append(f'<td style="background:{blue_shade(value)};color:{ink}" '
                         f'title="P({labels[i]} entails {labels[j]}) = {value:.2f}">{value:.2f}</td>')
        rows.append(f"<tr><th>{labels[i]}</th>{''.join(cells)}</tr>")
    return f"""
    <details class="more"><summary>Entailment probabilities</summary>
      <p>Each cell is RoBERTa-MNLI's probability that the row answer entails the column answer.
      Darker means stronger. A1 to A5 follow the order of the attempts above.</p>
      <table class="matrix">{head}{''.join(rows)}</table>
    </details>"""


def attention_block(result):
    focus = result["focus"]
    weights = focus["weights"]
    top = max(weights) or 1.0
    chips = []
    for token, weight in zip(focus["tokens"], weights):
        strength = weight / top
        hot = " hot" if strength > 0.55 else ""
        chips.append(f'<span class="chip{hot}" style="background:{blue_shade(strength)}">{escape(token)}</span>')
    first, second = focus["pair"]
    return f"""
    <details class="more"><summary>Where the judge looked</summary>
      <p>Attention from RoBERTa's last layer while it compared the two answers that agree least.
      Darker words drew more attention.</p>
      <div class="pair"><b>A{first + 1}:</b> {escape(result['sentences'][first])}</div>
      <div class="pair"><b>A{second + 1}:</b> {escape(result['sentences'][second])}</div>
      <div style="margin-top:10px">{''.join(chips)}</div>
    </details>"""


def render(result):
    return (verdict_block(result) + lead_block(result) + attempts_block(result)
            + '<div style="margin-top:16px">' + matrix_block(result) + attention_block(result) + "</div>")
