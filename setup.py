from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='vmware-tags',
    version='0.1.0',
    author='Clayton Black',
    author_email='cblack@fanatics.com',
    description='A utility for getting VMs based on tags',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'vmware-tags=vmwareTags.cli:main',
        ],
    }
)
