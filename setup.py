import os

import setuptools


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('README.md') as fin:
    README = fin.read()

install_dependencies = ('google-cloud-pubsub>=1.3',)


setuptools.setup(
    name='cloud-functions-dispatch',
    version='1.0b3',
    author='jeffrey k eliasen',
    author_email='jeff@jke.net',
    description='Dispatches decorated in-process function calls to cloud function for execution',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/seawolf42/cloud-functions-dispatch',
    packages=setuptools.find_packages(),
    license='MIT License',
    keywords='cloud functions',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Distributed Computing',
    ],
    python_requires='>=3.7',
    install_requires=install_dependencies,
)
