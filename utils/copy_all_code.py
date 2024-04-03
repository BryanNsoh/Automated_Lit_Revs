import os


def copy_py_to_txt(output_file, folder):
    with open(output_file, "w") as outfile:
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not (
                filename.endswith(".yaml") or filename.endswith(".json")
            ):
                file_path = os.path.join(folder, filename)
                with open(file_path, "r") as infile:
                    outfile.write(f"\n\n# Contents of {file_path}\n")
                    outfile.write(infile.read())


def main():
    current_folder = "./utils"
    output_filename = "all_python_contents.txt"
    copy_py_to_txt(output_filename, current_folder)
    print(f"All .py file contents copied to {output_filename}")


if __name__ == "__main__":
    main()
