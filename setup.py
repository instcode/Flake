from setuptools import setup

version = '0.0.1'

setup(
    name="Flake",
    version=version,
    keywords=["flake", "snowflake", "unique", "generator"],
    long_description=open(os.path.join(os.path.dirname(__file__), "README"), "r").read(),
    description="High performance id generating server using Thrift & Tornado.",
    author="Khoa Nguyen",
    author_email="instcode@gmail.com",
    url="http://github.com/instcode/flake",
    license="Apache Software License",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=[
        'vng.gpi.flake',
        'flake',
        'thrift',
        'thrift.protocol',
        'thrift.server',
        'thrift.transport'
    ],
    requires=['tornado (>=2.1)'],
    download_url="http://github.com/downloads/instcode/flake/flake-%s.tar.gz" % version,
)
