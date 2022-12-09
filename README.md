An attempt at organising my plotting scripts better. Main idea is to use this together with [Spirit](https://github.com/spirit-code/spirit) and [spirit-extras](https://github.com/MSallermann/spirit_extras).

# Setup
1. Change the variable `data_path` in `__paths__.py` to point to the `data` root folder.
2. Change the variable `spirit_path` in `__paths__.py` to point to the `spirit` root folder.
3. Run `setup_env.sh` from the root folder of this repository

# Producing a figure
The main idea is to invoke the python script `fig_dispatcher.py` on and pass special folders containing the information about how to create the plots to it in form of a `descriptor.yaml` file.

As an example look at the folder
```bash
Example_Plot/
├── create_renderings.py
├── descriptor.yaml
└── make_figure.py
Data
└── subfolder
    └── some_data.txt
__paths__.py
```
where
```yaml
# descriptor.yaml
figure: 
  script: "make_figure.main"
  output_file: "example_figure.png"
  dpi : 300
  title : "my figure title"
depends:
  data_file:
    output_files:
      - "{__paths__.data_path}/subfolder/some_data.txt"
  rendering:
    output_files: 
      - "rendering/rendering.png"
    callback: "create_rendering.main"
    some_key: "blablabla"
meta:
  meta_key1: "some meta information"
log: "log.txt"
```

If we invoke

```bash
python fig_dispatcher.py Example_Plot
```
the example figure will be created in the following order
1. The dependency `data_file`, with the associated file `{__paths__.data_path}/subfolder/some_data.txt`, will be checked for existence. The syntax `{__paths__.data_path}` signifies that the path is one of the module level string variables in the `__paths__` module. In this example it would simply be the `Data` folder. If the output file is not existent, an exception will be thrown.

2. The dependency `rendering`, with the associated output file, `rendering/rendering.png` will be checked for exixtence. This time the path is to be understood _relative_ to `Example Plot`, meaning it will check for `rendering.png` in `Example_Plot/rendering`. If `rendering.png` does not exist, the script will try to create it, by calling the `main()` function in the `create_rendering.py` module. If this fails, an exception will be thrown.

3. Lastly, the figure will be created by calling the `main()` function of `make_figure.py` 


# Writing the python scripts
The modules to create the dependencies/figure are completely standard python modules. 

## Passing information from `descriptor.yaml` to python files
However, one thing should be mentionend: `fig_dispatcher.py` will define module level variables for any dictionary key associated with the dependecies. The dictionary key `key` will be translated to a module level variable `SOME_KEY_` (all uppercase and with an underscore added at the back). This makes it possible to pass arbitrary information from `descriptor.yaml` to the python scripts.

__Note:__ 

(1) The only values that receive any prost-processing are the `output_files`. The rest of the dictionary values are reproduces exactly as is. 

(2) The `meta` field can be used to define inormation that is available in both the dependency callback module and the figure creation script.

(3) In the figure creation module (here `Example_Plot/make_figure.py`), the paths to the dependencies are available as `__DEP_NAME__` where `dep_name` would correspond to keys in the `depends` dictionary.

In our example the such defined module-level variables are:

In `create_rendering.py`
```python
__SOME_KEY_ = "blablabla"
__OUTPUT_FILES_ = ["/path/to/rendering/rendering.png"] # Absolute path to output file
__CALLBACK_ = "create_rendering.main"
__META_KEY1_ = "some meta information"
```

In `make_figure.py`
```python
SCRIPT_ = "make_figure.main"
OUTPUT_FILE_ = "/path/to/example_figure.png"
DPI_ = 300
TITLE_ = "my figure title"
META_KEY1_ = "some meta information"
RENDERING_ = ["/path/to/rendering/rendering.png"]
```

Look for example at the following script from the `Example Plot`, where this functionality is used to infer the location of the `output files` (via `plotter.render_to_png(__OUTPUT_FILES__[0]`) and to print the message `"blablabla"` via `print(__SOME_KEY__)`.

```python
# create_rendering.py
from spirit_extras import calculation_folder
from spirit_extras import data
from spirit_extras.pyvista_plotting import Spin_Plotter
import numpy as np
import os
 

def main():
    spin_system = data.Spin_System(
        np.array([[i, 0, 0] for i in range(10)]),
        np.array([[1, -1, 1] for i in range(10)]),
    )
    plotter = Spin_Plotter(spin_system)
    plotter.background_color = "black"
    plotter.arrows()

    if not os.path.exists(os.path.dirname(__OUTPUT_FILES__[0])):
        os.makedirs(os.path.dirname(__OUTPUT_FILES__[0]))

    print(__SOME_KEY__)
    plotter.render_to_png(__OUTPUT_FILES__[0])
```

# Log file
If the `log` field is specifed in the top level of `descriptor.yaml` a log file is created, which can be useful for debugging.

In the example it could look like:

```txt
================================================================================
                           2022-12-08 18:32:09.263142                           
================================================================================
------------------------------------------------------------
                   Gathering dependencies                   
------------------------------------------------------------
Adding dependency: `data_file`
{'output_files': ['{__paths__.data_path}/subfolder/some_data.txt']}
Replacing dependency output files...
Before: ['{__paths__.data_path}/subfolder/some_data.txt']
After: ['/home/moritz/Coding/plot_repo_template/Data/subfolder/some_data.txt']
callback function = None
---
Adding dependency: `rendering`
{'callback': 'create_rendering.main',
 'output_files': ['rendering/rendering.png'],
 'some_key': 'blablabla'}
Replacing dependency output files...
Before: ['rendering/rendering.png']
After: ['/home/moritz/Coding/plot_repo_template/Example_Plot/rendering/rendering.png']
callback function = create_rendering.main
Loading module = /home/moritz/Coding/plot_repo_template/Example_Plot/create_rendering.py
setting __OUTPUT_FILES__ = ['/home/moritz/Coding/plot_repo_template/Example_Plot/rendering/rendering.png']
setting __CALLBACK__ = create_rendering.main
setting __SOME_KEY__ = blablabla
setting __META_KEY1__ = some meta information
---
Checking dependencies ...
------------------------------------------------------------
                      Creating figure                       
------------------------------------------------------------
Loading module = /home/moritz/Coding/plot_repo_template/Example_Plot/make_figure.py
Figure outpur file /home/moritz/Coding/plot_repo_template/Example_Plot/example_figure.pngsetting __SCRIPT__ = make_figure.main
setting __OUTPUT_FILE__ = /home/moritz/Coding/plot_repo_template/Example_Plot/example_figure.png
setting __DPI__ = 300
setting __TITLE__ = my figure title
setting __META_KEY1__ = some meta information
setting __DATA_FILE__ = ['/home/moritz/Coding/plot_repo_template/Data/subfolder/some_data.txt']
setting __RENDERING__ = ['/home/moritz/Coding/plot_repo_template/Example_Plot/rendering/rendering.png']
--------------------------------------------------------------------------------
                             SUCCESSFULLY FINISHED                              
================================================================================
```