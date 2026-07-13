import pandas as pd
import glob

# 1. Get a list of all your research papers
pdf_files = glob.glob("path/to/your/pdfs/*.pdf")

corpus_data = []

# 2. Iterate through each file and extract metadata
for file_path in pdf_files:
    # (Simulated extraction logic)
    file_name = file_path.split("/")[-1]
    
    entry = {
        "Reference_Title": file_name,
        "Category": "Clinical Protocol" if "Protocol" in file_name else "Journal Article",
        "Clinical_Domain": "Metabolic / GLP-1",
        "Indexing_Status": "Verified"
    }
    corpus_data.append(entry)

# 3. Create the CSV
df = pd.DataFrame(corpus_data)
df.to_csv("research_metadata_index.csv", index=False)

print("Research papers successfully converted to CSV index.")