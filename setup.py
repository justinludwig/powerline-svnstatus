from setuptools import setup

setup(
    name         = 'powerline-svnstatus',
    description  = 'A Powerline segment for showing the status of a Subversion working directory',
    version      = '0.1',
    keywords     = 'powerline svn status prompt',
    license      = 'MIT',
    author       = 'Justin Ludwig',
    author_email = 'justin@ldwg.us',
    url          = 'https://github.com/justinludwig/powerline-svnstatus',
    packages     = ['powerline_svnstatus'],
    classifiers  = [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Terminals'
    ]
)
