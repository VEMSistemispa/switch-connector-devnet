import sys
from setuptools import setup, find_packages

NAME = "switch_connector"
VERSION = "1.0.0"

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="Switch device service",
    author_email="info@mydev.it",
    url="",
    keywords=["Swagger", "Switch device service"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    Connector API to switch devices
    """
)
