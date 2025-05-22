 
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, random_state=42, init='k-means++')
    kmeans.fit(features_scaled)
    wcss.append(kmeans.inertia_)


    # plot the elbow method
plt.figure(figsize=(10, 6))
plt.plot(range(1, 11), wcss, marker='o')
plt.title('Elbow Method for Optimal Clusters')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.xticks(range(1, 11))
plt.grid()
plt.show()


# initial model
kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, init='k-means++')
cluster= kmeans.fit_predict(features_scaled)
cluster

# Plot clusters using pickup lat and lng and fare from the features DataFrame
plt.figure(figsize=(10, 6))
scatter = plt.scatter(features['pickup_lng'], features['pickup_lat'], s=features['fare'],  # Use fare as the size of the points
                      c=cluster, cmap='viridis', alpha=0.6, edgecolor='k')

plt.xlabel('Pickup Longitude')
plt.ylabel('Pickup Latitude')
plt.title('K-Means Clusters of Trip Pickup Locations')
plt.colorbar(scatter, label='Cluster')
plt.grid(True)
plt.tight_layout()
plt.show()




