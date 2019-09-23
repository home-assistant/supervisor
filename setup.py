from setuptools import setup

from hassio.const import HASSIO_VERSION

setup(
    name="HassIO",
    version=HASSIO_VERSION,
    license="BSD License",
    author="The Home Assistant Authors",
    author_email="hello@home-assistant.io",
    url="https://home-assistant.io/",
    description=("Open-source private cloud os for Home-Assistant" " based on HassOS"),
    long_description=(
        "A maintainless private cloud operator system that"
        "setup a Home-Assistant instance. Based on HassOS"
    ),
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
    ],
    keywords=["docker", "home-assistant", "api"],
    zip_safe=False,
    platforms="any",
    packages=[
        "hassio",
        "hassio.docker",
        "hassio.addons",
        "hassio.api",
        "hassio.misc",
        "hassio.utils",
        "hassio.snapshots",
    ],
    include_package_data=True,
)
