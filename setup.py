import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sunset-scale",
    version="0.0.8",
    author="Julian Quandt",
    author_email="julian_quandt@live.de",
    description="A circular scale to assess ratings, rating-times, action-initiation-times and mouse-tracks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/julianquandt/sunset_scale",
    include_package_data = True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)