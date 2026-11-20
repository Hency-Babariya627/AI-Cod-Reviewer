class Dog:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name + " says woof"


print(Dog("Rex").speak())
