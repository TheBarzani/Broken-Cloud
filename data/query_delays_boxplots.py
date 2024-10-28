import pandas as pd
import matplotlib.pyplot as plt

def plot_individual_box_plots():
    """Generates individual box plots for the measured end-to-end delays of each query in milliseconds."""
    
    # Read the delays from CSV files
    category_year_data = pd.read_csv("category_year_delays.csv")
    motivation_keyword_data = pd.read_csv("motivation_keyword_delays.csv")
    name_details_data = pd.read_csv("name_details_delays.csv")

    # Create a list of queries and their respective data
    queries = {
        'Category-Year Delay': category_year_data['Delay (milliseconds)'],
        'Motivation Keyword Delay': motivation_keyword_data['Delay (milliseconds)'],
        'Name Details Delay': name_details_data['Delay (milliseconds)'],
    }

    # Generate individual box plots
    for query_name, delays in queries.items():
        plt.figure(figsize=(8, 5))
        plt.boxplot(delays)
        
        # Set plot title and labels
        plt.title(f'Box Plot of {query_name} (in milliseconds)', fontsize=14)
        plt.ylabel('Delay (milliseconds)', fontsize=12)
        plt.xticks([1], [query_name])  # Set x-ticks to display the query name
        
        # Save the plot as a PNG file
        plt.grid()
        plt.tight_layout()
        plt.savefig(f"{query_name.lower().replace(' ', '_')}_boxplot.png")  # Save using a formatted filename
        plt.close()  # Close the figure to free memory

if __name__ == "__main__":
    plot_individual_box_plots()
