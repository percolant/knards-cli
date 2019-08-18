from setuptools import setup, find_packages

setup(
  name='knards',
  packages=find_packages(where='src'),
  package_dir={'': 'src'},
  install_requires=[
    'Click',
    'readchar',
    'termcolor',
  ],
  entry_points='''
    [console_scripts]
    knl=knards.knards:main
  ''',
)
