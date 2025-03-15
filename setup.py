import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FlagCliAction",
    version="1.0.0",
    author="AdamantLife",
    author_email="contact.adamantmedia@gmail.com",
    description="Provides a framework for using enum Flags with the argparse module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdamantLife/FlagCliAction",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
