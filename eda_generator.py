from ydata_profiling import ProfileReport
import os

def generate_eda_report(
    df,
    output_path='output/eda_report.html',
    title="Clean+EDA Auto Report",
    target=None
):
    # Make sure the output folder exists
    output_folder = os.path.dirname(output_path)
    os.makedirs(output_folder, exist_ok=True)

    # Build the ProfileReport with beautiful settings
    profile = ProfileReport(
        df,
        title=title,
        explorative=True,         # Enables rich interactivity
        minimal=True,             # Simplified for easy reading
        correlations={
            "pearson": {"calculate": True},
            "spearman": {"calculate": True},
        },
        missing_diagrams={
            "heatmap": True,
            "dendrogram": True,
            "matrix": True,
            "bar": True
        },
        duplicates={"head": 10},
        interactions={"continuous": True},
        samples={"head": 10},
    )

    # Optionally set target for enhanced analysis
    if target and target in df.columns:
        print(f"Setting target variable for profiling: {target}")
        profile.set_variable(target)

    # Save the HTML report
    profile.to_file(output_path)

