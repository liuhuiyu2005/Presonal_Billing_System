from setuptools import setup

setup(
    name="PersonalBillingSystem",
    version="1.0.0",
    description="个人记账系统",
    author="Your Name",
    packages=[""],
    include_package_data=True,
    install_requires=[
        "flask==3.0.0",
        "waitress==3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "personal-billing=main:main",
        ],
    },
)