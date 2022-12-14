from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in menghua_erp/__init__.py
from menghua_erp import __version__ as version

setup(
	name="menghua_erp",
	version=version,
	description="MH ERPNext",
	author="Kitti U.",
	author_email="kittiu@ecosoft.co.th",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
