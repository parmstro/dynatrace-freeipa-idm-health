from setuptools import setup, find_packages

setup(
    name="freeipa_idm_health",
    version="1.0.39",
    description="Dynatrace EF2 extension for FreeIPA / Red Hat IdM health monitoring",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "dt-extensions-sdk",
        "ldap3",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "freeipa_idm_health=freeipa_idm_health.__main__:main",
        ],
    },
)
