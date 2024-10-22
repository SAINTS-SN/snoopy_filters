import os
import snpy
from shutil import copytree, ignore_patterns

# filters in your local installation of SNooPy
snpy_path = snpy.__path__[0]
filters_path = os.path.join(snpy.__path__[0], 
                            'filters/filters')

# this repository
new_filters = '.'

copytree(new_filters, filters_path, 
         ignore=ignore_patterns('*.git*'), 
         dirs_exist_ok=True)
