import os
import json
import re
from pathlib import Path

def extract_id(profile_url):
    m = re.search(r'user/(\d+)', str(profile_url))
    return int(m.group(1)) if m else None

def fix_summary(curr_file, prev_file):
    with open(curr_file, 'r', encoding='utf-8') as f:
        curr_data = json.load(f)
    with open(prev_file, 'r', encoding='utf-8') as f:
        prev_data = json.load(f)

    changed = False

    # The structure is data["guilds"]["Guild Name"]["participants"]["norm_key"]
    for guild_name, curr_guild_data in curr_data.get("guilds", {}).items():
        prev_guild_data = prev_data.get("guilds", {}).get(guild_name, {})
        
        # Build dictionary of prev_data users by their profile ID
        prev_by_id = {}
        for norm, user_data in prev_guild_data.get("participants", {}).items():
            uid = extract_id(user_data.get("profile"))
            if uid:
                prev_by_id[uid] = user_data

        curr_participants = curr_guild_data.get("participants", {})
        for norm, user_data in curr_participants.items():
            uid = extract_id(user_data.get("profile"))
            if uid and uid in prev_by_id:
                old_user_data = prev_by_id[uid]
                # Baseline is the previous week's 'current' value
                correct_baseline = old_user_data.get("current", 0)
                
                if user_data.get("baseline") != correct_baseline:
                    user_data["baseline"] = correct_baseline
                    # also update weekly
                    user_data["weekly"] = max(0, user_data["current"] - correct_baseline)
                    changed = True

    if changed:
        with open(curr_file, 'w', encoding='utf-8') as f:
            json.dump(curr_data, f, ensure_ascii=False, indent=2)
        print(f"Fixed {curr_file.name}")
    else:
        print(f"No changes needed for {curr_file.name}")

def main():
    root = Path(__file__).parent
    summaries = sorted([f for f in root.glob("summary_*.json")])
    
    if len(summaries) < 2:
        print("Not enough summaries to compare.")
        return
        
    for i in range(1, len(summaries)):
        prev_s = summaries[i-1]
        curr_s = summaries[i]
        fix_summary(curr_s, prev_s)

if __name__ == '__main__':
    main()
