import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cache-manager-grll",
    version="0.0.1",
    author="Guillaume Raille",
    author_email="guillaume.raille@gmail.com",
    description="A minimalistic pickle based cache manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grll/cache-manager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
