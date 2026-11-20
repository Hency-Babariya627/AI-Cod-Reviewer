def title_case(text):
    return " ".join(word.capitalize() for word in text.split())


answer = "a"
if answer:
	print(answer)
print(title_case("learning python is fun"))
