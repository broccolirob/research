import importlib
import pkgutil
import sys
from pathlib import Path

def main():
    tests_path = Path(__file__).parent / "tests"
    success = True
    for info in pkgutil.iter_modules([str(tests_path)]):
        if info.name.startswith("test"):
            module = importlib.import_module(f"tests.{info.name}")
            for name in dir(module):
                if name.startswith("test"):
                    func = getattr(module, name)
                    if callable(func):
                        try:
                            func()
                            print(f"{info.name}.{name}: PASS")
                        except AssertionError as e:
                            success = False
                            print(f"{info.name}.{name}: FAIL\n{e}")
                        except Exception as e:
                            success = False
                            print(f"{info.name}.{name}: ERROR\n{e}")
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
