#!/bin/bash
# Sync local Growth OS DB to GCS every 6 hours
# Run via cron: 0 */6 * * * /Users/Subho/growth-workflow-os/sync_db_to_gcs.sh

DB_PATH="/Users/Subho/growth-workflow-os/strategic_memory/growth_os.db"
GCS_BUCKET="growth-os-db-338789220059"

if [ ! -f "$DB_PATH" ]; then
    echo "DB not found at $DB_PATH"
    exit 1
fi

SIZE=$(wc -c < "$DB_PATH")
if [ "$SIZE" -lt 1000 ]; then
    echo "DB seems empty ($SIZE bytes)"
    exit 1
fi

echo "Syncing Growth OS DB to GCS ($SIZE bytes)..."
gsutil cp "$DB_PATH" "gs://${GCS_BUCKET}/growth_os.db"
echo "Done. Timestamp: $(date)"