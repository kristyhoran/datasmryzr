"""
This module provides functions for processing pairwise distances between isolates,
including generating histograms and heatmaps for visualization.
"""

import pandas as pd
import pathlib
import json
import altair as alt
from datasmryzr.utils import check_file_exists
from datasmryzr.distances import _get_distances


def _get_cluster_table(
        clusters: str
    ) -> pd.DataFrame:
    try:
    # if check_file_exists(clusters):
        cluster_df = pd.read_csv(clusters, sep=None, engine='python', dtype=str)
        return cluster_df
    except Exception as e:
        print(e)
        return pd.DataFrame()

def _get_distance_data(
        cluster_df: pd.DataFrame,
        distances_df: pd.DataFrame
    ) -> pd.DataFrame:

    pass

def _combine_cluster_ids(
                         clusters:pd.DataFrame) -> pd.DataFrame:
    
    thresholds = _get_thresholds(clusters)
    while thresholds:
        threshold = thresholds.pop(0)
        if thresholds != []:
            print(thresholds)
            clusters[f"Tx:{thresholds[0]}"] = clusters[[f"Tx:{threshold}", f"Tx:{thresholds[0]}"]].apply(lambda x: ':'.join(x) if not "UC" in f"{x[0]}" else x[0], axis = 1)

    return clusters

def _get_thresholds(clusters: pd.DataFrame) -> list:
    
    thresholds = sorted([int(t.split(':')[1]) for t in list(clusters.columns) if "Tx" in t], reverse=True)
    
    return thresholds

def _create_tree_for_traversal(
                               clusters: pd.DataFrame) -> dict:
    thresholds = _get_thresholds(clusters)
    tree = {'all': [c for c in clusters[f"Tx:{thresholds[0]}"].unique() if c != "UC"]}
    while thresholds:
        threshold = thresholds.pop(0)
        clusters = clusters[~clusters[f"Tx:{threshold}"].str.contains("UC")]
        for cl in clusters[f"Tx:{threshold}"].unique():
            if cl not in tree:
                tree[cl] = []
                if thresholds != []:
                    tree[cl] = list(clusters[clusters[f"Tx:{threshold}"] == cl][f"Tx:{thresholds[0]}"].unique())
                else:
                    tree[cl] = []
    return tree

def _construct_table_dict(tree, node, clusters, visited=None):
    # print(type(df))
    # print(type(df))
    # print(type(df))
    cols = list(clusters.columns)
    size = 0
    print(node)
    for col in cols:
        print(col)
        if node in clusters[col].unique():
            tmp = clusters[clusters[col] == node]
            size = tmp.shape[0]
            isolates = list(tmp['ID'].unique())
    # print(type(df))
    if visited is None:
        visited = set()  # Initialize the visited set
    visited.add(node)    # Mark the node as visited
    # print(node)
   
    data = {'Cluster ID': node, 'Num seqs':size, '_children': []}  # Store the children of the current node
    if "UC" not in node:
        for child in tree[node]:  # Recursively visit children
            if child not in visited:
                if "UC" not in child:
                    data['_children'].append(_construct_table_dict(tree = tree, node = child, clusters = clusters, visited=visited))
                # dfs_recursive(tree, child, clusters, visited)
    # print(data)
    return data

def get_cluster_distances(
        clusters: str,
        distances: str
    ) -> pd.DataFrame:
    cluster_df = _get_cluster_table(clusters)
    cluster_df = _combine_cluster_ids(cluster_df)
    thresholds = _get_thresholds(cluster_df)
    dists = {}
    if check_file_exists(distances) and not cluster_df.empty:
        distances_df = pd.read_csv(distances, sep = "\t")
        tree = _create_tree_for_traversal(cluster_df)
        id_col = distances_df.columns[0]
        
        for cl in tree:
            for th in thresholds:
                if cl in cluster_df[f"Tx:{th}"].values:
                    
                    isolates = list(cluster_df[cluster_df[f"Tx:{th}"] == cl]['ID'])
                    ccols = ["Isolate"]
                    ccols.extend(isolates)
                    dd = distances_df[distances_df["Isolate"].isin(isolates)][ccols]
                    tbl = dd.to_dict(orient='records')
                    col_dict = []
                    for col in ccols:
                        if col == id_col:
                            dct = {'field': col, 'title': col, 'type': 'string', 'headerFilter':'input',
                            'headerFilterPlaceholder':f'Search {col}',
                            'formatter':"textarea"}
                            col_dict.append(dct)
                        else:
                            dct = {'field': col, 'title': col, 'type': 'number', 'headerFilter':'number', 'headerFilterFunc':"<=",
                            'headerFilterPlaceholder':f'Less than ...',
                            'formatter':"number",}
                            col_dict.append(dct)
                    dists[cl] = {
                        'table': tbl,
                        'columns': col_dict
                    }
    return dists

def _save_cluster_table(cluster_table: dict) -> str:
    out_path = pathlib.Path.cwd() / "clusters.json"
    with open(out_path, 'w') as f:
        json.dump(cluster_table, f, indent=4)
    return str(out_path)

def get_cluster_table(
        clusters: str,
        distances: str
    ) -> str:
    
    distances_df = _get_distances(distances)
    cluster_df = _get_cluster_table(clusters)
    # print(cluster_df)
    thresholds = _get_thresholds(cluster_df)
    
    if cluster_df.empty or distances_df.empty:
        return {}
    else:
        cluster_df = _combine_cluster_ids(cluster_df)
        tree = _create_tree_for_traversal(cluster_df)
        cluster_table = _construct_table_dict(tree = tree, node = 'all', clusters= cluster_df)
        # print(raw_data)
        # cluster_table = _polish_cluster_table(raw_data, 'all')
        
        return _save_cluster_table(cluster_table['_children'])
    
def _get_clustered(clusters: str, threshold:int) -> pd.DataFrame:
    clustered = clusters[~clusters[f"Tx:{threshold}"].str.contains("UC")][clusters.columns[0]].tolist()
    return clustered

def _cluster_statistics(
        cluster_df: str,
        distances_df: str,
        thresholds: list,
        id_col: str = None
    ) -> pd.DataFrame:

    
    
    intra_clusters = []
    for th in thresholds:
        
        clustered = _get_clustered(cluster_df, th)
        
        cdf = distances_df[distances_df["Isolate1"].isin(clustered) & distances_df["Isolate2"].isin(clustered)]
        # print(cdf)
        for cl in cluster_df[f"Tx:{th}"].unique():
            
            if "UC" not in cl:
                
                cldf = cluster_df[cluster_df[f"Tx:{th}"] == cl]
                
                if not cdf.empty:
                    
                    tmp = cdf[cdf["Isolate1"].isin(cldf[id_col] )]
                    tmp = tmp[tmp["Isolate2"].isin(cldf[id_col])]
                    # print(tmp[["Isolate1", "Isolate2"]])
                    tmp["pair"] = tmp[["Isolate1", "Isolate2"]].apply(lambda x: "_".join(sorted(x)), axis=1)
                    tmp["Cluster ID"] = f"{cl}"
                    tmp["SNP Threshold"] = th
                    tmp["Measurement"] = "Intra-cluster distance"
                    intra_clusters.append(tmp)
                inter = cluster_df[(cluster_df[f"Tx:{th}"] != cl) & (~cluster_df[f"Tx:{th}"].str.contains("UC"))]
                # print(inter)
                for cluster in inter[f"Tx:{th}"].unique():
                    intery = inter[inter[f"Tx:{th}"] == cluster]
                    for i in cldf[id_col].unique(): # get each isolate in the cluster
                        interx = pd.concat([intery, cldf[cldf[id_col] == i]])
                        # print(interx)
                        tmp2 = cdf[cdf["Isolate1"]== i]
                        tmp2 = tmp2[~tmp2["Isolate2"].isin(interx[id_col])]
                        tmp2["pair"] = tmp2[["Isolate1", "Isolate2"]].apply(lambda x: "_".join(sorted(x)), axis=1)
                        tmp2["Cluster ID"] = f"{cl}"
                        tmp2["SNP Threshold"] = th
                        tmp2["Measurement"] = "Inter-cluster distance"
                        # print(tmp2)
                        intra_clusters.append(tmp2)


    cdf_all = pd.concat(intra_clusters, ignore_index=True)
    cdf_all.drop_duplicates(subset=["pair", "Cluster ID"], inplace=True)
    return cdf_all

def _generate_cluster_graphs(
        cdf_all: pd.DataFrame,
        clusters: pd.DataFrame,
        id_col: str,
        thresholds: int
    ) -> dict:
    
    charts = []
    for th in thresholds:
        clustered_list = _get_clustered(clusters, th)
        tmp = clusters[clusters[id_col].isin(clustered_list)]
        tmp = tmp.rename(columns={f"Tx:{th}": f"Tx_{th}"})
        uc = clusters[~clusters[id_col].isin(clustered_list)]
        uc = uc.rename(columns={f"Tx:{th}": f"Tx_{th}"})
        uc[f"Tx_{th}"] = "UC"
        num_cls = tmp.shape[0]
        clustered_graph = alt.Chart(tmp).mark_bar().encode(
            x=alt.X(f'Tx_{th}:N', title = None),
            y=alt.Y('count():Q', title = None).scale(domain=[0, clusters.shape[0]]),
            # column = "Clustered:N",
            color=alt.Color('Tx_{th}:N', scale=alt.Scale(scheme='viridis')).legend(None),
            tooltip=[f'Tx_{th}:N', 'count():Q']
        ).properties(
            width=200,
            title = "Number sequences per cluster"
            # height=300
        )
        unclustered_graph  = alt.Chart(uc).mark_bar(color="grey").encode(
            x=alt.X(f'Tx_{th}:N', title = None),
            y=alt.Y('count():Q', title = "Number of Isolates").scale(domain=[0, clusters.shape[0]]),
            # column = "Clustered:N",
            # color=alt.Color('threshold_9:N'),
            tooltip=[f'Tx_{th}:N', 'count():Q']
        ).properties(
            width=300/(num_cls + 1),
            # height=300
        )
        alt.hconcat(unclustered_graph,clustered_graph).configure_axis(
                            grid=False
            ).configure_view(
            stroke=None
        )
        graphs = [unclustered_graph,clustered_graph]
        for m in ["Intra-cluster distance", "Inter-cluster distance"]:
            box = alt.Chart(cdf_all[(cdf_all["Measurement"] == m) & (cdf_all["SNP Threshold"] == th)]).mark_boxplot(extent='min-max', opacity=.3).encode(
                    y=alt.Y(f"Distance:Q", sort=None, title = f"Pairwise Distance (threshold: {th})"),
                    x=alt.X('Cluster ID:N'),
                    
                    # tooltip=['pair', 'Distance:Q'],
                    color=alt.Color('Cluster ID').scale(scheme='viridis').legend(None)
                    
                )
            scatter = alt.Chart(cdf_all[(cdf_all["Measurement"] == m) & (cdf_all["SNP Threshold"] == th)]).mark_circle(size=80).encode(
                    y=alt.Y(f"Distance:Q", sort=None),
                    x=alt.X('Cluster ID:N'),
                    color=alt.Color('Cluster ID').scale(scheme='viridis').legend(None),
                    
                    # Add jitter if desired (e.g., using a calculated jitter column or a transform)
                    # yOffset='jitter_x:Q',
                    tooltip=['pair', f'Distance'],
                )
            chart = box + scatter
            chart = chart.properties(title=f"{m}", width = 500)
            graphs.append(chart)
        graph = alt.hconcat(*graphs).resolve_scale(
            y='independent').properties(
            title = alt.Title(f"SNP threshold {th}", anchor='start', fontSize=20, dy=-10, baseline='middle')
        )
        charts.append(graph)
    
    final_chart = alt.vconcat(*charts).configure_axis(
                        grid=False
                                    ).configure_view(
                                    stroke=None
                                )
    return final_chart.to_json()

def get_cluster_graphs(
        clusters: str,
        distances: str
    ) -> dict:

    distances_df = _get_distances(distances)
    cluster_df = _get_cluster_table(clusters)
    thresholds = _get_thresholds(cluster_df)
    cluster_df = _combine_cluster_ids(cluster_df)
    id_col = cluster_df.columns[0]
    try:
        cdf_all = _cluster_statistics(cluster_df = cluster_df, distances_df = distances_df, thresholds= thresholds, id_col = id_col)
        graph = _generate_cluster_graphs(cdf_all = cdf_all, clusters= cluster_df, id_col = id_col, thresholds= thresholds)
        return graph
    except Exception as e:
        print(e)
        return {}

# <button class="btn btn-sm btn-outline-secondary" style= "margin:2px;" id="information-button" data-bs-toggle="modal" data-bs-target="#myModal"><i class="bi bi-info-circle" style = "font-size: 1.2rem;"></i> Info</button>

