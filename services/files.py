def read_file_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"File is not found: {filepath}")
        return []
    except Exception as e:
        print(f"Error when reading file {filepath}: {e}")
        return []
