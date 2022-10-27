from setuptools import setup

setup(
    name='stdfparser',
    version='0.1',
    packages=['stdfparser', 'stdfparser.db', 'stdfparser.stdf', 'stdfparser.util', 'stdfparser.view',
              'stdfparser.parser_csv'],
    package_dir={'': 'src'},
    url='https://github.com/peterjcwu/stdfparser',
    license='MIT',
    author='Peter J.C. Wu',
    author_email='wolf952@gmail.com',
    description='Parse STDF'
)
