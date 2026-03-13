import streamlit as st
import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# --- STEP 1: LOAD DATA ---
@st.cache_resource
def load_adata():
    # Path for your Mac
    path = "/PseudobulkCounts.h5ad"
    return sc.read_h5ad(path)

adata_combined = load_adata()

# --- STEP 2: SIDEBAR GUI ---
st.sidebar.header("Filter & Plot Settings")

# 1. Gene Selection (Keep as selectbox because there are thousands of genes)
all_genes = adata_combined.var_names.tolist()
gene_of_interest = st.sidebar.selectbox("Select Gene", all_genes, index=all_genes.index("CXCL12") if "CXCL12" in all_genes else 0)

# 2. Subset CellType with Checkboxes
st.sidebar.subheader("Subset CellType")
selected_cells = []
unique_cells = sorted(adata_combined.obs['CellType'].unique().tolist())
for cell in unique_cells:
    if st.sidebar.checkbox(cell, value=True, key=f"cell_{cell}"):
        selected_cells.append(cell)

# 3. Subset DiseaseState with Checkboxes
st.sidebar.subheader("Subset DiseaseState")
selected_state = []
unique_states = sorted(adata_combined.obs['DiseaseState'].unique().tolist())
for state in unique_states:
    if st.sidebar.checkbox(state, value=True, key=f"state_{state}"):
        selected_state.append(state)

# 4. Group By (X-Axis) with Checkboxes
st.sidebar.subheader("Group By (X-Axis)")
plot_conditions = []
possible_groups = ['CellType', 'DiseaseState', 'Sex']
for group in possible_groups:
    # Set default: Check CellType and DiseaseState
    is_default = group in ['CellType', 'DiseaseState']
    if st.sidebar.checkbox(f"Group by {group}", value=is_default, key=f"group_{group}"):
        plot_conditions.append(group)
# --- STEP 3: THE FUNCTION ---
def run_web_plot(gene, states, cells, groups):
    p_value = np.nan 
    tukey_results = None
    
    # 1. Subset Data
    temp_adata = adata_combined[
        (adata_combined.obs['DiseaseState'].isin(states)) & 
        (adata_combined.obs['CellType'].isin(cells))
    ].copy()
    
    if temp_adata.n_obs == 0:
        st.error("No data found for this selection.")
        return

    # 2. Normalize & Process
    # Basic Pseudobulk Normalization (Counts Per Million equivalent)
    counts_matrix = temp_adata.X.T
    normalized_counts = (counts_matrix / counts_matrix.sum(axis=0)) * 1e6
    
    # Extract gene and metadata
    gene_idx = temp_adata.var_names.get_loc(gene)
    gene_counts = normalized_counts[gene_idx]
    
    # If gene_counts is a matrix (scipy sparse), convert to dense array
    if hasattr(gene_counts, "toarray"):
        gene_counts = gene_counts.toarray().flatten()
    else:
        gene_counts = np.array(gene_counts).flatten()

    gene_counts_df = pd.DataFrame({
        "counts": gene_counts,
        "log_counts": np.log10(gene_counts + 1)
    })
    
    for condition in groups:
        gene_counts_df[condition] = temp_adata.obs[condition].values
    
    # Create the combined Group label for the X-axis
    if groups:
        gene_counts_df['Group'] = gene_counts_df[groups].astype(str).agg(' | '.join, axis=1)
    else:
        # Fallback if no groups are selected
        gene_counts_df['Group'] = 'All'

    # 3. Stats Calculation
    grouped_data = [group['log_counts'].dropna().values for _, group in gene_counts_df.groupby('Group')]
    if len(grouped_data) > 1:
        try:
            anova_stat, p_value = stats.f_oneway(*grouped_data)
            if not np.isnan(p_value) and p_value < 0.05:
                tukey_results = pairwise_tukeyhsd(gene_counts_df['log_counts'], gene_counts_df['Group'])
        except Exception as e:
            st.error(f"Statistical error: {e}")

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sort the dataframe by Group to keep X-axis organized
    gene_counts_df = gene_counts_df.sort_values('Group')
    
    sns.boxplot(data=gene_counts_df, x="Group", y="log_counts", ax=ax, color='white', showfliers=False)
    sns.stripplot(data=gene_counts_df, x="Group", y="log_counts", color='black', alpha=0.4, jitter=True, ax=ax)
    
    plt.xticks(rotation=90)
    plt.ylabel("Log10(Normalized Counts + 1)")
    plt.title(f"Expression of {gene}")

#    # Annotate Significance
#    if tukey_results is not None:
#        tukey_df = pd.DataFrame(data=tukey_results.summary().data[1:], columns=tukey_results.summary().data[0])
#        sig_pairs = []
#        sig_pvals = []
#        for _, row in tukey_df.iterrows():
#            if row['p-adj'] < 0.05:
#                sig_pairs.append((row['group1'], row['group2']))
#                sig_pvals.append(row['p-adj'])
#        
#        if sig_pairs:
#            try:
#                annotator = Annotator(ax, sig_pairs, data=gene_counts_df, x="Group", y="log_counts")
#                annotator.set_pvalues(sig_pvals)
#                annotator.configure(test=None, text_format='star', loc='outside')
#                annotator.annotate()
#            except Exception as e:
#                # Silently skip annotation if plot is too crowded
#                pass

    if not np.isnan(p_value):
        st.metric("ANOVA p-value", f"{p_value:.4e}")

    st.pyplot(fig)

    # Show Table
    if tukey_results is not None:
        st.subheader("Significant Pairwise Comparisons (Tukey HSD)")
        
        # 1. We MUST define the dataframe here so it's available for the next line
        tukey_df = pd.DataFrame(data=tukey_results.summary().data[1:], 
                                columns=tukey_results.summary().data[0])
        
        # 2. Now we can filter and display it
        st.dataframe(tukey_df[tukey_df['p-adj'] < 0.05])

#    if tukey_results is not None:
#        st.subheader("Significant Pairwise Comparisons")
#        st.dataframe(tukey_df[tukey_df['p-adj'] < 0.05])

# --- STEP 4: RUN ---
if st.button("Generate Visualization"):
    run_web_plot(gene_of_interest, selected_state, selected_cells, plot_conditions)