import json

# Load both JSON files - results and completions
with open('/mnt/shared-storage-user/renqihan/harmbench/results/DirectRequest/default/results/8192_tokens/dapo_qw3-base-8b_all-correct-1-57k_lr1e-6_step222_step222.json', 'r') as f:
    dapo_data = json.load(f)

with open('/mnt/shared-storage-user/renqihan/harmbench/results/DirectRequest/default/results/8192_tokens/sft_qw3-base-8b_all-correct-8-57k_vanilla_lr5e-5_ep8_eos_nochange_step888.json', 'r') as f:
    sft_data = json.load(f)

# Load the original SFT completions file to get the unprocessed generations
with open('/mnt/shared-storage-user/renqihan/harmbench/results/DirectRequest/default/completions/8192_tokens/sft_qw3-base-8b_all-correct-8-57k_vanilla_lr5e-5_ep8_eos_nochange_step888.json', 'r') as f:
    sft_completions = json.load(f)

# Initialize result dictionaries
dapo_1_sft_0 = {}  # label=1 in DAPO, label=0 in SFT
sft_1_dapo_0 = {}  # label=1 in SFT, label=0 in DAPO

# Compare entries across both files
for key in dapo_data.keys():
    if key in sft_data and key in sft_completions:
        dapo_entry = dapo_data[key][0]  # Get first entry
        sft_entry = sft_data[key][0]    # Get first entry
        sft_completion = sft_completions[key][0]  # Get original completion
        
        dapo_label = dapo_entry.get('label', None)
        sft_label = sft_entry.get('label', None)
        
        # Check for label=1 in DAPO and label=0 in SFT
        if dapo_label == 1 and sft_label == 0:
            dapo_1_sft_0[key] = {
                'dapo_entry': dapo_entry,
                'sft_entry': sft_entry,
                'sft_ori_generation': sft_completion.get('generation', '')
            }
        
        # Check for label=1 in SFT and label=0 in DAPO
        elif sft_label == 1 and dapo_label == 0:
            sft_1_dapo_0[key] = {
                'dapo_entry': dapo_entry,
                'sft_entry': sft_entry,
                'sft_ori_generation': sft_completion.get('generation', '')
            }

# Save results to separate JSON files
with open('/mnt/shared-storage-user/renqihan/harmbench/dapo_1_sft_0_differences.json', 'w') as f:
    json.dump(dapo_1_sft_0, f, indent=2)

with open('/mnt/shared-storage-user/renqihan/harmbench/sft_1_dapo_0_differences.json', 'w') as f:
    json.dump(sft_1_dapo_0, f, indent=2)

print(f"Found {len(dapo_1_sft_0)} entries where DAPO has label=1 and SFT has label=0")
print(f"Found {len(sft_1_dapo_0)} entries where SFT has label=1 and DAPO has label=0")
print("\nEntries where DAPO=1 and SFT=0:")
for key in dapo_1_sft_0.keys():
    print(f"  - {key}")
print("\nEntries where SFT=1 and DAPO=0:")
for key in sft_1_dapo_0.keys():
    print(f"  - {key}")