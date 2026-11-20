def title_case(text):
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
import sys
print(sys.byteorder)
