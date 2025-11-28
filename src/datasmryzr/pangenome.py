"""
This module provides functions for processing pangenome files and generating visualisations
for pangenome analysis.
"""

import altair as alt
import pandas as pd
from Bio import SeqIO
import pathlib
import gzip
import csv
from datasmryzr.utils import check_file_exists, _open_df, _get_pangenome_acc

alt.data_transformers.disable_max_rows()



def _get_dataframe(_path:str) -> pd.DataFrame:

    """
    Reads a CSV file containing pangenome groups.

    Args:
        _path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the pangenome groups.
    """
    if not check_file_exists(_path):
        raise FileNotFoundError(f"File not found: {_path}")
    
    df = _open_df(_path)
    return df

def calc(data):

    return round(sum(data)/len(data)*100, 1)

def classify(data) -> str:
    if data["count"] >= 95:
        return "Core"
    elif data["count"] <95 or data["count"]>= 15:
        return "Intermediate"
    else:
        return "Rare"
    

def _generate_datatable(_rtab:str, detail_tab:str = "") -> tuple[pd.DataFrame, list]:
    
    detailed = _get_dataframe(detail_tab) if detail_tab != "" else pd.DataFrame()
    raw = _get_dataframe(_rtab)
    ids = raw.columns[1:].tolist()
    raw["count"] = raw[ids].apply(calc, axis=1)
    raw["panaroo_class"] = raw.apply(classify, axis=1)
    raw = raw.rename(columns = {"Gene":"gene_name"})
    if not detailed.empty:
        raw = pd.merge(raw, detailed[["gene_name","specific_class","general_class"]], how="left", on="gene_name")

    return raw,ids


def _make_pangenome_table(raw : pd.DataFrame, 
                          colname:str
                          ) -> str:
    
    # print(raw)
    # print(colname)
    grpd = raw.groupby([f"{colname}"]).count()
    total = raw["gene_name"].count()
    grpd["Percentage"] = round(grpd["gene_name"] / total * 100, 1)
    grpd["Percentage"] = grpd["Percentage"].astype(str) + "%"
    grpd = grpd[["gene_name", "Percentage"]]
    grpd = grpd.reset_index()
    grpd = grpd.rename(columns={f"{colname}":"Gene class", "gene_name":"Gene count"})
    grpd.sort_values("Gene count", ascending=False)

    grpd.to_csv("pangenome.txt", sep="\t", index=False)

    return "pangenome.txt"

def _pangenome_summary(
                        pangenome_rtab: str,
                        groups:str,
                        pangenome_characterization: str = "",
                        colname: str = "panaroo_class") -> str:
    
    raw,ids = _generate_datatable(pangenome_rtab, pangenome_characterization)
    colname = colname if pangenome_characterization == "" else "specific_class"
    try:
        grps = pd.read_csv(groups, sep="\t", header=0, dtype=str, names = ["variable","group"])
        if len(list(grps["group"].unique())) == 1:
            colname = "panaroo_class"
    except:
        grps = pd.DataFrame()
        colname = "panaroo_class"
    summary_table = _make_pangenome_table(raw, colname)
    return summary_table

def _graph(raw: pd.DataFrame, colname: str, grps:pd.DataFrame, ids:list) -> alt.Chart:
    """
    Generates a bar chart for the pangenome data.

    Args:
        raw (pd.DataFrame): DataFrame containing pangenome data.
        colname (str): Column name to group by.

    Returns:
        alt.Chart: Altair chart object.
    """
    # print(grps["group"].unique())
    
    
    _dtype = "basic" if colname == "panaroo_class" else "detail"
    
    xval = "panaroo_class" if colname == "panaroo_class" else "general_class"
    acc = _get_pangenome_acc(_dtype)
    colors, orders = acc[0], acc[1]
    if colname in raw.columns:
        
        raw["order"] = raw[colname].map(orders)
        summary = alt.Chart(raw, title = "Summary pangenome in dataset").mark_bar().encode(
                            x=alt.X(f"{xval}").title("Class"),
                            y = alt.Y("count()").title("Gene count"),
                            color=alt.Color(f"{colname}").scale(range=colors["_range"], domain=colors["domain"]).title("Gene class"),
                            order=alt.Order(
                            # Sort the segments of the bars by this field
                            'order',
                            sort='ascending'
                            )
                            ).properties(
                                width=alt.Step(75)
                            )
    else:
        summary = alt.Chart(raw, title = "Summary pangenome in dataset").mark_bar().encode(
                            x=alt.X(f"{xval}").title("Class"),
                            y = alt.Y("count()").title("Gene count"),
                            # color=alt.Color(f"{colname}").scale(range=colors["_range"], domain=colors["domain"]).title("Gene class"),
                            # order=alt.Order(
                            # # Sort the segments of the bars by this field
                            # 'order',
                            # sort='ascending'
                            # )
                            ).properties(
                                width=alt.Step(75)
                            )
    charts = []
    
    raw = raw.reset_index()
    
    raw_mltd = raw.melt(id_vars= ["index","gene_name", f"{colname}",], value_vars= ids )
    # print(raw)
    # print(raw_mltd)
    # if not grps.empty:
    # print(grps)
    try:
        if len(list(grps["group"].unique())) > 1:
            # grps = grps.rename(columns={"variable":"gene_name"})
            raw_mltd = raw_mltd.merge(grps, on="variable", how="left")
            
        else:
            raw_mltd["group"] = "dataset"
    except:
        raw_mltd["group"] = "dataset"
    # print(raw_mltd)
    # raw_mltd = raw_mltd.rename(columns={"variable":"Group"})
    
    raw_mltd = raw_mltd.fillna("Ungrouped")
    for grp in sorted(raw_mltd["group"].unique()):


        chart = alt.Chart(raw_mltd[(raw_mltd["value"] == 1) & (raw_mltd["group"] == grp)], title = alt.Title(f"Genes present in cluster: {grp}" if grp != 500 else f"Not grouped",
                                                                                                            anchor="end")).mark_tick().encode(
            x=alt.X('index').title(None).axis(None),
            y=alt.Y('value:O').axis(None),
            # column= "variable",
            row = alt.Row("variable").title(None).header(
                labelAngle=0,labelPadding=0, labelAlign="left", labelFontSize=12,).spacing(0),
            color=alt.Color(f"{colname}").scale(range=colors["_range"], domain=colors["domain"]).title("Gene class"),
            tooltip=[f"{colname}"]
        )

        charts.append(chart)

    isolates = alt.vconcat(*charts, spacing=15)
    return alt.hconcat(summary,isolates, spacing = 15).configure_axis(
        labelFontSize=12,
        titleFontSize=14,
        grid=False,
        ).to_json()

def do_pangenome_graph(
    pangenome_rtab: str,
    pangenome_characterization: str = "",
    groups: str = "",
    # colname: str = "panaroo_class"
) :
    
    raw,ids = _generate_datatable(pangenome_rtab, pangenome_characterization)
    colname = "panaroo_class" if pangenome_characterization == "" else "specific_class"
    print(raw)
    try:
        grps = pd.read_csv(groups, sep="\t", header=0, dtype=str, names = ["variable","group"])
    except:
        grps = pd.DataFrame()
    
    charts = _graph(raw, colname, grps, ids)
    return charts


    
    