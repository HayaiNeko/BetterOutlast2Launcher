import os
from widgets import show_error


class File:
    files = []
    game_directory = os.getcwd()
    demo_directory = None

    def __init__(self, path: str, demo_file: bool = False):
        self.path = path
        self.local_path = os.path.relpath(self.path, self.__class__.game_directory)
        self.lines = self._read_lines()

        if not demo_file:
            self.__class__.files.append(self)

    def _read_lines(self):
        if not os.path.exists(self.path):
            show_error(f"File not found: {self.path}")
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return file.readlines()
        except Exception as e:
            show_error(f"Unable to read file {self.path}: {e}")
            return []

    def write_lines(self):
        try:
            with open(self.path, "w", encoding="utf-8") as file:
                file.writelines(self.lines)
            print(f"[INFO] Updated lines written in {self.path}")
        except Exception as e:
            show_error(f"Unable to write to file {self.path}: {e}")

    def get_line(self, *search_terms: str) -> (int, str):
        for i, line in enumerate(self.lines):
            if all(term.lower() in line.lower() for term in search_terms):
                return i, line.strip()
        return -1, None

    def get_lines(self, *search_terms: str):
        lines = []
        for line in self.lines:
            if all(term.lower() in line.lower() for term in search_terms):
                lines.append(line.strip())
        return lines

    def get_lines_after(self, *search_terms):
        i, _ = self.get_line(*search_terms)

        if i == -1 or i + 1 >= len(self.lines):
            return []

        return self.lines[i + 1:]

    def replace_index(self, new_line, i, line = "Unknown"):
        if i >= 0:
            self.lines[i] = f"{new_line}\n"
            print(f"[INFO] Replaced {line} with {new_line} in {self.path}")

    def replace_line(self, new_line: str, *search_terms: str):
        i, line = self.get_line(*search_terms)
        self.replace_index(new_line, i, line)

    def replace_or_add(self, new_line: str, *search_terms: str):
        i, line = self.get_line(*search_terms)
        if i >= 0:
            self.lines[i] = f"{new_line}\n"
            print(f"[INFO] Replaced {line} by {new_line} in {self.path}")
        else:
            self.lines.append(f"{new_line}\n")
            print(f"[INFO] Added {new_line} in {self.path}")

    def remove_line(self, *search_terms):
        self.lines = [
            line for line in self.lines if not all(term.lower() in line.lower() for term in search_terms)
        ]
        print(f"[INFO] Deleted lines containing {search_terms}")

    def replace_term(self, term: str, newterm: str):
        """
        Replace all occurrences of `term` with `newterm`.
        """
        occurrences = 0
        for idx, line in enumerate(self.lines):
            if term in line:
                count = line.count(term)
                self.lines[idx] = line.replace(term, newterm)
                occurrences += count
        if occurrences > 0:
            print(f"[INFO] Replaced {occurrences} occurrences of '{term}' with '{newterm}' in {self.path}")
        else:
            print(f"[INFO] No occurrences of '{term}' found in {self.path}")

    def delete_duplicates(self, term: str):
        """
        Search for lines containing `term` and delete duplicates, keeping only the first occurrence.
        """
        seen = False
        new_lines = []
        deleted = 0
        for line in self.lines:
            if term in line:
                if not seen:
                    new_lines.append(line)
                    seen = True
                else:
                    deleted += 1
                    continue
            else:
                new_lines.append(line)
        self.lines = new_lines
        if deleted > 0:
            print(f"[INFO] Deleted {deleted} duplicate lines containing '{term}' in {self.path}, kept first occurrence")
        else:
            print(f"[INFO] No duplicate lines containing '{term}' found in {self.path}")

    def copy_file(self, other):
        other.lines = self.lines
        other.write_lines()

    def sync_file_with_old_patch(self):
        demo_file = File(os.path.join(self.__class__.demo_directory, self.local_path), demo_file=True)
        self.copy_file(demo_file)

    @classmethod
    def sync_all_with_old_patch(cls):
        for file in cls.files:
            file.sync_file_with_old_patch()
