import uuid

from setuptools import setup, find_packages
try: # for pip >= 10
        from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
        from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="pyfg",
    version="0.50",
    packages=find_packages(),
    author="XNET",
    author_email="lindblom+pyfg@spotify.com",
    description="Python API for fortigate",
    url="https://github.com/spotify/pyfg",
    include_package_data=True,
    install_requires=reqs
)
