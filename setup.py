from setuptools import setup, find_packages

setup(
    install_requires=[
        "bigip_parser @ https://artifactory.f5net.com/artifactory/api/pypi/f5-pypi-internal/bigip-parser/0.4.0/bigip_parser-0.4.0-py3-none-any.whl",
        "paramiko==2.6.0",
        "requests~=2.24.0",
        "bigsuds==1.0.6",
        "mock==2.0.0",
        "python-gnupg==0.4.6",
        "pytest==3.2.2",
        "fluent-logger==0.9.4",
        "ucs_modifier @ https://artifactory.f5net.com/artifactory/api/pypi/f5-pypi-internal/ucs-modifier/0.3.3/ucs_modifier-0.3.3-py3-none-any.whl",
    ],
    packages=find_packages(),
    include_package_data=True,
)