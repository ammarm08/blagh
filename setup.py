import re
from setuptools import setup
from os import path

project_path = path.abspath(path.dirname(__file__))


meta_file = open(path.join(project_path, "blagh", "metadata.py")).read()
md = dict(re.findall(r"__([a-z]+)__\s*=\s*'([^']+)'", meta_file))

with open(path.join(project_path, 'README.md')) as f:
    long_description = f.read()


setup(
    name='blagh',
    version=md['version'],
    author=md['author'],
    author_email=md['authoremail'],
    packages=['blagh'],
    url="http://github.com/ammarm08/blagh",
    license='MIT',
    description='Yet another blog post markup language and compiler',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[]
)
