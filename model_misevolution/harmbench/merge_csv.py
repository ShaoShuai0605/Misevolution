import glob
import pandas as pd

root_path = "/dataset/LLM-Tuning-Safety/HEx-PHI" # TODO: replace with your own path

categories = [1,3,4,5,6,7,8,9,10,11]
csv_files = [f"{root_path}/category_{i}.csv" for i in categories]
all_lines = []
for f in csv_files:
    with open(f, encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            all_lines.append(line)

df = pd.DataFrame({
    'Behavior': all_lines,
    'FunctionalCategory': '',
    'SemanticCategory': '',
    'Tags': '',
    'ContextString': '',
    'BehaviorID': range(len(all_lines))
})

df.to_csv('hex-phi.csv', index=False)