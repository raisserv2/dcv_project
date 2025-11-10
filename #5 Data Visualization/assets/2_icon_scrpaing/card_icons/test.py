import os

folder = "./"   # change to your folder path

for filename in os.listdir(folder):
    if filename.endswith(".webp"):
        new_name = filename.replace("_", " ")
        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)
        os.rename(old_path, new_path)
        print(f"{filename} → {new_name}")
