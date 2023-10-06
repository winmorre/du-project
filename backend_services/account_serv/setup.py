import setuptools

setuptools.setup(
    name="pipa-account-service",
    version="0.0.1",
    package_dir={"": "lib"},
    packages=setuptools.find_packages(where="lib"),
    include_package_data=True,
    entry_points={"console_scripts": ["app = manage.py runserver"]}
)
