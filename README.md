# U.S. Labor Market Shifts by Occupation Group
### A K-Means Clustering and Correlation Analysis of BLS OEWS 2023–2024

---

## 📂 Project Deep Dive

### Project Overview
**Dataset:** U.S. Bureau of Labor Statistics – Occupational Employment and Wage Statistics (OEWS), May 2023 and May 2024

The OEWS program produces the most detailed annual wage and employment estimates available for U.S. occupations, covering more than 800 detailed roles. This project analyzes **809 matched national-level occupations** to identify which of the 22 major occupation groups grew fastest in wages and employment, segment occupations into distinct labor market profiles, and test how wage growth relates to hiring and to an occupation's starting wage level.

### Research Questions
1. Which major occupation groups showed the strongest overall labor market growth from 2023 to 2024?
2. Is occupation-level wage growth correlated with employment growth?
3. Did low-, mid-, and high-wage occupations experience different patterns of wage and employment change?

---

## 🛠️ Tech Stack & Core Competencies

**Languages & Frameworks:** Python (pandas, NumPy, scikit-learn, SciPy, matplotlib, seaborn, openpyxl)

**Analytics & Modeling:** K-Means Clustering, Elbow Method, Z-Score Standardization, Pearson Correlation, OLS Trend Fitting, Tercile Segmentation, Group-Level Aggregation

**Domain Focus:** Labor Market & Workforce Analytics, Wage Dynamics, Public Economic Data

---

## Methods

| Step | Method | Purpose |
|------|--------|---------|
| 1 | Group aggregation and ranking | Compare average wage and employment growth across 22 major groups |
| 2 | Z-score performance heatmap | Put wage level, wage growth, employment growth and inequality on one comparable scale |
| 3 | K-means clustering (k = 3) | Segment occupations by multivariate labor market profile; k chosen with the elbow method |
| 4 | Pearson correlation + OLS line | Test whether wage growth and employment growth move together |
| 5 | Tercile wage tiers | Compare low-, mid- and high-wage occupations |

**Feature engineering and data reduction**
- Filtered each year to national (`AREA_TYPE = 1`), cross-industry, all-ownership (`OWN_CODE = 1235`) and detailed-occupation records.
- Merged both years on SOC code (831 matches), then dropped 22 occupations with missing key values → **809 occupations**.
- Converted BLS suppression symbols (`*`, `**`, `#`) to missing values.
- Derived year-over-year % change in annual mean wage and total employment.
- Computed the 90th/10th percentile wage ratio as an inequality measure.
- Assigned major groups from the first two digits of the SOC code, and wage tiers from terciles of the 2023 mean wage.
- Standardized all clustering features with `StandardScaler` so wage dollars do not dominate the distance calculations.

---

## Key Achievements & Objectives

- **Engineered a Modeling-Ready Dataset:** Reduced ~827K raw rows across two annual files to a clean, matched panel of 809 occupations with consistent filters and derived growth metrics.
- **Ranked Major Group Performance:** Built side-by-side wage and employment rankings and a four-metric z-score heatmap to identify the strongest and weakest occupation groups.
- **Segmented the Labor Market:** Applied k-means clustering to four standardized features to reveal distinct occupational segments.
- **Tested the Wage–Hiring Relationship:** Used Pearson correlation and an OLS trend line to show that wage growth and employment growth are statistically unrelated.
- **Quantified Wage Compression:** Showed that lower-paid occupations had faster wage growth but slower hiring than higher-paid ones.
- **Built a Reproducible Pipeline:** One script handles cleaning, analysis, all six figures and the CSV summary tables.

---

## 📈 Key Results

**Overall shift:** 89.5% of occupations raised wages, but only 57.5% added jobs. The mean wage change was +3.77% (median +3.96%), and the median occupation wage rose from $62,020 to $64,315.

**Major group leaders and laggards**

| Metric | Top Groups | Bottom Groups |
|--------|-----------|---------------|
| Wage growth | Community & Social Service (+6.86%), Protective Service (+6.67%), Installation, Maintenance & Repair (+5.73%) | Educational Instruction (−0.42%, the only negative group) |
| Employment growth | Food Preparation & Serving (+6.22%), Protective Service (+5.76%), Community & Social Service (+4.84%) | Production (−3.51%), Office & Administrative Support (−3.39%) |

**Z-score highlights**

| Group | Standout z-score | Interpretation |
|-------|------------------|----------------|
| Community & Social Service | Wage growth +1.96, employment growth +1.15 | Strong on both dimensions |
| Protective Service | Wage growth +1.85, employment growth +1.50 | Best combined performer |
| Healthcare Practitioners | Wage level +2.69 | Highest-paid group, near-average growth |
| Educational Instruction | Wage growth −2.61 | Clearest negative outlier |
| Production | Employment growth −1.98 | Steepest job contraction |

**Wage growth vs. employment growth**

| Statistic | Value |
|-----------|-------|
| Pearson r | 0.024 |
| p-value | 0.500 |
| OLS slope | 0.060 |

There is no meaningful relationship: the occupations raising pay fastest were not the ones hiring the most.

**Wage tiers (terciles of 2023 mean wage)**

| Tier | Avg Wage Growth | Avg Employment Growth |
|------|-----------------|-----------------------|
| Low-Wage | 4.67% | 0.44% |
| Mid-Wage | 4.02% | 0.73% |
| High-Wage | 2.62% | 1.76% |

The pattern is inverse: the lower the starting wage, the faster wages grew and the slower employment grew.

---

## 📊 Visual Highlights

| # | Visual | Chart Type | Purpose |
|---|--------|-----------|---------|
| 1 | Wage Growth by Major Group | Horizontal bar chart | Ranks the 22 groups by average wage change |
| 2 | Employment Growth by Major Group | Horizontal bar chart | Ranks the 22 groups by average employment change |
| 3 | Major Group Z-Score Heatmap | Heatmap | Compares four metrics on one standardized scale |
| 4 | K-Means Segments | Elbow curve + scatter plot | Shows how k was chosen and how occupations cluster |
| 5 | Wage vs Employment Growth | Scatter plot with OLS line | Tests the wage–hiring relationship |
| 6 | Wage Tier Comparison | Grouped bar chart | Contrasts low-, mid- and high-wage occupations |

### Wage Growth by Major Group
Community & Social Service (+6.86%) and Protective Service (+6.67%) lead. Educational Instruction is the only group with a decline (−0.42%).

![Wage growth by major group](figures/fig1_wage_growth_by_major_group.png)

### Employment Growth by Major Group
Food Preparation & Serving leads at +6.22%, while Production (−3.51%) and Office & Administrative Support (−3.39%) lost the most jobs.

![Employment growth by major group](figures/fig2_employment_growth_by_major_group.png)

### Major Group Z-Score Heatmap
Protective Service and Community & Social Service are green on both growth dimensions. Healthcare Practitioners leads on wage level, and Educational Instruction is the deepest red on wage growth.

![Z-score heatmap](figures/fig3_major_group_zscore_heatmap.png)

### K-Means Segments
The elbow curve supports a three-cluster solution. The segments separate mainly by wage level and differ in how wage growth and employment change combine. Full cluster profiles are in `outputs/cluster_profiles.csv`.

![K-means segments](figures/fig4_kmeans_segments.png)

### Wage Growth vs Employment Growth
The OLS line is nearly flat (slope = 0.060; r = 0.024, p = 0.500). Low-wage and high-wage occupations are scattered evenly across the plot.

![Wage vs employment growth](figures/fig5_wage_vs_employment_growth.png)

### Wage Tier Comparison
Low-wage occupations had the fastest wage growth (4.67%) and the weakest hiring (0.44%). High-wage occupations show the reverse (2.62% wage growth, 1.76% employment growth).

![Wage tier comparison](figures/fig6_wage_tier_comparison.png)

---

## 💡 Selected Observations & Insights

- **Pay Rose Faster Than Hiring:** Nearly 9 in 10 occupations raised wages, but fewer than 6 in 10 added workers. This is consistent with a tight post-pandemic labor market in which employers competed on pay to retain staff.
- **Public-Facing Service Roles Led:** Community & Social Service and Protective Service were the only groups to rank in the top three for both wage and employment growth.
- **Automation Signals in Production and Office Work:** The two groups with the steepest job losses are also those most exposed to automation and process digitization.
- **Educational Instruction Is a Paradox:** It was the only group whose average wage fell, yet it still added workers (+3.32%).
- **Wage Growth and Hiring Are Decoupled:** With r = 0.024, knowing how fast an occupation's pay rose tells you almost nothing about whether it hired.
- **The Bottom Is Catching Up:** Low-wage occupations grew wages about 2 percentage points faster than high-wage ones. Inequality within occupations stayed stable overall: the median 90/10 ratio barely moved (2.28 → 2.29).
- **Extreme Movers Are Niche Roles:** The largest individual swings, such as Fashion Designers (+26.2%) and Athletes & Sports Competitors (−21.0%), come from occupations with small employment pools, where survey sampling changes can drive large percentage moves.

> **Note:** These results describe associations in the data. They do not show that membership in any occupation group or wage tier causes wage or employment changes.

---

## ✅ Recommendations

- **Workforce policy:** Expand training, apprenticeship and recruitment pipelines for Community & Social Service, Protective Service and Installation & Repair roles, where wage pressure signals persistent shortages.
- **Employers in high-wage sectors:** Plan for continued competition for talent, since high-wage occupations are adding jobs fastest even though their percentage raises are smaller.
- **Compensation and HR teams:** Build a tier adjustment into market benchmarking. Entry-level and frontline wages are rising about 2 points faster than high-wage roles.
- **Workforce transition:** Prioritize reskilling programs for Production and Office & Administrative workers facing job contraction.
- **Future analysis:**
  - Extend to state and metro-area data and to more OEWS years.
  - Weight group averages by employment.
  - Add O\*NET automation-exposure scores to test the displacement hypothesis directly.

---

## ⚙️ Repository Architecture & Usage

### Repository Structure
```
bls-oews-labor-market-analysis/
├── README.md
├── requirements.txt
├── LICENSE
├── src/
│   └── oews_analysis.py          # Full pipeline: load → clean → analyze → plot → export
├── data/
│   └── README.md                 # How to download the BLS files (raw data not tracked)
├── figures/                      # Six generated figures shown in this README
│   ├── fig1_wage_growth_by_major_group.png
│   ├── fig2_employment_growth_by_major_group.png
│   ├── fig3_major_group_zscore_heatmap.png
│   ├── fig4_kmeans_segments.png
│   ├── fig5_wage_vs_employment_growth.png
│   └── fig6_wage_tier_comparison.png
└── outputs/                      # Generated summary tables (CSV)
    ├── major_group_summary.csv
    ├── cluster_profiles.csv
    └── wage_tier_summary.csv
```

### How to Reproduce
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/bls-oews-labor-market-analysis.git
   cd bls-oews-labor-market-analysis
   ```
2. Download the May 2023 and May 2024 OEWS "All data" files into `data/` (see `data/README.md`).
3. Install the dependencies and run the pipeline:
   ```bash
   pip install -r requirements.txt
   python src/oews_analysis.py --file-2023 data/all_data_M_2023.xlsx --file-2024 data/all_data_M_2024.xlsx
   ```
   If you have a single combined file with a `YEAR` column, run `python src/oews_analysis.py --data data/data_2023-2024.xlsx` instead.

**Python packages:** pandas, numpy, openpyxl, matplotlib, seaborn, scipy, scikit-learn

---

## 📋 Data Source & Technical Limitations

### Dataset Profile
This project uses the national **Occupational Employment and Wage Statistics** files published by the U.S. Bureau of Labor Statistics for May 2023 and May 2024. Each raw file contains roughly 413,000 rows and 32 columns.

| Field | Description |
|-------|-------------|
| `OCC_CODE` | Standard Occupational Classification (SOC) code; first two digits identify the major group |
| `OCC_TITLE` | Occupation title |
| `AREA_TYPE` | Geographic level (1 = national) |
| `I_GROUP` | Industry aggregation level (filtered to cross-industry) |
| `OWN_CODE` | Ownership type (1235 = all ownerships combined) |
| `O_GROUP` | Occupation hierarchy level (filtered to detailed) |
| `TOT_EMP` | Estimated total employment |
| `A_MEAN` | Annual mean wage |
| `A_MEDIAN` | Annual median wage |
| `A_PCT10` / `A_PCT90` | 10th and 90th percentile annual wages (used for the 90/10 inequality ratio) |

**Source:** [Occupational Employment and Wage Statistics — U.S. Bureau of Labor Statistics](https://www.bls.gov/oes/tables.htm)

**Dataset License:** Public domain (U.S. federal government data)

### Limitations
- Only two survey years are covered, so the results describe a one-year change, not a long-term trend.
- OEWS estimates are based on surveys. Small occupations can show large percentage swings because of sampling changes.
- Group and tier averages are unweighted, so a small occupation counts as much as a very large one.
- The analysis is national only and may hide regional differences.
- Top-coded wages (`#`) are treated as missing, which slightly understates growth at the very top of the distribution.

---

## 🛡️ Data Integrity Notice

This public repository contains analysis of publicly available U.S. federal labor statistics. It contains no proprietary corporate materials, protected institutional data or restricted commercial information.

---

## Author
**Takudzwa Melody Mazhambe** | [LinkedIn](#)
