import itertools
import random

S = [random.randint(-10, 10) for _ in range(15)]

# O(2^|S|)
for r in range(1, len(S) + 1):
    for c in itertools.combinations(S, r):
        print(c)