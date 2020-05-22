import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wafamole",
    version="0.0.2",
    author="Valenza, Demetrio",
    author_email="[andrea.valenza | luca.demetrio]@dibris.unige.it",
    description="Fuzzing ML-based WAFs for fun and profit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    package_dir={"wafamole" : "wafamole"},
    package_data={"wafamole" : ["tokenizer/*","models/custom/example_models/*"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    py_modules=['wafamole'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        wafamole=wafamole.cli:wafamole
    ''',

)
