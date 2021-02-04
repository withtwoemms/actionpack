from pathlib import Path
from setuptools import setup, find_packages


setup(
    name='actionpack',
    description='a lib for describing Actions and how they should be performed',
    long_description=Path(__file__).absolute().parent.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=[
        'setuptools-git-version==1.0.3'
    ],
    packages=find_packages(exclude=['tests']),
    maintainer='Emmanuel I. Obi',
    maintainer_email='withtwoemms@gmail.com',
    url='https://github.com/withtwoemms/actionpack',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'OSlash==0.5.1',
        'requests==2.25.1',
        'validators==0.18.2',
    ]
)

