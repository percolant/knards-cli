from setuptools import setup, find_packages

setup(
  name='knards',
  packages=find_packages(where='src'),
  package_dir={'': 'src'},
  install_requires=[
    'Click',
    'readchar',
    'termcolor',
    'blist',
  ],
  entry_points='''
    [console_scripts]
    kn=knards.knards:main
  ''',
)
