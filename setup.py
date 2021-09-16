# coding=utf-8

from setuptools import setup, find_packages

# with open("README.md", "r",encoding='utf8') as fh:
#     long_description = fh.read()

setup(
    name='sync2asyncio',  #
    version=0.1,
    description=(
        'convert sync to asyncio '
    ),
    # long_description=open('README.md', 'r',encoding='utf8').read(),
    keywords=("asyncio","async","sync"),
    long_description_content_type="text/markdown",
    long_description=open('README.md', 'r', encoding='utf8').read(),
    author='bfzs',
    author_email='ydf0509@sohu.com',
    maintainer='ydf',
    maintainer_email='ydf0509@sohu.com',
    license='BSD License',
    # packages=['douban'], #
    packages=find_packages(),
    # packages=['function_scheduling_distributed_framework'], # 这样内层级文件夹的没有打包进去。
    include_package_data=True,
    platforms=["all"],
    url='https://github.com/ydf0509/distributed_framework',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'threadpool_executor_shrink_able',

    ]
)
"""
官方 https://pypi.org/simple
清华 https://pypi.tuna.tsinghua.edu.cn/simple
豆瓣 https://pypi.douban.com/simple/ 
阿里云 https://mirrors.aliyun.com/pypi/simple/

打包上传
python setup.py sdist upload -r pypi

# python setup.py bdist_wheel
python setup.py bdist_wheel & twine upload dist/function_scheduling_distributed_framework-11.7-py3-none-any.whl
python setup.py sdist & twine upload dist/sync2asyncio-0.1.tar.gz



最快的下载方式，上传立即可安装。阿里云源同步官网pypi间隔要等很久。
./pip install sync2asyncio==3.5 -i https://pypi.org/simple   
最新版下载
./pip install sync2asyncio --upgrade -i https://pypi.org/simple       
"""

