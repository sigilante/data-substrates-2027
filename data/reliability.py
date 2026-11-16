"""Inter-coder reliability for the classification sample.

Pairs second-coder.csv (and, when present, third-coder.csv) with steps.csv on
(system, sub, step).  Ops are parsed by vocabulary words only.  Reports raw
agreement, Cohen's kappa with a 95% percentile bootstrap CI (5000 resamples,
seed 1), Gwet's AC1, and each coder's marginal rate.
"""
import csv, random, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
C = {"add","remove","rename","hoist","plunge","wrap","head","in","map","convert"}
X = {"filter","container","compute","read","re-encode"}
def ops(s): return [t for t in re.findall(r"[a-z][a-z-]*", s or "") if t in C | X]
A = {(r['system'], r['sub'], r['step']): r for r in csv.DictReader(open(os.path.join(HERE, 'steps.csv')))}
def items(other):
    rows = list(csv.DictReader(open(os.path.join(HERE, other))))
    out = []
    for b in rows:
        a = A[(b['system'], b['sub'], b['step'])]
        fb = b['flags'].strip()
        out.append(dict(
            kind=(a['kind'], b['kind'].strip()),
            cambria=(set(ops(a['ops'])) <= C, set(ops(b['ops'])) <= C),
            lens=(a['lens'] == 'yes', set(ops(b['ops'])) <= C and not fb),
            e=('e' in a['flags'], 'e' in fb), o=('o' in a['flags'], 'o' in fb), j=('j' in a['flags'], 'j' in fb)))
    return out
def kappa(pairs):
    n = len(pairs); po = sum(x == y for x, y in pairs) / n
    cats = {c for p in pairs for c in p}
    pe = sum((sum(x == c for x, _ in pairs) / n) * (sum(y == c for _, y in pairs) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else float('nan')
def ac1(pairs):
    n = len(pairs); po = sum(x == y for x, y in pairs) / n
    cats = sorted({c for p in pairs for c in p}, key=str); q = len(cats)
    if q < 2: return 1.0
    pi = [(sum(x == c for x, _ in pairs) + sum(y == c for _, y in pairs)) / (2 * n) for c in cats]
    pe = sum(p * (1 - p) for p in pi) / (q - 1)
    return (po - pe) / (1 - pe)
def boot(pairs, B=5000):
    rnd = random.Random(1); ks = []
    for _ in range(B):
        s = [pairs[rnd.randrange(len(pairs))] for _ in pairs]
        k = kappa(s)[1]
        if k == k: ks.append(k)
    ks.sort(); return ks[int(.025 * len(ks))], ks[int(.975 * len(ks)) - 1]
other = sys.argv[1] if len(sys.argv) > 1 else 'second-coder.csv'
it = items(other)
print(f"{other}: n={len(it)}")
for f in ['kind', 'cambria', 'lens', 'e', 'o', 'j']:
    p = [x[f] for x in it]; po, k = kappa(p); lo, hi = boot(p)
    extra = '' if f == 'kind' else f"  rate A {sum(a for a,_ in p)}/{len(p)}  B {sum(b for _,b in p)}/{len(p)}"
    print(f"{f:8} agree {po*100:4.0f}%  kappa {k:5.2f} [{lo:5.2f},{hi:5.2f}]  AC1 {ac1(p):4.2f}{extra}")
dis = [x for x in it if x['lens'][0] != x['lens'][1]]
print("lens disagreements:", len(dis), " turning on j alone:", sum(1 for x in dis if x['j'][0] != x['j'][1] and x['e'][0] == x['e'][1] and x['o'][0] == x['o'][1] and x['cambria'][0] == x['cambria'][1]))
