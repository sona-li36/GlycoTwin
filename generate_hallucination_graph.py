import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. Ensure the directory exists
output_dir = 'data/processed'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Define the data
data = {
    'Metric Category': ['Dosing Accuracy', 'Biomarker Tracking', 'Protocol Alignment', 'Side-Effect Mitigation'],
    'Standard LLM (Baseline %)': [15.2, 12.8, 18.5, 14.1],
    'GlycoTwin (Proposed %)': [1.8, 1.5, 2.0, 1.9]
}
df = pd.DataFrame(data)

# 3. Create the plot
fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(df['Metric Category']))
width = 0.35

rects1 = ax.bar([i - width/2 for i in x], df['Standard LLM (Baseline %)'], width, label='Standard LLM (Baseline)', color='#ff9999')
rects2 = ax.bar([i + width/2 for i in x], df['GlycoTwin (Proposed %)'], width, label='GlycoTwin (CRAG + SDDT)', color='#66b3ff')

ax.set_ylabel('Hallucination Rate (%)')
ax.set_title('Medical Hallucination Rate: Baseline vs. GlycoTwin')
ax.set_xticks(x)
ax.set_xticklabels(df['Metric Category'])
ax.legend()

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
plt.tight_layout()

# 4. Save to the specific folder
file_path = os.path.join(output_dir, 'hallucination_comparison_v1.png')
plt.savefig(file_path)
plt.show()

print(f"Successfully saved to: {file_path}")