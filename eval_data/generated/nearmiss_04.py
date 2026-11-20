import re

pattern = r"\d+\.\d+"
print(re.findall(pattern, "pi is 3.14"))
