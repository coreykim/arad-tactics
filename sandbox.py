class Sponge():
    def __init__(self):
        self.a = 5
class Water():
    def __init__(self, sponge):
        self.soak = sponge.a
bob = Sponge()
dasani = Water(bob)
bob.a = 8

print dasani.soak