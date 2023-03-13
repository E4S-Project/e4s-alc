from setuptools import setup

setup(
    name='e4s-alc',
    description='Build docker containers quickly with Spack integration.',
    version='0.1.0',
    install_requires=[
        'docker',
        'podman'
    ],
    entry_points={
        'console_scripts': [
            'e4s-alc = e4s_alc.cli.entry:main',
        ]
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
