import os
from utils import show_error


class File:
    def __init__(self, path: str):
        self.path = path
        self.lines = self._read_lines()

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

    def replace_index(self, new_line, i, line = "Unknown"):
        if i >= 0:
            self.lines[i] = f"{new_line}\n"
            print(f"[INFO] Replaced {line} in {self.path}")

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

    def delete_line(self, *search_terms):
        self.lines = [
            line for line in self.lines if not all(term.lower() in line.lower() for term in search_terms)
        ]
        print(f"[INFO] Deleted lines containing {search_terms}")

    def copy_file(self, other):
        other.lines = self.lines
        other.write_lines()