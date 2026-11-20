def percent(part, whole):
    return round(part / whole * 100, 1)


class Tally:
    def __init__(self):
        self.counts = {}

    def add(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1

    def total(self):
        return sum(self.counts.values())


tally = Tally()
tally.add("a")
tally.add("a")
tally.add("b")
print("a share:", percent(tally.counts["a"], tally.total()), "%")
