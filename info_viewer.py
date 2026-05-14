"""Simple information viewer for README_RESOURCE_OPTIMIZED.md."""

from pathlib import Path


def load_readme() -> str:
    readme_path = Path(__file__).resolve().parent / 'README_RESOURCE_OPTIMIZED.md'
    if not readme_path.exists():
        return 'Error: README_RESOURCE_OPTIMIZED.md not found in the application folder.'

    return readme_path.read_text(encoding='utf-8')


def main() -> None:
    print('--- VRChat Bot Resource-Optimized Information ---\n')
    content = load_readme()
    print(content)


if __name__ == '__main__':
    main()
