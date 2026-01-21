"""
Automate deployment to PyPi
"""

import invoke,pathlib


def get_token():

    with open(f"{pathlib.Path(__file__).parent /'token.json' }", "r") as cfg:

        return cfg['token']

@invoke.task
def deploy(ctx):
    """
    Automate deployment
    rm -rf build/* dist/*
    bumpversion patch --verbose
    python3 setup.py sdist bdist_wheel
    twine upload dist/*
    git push --tags
    """
    ctx.run("python3 -m build")
    ctx.run("python3 -m twine check dist/*")
    ctx.run(f"python3 -m twine upload --config-file {pathlib.Path(__file__).parent / '.pypirc' } dist/*")
    