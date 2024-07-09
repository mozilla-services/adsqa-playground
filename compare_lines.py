def read_lines(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def parse_categories(lines):
    categories = {}
    current_title = None

    for line in lines:
        if line.startswith("title:"):
            current_title = line.replace("title: ", "").strip()
            if current_title not in categories:
                categories[current_title] = []
        elif line.startswith("http"):
            continue  # Skip the URL lines
        elif current_title:
            keywords = line.split(',')
            categories[current_title].extend([keyword.strip() for keyword in keywords if keyword.strip()])

    return categories

def compare_files(oldfile, newfile, output_file):
    lines1 = read_lines(oldfile)
    lines2 = read_lines(newfile)

    categories1 = parse_categories(lines1)
    categories2 = parse_categories(lines2)

    with open(output_file, 'w') as file:
        # Compare categories in oldfile with newfile
        for title in categories1.keys():
            keywords1 = categories1.get(title, [])
            keywords2 = categories2.get(title, [])

            added_keywords = [keyword for keyword in keywords2 if keyword not in keywords1]
            removed_keywords = [keyword for keyword in keywords1 if keyword not in keywords2]

            if added_keywords or removed_keywords:
                file.write(f"title: {title}\n")
                if added_keywords:
                    file.write(f"added: {', '.join(added_keywords)}\n")
                if removed_keywords:
                    file.write(f"removed: {', '.join(removed_keywords)}\n")
                file.write("\n")

        # Compare categories in newfile that are not in oldfile
        for title in categories2.keys():
            if title not in categories1:
                keywords2 = categories2.get(title, [])
                file.write(f"title: {title}\n")
                file.write(f"added: {', '.join(keywords2)}\n")
                file.write("\n")

if __name__ == "__main__":
    oldfile = "oldfile2.txt"
    newfile = "newfile.txt"
    output_file = "differences.txt"
    compare_files(oldfile, newfile, output_file)
