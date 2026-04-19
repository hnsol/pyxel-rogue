class RogueRng:
    """Small RNG facade matching Rogue 5.4.4 helper names."""

    def __init__(self, backend):
        self.backend = backend

    def rnd(self, n):
        return self.randrange(n) if n > 0 else 0

    def roll(self, number, sides):
        return sum(self.rnd(sides) + 1 for _ in range(number))

    def spread(self, nm):
        return nm - nm // 20 + self.rnd(nm // 10)

    def randint(self, a, b):
        return self.backend.randint(a, b)

    def randrange(self, n):
        return self.backend.randrange(n)

    def random(self):
        return self.backend.random()

    def choice(self, seq):
        return self.backend.choice(seq)

    def shuffle(self, seq):
        self.backend.shuffle(seq)

    def sample(self, seq, k):
        return self.backend.sample(seq, k)
