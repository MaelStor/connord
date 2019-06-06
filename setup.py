"""setup.py"""
from setuptools import setup, find_packages
from connord import __version__


def readme():
    """Parse README.md

    : returns: README.md as string
    """
    with open("README.md") as file_handle:
        return file_handle.read()


setup(
    name="connord",
    version=__version__,
    description="Command-Line tool to connect to nordvpn.",
    long_description=readme(),
    long_description_content_type="text/markdown; charset=UTF-8; variant=GFM",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: System :: Systems Administration",
    ],
    install_requires=[
        "requests>=2.22.0,<3.0.0",
        "cachetools>=3.1.1,<4.0.0",
        "Jinja2>=2.10.1,<3.0.0",
        "netaddr>=0.7.19,<1.0.0",
        "PyYAML>=5.1,<6.0",
        "python-iptables>=0.14.0,<1.0.0",
    ],
    tests_require=["pytest", "pytest-cov", "vermin", "mock"],
    python_requires=">=3.5",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["connord = connord.__main__:main"]},
    url="http://gitlab.noiams.space/maelstor/connord",
    author="Mael Stor",
    author_email="maelstor@posteo.de",
    license="GPL-3.0-or-later",
    zip_safe=False,
)
