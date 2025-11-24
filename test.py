import os

with open("test_write.txt", "w") as f:
    f.write("test")
os.remove("test_write.txt")
print("Hai i permessi di scrittura!")