from setuptools import setup
import os
from glob import glob

package_name = 'my_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/' + package_name, ['package.xml']),
        

    ],
    install_requires=['setuptools','evdev'],
    zip_safe=True,
    maintainer='anan',
    maintainer_email='your@email.com',
    description='Google Sheets updater node',
    license='MIT',
    extras_require={
        'test' : ['pytest']
    },
    entry_points={
        'console_scripts': [
            'sheet = my_py_pkg.my_sheet_updater:main',
            'barcode = my_py_pkg.barcode_reader_node:main',
            'lcd = my_py_pkg.lcd_display_node:main'

        ],
    },
    package_data={
    },
    include_package_data=True,
)

