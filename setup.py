import setuptools
from io import open

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

def readme():
    with open("README.md", encoding="utf-8") as f:
        README = f.read()
    return README

setuptools.setup(
    name='thai-personal-card-extract',
    include_package_data=True,
    version='1.0.0',
    install_requires=requirements,
    license='Apache License 2.0',
    description='Library for extract infomation from thai personal identity card',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author='ggafiled.io (Nattapol Krobklang)',
    author_email='gafewkik234@gmail.com',
    url='https://github.com/ggafiled/ThaiPersonalCardExtrac',
    project_urls={
        "Bug Tracker": "https://github.com/ggafiled/ThaiPersonalCardExtrac/issues",
    },
    download_url='https://github.com/ggafiled/ThaiPersonalCardExtrac.git',
    keywords=['ocr optical character recognition deep learning neural network'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Text Processing'
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)