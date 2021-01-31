from pathlib import Path
from setuptools import setup, find_packages


setup(
    name='actionpack',
    description='a lib for describing Actions and how they should be performed',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=[
        'setuptools-git-version==1.0.3'
    ],
    packages=find_packages(exclude=['tests']),
    maintainer='Emmanuel I. Obi',
    maintainer_email='withtwoemms@gmail.com',
    url='https://github.com/withtwoemms/action-pack',
    include_package_data=True,
    install_requires=[
        'OSlash==0.5.1',
    ]
)
