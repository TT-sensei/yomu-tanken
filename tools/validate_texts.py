#!/usr/bin/env python3
"""texts.json の検証スクリプト（依存ライブラリなし）。
使い方: python3 tools/validate_texts.py [texts.jsonのパス]
チェック内容: idの重複、問題文の重複、正解が選択肢にあるか、evidence/order の範囲、必須フィールド。"""
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "texts.json"
data = json.load(open(path, encoding="utf-8"))
errors = []
ids = set()
for t in data:
    tid = t.get("id", "?")
    if tid in ids: errors.append(f"{tid}: idが重複しています")
    ids.add(tid)
    for k in ("grade", "kind", "title", "sentences", "questions"):
        if k not in t: errors.append(f"{tid}: {k} がありません")
    qs = [q.get("q") for q in t.get("questions", [])]
    if len(qs) != len(set(qs)): errors.append(f"{tid}: 問題文が重複しています（とっくん記録のキーが衝突します）")
    for i, q in enumerate(t.get("questions", [])):
        if q.get("answer") not in q.get("choices", []):
            errors.append(f"{tid} 問題{i+1}: answer が choices にありません")
        ev = q.get("evidence")
        if not isinstance(ev, int) or not (0 <= ev < len(t.get("sentences", []))):
            errors.append(f"{tid} 問題{i+1}: evidence が文の範囲外です")
    if "order" in t:
        o = t["order"]
        if len(set(o)) != len(o): errors.append(f"{tid}: order に重複があります")
        if any(not (0 <= i < len(t["sentences"])) for i in o): errors.append(f"{tid}: order が文の範囲外です")
if errors:
    print("NG:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: {len(data)}本 / {sum(len(t['questions']) for t in data)}問")
