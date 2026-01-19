# Quick Start: Adding New Estimates to MySQL

## Simple 3-Step Process

### Step 1: Add JSON File
Place your JSON file in the `json_template` folder:
```bash
# Example: Copy your new full dataset
cp /path/to/your/fulldata.json json_template/
```

### Step 2: Run the Script
```bash
# Make sure you're in the project root
cd "/Users/ebpearls/Desktop/Ai estimation"

# Run the import script
python insert_json_mysql.py
```

### Step 3: Done! ✅
The script will:
- Process ALL JSON files in `json_template/`
- Skip any duplicate records automatically
- Show you a summary of what was added

## Example Scenarios

### Scenario A: You have halfdata.json (30 estimates) and get fulldata.json (100 estimates)

```bash
# 1. Add the new file
cp fulldata.json json_template/

# 2. Run the script
python insert_json_mysql.py

# Result:
# ✓ Processes halfdata.json → Skips all 2500 records (already exist)
# ✓ Processes fulldata.json → Inserts 5500 NEW records, skips 2500 duplicates
# ✓ Total in database: 8000 records
```

### Scenario B: You get 10 new project estimates

```bash
# 1. Add the new file
cp new_projects.json json_template/

# 2. Run the script
python insert_json_mysql.py

# Result:
# ✓ Processes all existing files → Skips all existing records
# ✓ Processes new_projects.json → Inserts all new records
# ✓ Database updated with new projects only
```

### Scenario C: You accidentally run the script twice

```bash
# First run
python insert_json_mysql.py
# ✓ Inserts 8000 records

# Oops, ran it again!
python insert_json_mysql.py
# ✓ Skips all 8000 records (duplicates detected)
# ✓ No duplicates created - safe!
```

## What Gets Inserted?

For each task in your JSON:
```json
{
  "estimation": "Dating App",
  "epic": "User Authentication",
  "task": "Email login with password validation",
  "platform": "Flutter",
  "hours": 8
}
```

This becomes a searchable record with:
- All the metadata (estimation, epic, task, platform, hours)
- An embedding vector for semantic search
- A UNIQUE constraint to prevent duplicates

## Checking Your Data

### Count total records:
```sql
SELECT COUNT(*) FROM json_embeddings;
```

### Count by estimation:
```sql
SELECT estimation_name, COUNT(*) as task_count 
FROM json_embeddings 
GROUP BY estimation_name;
```

### See recent additions:
```sql
SELECT estimation_name, epic_name, task_name, platform, estimated_hour 
FROM json_embeddings 
ORDER BY created_at DESC 
LIMIT 20;
```

## Need Help?

Check `json_template/README.md` for detailed documentation!
