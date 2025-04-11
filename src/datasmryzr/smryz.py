from datasmryzr.annotate import construct_annotations
from datasmryzr.utils import check_file_exists
from datasmryzr.tables import generate_table
from datasmryzr.core_genome import _plot_snpdensity
from datasmryzr.distances import _plot_snp_distances, _plot_snp_heatmap

from datasmryzr.tree import _get_tree_string
import pandas as pd
import pathlib
import json
import jinja2


# reporthtml = pathlib.Path(f'report_{args.pipeline}.html')
#     # # path to html template
#     indexhtml = pathlib.Path(args.template_dir,'index.html') 


data = {
    "title": "",
    "num_isos": 0,
    "background_color":"",
    "font_color":"",
    "date":"",
    "user":"",
    "phylo":"",
    "tables":{},
    "columns":{},
    "comment":{},
    "newick":"",
    "snp_distances":{},
    "snp_heatmap":{},
    "snp_density":{},
    "metadata_tree":{},
    "metadata_columns":[],
    "colors_css":{
        "some_color_name":{"color":"some hash"}
    },
    "legend":{
        "category":"",
        "values":{
            "color":"",
            "label":""
        }
    },
    "snp_distances":{},
    "heatmap":{},
    "snp_density":{},
}