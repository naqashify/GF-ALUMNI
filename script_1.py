# Now create the complete corrected alumni dataset with all fields needed for the dashboard
import pandas as pd
import json

# Read the Excel file
df_alumni = pd.read_excel('Alumni-Data-2025-Updated-23rd-Sept-1.xlsx', sheet_name='Sheet1')

print("Creating COMPLETE CORRECTED alumni dataset...")

# Create the complete corrected alumni data
complete_corrected_alumni = []

for idx, row in df_alumni.iterrows():
    # Determine Alumni State Chapter (with fallback logic)
    base_location = row['Base Location - State'] if pd.notna(row['Base Location - State']) else None
    fellowship_location = row['Fellowship Location'] if pd.notna(row['Fellowship Location']) else None
    
    # Priority 1: Base Location - State (if meaningful)
    if (base_location and 
        str(base_location).strip() not in ['', 'nan', 'No Data Available', 'No Data available', 'No Data Available\n', 'No Data available\n']):
        alumni_state_chapter = str(base_location).strip()
    # Priority 2: Extract state from Fellowship Location
    elif fellowship_location:
        fellowship_str = str(fellowship_location).strip()
        if ' - ' in fellowship_str:
            alumni_state_chapter = fellowship_str.split(' - ')[0].strip()
        else:
            alumni_state_chapter = fellowship_str.strip()
    else:
        alumni_state_chapter = 'Unknown Chapter'
    
    # Clean support status
    support_raw = row['Are you willing to support the current batches with mentoring and guidance?']
    if pd.isna(support_raw):
        support_status = 'Unknown'
    elif str(support_raw).strip() == 'Yes':
        support_status = 'Yes'
    elif str(support_raw).strip() == "No. Won't be able to give time":
        support_status = 'No'
    else:
        support_status = 'Unknown'
    
    # Create complete alumni record
    alumni_record = {
        'sr_no': int(row['Sr. No']) if pd.notna(row['Sr. No']) else idx + 1,
        'batch': str(row['GF Batch']).strip() if pd.notna(row['GF Batch']) else 'Unknown',
        'name': str(row['Name']).strip() if pd.notna(row['Name']) else 'Unknown',
        'alumni_state_chapter': alumni_state_chapter,
        'email': str(row['Email']).strip() if pd.notna(row['Email']) and str(row['Email']) != 'nan' else 'Not Available',
        'big_bet': str(row['Big Bet']).strip() if pd.notna(row['Big Bet']) and str(row['Big Bet']) != 'nan' else 'Unknown',
        'work_status': str(row['Work status']).strip() if pd.notna(row['Work status']) and str(row['Work status']) != 'nan' else 'Unknown',
        'org_name': str(row['Org Name']).strip() if pd.notna(row['Org Name']) and str(row['Org Name']) != 'nan' else 'Unknown',
        'designation': str(row['Designation']).strip() if pd.notna(row['Designation']) and str(row['Designation']) != 'nan' else 'Unknown',
        'college': str(row['College']).strip() if pd.notna(row['College']) and str(row['College']) != 'nan' else 'Unknown',
        'university': str(row['University']).strip() if pd.notna(row['University']) and str(row['University']) != 'nan' else 'Unknown',
        'linkedin': str(row['Your LinkedIn profile link:']).strip() if pd.notna(row['Your LinkedIn profile link:']) and str(row['Your LinkedIn profile link:']) != 'nan' else 'Not Available',
        'support_status': support_status
    }
    complete_corrected_alumni.append(alumni_record)

print(f"Created complete corrected dataset with {len(complete_corrected_alumni)} alumni records")

# Create EXACT batch distribution
exact_batch_counts = {}
for alumni in complete_corrected_alumni:
    batch = alumni['batch']
    exact_batch_counts[batch] = exact_batch_counts.get(batch, 0) + 1

# Add B-13 with 0 count since it's missing
if 'B-13' not in exact_batch_counts:
    exact_batch_counts['B-13'] = 0

# Sort and create batch distribution
exact_batch_data = []
sorted_batches = sorted(exact_batch_counts.keys(), key=lambda x: int(x.replace('B-', '')) if x.startswith('B-') and x.replace('B-', '').isdigit() else float('inf'))

print(f"\nEXACT BATCH DISTRIBUTION (from complete data):")
for batch in sorted_batches:
    count = exact_batch_counts[batch]
    exact_batch_data.append({'batch': batch, 'count': count})
    print(f"  {batch}: {count} alumni")

# Create EXACT state chapters distribution
exact_chapter_counts = {}
for alumni in complete_corrected_alumni:
    chapter = alumni['alumni_state_chapter']
    if chapter != 'Unknown Chapter':
        exact_chapter_counts[chapter] = exact_chapter_counts.get(chapter, 0) + 1

exact_chapter_distribution = []
for chapter, count in exact_chapter_counts.items():
    exact_chapter_distribution.append({
        'state': chapter,  # Keep 'state' key for consistency
        'count': count,
        'percentage': round((count / len(complete_corrected_alumni)) * 100, 2)
    })

exact_chapter_distribution.sort(key=lambda x: x['count'], reverse=True)

print(f"\nEXACT STATE CHAPTERS DISTRIBUTION (top 15):")
for i, chapter in enumerate(exact_chapter_distribution[:15]):
    print(f"  {i+1}. {chapter['state']}: {chapter['count']} alumni ({chapter['percentage']}%)")

# Create work status distribution
work_status_counts = {}
for alumni in complete_corrected_alumni:
    status = alumni['work_status']
    work_status_counts[status] = work_status_counts.get(status, 0) + 1

work_status_data = []
for status, count in work_status_counts.items():
    work_status_data.append({
        'status': status,
        'count': count,
        'percentage': round((count / len(complete_corrected_alumni)) * 100, 2)
    })

work_status_data.sort(key=lambda x: x['count'], reverse=True)

print(f"\nWORK STATUS DISTRIBUTION:")
for status_info in work_status_data:
    print(f"  {status_info['status']}: {status_info['count']} ({status_info['percentage']}%)")

# Create support status distribution
support_counts = {'Yes': 0, 'No': 0, 'Unknown': 0}
for alumni in complete_corrected_alumni:
    support_counts[alumni['support_status']] += 1

print(f"\nSUPPORT STATUS DISTRIBUTION:")
for status, count in support_counts.items():
    print(f"  {status}: {count} alumni")

# Count unique colleges
unique_colleges = set()
for alumni in complete_corrected_alumni:
    if alumni['college'] not in ['Unknown', 'Not Available']:
        unique_colleges.add(alumni['college'])

print(f"\nUnique colleges represented: {len(unique_colleges)}")

# Create the final EXACT corrected dashboard data
final_exact_dashboard_data = {
    'alumni_data': complete_corrected_alumni,
    'batch_distribution': exact_batch_data,
    'state_distribution': exact_chapter_distribution,
    'work_status_distribution': work_status_data,
    'summary_stats': {
        'total_alumni': len(complete_corrected_alumni),
        'total_batches': len(exact_batch_data),
        'support_yes': support_counts['Yes'],
        'support_no': support_counts['No'],
        'support_unknown': support_counts['Unknown'],
        'states_represented': len(exact_chapter_distribution),
        'colleges_represented': len(unique_colleges),
        'work_status_categories': len(work_status_counts)
    }
}

# Save the final exact corrected data
with open('final_exact_corrected_alumni_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_exact_dashboard_data, f, indent=2, ensure_ascii=False)

print(f"\nFINAL EXACT CORRECTED DATA SAVED!")
print(f"Summary:")
print(f"  - Total alumni: {len(complete_corrected_alumni)}")
print(f"  - Total batches: {len(exact_batch_data)} (including B-13: 0)")
print(f"  - Alumni State Chapters: {len(exact_chapter_distribution)}")
print(f"  - Support Yes: {support_counts['Yes']}")
print(f"  - Support No: {support_counts['No']}")
print(f"  - Support Unknown: {support_counts['Unknown']}")
print(f"  - Colleges represented: {len(unique_colleges)}")
print(f"  - Work status categories: {len(work_status_counts)}")

# Show verification of batch data
print(f"\nVERIFICATION - First 5 alumni with their exact batches:")
for i in range(5):
    alumni = complete_corrected_alumni[i]
    print(f"  {i+1}. {alumni['name']} - {alumni['batch']} - {alumni['alumni_state_chapter']}")

print(f"\nReady to create dashboard with EXACT Excel data!")