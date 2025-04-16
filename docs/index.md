# Welcome to datasmryzr documentation

![Python package](https://github.com/kristyhoran/datasmryzr/actions/workflows/python-package.yml/badge.svg)


Datasmryzr is a small command-line tool that is designed to collate and render pathogen genomics analysis results, such as trees, tables and matrices as a `.html` for sharing and interactive interrogation. 

## Installation

`datasmryzr` is a python package with simply dependencies. It is recommended to use a virtual or conda environment for installation.

```
<activate enviornment>
pip3 install git+https://github.com/kristyhoran/datasmryzr
```

## Usage

`datasmryzr` allows users to generate standalone `.html` files for visualisation, searching and sharing of genomic analysis results. It has been designed for pathogen genomics needs, but could also be used for other types of tabular and newick based data.

### Inputs

Any combination of tables, newick or vcf can be supplied for generation of the html report. However, there are some things to be aware of in order to get the desired result.

* Tabular data (comma or tab-delimited files) can be used as input. 
    * All columns in input tables will be rendered - in the order that they are supplied.
    * File names will be used as menu labels in the `.html` file - so use sensible ones :wink:

* Pairwise matrix data (comma or tab-delimited files) can be supplied to generate distributions and heatmaps of distances.

* Newick file - a single newick file can be supplied per report.

* An annotation file can also be supplied if you want to be able to add colored annotations to the tree. This file can be one that has been already specified as tabular data or it can be an additional file.
    * The first column in the annotation file MUST contain names that match exactly to the tiplabels in the newick file.
    * If you only want a subset of values from the annotation file, you can supply these as a comma separated list in the command.
    * Only categorical variables can be visualised on the tree at the moment. If you want to display numerical values as categorical, you can provide this information in a configuration file (see below for details).

* If you would like to visualise the distribution of variants across the reference genome, you will need to also supply the vcf, with all samples in it (for example the core.vcf output from snippy), a reference genome and a mask file if one has been used.

### tree annotation

A common use case for collation and display of genomic data is annotation of a tree. 