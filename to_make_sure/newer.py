def compare_files(file1_path, file2_path):
    try:
        with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
            file1_lines = file1.readlines()
            file2_lines = file2.readlines()

        max_lines = max(len(file1_lines), len(file2_lines))

        differences = []

        for i in range(max_lines):
            file1_line = file1_lines[i].strip() if i < len(file1_lines) else ""
            file2_line = file2_lines[i].strip() if i < len(file2_lines) else ""

            if file1_line != file2_line:
                differences.append((i + 1, file1_line, file2_line))

        if not differences:
            print("The files are identical.")
        else:
            print("Differences found:")
            for line_num, line1, line2 in differences:
                print(f"Line {line_num}:\nFile1: {line1}\nFile2: {line2}\n")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
file1_path = '../bruh.txt'
file2_path = '../text_send.txt'
compare_files(file1_path, file2_path)
