# Let's re-examine the Excel file very carefully to get the EXACT batch information and state chapters
import pandas as pd
import json

# Read the Excel file
df_alumni = pd.read_excel('Alumni-Data-2025-Updated-23rd-Sept-1.xlsx', sheet_name='Sheet1')

print("=== DETAILED EXCEL ANALYSIS ===")
print(f"Total records in Excel: {len(df_alumni)}")
print(f"Columns in Excel:")
for i, col in enumerate(df_alumni.columns):
    print(f"  {i+1}. '{col}'")

print(f"\n=== BATCH ANALYSIS ===")
batch_column = 'GF Batch'
print(f"Analyzing column: '{batch_column}'")

if batch_column in df_alumni.columns:
    # Get all unique batch values
    batch_values = df_alumni[batch_column].dropna().unique()
    print(f"Unique batch values found: {sorted(batch_values)}")
    
    # Get exact count for each batch
    batch_counts = df_alumni[batch_column].value_counts()
    print(f"\nEXACT batch distribution from Excel:")
    
    # Sort batches numerically
    sorted_batches = sorted(batch_counts.index, key=lambda x: int(x.replace('B-', '')) if x.startswith('B-') and x.replace('B-', '').isdigit() else float('inf'))
    
    total_check = 0
    for batch in sorted_batches:
        count = batch_counts[batch]
        total_check += count
        print(f"  {batch}: {count} alumni")
    
    print(f"Total alumni from batch count: {total_check}")
    print(f"Total records in Excel: {len(df_alumni)}")
    
    # Check for any missing batches in sequence
    batch_numbers = []
    for batch in sorted_batches:
        if batch.startswith('B-') and batch.replace('B-', '').isdigit():
            batch_numbers.append(int(batch.replace('B-', '')))
    
    if batch_numbers:
        min_batch = min(batch_numbers)
        max_batch = max(batch_numbers)
        print(f"\nBatch sequence: B-{min_batch} to B-{max_batch}")
        
        missing_batches = []
        for i in range(min_batch, max_batch + 1):
            batch_name = f'B-{i}'
            if batch_name not in batch_counts:
                missing_batches.append(batch_name)
        
        if missing_batches:
            print(f"Missing batches (0 alumni): {missing_batches}")
        else:
            print("No missing batches in sequence")

print(f"\n=== STATE CHAPTERS ANALYSIS ===")

# Check Base Location - State column first
base_location_col = 'Base Location - State'
print(f"Analyzing '{base_location_col}' column:")

if base_location_col in df_alumni.columns:
    base_location_data = df_alumni[base_location_col]
    non_null_base = base_location_data.dropna()
    print(f"Non-null values in Base Location - State: {len(non_null_base)}")
    print(f"Null values in Base Location - State: {len(base_location_data) - len(non_null_base)}")
    
    if len(non_null_base) > 0:
        print(f"Sample Base Location - State values:")
        for i, value in enumerate(non_null_base.head(10)):
            print(f"  {i+1}. '{value}'")
        
        # Get unique base location values
        unique_base_locations = non_null_base.unique()
        print(f"\nAll unique Base Location - State values ({len(unique_base_locations)}):")
        for i, location in enumerate(sorted(unique_base_locations)):
            count = (base_location_data == location).sum()
            print(f"  {i+1}. '{location}': {count} alumni")

# Check Fellowship Location as fallback
fellowship_col = 'Fellowship Location'
print(f"\nAnalyzing '{fellowship_col}' column:")

if fellowship_col in df_alumni.columns:
    fellowship_data = df_alumni[fellowship_col]
    non_null_fellowship = fellowship_data.dropna()
    print(f"Non-null values in Fellowship Location: {len(non_null_fellowship)}")
    
    # Extract states from Fellowship Location
    states_from_fellowship = []
    for location in non_null_fellowship:
        if ' - ' in str(location):
            state = str(location).split(' - ')[0].strip()
            states_from_fellowship.append(state)
        else:
            states_from_fellowship.append(str(location).strip())
    
    # Count states from fellowship locations
    from collections import Counter
    state_counts_fellowship = Counter(states_from_fellowship)
    
    print(f"\nStates extracted from Fellowship Location (top 20):")
    for i, (state, count) in enumerate(state_counts_fellowship.most_common(20)):
        print(f"  {i+1}. {state}: {count} alumni")

print(f"\n=== CREATING DEFINITIVE STATE CHAPTERS MAPPING ===")

# Create the most accurate state chapters mapping
final_state_chapters = {}
alumni_records = []

for idx, row in df_alumni.iterrows():
    # Get batch
    batch = str(row[batch_column]).strip() if pd.notna(row[batch_column]) else 'Unknown'
    
    # Determine state chapter with priority: Base Location -> Fellowship Location state
    state_chapter = None
    
    # Priority 1: Base Location - State
    base_loc = row[base_location_col] if base_location_col in df_alumni.columns else None
    if pd.notna(base_loc) and str(base_loc).strip() not in ['', 'nan', 'No Data Available', 'No Data available']:
        state_chapter = str(base_loc).strip()
    
    # Priority 2: Extract state from Fellowship Location
    elif fellowship_col in df_alumni.columns:
        fellowship_loc = row[fellowship_col]
        if pd.notna(fellowship_loc):
            fellowship_str = str(fellowship_loc).strip()
            if ' - ' in fellowship_str:
                state_chapter = fellowship_str.split(' - ')[0].strip()
            else:
                state_chapter = fellowship_str.strip()
    
    # Default
    if not state_chapter or state_chapter in ['nan', 'None', '']:
        state_chapter = 'Unknown Chapter'
    
    # Count state chapters
    if state_chapter in final_state_chapters:
        final_state_chapters[state_chapter] += 1
    else:
        final_state_chapters[state_chapter] = 1
    
    # Store alumni record
    alumni_records.append({
        'sr_no': int(row['Sr. No']) if pd.notna(row['Sr. No']) else idx + 1,
        'batch': batch,
        'name': str(row['Name']).strip() if pd.notna(row['Name']) else 'Unknown',
        'alumni_state_chapter': state_chapter,
        'base_location_original': str(base_loc) if pd.notna(base_loc) else 'Not Available',
        'fellowship_location': str(row[fellowship_col]) if fellowship_col in df_alumni.columns and pd.notna(row[fellowship_col]) else 'Not Available'
    })

print(f"\nFINAL STATE CHAPTERS DISTRIBUTION:")
sorted_chapters = sorted(final_state_chapters.items(), key=lambda x: x[1], reverse=True)
for i, (chapter, count) in enumerate(sorted_chapters):
    percentage = (count / len(df_alumni)) * 100
    print(f"  {i+1}. {chapter}: {count} alumni ({percentage:.2f}%)")

print(f"\nTotal chapters: {len(final_state_chapters)}")

# Create the final corrected batch distribution
final_batch_counts = {}
for record in alumni_records:
    batch = record['batch']
    if batch in final_batch_counts:
        final_batch_counts[batch] += 1
    else:
        final_batch_counts[batch] = 1

print(f"\n=== FINAL CORRECTED BATCH DISTRIBUTION ===")
sorted_batch_keys = sorted(final_batch_counts.keys(), key=lambda x: int(x.replace('B-', '')) if x.startswith('B-') and x.replace('B-', '').isdigit() else float('inf'))

final_batch_data = []
for batch in sorted_batch_keys:
    count = final_batch_counts[batch]
    final_batch_data.append({'batch': batch, 'count': count})
    print(f"  {batch}: {count} alumni")

# Add any missing batches in sequence with 0 count
if sorted_batch_keys and sorted_batch_keys[0].startswith('B-'):
    batch_numbers = [int(b.replace('B-', '')) for b in sorted_batch_keys if b.startswith('B-') and b.replace('B-', '').isdigit()]
    if batch_numbers:
        for i in range(min(batch_numbers), max(batch_numbers) + 1):
            batch_name = f'B-{i}'
            if batch_name not in final_batch_counts:
                final_batch_data.append({'batch': batch_name, 'count': 0})
                print(f"  {batch_name}: 0 alumni (missing from data)")

# Sort final batch data
final_batch_data.sort(key=lambda x: int(x['batch'].replace('B-', '')) if x['batch'].startswith('B-') and x['batch'].replace('B-', '').isdigit() else float('inf'))

print(f"\nTotal alumni in final data: {len(alumni_records)}")

# Save sample of the corrected data for verification
print(f"\n=== SAMPLE CORRECTED RECORDS ===")
for i in range(min(5, len(alumni_records))):
    record = alumni_records[i]
    print(f"{i+1}. {record['name']} ({record['batch']}) - {record['alumni_state_chapter']}")

# Save the corrected data
corrected_data = {
    'total_alumni': len(alumni_records),
    'batch_distribution': final_batch_data,
    'state_chapters_distribution': sorted_chapters,
    'sample_records': alumni_records[:10]
}

with open('excel_corrected_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(corrected_data, f, indent=2, ensure_ascii=False)

print(f"\nCorrected analysis saved to excel_corrected_analysis.json")
print(f"Ready to create the final dashboard with EXACT Excel data")