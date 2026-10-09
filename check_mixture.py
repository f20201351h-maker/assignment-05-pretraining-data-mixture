"""Reconcile mixture.yaml and print the numbers quoted in the README.

Usage: python check_mixture.py
Fails with an AssertionError if any share, tier split or reserve does not add up.
"""
import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(__file__).with_name("mixture.yaml").read_text(encoding="utf-8"))
lanes = cfg["lanes"]
B = cfg["budget"]
main, anneal = B["main_run"], B["anneal"]
close = lambda a, b, tol=1e-6: abs(a - b) <= tol

# 1. Budget and stage arithmetic
assert close(main + anneal + B["post_training_cap"], B["total"]), "stage budgets != total"
assert close(sum(s["span"] for s in cfg["stages"].values()), 1.0), "stage spans != 1"
for name, s in cfg["stages"].items():
    assert set(s["mix"]) == set(lanes), name
    assert close(sum(s["mix"].values()), 100), f"{name} mix sums to {sum(s['mix'].values())}"
assert close(sum(cfg["anneal_mix"].values()), 100), "anneal mix != 100"

# 2. Token demand per lane
main_tok = {l: sum(s["span"] * s["mix"][l] / 100 * main for s in cfg["stages"].values()) for l in lanes}
ann_tok = {l: cfg["anneal_mix"][l] / 100 * anneal for l in lanes}
assert close(sum(main_tok.values()), main, 1e-3) and close(sum(ann_tok.values()), anneal, 1e-3)

print("## Lane demand (B tokens)\n")
print("| lane | main avg % | main B | anneal % | anneal B | % of main+anneal |")
print("|---|---|---|---|---|---|")
for l in lanes:
    tot = (main_tok[l] + ann_tok[l]) / (main + anneal) * 100
    print(f"| {l} | {main_tok[l] / main * 100:.2f} | {main_tok[l]:.1f} | {cfg['anneal_mix'][l]} | {ann_tok[l]:.1f} | {tot:.2f} |")

# 3. Protected floor per stage
print("\n## Protected always-on floor (% of every batch)\n")
for name, s in cfg["stages"].items():
    parts = {l: s["mix"][l] for l in cfg["protected"]}
    print(f"- {name}: {sum(parts.values()):g}  {parts}")

# 4. Indic tiers reconcile with the headline
tiers = cfg["indic_main_tiers"]
assert close(sum(tiers.values()), main_tok["indic"], 1e-3), "Indic tiers != Indic main tokens"
assert close(sum(cfg["indic_anneal"].values()), ann_tok["indic"], 1e-3), "Indic anneal split != anneal Indic"
print("\n## Indic tiers, main run\n")
for k, v in tiers.items():
    print(f"- {k}: {v}B = {v / main_tok['indic'] * 100:.1f}% of Indic = {v / main * 100:.2f}% of main run")
native = tiers["A_verified_native"] + tiers["B_unverified_native"]
print(f"- native (A+B): {native / main_tok['indic'] * 100:.1f}% of the Indic lane")

# 5. Supply: unique tokens, reserve, passes in the main run
P = cfg["pools"]
web_candidates = main_tok["web"] / cfg["selector_keep"]["web"]
demand = {
    "web": web_candidates,                       # candidates the selector must see
    "code": main_tok["code"], "code_high": main_tok["code"],
    "stem": main_tok["stem"], "long_context": main_tok["long_context"],
    "indic_A": tiers["A_verified_native"], "indic_B": tiers["B_unverified_native"],
    "indic_C": tiers["C_translated"], "indic_D": tiers["D_synthetic"],
    "reasoning": main_tok["reasoning"], "agentic_multistep": main_tok["agentic"],
}
carve = {"code": 60, "code_high": 60}            # repo-packed code moved to the long-context lane
print("\n## Supply check, main run\n")
print("| pool | unique B | held back B | main demand B | passes | to generate B (at 4 passes) | source |")
print("|---|---|---|---|---|---|---|")
for k, d in demand.items():
    p = P[k]
    avail = p["unique"] - p["reserve"] - carve.get(k, 0)
    assert avail >= 0, k
    passes = d / avail if avail > 0 else float("inf")
    need = max(0.0, d / cfg["max_passes"] - avail)
    ptxt = f"{passes:.2f}" if passes < 100 else "n/a"
    print(f"| {k} | {p['unique']} | {p['reserve'] + carve.get(k, 0):g} | {d:.1f} | {ptxt} | {need:.1f} | {p['kind']} |")
    if k in ("indic_A", "indic_B", "stem", "long_context", "code", "agentic_multistep"):
        assert passes <= cfg["max_passes"], f"{k} exceeds {cfg['max_passes']} passes"

# 6. Reserve is not double counted: anneal demand for scarce lanes vs what was held back
print("\n## Anneal reserve\n")
r_ind = cfg["indic_anneal"]
assert r_ind["A_reserved_fresh"] <= P["indic_A"]["reserve"]
print(f"- Indic: {r_ind['A_reserved_fresh']}B fresh Tier A + {r_ind['A_replay_top']}B replay + {r_ind['D_synthetic_verified']}B Tier D = {ann_tok['indic']:.1f}B")
for lane, pool in (("reasoning", "reasoning"), ("agentic", "agentic_tierA")):
    print(f"- {lane}: anneal {ann_tok[lane]:.1f}B from {P[pool]['reserve']}B held back = {ann_tok[lane] / P[pool]['reserve']:.1f} passes")
main_unique = main_tok["reasoning"] / cfg["max_passes"]
have = P["reasoning"]["unique"] - P["reasoning"]["reserve"]
print(f"- reasoning, main run: {main_tok['reasoning']:.1f}B needs {main_unique:.1f}B unique at 4 passes; {have}B left after the reserve; {main_unique - have:.1f}B to generate")

# 7. Reasoning-length bands: samples vs tokens
rb = cfg["reasoning_bands"]
assert close(sum(b["sample_share"] for b in rb.values()), 100)
w = {k: b["sample_share"] * b["mean_tokens"] for k, b in rb.items()}
print("\n## Reasoning bands: share of samples vs share of tokens\n")
for k, b in rb.items():
    print(f"- {k}: {b['sample_share']}% of samples, {w[k] / sum(w.values()) * 100:.1f}% of trace tokens")

# 8. What the same absolute scarce-lane tokens look like at the low end of the course budget range
small_main = 2400 * main / B["total"]
code_share = main_tok["code"] / main
fixed = sum(main_tok[l] for l in lanes if l not in ("web", "code"))
web_small = small_main * (1 - code_share) - fixed
print(f"\n## 2.4T run, scarce lanes fixed in tokens, code held at {code_share:.1%}\n")
print(f"- Indic {main_tok['indic'] / small_main:.1%}, web {web_small / small_main:.1%} of the main run")

# 9. Proxy cost (estimate): FLOPs ~ 6 * params * tokens
print("\n## Proxy compute (estimate)\n")
for params, toks in ((1e9, 20e9), (3e9, 30e9)):
    flops = 6 * params * toks
    for util in (0.35, 0.45):
        hours = flops / (989e12 * util) / 3600   # H100 dense bf16 peak ~989 TFLOPS
        print(f"- {params / 1e9:.0f}B params x {toks / 1e9:.0f}B tokens: {flops:.1e} FLOPs, {hours:.0f} H100-hours at {util:.0%} utilisation")

print("\nAll checks passed.")
sys.exit(0)
