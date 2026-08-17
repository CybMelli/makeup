import itertools
from datetime import datetime
import os 
LEET = {'a':'@','b':'8','e':'3','i':'1','o':'0','g':'9','l':'1','z':'2'}
PREFIXES = ['my','the','super','ultra','king','root','admin']
SURFIXES = ['123','2024','2025','!','@','666','777']
SYMBOLS = '!@#$%^&*'

def mutate (word):
    #case combo
    variants = {''.join(c) for c in itertools.product(*[(c.lower(), c.upper()) for c in word])}

    #Leet
    variants.add(word.translate(str.maketrans(LEET)))

    #Prefixes + Surfixes
     
    variants = {p+v for v in variants for p in PREFIXES}
    variants = {v+s for v in variants for s in SURFIXES}

    #Symbol 
    varinats = {v[:i]+s+v[i:]for v in variants for s in SYMBOLS for i in range (len(v))}
    return sorted(variants)

base = input ("Enter your base:")
out = mutate(base)
    
script_dir = os.path.dirname(os.path.abspath(__file__))
fname = os.path.join (script_dir, f"passlist_{base}_{datetime.now().strftime('%H%M%S')}.txt")

with open (fname,'w') as f:
    f.write('\n'.join(out))

print (f"{len(out)}passwords->{fname}")
print (f"savedto:{fname}")


    