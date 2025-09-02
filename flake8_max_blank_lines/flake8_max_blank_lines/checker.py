# flake8: noqa
# pylint: skip-file
# type: ignore



class MaxBlankLinesChecker:
    name = "flake8-max-blank-lines"
    version = "0.1.0"
    MAX_BLANK_LINES = 2

    def __init__(self, tree, filename) -> None:
        self.filename = filename
        self.tree = tree



    def run(self):
        with open(self.filename, "r", encoding="utf-8", newline='') as f:
            content = f.read()
        
        # Normalize line endings to LF
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        lines = content.split('\n')

        prev_func_end = None
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            
            # Look for function or class definitions
            if stripped.startswith("def ") or stripped.startswith("class "):
                # Find the start of this function/class (including decorators)
                func_start = i
                
                # Look backwards for decorators
                j = i - 1
                while j >= 0:
                    prev_line = lines[j].lstrip()
                    if prev_line.startswith("@"):
                        func_start = j
                        j -= 1
                    elif not prev_line.strip():  # Skip blank lines
                        j -= 1
                    else:
                        break
                
                # Count CONSECUTIVE blank lines immediately before this function
                if prev_func_end is not None:
                    blank_lines = 0
                    
                    # Count backwards from func_start to find consecutive blank lines
                    k = func_start - 1
                    while k > prev_func_end and not lines[k].strip():
                        blank_lines += 1
                        k -= 1
                    
                    if blank_lines > self.MAX_BLANK_LINES:
                        yield (
                            i + 1,
                            0,
                            f"X303 Too many blank lines ({blank_lines}) before function/class definition (max {self.MAX_BLANK_LINES})",
                            type(self),
                        )
                
                prev_func_end = i
            
            i += 1