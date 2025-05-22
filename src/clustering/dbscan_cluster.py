dbscan = DBSCAN(eps=0.3, min_samples=10)  # You can tune these values
dbscan.fit_predict(features_scaled)


n_clusters = len(set(dbscan.labels_)) - (1 if -1 in dbscan.labels_ else 0)
n_noise = list(dbscan.labels_).count(-1)


# Plot the clusters
plt.figure(figsize=(10, 6))
unique_labels = set(dbscan.labels_)

for label in unique_labels:
    color = 'k' if label == -1 else plt.cm.jet(float(label) / max(unique_labels))
    class_member_mask = (dbscan.labels_ == label)
    xy = features[class_member_mask]
    plt.plot(xy['pickup_lng'], xy['pickup_lat'], 'o', markerfacecolor=color,
             markeredgecolor='k', markersize=7)

plt.title('DBSCAN Clustering of Pickup Locations')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.show()
plt.savefig('dbscan_clusters.png', dpi=400, bbox_inches='tight')


