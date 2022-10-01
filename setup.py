from distutils.core import setup


setup(
    name='nice_tools',
    packages=['nice_tools'],
    version='0.0.5',
    license='MIT',
    description='A collection of tools for python',
    author='amiwrpremium',
    author_email='amiwrpremium@gmail.com',
    url='https://github.com/amiwrpremium/nice_tools',
    keywords=['tools', 'threading', 'thread', 'logging', "logger"],
    install_requires=[
        'python-telegram-bot',
        'requests',
        'aiohttp',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
