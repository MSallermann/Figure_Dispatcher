SPIRIT_PATH=$( python3 __paths__.py spirit_path)
python3 -m venv ./python_environment
source ./python_environment/bin/activate
pip install spirit-extras --upgrade
pip install wheel
pip install black
pip install scipy
pip install tqdm # pyvista ..
pip install -e $SPIRIT_PATH/core/python