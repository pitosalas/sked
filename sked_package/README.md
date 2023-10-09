# sked.py

# Developing

sked/ contains the python packate in sked_pitosalas as well as other files that were used to assist development
sked/sked_pitosalas contains the code that will turn into the package uploaded to pypi
sked/sked_pitosalas/pyproject.toml is where the package is configured

# Distributing


* Increment version number in pyproject.toml
```
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=mytoken 

python3 -m build
python3 -m twine upload --repository testpypi dist/* 
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U sked_pitosalas
pyenv rehash

# or
python3 -m build; python3 -m twine upload --skip-existing --repository testpypi dist/* ; python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U sked_pitosalas; pyenv rehash
