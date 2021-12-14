
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='CwnAnnot',    
    version='0.1.0',    
    description='A CWN Annotation Utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lopentu/CwnAnnot',    
    author='Sean Tseng',    
    author_email='seantyh@gmail.com',  # Optional    
    classifiers=[        
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',                
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='language resource, nlp, annnotation',
    package_dir={'': 'src'},
    python_requires='>=3.6, <4',
    install_requires=['CwnGraph']
)