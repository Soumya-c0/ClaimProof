import matplotlib.pyplot as plt
import numpy as np

def generate_charts():
    # Comparison Categories
    labels = ['ClaimProof\n(Deterministic)', 'Standard RAG\n(LLM Evaluation)']
    
    # Example metrics (we will update these based on your final terminal output)
    latency = [0.045, 5.2] # seconds
    cost = [0.00, 0.015] # dollars

    width = 0.4
    x = np.arange(len(labels))

    # 1. Latency Chart (Lower is better)
    fig, ax = plt.subplots(figsize=(6, 5))
    bars = ax.bar(labels, latency, width, color=['#15803D', '#B45309'])
    ax.set_ylabel('Execution Time (seconds)', fontweight='bold')
    ax.set_title('Latency per Claim Assessment', pad=15, fontweight='bold')
    ax.bar_label(bars, fmt='%.3fs', padding=3, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('latency_chart.png', dpi=300)
    print("Generated latency_chart.png")

    # 2. Cost Chart (Lower is better)
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    bars2 = ax2.bar(labels, cost, width, color=['#15803D', '#B45309'])
    ax2.set_ylabel('Inference Cost (USD)', fontweight='bold')
    ax2.set_title('API Cost per Claim', pad=15, fontweight='bold')
    ax2.bar_label(bars2, fmt='$%.3f', padding=3, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig('cost_chart.png', dpi=300)
    print("Generated cost_chart.png")

if __name__ == "__main__":
    generate_charts()