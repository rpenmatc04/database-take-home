#!/usr/bin/env python3
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# Ensure scripts directory is in path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from scripts.constants import NUM_NODES, NUM_QUERIES, LAMBDA_PARAM, RANDOM_SEED


def visualize_exponential_distribution(
    num_nodes=NUM_NODES,
    num_queries=NUM_QUERIES,
    lambda_param=LAMBDA_PARAM,
    seed=RANDOM_SEED,
    num_samples=100000  # Large sample size for accurate probability estimation
):
    """
    Visualize the probability distribution of nodes being queried based on 
    the exponential distribution used in generate_queries.
    
    Args:
        num_nodes: Number of nodes in the graph (500)
        num_queries: Number of queries in actual use
        lambda_param: Parameter for exponential distribution
        seed: Random seed for reproducibility
        num_samples: Number of samples to generate for probability estimation
    """
    np.random.seed(seed)
    
    # Generate a large sample to estimate probabilities
    exp_values = np.random.exponential(scale=1 / lambda_param, size=num_samples)
    scaled_values = (exp_values % num_nodes).astype(int)
    
    # Count occurrences of each node
    node_counts = Counter(scaled_values)
    
    # Calculate probability for each node (0 to 499)
    nodes = list(range(num_nodes))
    probabilities = [node_counts.get(node, 0) / num_samples for node in nodes]
    
    # Create the visualization
    _, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))
    
    # Plot 1: Bar chart of probabilities for all nodes
    ax1.bar(nodes, probabilities, width=1.0, edgecolor='none', alpha=0.7)
    ax1.set_xlabel('Node ID')
    ax1.set_ylabel('Probability of Being Queried')
    ax1.set_title(f'Query Probability Distribution (Exponential with λ={lambda_param})')
    ax1.set_xlim(-0.5, num_nodes - 0.5)
    
    # Add grid for better readability
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Zoomed view of first 25 nodes
    ax2.bar(nodes[:25], probabilities[:25], width=0.8, edgecolor='none', alpha=0.7, color='green')
    ax2.set_xlabel('Node ID')
    ax2.set_ylabel('Probability of Being Queried')
    ax2.set_title('Query Probability Distribution (Zoomed: Nodes 0-24)')
    ax2.set_xlim(-0.5, 24.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Zoomed view of first 50 nodes (where most probability mass is)
    ax3.bar(nodes[:50], probabilities[:50], width=0.8, edgecolor='none', alpha=0.7, color='orange')
    ax3.set_xlabel('Node ID')
    ax3.set_ylabel('Probability of Being Queried')
    ax3.set_title('Query Probability Distribution (Zoomed: Nodes 0-49)')
    ax3.set_xlim(-0.5, 49.5)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Add statistics text
    max_prob_node = np.argmax(probabilities)
    max_prob = probabilities[max_prob_node]
    
    # Calculate cumulative probability for first 10, 50, 100 nodes
    cum_prob_10 = sum(probabilities[:10])
    cum_prob_50 = sum(probabilities[:50])
    cum_prob_100 = sum(probabilities[:100])
    
    stats_text = (
        f'Statistics:\n'
        f'Most likely node: {max_prob_node} (p={max_prob:.4f})\n'
        f'Cumulative probability:\n'
        f'  Nodes 0-9: {cum_prob_10:.2%}\n'
        f'  Nodes 0-49: {cum_prob_50:.2%}\n'
        f'  Nodes 0-99: {cum_prob_100:.2%}'
    )
    
    ax1.text(0.98, 0.95, stats_text, transform=ax1.transAxes, 
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             fontsize=9)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(project_root, "data", "exponential_distribution.png")
    plt.savefig(output_path, dpi=150)
    print(f"Exponential distribution visualization saved to {output_path}")
    
    # Also create a histogram showing the actual expected query counts
    _, ax4 = plt.subplots(figsize=(12, 6))
    
    # Generate expected counts for actual number of queries
    expected_counts = [prob * num_queries for prob in probabilities]
    
    # Create bins for better visualization
    bin_size = 10
    num_bins = num_nodes // bin_size
    binned_counts = []
    bin_labels = []
    
    for i in range(num_bins):
        start = i * bin_size
        end = (i + 1) * bin_size
        binned_counts.append(sum(expected_counts[start:end]))
        bin_labels.append(f"{start}-{end-1}")
    
    ax4.bar(range(num_bins), binned_counts, width=0.8, alpha=0.7)
    ax4.set_xlabel('Node ID Range')
    ax4.set_ylabel(f'Expected Number of Queries (out of {num_queries} total)')
    ax4.set_title('Expected Query Count Distribution by Node Range')
    ax4.set_xticks(range(0, num_bins, 5))
    ax4.set_xticklabels([bin_labels[i] for i in range(0, num_bins, 5)], rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    output_path2 = os.path.join(project_root, "data", "expected_query_counts.png")
    plt.savefig(output_path2, dpi=150)
    print(f"Expected query counts visualization saved to {output_path2}")
    
    plt.show()
    
    return nodes, probabilities


if __name__ == "__main__":
    print("Visualizing exponential distribution used for query generation...")
    nodes, probabilities = visualize_exponential_distribution()
    
    # Print some key statistics
    print(f"\nKey Statistics:")
    print(f"Total nodes: {NUM_NODES}")
    print(f"Lambda parameter: {LAMBDA_PARAM}")
    print(f"Number of queries: {NUM_QUERIES}")
    
    # Find nodes with highest probabilities
    sorted_probs = sorted(enumerate(probabilities), key=lambda x: x[1], reverse=True)
    print(f"\nTop 10 most likely nodes to be queried:")
    for i, (node, prob) in enumerate(sorted_probs[:10]):
        expected_queries = prob * NUM_QUERIES
        print(f"  {i+1}. Node {node}: p={prob:.4f} (expected {expected_queries:.1f} queries)")