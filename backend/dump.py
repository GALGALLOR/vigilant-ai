import sqlite3
import json
conn = sqlite3.connect('vigilant.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT start, end, caption, event_type FROM events ORDER BY start").fetchall()

print("EVENTS DUMP:")
for r in rows:
    print(f"[{r['start']} - {r['end']}] Type: {r['event_type']}")
    print(f"Caption: {r['caption']}\n")

# Let's also dump the summary
print("-" * 50)
summary = conn.execute("SELECT summary, intent FROM video_summaries").fetchone()
if summary:
    print("GEMINI SUMMARY:")
    print(summary['summary'])
    print(f"INTENT: {summary['intent']}")
