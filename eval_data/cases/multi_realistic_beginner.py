import os
import random


def play():
    l = [1, 2, 3, 4, 5, 6]  
    target = random.choice(l)
    try:
        guess = int(input("Guess the number (1-6): "))
    except:
        print("That was not a number")
        return
    if guess == target:
        print("Correct!")
    else:
        print("Wrong, it was", target)


play()
