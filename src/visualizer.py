import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns
import pandas as pd

def generate_graph(log_path, target_plot_path):
    # Read and parse the log file
    with open(log_path, "r") as f:
        lines = f.readlines()[1:]  # Skip the processing time line

    data = {"Timestamp": [], "Object": [], "Count": []}

    # Parse lines to extract object counts, object names, and exact times
    for line in lines:
        parts = line.split()
        
        # Ensure the line has enough parts before accessing them
        if len(parts) < 4:
            #print(f"Skipping malformed line: {line.strip()}")
            continue
        
        count = int(parts[1])
        object_class = parts[2].strip('(s)')
        timestamp = parts[-1]
        
        # Append to data dictionary
        data["Timestamp"].append(timestamp)
        data["Object"].append(object_class)
        data["Count"].append(count)

    # Convert the data to a DataFrame for Seaborn
    df = pd.DataFrame(data)

    # Set Seaborn style
    sns.set_theme(style="whitegrid")

    # Create the plot
    plt.figure(figsize=(14, 6))
    sns.scatterplot(data=df, x="Timestamp", y="Count", hue="Object", style="Object", s=100, palette="viridis")
    # Set the y-axis to display integer ticks only
    plt.yticks(range(int(df["Count"].min()), int(df["Count"].max()) + 1))

    # Customize the plot
    plt.xticks(rotation=45, ha='right')  # Rotate timestamp labels for readability
    plt.xlabel("Timestamps")
    plt.ylabel("Count of Objects")
    plt.title("Timeline of Object Appearances")
    plt.legend(title="Object Types")
    plt.tight_layout()  # Adjust layout to prevent clipping of tick labels
    #plt.show()

    plt.savefig(f"{target_plot_path}/plot.png", bbox_inches='tight')

    plt.close()
