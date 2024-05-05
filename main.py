import pandas as pd
import tkinter as tk
from tkinter import filedialog
import numpy as np

def euclidean_distance(point1, point2):
    return np.sqrt(np.sum((point1 - point2) ** 2))
def initialize_centroids(data, k):
    centroids = data.sample(k, random_state=42)
    print(centroids , " initial centroids")
    return centroids
def detectOutliers(data):
    ratings = data['IMDB Rating'].sort_values()
    Q1 = np.percentile(ratings, 25)
    Q3 = np.percentile(ratings, 75)
    IQR = Q3 - Q1
    threshold_multiplier = 1.5
    lower_bound = Q1 - threshold_multiplier * IQR
    upper_bound = Q3 + threshold_multiplier * IQR

    without_outliers = data[(data['IMDB Rating'] >= lower_bound) & (data['IMDB Rating'] <= upper_bound)]

    return without_outliers

def read_data(file_path, percentage):
    columns_to_keep = ['Movie Name', 'IMDB Rating']
    df = pd.read_csv(file_path, usecols=columns_to_keep)
    num_records = int(len(df) * percentage / 100)
    return df.head(num_records)
def assign_to_clusters(data, centroids):
    clusters = {}
    for index, point_location in data.iterrows():
      #  print(point_location , " --point location")
        distances = [euclidean_distance(point_location, centroid) for centroid in centroids.values]
        cluster_idx = np.argmin(distances) # which cluster
        if cluster_idx not in clusters:
            clusters[cluster_idx] = []   # list for each cluster
        clusters[cluster_idx].append(index)
       # print(clusters[cluster_idx], "  clusters[cluster_idx]")

    return clusters

def update_centroids(data, clusters):
    centroids = []
    # print(clusters.items() , " clusters.items()")
    for cluster_idx, data_indices in clusters.items():
        cluster_data = data.loc[data_indices]
        #print(cluster_idx, " -- " , cluster_data)
        centroid = cluster_data.mean()
       # print(centroid , " mean centroid")
        centroids.append(centroid)
    return pd.DataFrame(centroids)


# def assign_to_clusters(data, centroids):
#     clusters = {}
#     # lower , upper = detectOutliers(data)
#     for i in range(len(data)):
#         point_location = data.iloc[i]
#         print(point_location , " --point location")
#         # point = point_location['IMDB Rating']
#         # print(point_location , " --  point_location")
#         # if point < lower or point > upper:
#         #     continue
#         distances = [euclidean_distance(point_location, centroid) for centroid in centroids.values]
#         cluster_idx = np.argmin(distances)
#         if cluster_idx not in clusters:
#             clusters[cluster_idx] = []
#         clusters[cluster_idx].append(i)   #append index of rating
#        # print(clusters[cluster_idx], "  clusters[cluster_idx]")
#
#     return clusters
#
# def update_centroids(data, clusters):
#     centroids = []
#     # lower , upper = detectOutliers(data)
#     # print(clusters.items() , " clusters.items()")
#     for cluster_idx, data_indices in clusters.items():
#         cluster_data = data.iloc[data_indices]
#         # point = cluster_data['IMDB Rating']
#         # print(point, " --  update")
#         # if point < lower or point > upper:
#         #     continue
#         #print(cluster_idx, " -- " , cluster_data)
#         centroid = cluster_data.mean()
#        # print(centroid , " mean centroid")
#         centroids.append(centroid)
#     return pd.DataFrame(centroids)

def printOutliers(data):
    ratings = data['IMDB Rating'].sort_values()
    Q1 = np.percentile(ratings, 25)
    Q3 = np.percentile(ratings, 75)
    IQR = Q3 - Q1
    threshold_multiplier = 1.5
    lower_bound = Q1 - threshold_multiplier * IQR
    upper_bound = Q3 + threshold_multiplier * IQR

    outliers = [rating for rating in ratings if rating < lower_bound or rating > upper_bound]
    return outliers

def k_means(data, k, max_iterations=1000):
    # Initialize centroids
    centroids = initialize_centroids(data, k)
   # print(centroids, " -- initialize_centroids")

    for _ in range(max_iterations):
        clusters = assign_to_clusters(data, centroids)
        new_centroids = update_centroids(data, clusters)

        if (centroids.equals(new_centroids)):
            # print(centroids , " -- if centroids")
            break
        # print(centroids, " -- centroids")
        centroids = new_centroids

    return centroids, clusters


def main():
    file_path = file_path_entry.get()
    percentage = float(Percentage_entry.get())
    k = int(k_entry.get())
    data = read_data(file_path, percentage)

    data_without_outliers = detectOutliers(data)

    final_centroids, clusters = k_means(data_without_outliers[['IMDB Rating']], k)
    # final centroid
    final_centroid_text.delete(1.0, tk.END)
    final_centroid_text.insert(tk.END, "Final Centroids:\n")
    final_centroid_text.insert(tk.END, final_centroids)


    clusters_text.delete(1.0, tk.END)
    clusters_text.insert(tk.END, "Clusters:\n")
    for cluster_idx, data_indices in clusters.items():
        valid_indices = [idx for idx in data_indices if idx in data_without_outliers.index]
        cluster_ratings = data_without_outliers.loc[valid_indices, 'IMDB Rating']
        cluster_movie_names = data_without_outliers.loc[valid_indices, 'Movie Name']
        clusters_text.insert(tk.END, f"Cluster {cluster_idx} (Total Rows: {len(valid_indices)}):\n")  # Print total rows
        for rating, movie_name in zip(cluster_ratings.values, cluster_movie_names.values):
            clusters_text.insert(tk.END, f"  Rating: {rating} -> Movie Name: {movie_name}\n")

    # outliers
    outlier_ratings = printOutliers(data)
    outlier_movies = data[data['IMDB Rating'].isin(outlier_ratings)]['Movie Name']


    Outliers_text.delete(1.0, tk.END)
    Outliers_text.insert(tk.END, "Outliers:\n")
    for rating, movie_name in zip(outlier_ratings, outlier_movies):
        Outliers_text.insert(tk.END, f"Rating: {rating}, Movie Name: {movie_name}\n")



window = tk.Tk()
window.title("Clustering")
def browse_file():
    file_path = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)  # Clear any previous text
    file_path_entry.insert(0, file_path)  # Insert the selected file path into the entry field

file_path_label = tk.Label(window, text="file path:")
file_path_label.grid(row=1, column=0, padx=10, pady=5)
file_path_entry = tk.Entry(window)
file_path_entry.grid(row=1, column=1, padx=10, pady=5)
browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.grid(row=1, column=2, padx=10, pady=5)
# Minimum Confidence
Percentage_label = tk.Label(window, text="Percentage(%):")
Percentage_label.grid(row=2, column=0, padx=10, pady=5)
Percentage_entry = tk.Entry(window)
Percentage_entry.grid(row=2, column=1, padx=10, pady=5)

k_label = tk.Label(window, text="k(%):")
k_label.grid(row=3, column=0, padx=10, pady=5)
k_entry = tk.Entry(window)
k_entry.grid(row=3, column=1, padx=10, pady=5)
# Analyze Button
analyze_button = tk.Button(window, text="Analyze", command=main)
analyze_button.grid(row=4, column=0, columnspan=3, pady=10)

# Output Widgets
final_centroid_label = tk.Label(window, text="Final centroids:")
final_centroid_label.grid(row=5, column=0, padx=10, pady=5)
final_centroid_text = tk.Text(window, height=10, width=80)
final_centroid_text.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

clusters_label = tk.Label(window, text="clusters:")
clusters_label.grid(row=7, column=0, padx=10, pady=5)
clusters_text = tk.Text(window, height=10, width=80)
clusters_text.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

Outliers_label = tk.Label(window, text="Outliers:")
Outliers_label.grid(row=5, column=10, padx=10, pady=5)
Outliers_text = tk.Text(window, height=10, width=80)
Outliers_text.grid(row=6, column=10, columnspan=3, padx=10, pady=5)

# Run the application
window.mainloop()


if __name__ == "__main__":
    main()

