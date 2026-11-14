#!/usr/bin/env python3
"""texts.json の構造・記録キー・選択肢を検証する（依存ライブラリなし）。"""
import json, re, sys

path = sys.argv[1] if len(sys.argv) > 1 else "texts.json"
try:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
except (OSError, json.JSONDecodeError) as exc:
    print(f"NG: JSONを読み込めません: {exc}")
    sys.exit(1)

errors = []
ids = set()
total_questions = 0

def plain(value):
    return re.sub(r"([一-龯々]+)《[^》]+》", r"\1", str(value))

for t in data:
    tid = t.get("id", "?")
    if tid in ids:
        errors.append(f"{tid}: idが重複しています")
    ids.add(tid)

    for key in ("grade", "kind", "title", "sentences", "questions"):
        if key not in t:
            errors.append(f"{tid}: {key} がありません")

    if t.get("grade") not in (1, 2):
        errors.append(f"{tid}: grade は1または2にしてください")
    if t.get("kind") not in ("ものがたり", "せつめい"):
        errors.append(f"{tid}: kind が不正です")
    if not isinstance(t.get("sentences"), list) or not t["sentences"]:
        errors.append(f"{tid}: sentences は1文以上の配列にしてください")
        continue
    if not isinstance(t.get("questions"), list) or not t["questions"]:
        errors.append(f"{tid}: questions は1問以上の配列にしてください")
        continue

    question_keys = [plain(q.get("q", "")) for q in t["questions"]]
    if len(question_keys) != len(set(question_keys)):
        errors.append(f"{tid}: 問題文が重複しています（とっくん記録のキーが衝突します）")

    for i, q in enumerate(t["questions"], 1):
        total_questions += 1
        if not isinstance(q.get("q"), str) or not q["q"].strip():
            errors.append(f"{tid} 問題{i}: q がありません")
        if not isinstance(q.get("explain"), str) or not q["explain"].strip():
            errors.append(f"{tid} 問題{i}: explain がありません")

        if q.get("format") == "sort":
            cards = q.get("cards", [])
            ev = q.get("evidence")
            if not isinstance(cards, list) or len(cards) < 3:
                errors.append(f"{tid} 問題{i}: sort の cards は3つ以上必要です")
            if (not isinstance(ev, list) or len(ev) != len(cards)
                    or any(not isinstance(x, int) or isinstance(x, bool)
                           or not (0 <= x < len(t["sentences"])) for x in ev)):
                errors.append(f"{tid} 問題{i}: sort の evidence はcardsと同じ長さの文番号リストにしてください")
            continue

        choices = q.get("choices", [])
        if not isinstance(choices, list) or len(choices) != 3:
            errors.append(f"{tid} 問題{i}: choices は3つにしてください")
            continue
        normalized_choices = [plain(c) for c in choices]
        if len(normalized_choices) != len(set(normalized_choices)):
            errors.append(f"{tid} 問題{i}: ふりがなを除くと同じ選択肢があります")
        if q.get("answer") not in choices:
            errors.append(f"{tid} 問題{i}: answer が choices にありません")
        ev = q.get("evidence")
        if not isinstance(ev, int) or isinstance(ev, bool) or not (0 <= ev < len(t["sentences"])):
            errors.append(f"{tid} 問題{i}: evidence が文の範囲外です")

        skill = q.get("skill")
        if skill is not None and (not isinstance(skill, str) or not skill.strip()):
            errors.append(f"{tid} 問題{i}: skill は空でない文字列にしてください")

    if "order" in t:
        order = t["order"]
        if (not isinstance(order, list) or len(order) < 2
                or any(not isinstance(x, int) or isinstance(x, bool)
                       or not (0 <= x < len(t["sentences"])) for x in order)):
            errors.append(f"{tid}: order は範囲内の文番号を2つ以上並べた配列にしてください")
        elif len(set(order)) != len(order):
            errors.append(f"{tid}: order に重複があります")

if errors:
    print("NG:")
    for error in errors:
        print(" -", error)
    sys.exit(1)

print(f"OK: {len(data)}本 / {total_questions}問")
