"""Allow devenv to be run as a module: python -m devenv"""

from .cli import main

if __name__ == '__main__':
    main()
