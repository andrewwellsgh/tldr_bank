import os

# Change this to your project root
project_root = "./src/tldr_bank"
output_file = "project_export.txt"

# Collect all Python files recursively
py_files = []
for root, dirs, files in os.walk(project_root):
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

# Write to single output file
with open(output_file, "w", encoding="utf-8") as out:
    for f in py_files:
        out.write("#" * 80 + "\n")
        out.write(f"# FILE: {os.path.relpath(f, project_root)}\n")
        out.write("#" * 80 + "\n\n")
        with open(f, "r", encoding="utf-8") as infile:
            out.write(infile.read())
        out.write("\n\n")