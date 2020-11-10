from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='metawave',
    version='1.0',
    description='Tool for generating meta-information for TTS datasets',
    long_description=readme(),
    keywords='TTS datasets meta analytics',
    url='https://github.com/cadia-lvl/metawave',
    author='atlisig',
    author_email='atlithors@ru.is',
    packages=find_packages(),
    install_requires=[
        'absl-py==0.2.2',
        'astor==0.6.2',
        'astroid==1.6.4',
        'audioread==2.1.6',
        'bleach==1.5.0',
        'cffi==1.11.5',
        'cycler==0.10.0',
        'Cython==0.28.3',
        'decorator==4.3.0',
        'gast==0.2.0',
        'grpcio==1.12.0',
        'h5py==2.7.1',
        'hmmlearn==0.2.0',
        'html5lib==0.9999999',
        'imageio==2.3.0',
        'isort==4.3.4',
        'joblib==0.11',
        'kiwisolver==1.0.1',
        'lazy-object-proxy==1.3.1',
        'librosa==0.6.1',
        'llvmlite==0.23.2',
        'Markdown==2.6.11',
        'matplotlib==2.2.2',
        'mccabe==0.6.1',
        'numba==0.38.1',
        'numpy==1.14.3',
        'Pillow==7.1.0',
        'protobuf==3.5.2.post1',
        'pycparser==2.18',
        'pylint==1.9.1',
        'pyparsing==2.2.0',
        'PySoundFile==0.9.0.post1',
        'python-dateutil==2.7.3',
        'pytz==2018.4',
        'pyworld==0.2.4',
        'PyYAML==3.12',
        'resampy==0.2.0',
        'scikit-learn==0.19.1',
        'scipy==1.1.0',
        'six==1.11.0',
        'tensorboard==1.8.0',
        'termcolor==1.1.0',
        'tqdm==4.23.4',
        'Werkzeug==0.14.1',
        'wrapt==1.10.11'
    ],
    entry_points={
          'console_scripts': ['metawave=metawave.metawave:main'],
      },
    include_package_data=True,
    zip_safe=False)
