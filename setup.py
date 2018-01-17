from setuptools import setup

setup(
    name='smartband',
    keywords='Library for BLE fitness bands.',
    version='0.1',
    author='Alistair Buxton',
    author_email='a.j.buxton@gmail.com',
    url='http://github.com/ali1234/smartband',
    license='GPLv3+',
    platforms=['linux'],
    packages=['smartband'],
    entry_points={
        'console_scripts': [
            'smartband = smartband.__main__:main'
        ]
    },
    install_requires=[
        'bluepy'
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
)
