from setuptools import setup, find_packages

setup(
    name='oniref',
    version='0.1',
    description='Oxygen Not Included reference database',
    author_email='tim.prince@gmail.com',
    packages=find_packages(),
    install_requires=['pint', 'pyyaml', 'polib'],
    entry_points={},
    tests_require=[
        'pytest',
    ],
)
