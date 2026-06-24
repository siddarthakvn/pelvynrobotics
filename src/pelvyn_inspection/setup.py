from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'pelvyn_inspection'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sai Siddartha',
    maintainer_email='sai.siddartha@example.com',
    description='Pelvyn AUV inspection mission nodes',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'stable_mission = pelvyn_inspection.stable_mission:main',
            'sensor_monitor = pelvyn_inspection.sensor_monitor:main',
            'topic_explorer = pelvyn_inspection.topic_explorer:main',
        ],
    },
)
