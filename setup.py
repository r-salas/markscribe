import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r") as fp:
    long_description = fp.read()

about = {}
with open(os.path.join(here, "markscribe", "version.py"), "r") as f:
    exec(f.read(), about)

setuptools.setup(
    name="markscribe",
    version=about["__version__"],
    author=about["__author__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    install_requires=[
        "openai>=1.0.0",
        "typer>=0.10.0",
        "pdf2image>=1.16.0",
        "Pillow>=9.0.0",
        "tqdm>=4.50.0"
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers"
    ],
    entry_points={
        'console_scripts': [
            'markscribe=markscribe.cli:run',
        ],
    },
)
