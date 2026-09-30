# -*- coding: utf-8 -*-
"""
把《Ordinary Magic》英文单文件笔记 Ordinary-Magic-Notes-EN.md 拆成 en/docs/ 下的分篇。

用法：python scripts/split_notes_en.py
幂等：可 rm -rf en 后重跑。分篇一律由本脚本从英文单文件生成，禁止手改 en/docs/。
英文分篇与中文 docs/ 结构一一对应，是同一仓库 en/ 子目录（见 SKILL.md 多语言指引）。
"""
import os, re

ROOT = "/Users/semedia_editing/WorkBuddy/2026-09-30-11-36-01/ordinary-magic-notes"
SRC = "Ordinary-Magic-Notes-EN.md"
OUT = "en/docs"

BOOK = "Ordinary Magic Reading Notes"

def yq(s):
    """Wrap a string as a YAML double-quoted scalar (escapes backslashes and quotes).
    Required because several EN titles contain ASCII colon-space (e.g. 'Dynamic Norms: Why...')
    which is illegal in a YAML plain scalar and silently drops page.title."""
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

# 纯英文标题（浏览器标签不得出现中文），目录页 H1 同步纯英文
INDEX_TITLE = "Ordinary Magic · Reading Notes Index (16 Themes)"
INDEX_DESC = "A practical reader's notebook that breaks down Gregory M. Walton's Ordinary Magic into 16 high-pressure decision scenarios: downward spiral, learned helplessness, identity reframing, threatened ego, trust rebuilding, belonging, institutional design, dynamic norms, self-transcendent purpose, institutional messaging, and ripple effects — with 60 actionable algorithms."
INDEX_KEYWORDS = ("Ordinary Magic, Gregory Walton, wise interventions, reading notes, "
                 "downward spiral, learned helplessness, narrative reframing, belonging, "
                 "dynamic norms, self-transcendent purpose, institutional messaging, ripple effects")
INDEX_H1 = "📘 Ordinary Magic · Reading Notes Index (16 Themes)"

# (output filename, front matter title, start predicate, keywords, description)
SECTIONS = [
    ("00-start-here-30-second-orientation.md", f"Start Here: 30-Second Orientation · {BOOK}",
     lambda l: l.startswith("## 🚪 Start Here"),
     "ordinary magic, reading notes, wise interventions, sandbox, glossary",
     "What the book is about, how the sandbox works, three background essentials, character index, and a 39-term plain-language glossary."),

    ("roadmap-16-topic-evolution-map.md", f"Learning Evolution Roadmap: 16-Theme Map · {BOOK}",
     lambda l: l.startswith("## 🧭 Learning"),
     "learning roadmap, evolution map, ordinary magic chapter map, core insights",
     "A four-column map of 16 themes x author's core insight x my transferable conclusion x current status."),

    ("01-downward-spiral-newhire.md", f"Downward Spiral: How One Flat No Undoes a New Hire · {BOOK}",
     lambda l: l.startswith("### 01."),
     "downward spiral, spiraling down, attribution, action precedes belief, micro-win",
     "What ruins a person is never the small event but the meaning he assigns to it; fix by allowing bottoming out, stripping stakes, and a threat-free micro-loop."),

    ("02-learned-helplessness-work-order.md", f"Can I Do It: Downgrading 'We're Doomed' to a Ticket · {BOOK}",
     lambda l: l.startswith("### 02."),
     "learned helplessness, attribution dimensions, paradoxical intention, quantify",
     "When a team says 'we're finished', don't rebut the conclusion—break the quantifiers: turn 'finished' into '3 bugs and 1 interaction slip'; ban qualifiers, force quantification."),

    ("03-identity-reframing-labels.md", f"Who Am I: Give Him a Noun, Then Lock His Behavior with It · {BOOK}",
     lambda l: l.startswith("### 03."),
     "identity reframing, power of nouns, self-consistency bias, tearing off labels",
     "To change behavior, don't correct the action—redefine who he is; purify the positive motive behind a negative behavior, mint a noun-amulet, then give one minimal on-identity move."),

    ("04-threatened-ego-comfort-backfires.md", f"Do You Love Me: Why Comfort Backfires on the Wounded · {BOOK}",
     lambda l: l.startswith("### 04."),
     "threatened ego, comfort is condescension, saying-is-believing, advocate effect",
     "To the just-crushed, 'it's fine, just skip it' is a verdict not comfort; the fix is block sympathy, flip identity by asking him for help, trigger saying-is-believing."),

    ("05-trust-rebuilding-suspicion.md", f"Can I Trust You: Stop Self-Defending, Show Him the Endgame · {BOOK}",
     lambda l: l.startswith("### 05."),
     "trust rebuilding, confirmation bias, self-incrimination trap, structural transparency",
     "When someone is sure you're out to get him, every good deed is decoded as conspiracy; freeze self-defense, claim the worst label, fast-forward 24h past destruction, use structure over moral trust."),

    ("06-belonging-outsider.md", f"Do I Belong: Don't Make Him Fit In, Make Him Irreplaceable · {BOOK}",
     lambda l: l.startswith("### 06."),
     "belonging uncertainty, outsider, functional complementarity, superordinate goal",
     "'just chat more and fit in' is toxic; reframe his misfit as the system's scarce asset and build belonging through shared crisis, not team-building."),

    ("07-institutional-design-linkage.md", f"Macro System: What a System Whispers Matters More Than Its Text · {BOOK}",
     lambda l: l.startswith("### 07."),
     "institutional design, collective punishment, procedural justice, restorative, tragedy of commons",
     "A process needing four sign-offs to reimburse 50 yuan whispers 'we assume you're all thieves'; four checks plus treating violations as system bug reports."),

    ("08-crisis-leadership-veto.md", f"Trial I: When Three Correct Mechanisms Cancel Each Other · {BOOK}",
     lambda l: l.startswith("### 08."),
     "crisis leadership, horizontal veto, dual-signature, single owner, asymmetric incentive",
     "Three perfect gears mesh and jam; fix structure before narrative—pull the horizontal veto, lock a single owner, asymmetric incentive, encapsulate the defender."),

    ("09-brilliant-jerk-blackmail.md", f"Trial II: The Genius You Punished Will Blackmail You Back · {BOOK}",
     lambda l: l.startswith("### 09."),
     "brilliant jerk, blackmail, architecture of hope, legal escape hatch, dynamic randomness",
     "Drive a genius to the bottom then hand him a key to lock his teammates and he'll run a black market; cut the ransom surface, carve a legal escape hatch, inject dynamic randomness."),

    ("10-whistleblower-side-letter.md", f"Trial III: The Side Letter Is the Knife You Handed Him · {BOOK}",
     lambda l: l.startswith("### 10."),
     "whistleblower paradox, side letter, self-reporting disclosure, procedural justice, IPO compliance",
     "Publicly shaming him while privately slipping a non-disclosable payoff is handcuffing yourself and giving him the key; ban side letters, three-layer cut, self-report before he blows."),

    ("11-wise-feedback-meta-signal.md", f"Trial IV: You Won the Rule, Lost the Balance Sheet · {BOOK}",
     lambda l: l.startswith("### 11."),
     "wise feedback, meta-signal, dual-track narrative, off-ramp, innovation sandbox",
     "A penalty's damage comes from the meta-signal it broadcasts to the whole company; a four-step Wise Repair checklist."),

    ("12-narrative-reframing-endowment.md", f"Narrative Reframing: The First Principle of the Whole Book · {BOOK}",
     lambda l: l.startswith("### 12."),
     "narrative reframing, endowment effect, overjustification, cold treatment, Archimedes lever",
     "Don't change the task on his desk—change his interpretation of it; diagnose the narrative virus, find the Archimedes lever, create behavioral evidence not promises."),

    ("13-dynamic-norms-belief-gap.md", f"Dynamic Norms: Why 'Everyone Wants to Grind' Is a Silent Lie · {BOOK}",
     lambda l: l.startswith("### 13."),
     "dynamic norms, pluralistic ignorance, Schelling point, information cascades, default architecture",
     "The most toxic group pressure isn't the system but 'everyone performs, everyone thinks only I perform'; measure the private belief gap, sell trajectory not absolute, sandbox exceptions, change defaults."),

    ("14-self-transcendent-purpose-dual-motive.md", f"Self-Transcendent Purpose: Why 'Tech for Good' and 'It's Just Money' Are Both Poison · {BOOK}",
     lambda l: l.startswith("### 14."),
     "self-transcendent purpose, dual-motive architecture, motivation, saying-is-believing",
     "To endure extreme drudgery, money fatigues and slogans breed cynicism; only the dual-motive (transcendent purpose + self-interest) bites—make business the armor of the sacred."),

    ("15-institutional-metaphor-scaffolding.md", f"Institutional Metaphor: Why Tearing Down Cubicles Beats Bonuses · {BOOK}",
     lambda l: l.startswith("### 15."),
     "institutional messaging, scaffolding metaphor, assimilative metaphor, API interface, implicit intent",
     "The brain is a tireless decoder of implicit intent; strip assimilative symbols, build low-friction interfaces, lock asymmetric boundaries, appropriate protest symbols as radar."),

    ("16-ripple-effects-recursive-cycle.md", f"Ripple Effects: Why a 'Miracle' Reverts in Six Months · {BOOK}",
     lambda l: l.startswith("### 16."),
     "ripple effects, recursive cycle, affordance, critical juncture, generational mentorship, probe",
     "Any intervention decays unless it forms a self-sustaining recursive loop; lock critical windows, retrofit affordances, frame pioneers as probes, roll generational mentorship, micro-dashboards."),

    ("A-appendix-a-60-action-algorithms.md", f"Appendix A: 60 Action Algorithms · {BOOK}",
     lambda l: l.startswith("## 🧾 Appendix A"),
     "action algorithms, checklist, attribution, trust, belonging, institution, violation repair",
     "60 algorithms distilled from 16 sandboxes, grouped into 7 scenarios, each written as 'trigger signal → action', usable as a checklist."),

    ("B-boundaries-13-failure-conditions.md", f"Methodological Boundaries & Known Blind Spots · {BOOK}",
     lambda l: l.startswith("## ⚠️ Method"),
     "method boundaries, psychology intervention failure, zero-sum, narcissism, illegality",
     "5 source boundaries of this notebook plus 13 failure conditions of the method itself, and my 12-round thinking minefield."),

    ("C-appendix-b-bibliography.md", f"Appendix B: Bibliography & Data Verification · {BOOK}",
     lambda l: l.startswith("## 📎 Appendix B"),
     "bibliography, ISBN, 9780593580899, ordinary magic contents, confidence",
     "Verified bibliography (ISBN 9780593580899 / 464pp / 2025-03-25), the real 11-chapter contents with page numbers, and a confidence table for all quotes/data."),

    ("Z-closing-structure-vs-narrative.md", f"Closing: What This Notebook Actually Changed · {BOOK}",
     lambda l: l.startswith("## 🧩 Closing"),
     "closing, summary, structure vs narrative, meta-signal, reading notes summary",
     "Three layers of reordered judgment: from changing behavior to changing interpretation, from interpretation to changing structure, from structure to changing my own instincts."),
]

ANCHOR_MAP = {
    "#guide": "00-start-here-30-second-orientation.md",
    "#roadmap": "roadmap-16-topic-evolution-map.md",
    "#appendix-a": "A-appendix-a-60-action-algorithms.md",
    "#limits": "B-boundaries-13-failure-conditions.md",
    "#appendix-b": "C-appendix-b-bibliography.md",
    "#closing": "Z-closing-structure-vs-narrative.md",
}

TOPIC_FILE = {int(fn[:2]): fn for fn, *_ in SECTIONS if re.match(r"^\d\d-", fn)}

NAV_LABEL = "[📚 Index](./)"

def rewrite_links(text):
    def rep(m):
        label, url = m.group(1), m.group(2)
        if url in ANCHOR_MAP:
            return f"[{label}]({ANCHOR_MAP[url]})"
        m2 = re.fullmatch(r"#d(\d\d)", url)
        if m2 and int(m2.group(1)) in TOPIC_FILE:
            return f"[{label}]({TOPIC_FILE[int(m2.group(1))]})"
        return m.group(0)
    return re.sub(r"\[([^\]]*)\]\((#[^)]+)\)", rep, text)

def strip_leading_heading(block):
    out = []
    for l in block:
        if re.match(r"^<a id=", l.strip()):
            continue
        m = re.match(r"^### (\d+)\. (.*)$", l)
        if m:
            out.append(f"# {m.group(2)}")
        elif l.startswith("## "):
            out.append("# " + l[3:])
        else:
            out.append(l)
    while out and not out[0].strip(): out.pop(0)
    while out and not out[-1].strip(): out.pop()
    return out

def main():
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    L = open(os.path.join(ROOT, SRC), encoding="utf-8").read().split("\n")
    starts = []
    for _, _, pred, _, _ in SECTIONS:
        starts.append(next(i for i, l in enumerate(L) if pred(l)))
    starts.append(len(L))

    head = strip_leading_heading([l for l in L[:starts[0]] if not l.startswith("# ")])

    for i, (fname, title, _, kw, desc) in enumerate(SECTIONS):
        block = L[starts[i]:starts[i + 1]]
        if i == 0 and head:
            block = head + [""] + block
        body = "\n".join(strip_leading_heading(block))
        body = rewrite_links(body)
        prevf = SECTIONS[i - 1][0] if i > 0 else None
        nextf = SECTIONS[i + 1][0] if i < len(SECTIONS) - 1 else None
        nav = NAV_LABEL
        if prevf: nav += f"　·　[⬅️ Prev]({prevf})"
        if nextf: nav += f"　·　[Next ➡️]({nextf})"
        content = (
            f"---\ntitle: {yq(title)}\ndescription: {yq(desc)}\nkeywords: {yq(kw)}\nlang: en\n---\n\n"
            f"> {nav}\n\n---\n\n{body}\n\n---\n\n> {nav}\n"
        )
        open(os.path.join(ROOT, OUT, fname), "w", encoding="utf-8").write(content)
        print(f"  ✓ {fname} ({len(content)} chars)")

    index = f"""---
title: {yq(INDEX_TITLE)}
description: {yq(INDEX_DESC)}
keywords: {yq(INDEX_KEYWORDS)}
lang: en
---

# {INDEX_H1}

{INDEX_DESC}

| Page | One-liner |
| :--- | :--- |
""" + "\n".join(
        f"| **[{t.split(' · ')[0]}]({f})** | {SECTIONS[i][4]} |"
        for i, (f, t, *_r) in enumerate(SECTIONS)
    ) + "\n"
    open(os.path.join(ROOT, OUT, "index.md"), "w", encoding="utf-8").write(index)
    print(f"  ✓ index.md ({len(index)} chars)")

if __name__ == "__main__":
    main()
