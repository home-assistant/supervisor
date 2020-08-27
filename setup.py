"""Home Assistant Supervisor setup."""
from setuptools import setup

from supervisor.const import SUPERVISOR_VERSION

setup(
    name="Supervisor",
    version=SUPERVISOR_VERSION,
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
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["docker", "home-assistant", "api"],
    zip_safe=False,
    platforms="any",
    packages=[
        "supervisor",
        "supervisor.docker",
        "supervisor.addons",
        "supervisor.api",
        "supervisor.dbus",
        "supervisor.dbus.payloads",
        "supervisor.dbus.network",
        "supervisor.discovery",
        "supervisor.discovery.services",
        "supervisor.services",
        "supervisor.services.modules",
        "supervisor.homeassistant",
        "supervisor.host",
        "supervisor.misc",
        "supervisor.utils",
        "supervisor.plugins",
        "supervisor.snapshots",
        "supervisor.store",
    ],
    include_package_data=True,
)
