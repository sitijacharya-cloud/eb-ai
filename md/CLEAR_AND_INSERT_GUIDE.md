# Clear and Insert New Estimates

## Quick Workflow

### Step 1: Clear Old Data from MySQL
```sql
-- Connect to MySQL
mysql -u root -p

-- Use the database
USE vector_db;

-- Clear all records from the table
TRUNCATE TABLE json_embeddings;

-- Verify it's empty
SELECT COUNT(*) FROM json_embeddings;
-- Should show: 0

-- Exit MySQL
exit;
```

### Step 2: Add New JSON File
```bash
# Remove old JSON files (optional)
rm json_template/halfdata.json

# Add your new complete JSON file
cp /path/to/your/fulldata.json json_template/
```

### Step 3: Run the Import Script
```bash
# From project root
cd "/Users/ebpearls/Desktop/Ai estimation"

# Run the script
python insert_json_mysql.py
```

## What Happens

The script will:
1. ✅ Find ALL JSON files in `json_template/` folder
2. ✅ Process each file and extract estimations, epics, and tasks
3. ✅ Generate embeddings for semantic search
4. ✅ Insert all records into MySQL
5. ✅ Show you a summary of what was processed

## Example Output

```
============================================================
JSON to MySQL Embedding Pipeline
============================================================

📂 Found 1 JSON file(s) to process:
   1. fulldata.json

✓ Connected to MySQL database: vector_db
✓ Current records in database: 0

============================================================
Processing: fulldata.json
============================================================
✓ Loaded 100 estimations from file
✓ Created 8000 flattened records

Processing batch 1/80 (records 1-100)...
Inserted 100 records

Processing batch 2/80 (records 101-200)...
Inserted 100 records

... (continues for all batches)

✅ File processed successfully!
   - Total records: 8000
   - Inserted: 8000

============================================================
FINAL SUMMARY
============================================================
✓ Files processed: 1
✓ Total estimations: 100
✓ Total records processed: 8000
✓ Records inserted: 8000

📊 Database Statistics:
   - Before: 0 records
   - After: 8000 records
   - Added: 8000 records

============================================================
✅ ALL FILES PROCESSED SUCCESSFULLY!
============================================================
```

## Quick Commands

### Clear database and start fresh:
```bash
# One-liner to clear the table
mysql -u root -pNepal@2001 vector_db -e "TRUNCATE TABLE json_embeddings;"
```

### Check current record count:
```bash
mysql -u root -pNepal@2001 vector_db -e "SELECT COUNT(*) FROM json_embeddings;"
```

### View sample records:
```bash
mysql -u root -pNepal@2001 vector_db -e "SELECT estimation_name, epic_name, task_name, platform, estimated_hour FROM json_embeddings LIMIT 10;"
```

## File Structure

Your JSON file should look like this:
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
              },
              {
                "platform": {"name": "API"},
                "estimatedHour": 12
              }
            ]
          }
        ]
      }
    ]
  }
]
```

## Tips

1. **Always clear before inserting new data** if you want a fresh start
2. **The script processes ALL JSON files** in `json_template/` folder
3. **Multiple files are OK** - the script will process them all
4. **Large files are fine** - processing happens in batches of 100 records
5. **Check the output** - it shows exactly what was processed

## Troubleshooting

### "Table doesn't exist"
The script will create the table automatically on first run.

### "Connection refused"
Make sure MySQL is running:
```bash
# Check MySQL status
mysql.server status

# Start MySQL if needed
mysql.server start
```

### "File not found"
Make sure your JSON file is in the `json_template/` folder:
```bash
ls -la json_template/
```
