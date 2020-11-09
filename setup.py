import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-animethemes",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Buzzbyte",
    description="A Python wrapper for AnimeThemes.moe API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/buzzbyte/python-animethemes",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
)