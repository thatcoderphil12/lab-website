import streamlit as st
import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# --- STEP 1: LOAD DATA ---
@st.cache_resource
def load_adata():
    path = "/2025_Dec_pseudobulk_all_cells_log1p_cpm_qn.h5ad"
    return sc.read_h5ad(path)

adata_combined = load_adata()

# --- HELPER FUNCTION FOR SIDEBAR ---
def get_safe_options(df, col_name):
    """Returns unique values for a column, skipping NaNs and missing columns."""
    if col_name in df.columns:
        # dropna() prevents sorted() from crashing on empty cells
        return sorted(df[col_name].dropna().unique().tolist())
    return []

# --- STEP 2: SIDEBAR GUI ---
st.sidebar.header("Filter & Plot Settings")

# 1. Gene Selection
all_genes = adata_combined.var_names.tolist()
gene_of_interest = st.sidebar.selectbox("Select Gene", all_genes, index=all_genes.index("IL4R") if "IL4R" in all_genes else 0)

# 2. Min Cells Filter
min_cells = st.sidebar.slider("Minimum Cells per Pseudobulk", 0, 500, 50)

# 3. Dynamic Filters
st.sidebar.subheader("Filters")

# Safely get options for Cell Type and Location
cell_options = get_safe_options(adata_combined.obs, 'cell_type_general')
selected_cells = st.sidebar.multiselect("Cell Type", cell_options, default=None)

loc_options = get_safe_options(adata_combined.obs, 'Location')
selected_location = st.sidebar.multiselect("Location", loc_options, default=None)

# 4. X-Axis Grouping
st.sidebar.subheader("Plotting Options")
# Only show columns that actually exist in your file
possible_groups = ['DiseaseStatus', 'cell_type_general', 'Location']
actual_groups = [g for g in possible_groups if g in adata_combined.obs.columns]

group_by = st.sidebar.selectbox("Group By (X-Axis)", actual_groups if actual_groups else adata_combined.obs.columns)
log_transform = st.sidebar.toggle("Log Transform (log1p)", value=False)

# --- STEP 3: THE PLOTTING FUNCTION ---
def run_enhanced_plot(gene, min_c, cells, locs, group_col, do_log):
    temp_adata = adata_combined.copy()
    
    # Apply Filters (only if user selected something)
    if cells:
        temp_adata = temp_adata[temp_adata.obs['cell_type_general'].isin(cells)]
    if locs:
        temp_adata = temp_adata[temp_adata.obs['Location'].isin(locs)]
    
    # Filter by min_cells
    if "psbulk_cells" in temp_adata.obs.columns:
        temp_adata = temp_adata[temp_adata.obs["psbulk_cells"] >= min_c]
    
    if temp_adata.n_obs == 0:
        st.error("No data found for this selection. Try lowering 'Min Cells' or removing filters.")
        return

    # Extract Expression
    expr = temp_adata[:, gene].X
    if hasattr(expr, "toarray"):
        expr = expr.toarray().flatten()
    else:
        expr = np.array(expr).flatten()

    df_plot = pd.DataFrame({
        "Expression": expr,
        group_col: temp_adata.obs[group_col].values
    }).dropna() # Remove any rows with missing group labels

    if do_log:
        df_plot["Expression"] = np.log1p(df_plot["Expression"])

    # Plotting
    fig, ax = plt.subplots(figsize=(6, 5))
    mpl.rcParams['pdf.fonttype'] = 42
    
    sns.boxplot(data=df_plot, x=group_col, y="Expression", color="white", fliersize=0, width=0.4, ax=ax)
    
    # Adaptive palette
    n_colors = len(df_plot[group_col].unique())
    palette = sns.color_palette("Set1", n_colors) 
    
    sns.stripplot(data=df_plot, x=group_col, y="Expression", hue=group_col, jitter=0.2, alpha=0.7, size=6, palette=palette, ax=ax)
    
    ax.set_title(f"{gene} expression")
    plt.xticks(rotation=45)
    if ax.get_legend(): ax.get_legend().remove()
    
    # Stats
    groups = [gdf["Expression"].values for _, gdf in df_plot.groupby(group_col)]
    if len(groups) > 1:
        f_stat, p_val = stats.f_oneway(*groups)
        st.metric("ANOVA p-value", f"{p_val:.4e}")
        
        if p_val < 0.05:
            st.subheader("Tukey HSD Results")
            tukey = pairwise_tukeyhsd(df_plot['Expression'], df_plot[group_col])
            st.dataframe(pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0]))

    st.pyplot(fig)

# --- STEP 4: RUN ---
if st.button("Generate Visualization"):
    run_enhanced_plot(gene_of_interest, min_cells, selected_cells, selected_location, group_by, log_transform)