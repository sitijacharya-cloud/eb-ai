# JSON Templates Folder

This folder contains JSON estimation templates that will be processed and stored in MySQL with embeddings.

## How to Use

### 1. Add Your JSON Files Here
Simply place your JSON estimation files in this folder:
```
json_template/
├── halfdata.json          (30 estimates - already added)
├── fulldata.json          (all estimates - add this)
├── new_estimates.json     (any new estimates)
└── ...
```

### 2. Run the Import Script
From the project root, run:
```bash
python insert_json_mysql.py
```

### 3. What Happens
- ✅ **Processes ALL JSON files** in this folder automatically
- ✅ **Skips duplicates** - won't re-insert existing data
- ✅ **Shows progress** for each file and batch
- ✅ **Generates embeddings** for semantic search
- ✅ **Safe to run multiple times** - won't duplicate data

## Duplicate Detection

The script uses a **UNIQUE constraint** on:
- `estimation_id`
- `epic_id`
- `task_name`
- `platform`

If you run the script again with the same data, it will:
- ✅ Skip existing records (no duplicates)
- ✅ Only insert NEW records
- ✅ Show you how many were inserted vs skipped

## Example Workflow

### Scenario 1: Adding More Estimates
1. You currently have `halfdata.json` (30 estimates)
2. You get `fulldata.json` (all 100 estimates)
3. Place `fulldata.json` in this folder
4. Run: `python insert_json_mysql.py`
5. Result: It will insert the 70 NEW estimates, skip the 30 existing ones

### Scenario 2: Incremental Updates
1. You add `new_project_estimates.json` with 10 new projects
2. Run: `python insert_json_mysql.py`
3. Result: It will insert all 10 new projects, skip any duplicates

### Scenario 3: Re-running Safely
1. You accidentally run the script twice
2. Result: Second run will skip all duplicates, insert nothing (safe!)

## File Requirements

Each JSON file should have this structure:
```json
[
  {
    "id": 1,
    "name": "Project Name",
    "epics": [
      {
        "id": 1,
        "name": "Epic Name",
        "tasks": [
          {
            "name": "Task Name",
            "hours": [
              {
                "platform": {"name": "Flutter"},
                "estimatedHour": 8
              }
            ]
          }
        ]
      }
    ]
  }
]
```

## Output Example

```
============================================================
JSON to MySQL Embedding Pipeline
============================================================

📂 Found 2 JSON file(s) to process:
   1. halfdata.json
   2. fulldata.json

✓ Connected to MySQL database: vector_db
✓ Current records in database: 2500

============================================================
Processing: halfdata.json
============================================================
✓ Loaded 30 estimations from file
✓ Created 2500 flattened records

Processing batch 1/25 (records 1-100)...
Inserted 0 new records (skipped 100 duplicates)
...

✅ File processed successfully!
   - Total records: 2500
   - Inserted: 0
   - Skipped (duplicates): 2500

============================================================
Processing: fulldata.json
============================================================
✓ Loaded 100 estimations from file
✓ Created 8000 flattened records

Processing batch 1/80 (records 1-100)...
Inserted 100 new records (skipped 0 duplicates)
...

✅ File processed successfully!
   - Total records: 8000
   - Inserted: 5500
   - Skipped (duplicates): 2500

============================================================
FINAL SUMMARY
============================================================
✓ Files processed: 2
✓ Total estimations: 130
✓ Total records processed: 10500
✓ New records inserted: 5500
✓ Duplicates skipped: 2500

📊 Database Statistics:
   - Before: 2500 records
   - After: 8000 records
   - Added: 5500 records

============================================================
✅ ALL FILES PROCESSED SUCCESSFULLY!
============================================================
```

## Tips

1. **Always place JSON files in this folder** before running the script
2. **No need to delete old files** - the script handles duplicates
3. **Run anytime** - it's safe to run multiple times
4. **Check the output** - it shows exactly what was inserted/skipped
5. **Large files are OK** - the script processes in batches (100 records at a time)

## Troubleshooting

### "No JSON files found"
- Make sure your JSON files are in the `json_template` folder
- Check file extensions are `.json` (lowercase)

### "Duplicate key error"
- The script should auto-skip duplicates
- If you see this error, the UNIQUE constraint might not be set up
- Run the script once to create the constraint

### "API rate limit"
- The script has built-in rate limiting (1 second between batches)
- If you still hit limits, increase the `time.sleep(1)` value in the script

## Database Schema

Records are stored with this structure:
- `estimation_id` - Project ID
- `estimation_name` - Project name
- `epic_id` - Epic ID
- `epic_name` - Epic name
- `task_name` - Task description
- `platform` - Platform (Flutter, Web App, API, CMS)
- `estimated_hour` - Hours for this task/platform
- `content_text` - Text used for embedding (Epic + Task name only)
- `embedding` - Vector embedding for semantic search
- `created_at` - Timestamp

**UNIQUE constraint**: (estimation_id, epic_id, task_name, platform)
