import itertools
from datetime import datetime
import os

LEET = {'a':'@','e':'3','i':'1','o':'0','s':'$','t':'7','b':'8','g':'9','l':'1','z':'2'}
PREFIXES = ['my', 'the', 'super', 'ultra', 'king', 'admin', 'root']
SUFFIXES = ['123','2025','2026','!','@','666','777']
SYMBOLS = '!@#$%^&*'

def mutate(word):
    # Case combos 
    variants = {''.join(c) for c in itertools.product(*[(c.lower(), c.upper()) for c in word])}

    # Leet 
    variants.add(word.translate(str.maketrans(LEET)))

    # Prefixes + Suffixes
    variants = {p + v for v in variants for p in PREFIXES}
    variants = {v + s for v in variants for s in SUFFIXES}

    # Symbol injection
    variants = {v[:i] + s + v[i:] for v in variants for s in SYMBOLS for i in range(len(v))}

    return sorted(variants)

base = input("Enter your base: ")
out = mutate(base)

# Save to script's directory, not wherever you run from
script_dir = os.path.dirname(os.path.abspath(__file__))
fname = os.path.join(script_dir, f"passlist_{base}_{datetime.now().strftime('%H%M%S')}.txt")

with open(fname, 'w') as f:
    f.write('\n'.join(out))

print(f"✅ {len(out)} passwords -> {fname}")
print(f"📁 Saved to: {fname}")