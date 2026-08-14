from functions.run_python_file import run_python_file


print("1. main.py:")
print(run_python_file("calculator", "main.py"))

print("\n2. main.py with argument:")
print(run_python_file("calculator", "main.py", ["3 + 5"]))

print("\n3. tests.py:")
print(run_python_file("calculator", "tests.py"))

print("\n4. outside working directory:")
print(run_python_file("calculator", "../main.py"))

print("\n5. nonexistent file:")
print(run_python_file("calculator", "nonexistent.py"))

print("\n6. non-Python file:")
print(run_python_file("calculator", "lorem.txt"))
