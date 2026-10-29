"""
BLS OEWS 2023-2024: Occupational Labor Market Analysis
Author: Takudzwa M. Mazhambe

Research questions
  Q1. Which major occupation groups showed the strongest overall labor
      market growth (wages and employment) from May 2023 to May 2024?
  Q2. Is occupation-level wage growth correlated with employment growth?
  Q3. Did low-, mid-, and high-wage occupations experience different
      patterns of wage and employment change?

Outputs
  figures/  six PNG figures
  outputs/  CSV summary tables

Usage
  python src/oews_analysis.py                              # combined file with a YEAR column
  python src/oews_analysis.py --file-2023 a.xlsx --file-2024 b.xlsx
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "data_2023-2024.xlsx"
FIG_DIR = ROOT / "figures"
OUT_DIR = ROOT / "outputs"

NUM_COLS = ["TOT_EMP", "A_MEAN", "A_MEDIAN", "A_PCT10", "A_PCT90"]

# First two digits of the SOC code identify the major occupation group
SOC_MAJOR_GROUPS = {
    "11": "Management",
    "13": "Business & Financial Operations",
    "15": "Computer & Mathematical",
    "17": "Architecture & Engineering",
    "19": "Life, Physical & Social Science",
    "21": "Community & Social Service",
    "23": "Legal",
    "25": "Educational Instruction & Library",
    "27": "Arts, Design, Entertainment & Media",
    "29": "Healthcare Practitioners & Technical",
    "31": "Healthcare Support",
    "33": "Protective Service",
    "35": "Food Preparation & Serving",
    "37": "Building & Grounds Maintenance",
    "39": "Personal Care & Service",
    "41": "Sales & Related",
    "43": "Office & Administrative Support",
    "45": "Farming, Fishing & Forestry",
    "47": "Construction & Extraction",
    "49": "Installation, Maintenance & Repair",
    "51": "Production",
    "53": "Transportation & Material Moving",
}

POS, NEG = "#2E7D32", "#C62828"
TIER_COLORS = {"Low-Wage": "#C55A11", "Mid-Wage": "#1F7391", "High-Wage": "#1B2A4A"}

plt.rcParams.update({"figure.dpi": 150, "font.size": 10, "axes.titleweight": "bold"})


# ----------------------------------------------------------------------
# 1. Load and clean
# ----------------------------------------------------------------------
def read_any(path):
    path = Path(path)
    df = pd.read_csv(path, dtype=str) if path.suffix == ".csv" else pd.read_excel(path, dtype=str)
    df.columns = df.columns.str.upper().str.strip()
    return df


def clean_filter(df):
    """National, cross-industry, all-ownership, detailed occupations only.
    BLS suppression symbols (*, **, #) are coerced to NaN."""
    mask = (
        (pd.to_numeric(df["AREA_TYPE"], errors="coerce") == 1)
        & (df["I_GROUP"].str.lower().str.strip() == "cross-industry")
        & (pd.to_numeric(df["OWN_CODE"], errors="coerce") == 1235)
        & (df["O_GROUP"].str.lower().str.strip() == "detailed")
    )
    out = df.loc[mask, ["OCC_CODE", "OCC_TITLE"] + NUM_COLS].copy()
    for c in NUM_COLS:
        out[c] = pd.to_numeric(out[c].str.replace(",", "", regex=False), errors="coerce")
    return out


def load_years(args):
    if args.file_2023 and args.file_2024:
        raw23, raw24 = read_any(args.file_2023), read_any(args.file_2024)
    else:
        raw = read_any(args.data)
        year = pd.to_numeric(raw["YEAR"], errors="coerce")
        raw23, raw24 = raw[year == 2023], raw[year == 2024]
    print(f"Raw rows -> 2023: {len(raw23):,} | 2024: {len(raw24):,}")
    return clean_filter(raw23), clean_filter(raw24)


def build_dataset(d23, d24):
    df = d23.merge(d24, on="OCC_CODE", suffixes=("_23", "_24"))
    print(f"Occupations matched across years: {len(df)}")
    key = ["A_MEAN_23", "A_MEAN_24", "A_MEDIAN_23", "A_MEDIAN_24", "TOT_EMP_23", "TOT_EMP_24"]
    df = df.dropna(subset=key).copy()
    print(f"Final analytical dataset: {len(df)} occupations")

    df["OCC_TITLE"] = df["OCC_TITLE_24"]
    df["WAGE_CHG_PCT"] = (df["A_MEAN_24"] - df["A_MEAN_23"]) / df["A_MEAN_23"] * 100
    df["EMP_CHG_PCT"] = (df["TOT_EMP_24"] - df["TOT_EMP_23"]) / df["TOT_EMP_23"] * 100
    df["RATIO_9010_23"] = df["A_PCT90_23"] / df["A_PCT10_23"]
    df["RATIO_9010_24"] = df["A_PCT90_24"] / df["A_PCT10_24"]
    df["MAJOR_GROUP"] = df["OCC_CODE"].str[:2].map(SOC_MAJOR_GROUPS)
    df["WAGE_TIER"] = pd.qcut(df["A_MEAN_23"], q=3, labels=list(TIER_COLORS))
    return df


# ----------------------------------------------------------------------
# 2. Q1 - Major group performance (Figures 1-4)
# ----------------------------------------------------------------------
def group_summary(df):
    g = (df.groupby("MAJOR_GROUP")
           .agg(n_occupations=("OCC_CODE", "count"),
                avg_wage_2023=("A_MEAN_23", "mean"),
                avg_wage_growth_pct=("WAGE_CHG_PCT", "mean"),
                avg_emp_growth_pct=("EMP_CHG_PCT", "mean"),
                avg_ratio_9010=("RATIO_9010_23", "mean"))
           .round(3))
    g.sort_values("avg_wage_growth_pct", ascending=False).to_csv(OUT_DIR / "major_group_summary.csv")
    return g


def barh_by_group(series, title, xlabel, fname):
    s = series.sort_values()
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(s.index, s.values, color=[POS if v > 0 else NEG for v in s.values])
    for i, v in enumerate(s.values):
        ax.text(v + (0.08 if v >= 0 else -0.08), i, f"{v:.2f}%",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.margins(x=0.12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / fname)
    plt.close(fig)


def fig_heatmap(g):
    cols = {"avg_wage_2023": "Wage level", "avg_wage_growth_pct": "Wage growth",
            "avg_emp_growth_pct": "Employment growth", "avg_ratio_9010": "90/10 inequality"}
    hm = g[list(cols)].rename(columns=cols).sort_values("Wage growth", ascending=False)
    z = (hm - hm.mean()) / hm.std()
    fig, ax = plt.subplots(figsize=(9, 9))
    sns.heatmap(z, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
                linewidths=0.5, cbar_kws={"label": "z-score"}, ax=ax)
    ax.set_title("Major Group Performance (z-scores across groups)")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_major_group_zscore_heatmap.png")
    plt.close(fig)


def fig_kmeans(df, k=3):
    feats = ["A_MEAN_23", "WAGE_CHG_PCT", "EMP_CHG_PCT", "RATIO_9010_23"]
    X = df[feats].replace([np.inf, -np.inf], np.nan).dropna()
    Xs = StandardScaler().fit_transform(X)

    ks = range(2, 11)
    wcss = [KMeans(n_clusters=i, random_state=42, n_init=10).fit(Xs).inertia_ for i in ks]
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(Xs)

    # Renumber clusters from lowest to highest average wage so labels are stable
    order = pd.Series(X["A_MEAN_23"].values).groupby(labels).mean().sort_values().index
    remap = {old: new for new, old in enumerate(order, start=1)}
    df["CLUSTER"] = pd.Series([remap[l] for l in labels], index=X.index).astype("Int64")

    prof = (df.dropna(subset=["CLUSTER"]).groupby("CLUSTER")
              .agg(n=("OCC_CODE", "count"), avg_wage_2023=("A_MEAN_23", "mean"),
                   avg_wage_growth_pct=("WAGE_CHG_PCT", "mean"),
                   avg_emp_growth_pct=("EMP_CHG_PCT", "mean"),
                   share_emp_decline=("EMP_CHG_PCT", lambda s: (s < 0).mean()),
                   avg_ratio_9010=("RATIO_9010_23", "mean"))
              .round(3))
    prof.to_csv(OUT_DIR / "cluster_profiles.csv")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.5))
    a1.plot(list(ks), wcss, "o-", color="#1F7391")
    a1.axvline(k, ls="--", color="grey")
    a1.set_title("Elbow Method (WCSS by k)")
    a1.set_xlabel("Number of clusters (k)")
    a1.set_ylabel("Within-cluster sum of squares")

    palette = ["#C55A11", "#1F7391", "#1B2A4A", "#6A1B9A", "#2E7D32"]
    for c in sorted(df["CLUSTER"].dropna().unique()):
        sub = df[df["CLUSTER"] == c]
        a2.scatter(sub["A_MEAN_23"] / 1000, sub["WAGE_CHG_PCT"], s=18, alpha=0.6,
                   color=palette[int(c) - 1], label=f"Cluster {int(c)} (n={len(sub)})")
    a2.axhline(0, color="grey", ls="--", lw=0.8)
    a2.set_ylim(-25, 30)
    a2.set_title(f"K-Means Segments (k={k}): Wage Level vs Wage Growth")
    a2.set_xlabel("2023 Annual Mean Wage ($K)")
    a2.set_ylabel("Wage Change 2023-2024 (%)")
    a2.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_kmeans_segments.png")
    plt.close(fig)
    return prof


# ----------------------------------------------------------------------
# 3. Q2 - Wage growth vs employment growth (Figure 5)
# ----------------------------------------------------------------------
def fig_wage_vs_emp(df):
    p = df[df["EMP_CHG_PCT"].between(-50, 50) & df["WAGE_CHG_PCT"].between(-25, 30)]
    r, pval = stats.pearsonr(p["WAGE_CHG_PCT"], p["EMP_CHG_PCT"])
    slope, intercept = np.polyfit(p["WAGE_CHG_PCT"], p["EMP_CHG_PCT"], 1)

    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(p["WAGE_CHG_PCT"], p["EMP_CHG_PCT"], c=p["A_MEAN_23"] / 1000,
                    cmap="viridis", s=26, alpha=0.65, edgecolors="grey", linewidth=0.3)
    xs = np.linspace(p["WAGE_CHG_PCT"].min(), p["WAGE_CHG_PCT"].max(), 100)
    ax.plot(xs, slope * xs + intercept, color="red", lw=1.8, label=f"OLS fit (slope = {slope:.3f})")
    ax.axhline(0, color="grey", ls="--", alpha=0.5)
    ax.axvline(0, color="grey", ls="--", alpha=0.5)
    plt.colorbar(sc, ax=ax, label="2023 Mean Wage ($K)")
    ax.text(0.03, 0.96, f"Pearson r = {r:.3f}\np = {pval:.3f}\nn = {len(p)}",
            transform=ax.transAxes, va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.6))
    ax.set_title("Wage Growth vs Employment Growth by Occupation (2023-2024)")
    ax.set_xlabel("Wage Change (%)")
    ax.set_ylabel("Employment Change (%)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig5_wage_vs_employment_growth.png")
    plt.close(fig)
    return r, pval, slope, len(p)


# ----------------------------------------------------------------------
# 4. Q3 - Wage tiers (Figure 6)
# ----------------------------------------------------------------------
def fig_wage_tiers(df):
    t = (df.groupby("WAGE_TIER", observed=True)
           .agg(n=("OCC_CODE", "count"),
                avg_wage_2023=("A_MEAN_23", "mean"),
                avg_wage_growth_pct=("WAGE_CHG_PCT", "mean"),
                avg_emp_growth_pct=("EMP_CHG_PCT", "mean"))
           .round(3))
    t.to_csv(OUT_DIR / "wage_tier_summary.csv")

    x = np.arange(len(t))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5.5))
    b1 = ax.bar(x - w / 2, t["avg_wage_growth_pct"], w, label="Avg wage growth", color="#1F7391")
    b2 = ax.bar(x + w / 2, t["avg_emp_growth_pct"], w, label="Avg employment growth", color="#C55A11")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05,
                    f"{b.get_height():.2f}%", ha="center", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i}\n(n={n})" for i, n in zip(t.index, t["n"])])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("Percent change, 2023-2024")
    ax.set_title("Wage vs Employment Growth by 2023 Wage Tier (terciles)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig6_wage_tier_comparison.png")
    plt.close(fig)
    return t


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=DEFAULT_DATA, help="Combined 2023+2024 file with a YEAR column")
    ap.add_argument("--file-2023", help="Separate May 2023 OEWS file")
    ap.add_argument("--file-2024", help="Separate May 2024 OEWS file")
    args = ap.parse_args()

    FIG_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)

    d23, d24 = load_years(args)
    df = build_dataset(d23, d24)

    # Q1
    g = group_summary(df)
    barh_by_group(g["avg_wage_growth_pct"], "Average Wage Growth by Major Occupation Group (2023-2024)",
                  "Average wage change (%)", "fig1_wage_growth_by_major_group.png")
    barh_by_group(g["avg_emp_growth_pct"], "Average Employment Growth by Major Occupation Group (2023-2024)",
                  "Average employment change (%)", "fig2_employment_growth_by_major_group.png")
    fig_heatmap(g)
    prof = fig_kmeans(df)

    # Q2
    r, pval, slope, n = fig_wage_vs_emp(df)

    # Q3
    tiers = fig_wage_tiers(df)

    df.to_csv(OUT_DIR / "occupations_clean.csv", index=False)

    print("\n=== Q1: Major groups (sorted by wage growth) ===")
    print(g.sort_values("avg_wage_growth_pct", ascending=False).to_string())
    print("\n=== Q1: K-means cluster profiles ===")
    print(prof.to_string())
    print(f"\n=== Q2: Wage vs employment growth ===\nr = {r:.3f}, p = {pval:.3f}, slope = {slope:.3f}, n = {n}")
    print("\n=== Q3: Wage tiers ===")
    print(tiers.to_string())
    print(f"\nFigures saved to {FIG_DIR}\nTables saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
