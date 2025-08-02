try:
    from ydata_profiling import ProfileReport
except ImportError:
    ProfileReport = None

import os

def generate_eda_report(
    df,
    output_path='output/eda_report.html',
    title="Clean+EDA Auto Report",
    target=None
):
    if ProfileReport is None:
        raise ImportError("ydata_profiling is not installed. Please install it using: pip install ydata-profiling")

    # Ensure the output directory exists
    output_folder = os.path.dirname(output_path)
    os.makedirs(output_folder, exist_ok=True)

    # Build the ProfileReport with rich settings
    profile = ProfileReport(
        df,
        title=title,
        explorative=True,
        minimal=True,
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

    # Optional: set target variable for profiling if specified
    if target and target in df.columns:
        print(f"Setting target variable for profiling: {target}")
        profile.set_variable(target)

    # Save the generated HTML report
    profile.to_file(output_path)
