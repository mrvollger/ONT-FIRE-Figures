import pandas as pd
import numpy as np
import sys
import os
import math
import polars as pl
import glob


coverage_within_n_sd = 5  # snakemake.params.coverage_within_n_sd
MIN_coverage = 4  # snakemake.params.min_coverage


def get_min_coverage(median):
    sd = math.sqrt(median)
    mmin = median - coverage_within_n_sd * sd
    return max(mmin, MIN_coverage)


def get_max_coverage(median):
    sd = math.sqrt(median)
    return median + coverage_within_n_sd * sd


def weighted_median(df, val, weight):
    # group by value and sum the weights
    gdf = df.groupby(val)[weight].sum().reset_index().sort_values(val)
    gdf["cumsum"] = gdf[weight].cumsum()
    gdf["cutoff"] = gdf[weight].sum() / 2.0
    comparison = gdf[gdf["cumsum"] >= gdf["cutoff"]][val]
    return comparison.iloc[0]


def polars_read(f):
    # Reading the CSV file using the lazy API
    df = (
        pl.read_csv(
            f,
            separator="\t",
            has_header=False,
            new_columns=["chr", "start", "end", "coverage"],
            low_memory=True,
        )
        .lazy()
        .filter(pl.col("coverage") > 0)
        # .filter(pl.col("chr").is_in(snakemake.params.chroms))
        .drop("chr")
        .with_columns((pl.col("end") - pl.col("start")).alias("weight"))
        .drop(["start", "end"])
        .collect()
        .to_pandas()
    )
    return df


for f in sys.argv[1:]:
    print(f, file=sys.stderr)
    df = polars_read(f)
    coverage = weighted_median(df, "coverage", "weight")

    min_coverage = get_min_coverage(coverage)
    max_coverage = get_max_coverage(coverage)
    mean = (df["coverage"] * df["weight"]).sum() / df["weight"].sum()
    print(f"{f} mean coverage: {mean}")
    print(f"{f} median coverage: {coverage}")

    if coverage <= 1:
        raise ValueError(
            f"Median coverage is {coverage}! Did you use the correct reference, or is data missing from most of your genome. If so consider the keep_chromosomes parameter in config.yaml"
        )
