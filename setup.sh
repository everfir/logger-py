#!/bin/bash

python setup.py install
python setup.py sdist bdist_wheel
rm dist/*egg
twine upload dist/* 
