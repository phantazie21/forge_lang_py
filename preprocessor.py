import pathlib
import re
import error

IMPORT_PATTERN = re.compile(r'import\s+(?P<module><\w+>|"[\w\/\.\:]+\.fl")')
HEADERS = pathlib.Path("C:/Users/phanta/forge_lang_py/headers") #Change statically!

class Import:
    def __init__(self, path, line, start, end, module):
        self.path = path
        self.line = line
        self.start = start
        self.end = end
        self.module = module

class PreProcessor:
    def __init__(self, source, filename=""):
        self.includes : dict[str, Import] = {}
        self.source : str = source
        self.lines = 1
        self.filepath = pathlib.Path(filename).resolve()
        self.resolve_imports()
    
    def resolve_imports(self):
        def process_imports(source, filepath, processed_files):
            paths = set()
            lines = source.splitlines(keepends=True)
            for n, line in enumerate(lines):
                try:
                    if line.strip() and (match := IMPORT_PATTERN.match(line.strip())):
                        module = match.group("module")
                        path = pathlib.Path(filepath.parent / module[1:-1])
                        if module.startswith("<"):
                            path = HEADERS / f"{module[1:-1]}.fl"
                        path = path.resolve()
                        if not path.is_file():
                            raise Exception(f'Cannot find module "{path}".')
                        if path == filepath:
                            raise Exception("Cannot import current module.")
                        if path in processed_files:
                            raise Exception(f'Cyclical import detected: "{path}".')
                        paths.add(path)
                        self.includes[path.as_posix()] = Import(path, n, match.start(), match.end(), module)
                except Exception as e:
                    error.error(n + 1, e)
                    break
            for module in list(self.includes.values()):
                if module.path in processed_files:
                    continue
                text = module.path.read_text()
                self.lines += text.count("\n")
                source = source.replace(f"import {module.module}", text)
                processed_files.add(module.path)
                source = process_imports(source, module.path, processed_files)
            return source

        processed_files = set()
        processed_files.add(self.filepath)
        self.source = process_imports(self.source, self.filepath, processed_files)