import os
import json
import re
from pathlib import Path

def extract_id(profile_url):
    m = re.search(r'user/(\d+)', str(profile_url))
    return int(m.group(1)) if m else None

def fix_week(week_file_curr, guild_name, summary_file_prev, baseline_file_curr):
    with open(week_file_curr, 'r', encoding='utf-8') as f:
        curr_data = json.load(f)
        
    with open(summary_file_prev, 'r', encoding='utf-8') as f:
        prev_summary = json.load(f)
        
    prev_guild_data = prev_summary.get("guilds", {}).get(guild_name, {})
        
    # Build dictionary of prev_data users by their profile ID
    prev_by_id = {}
    for norm, user_data in prev_guild_data.get("participants", {}).items():
        uid = extract_id(user_data.get("profile"))
        if uid:
            prev_by_id[uid] = user_data
            
    # Also load the current baseline file to fix it
    with open(baseline_file_curr, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
        
    changed = False
    for norm, user_data in curr_data.get("participants", {}).items():
        uid = extract_id(user_data.get("profile"))
        if uid and uid in prev_by_id:
            old_user_data = prev_by_id[uid]
            # Baseline is the previous week's 'current' value
            correct_baseline = old_user_data.get("current", 0)
            
            if user_data.get("baseline") != correct_baseline:
                user_data["baseline"] = correct_baseline
                # also update weekly
                user_data["weekly"] = max(0, user_data["current"] - correct_baseline)
                # also fix the baseline file
                base_data[norm] = correct_baseline
                changed = True

    if changed:
        with open(week_file_curr, 'w', encoding='utf-8') as f:
            json.dump(curr_data, f, ensure_ascii=False, indent=2)
        with open(baseline_file_curr, 'w', encoding='utf-8') as f:
            json.dump(base_data, f, ensure_ascii=False, indent=2)
        print(f"Fixed {week_file_curr.name} using {summary_file_prev.name}")
    else:
        print(f"No changes needed for {week_file_curr.name}")

def main():
    root = Path(__file__).parent
    for guild in ["Eternal Watchers", "Eternal Demonic", "Eternal Angelic"]:
        guild_dir = root / guild
        if not guild_dir.exists(): continue
        
        weeks = sorted([f for f in guild_dir.glob("week_*.json")])
        
        if len(weeks) < 2:
            continue
            
        for i in range(1, len(weeks)):
            prev_w = weeks[i-1]
            curr_w = weeks[i]
            
            # Use prev_w.name to match the summary filename exactly, e.g. summary_2025-10-13_0030...
            summary_name = prev_w.name.replace("week_", "summary_")
            summary_file_prev = root / summary_name
            
            # Match the baseline file for curr_w
            date_str = curr_w.name[5:20]
            curr_b = guild_dir / f"baseline_{date_str}.json"
            
            if summary_file_prev.exists() and curr_b.exists():
                fix_week(curr_w, guild, summary_file_prev, curr_b)

if __name__ == '__main__':
    main()
