import json
import os
from datetime import datetime

import pandas as pd

import mimecast as mc

# Add endpoints
find_groups = "/api/directory/find-groups"
members = "/api/directory/get-group-members"

# Request body
find_groups_data = str({"meta": {"pagination": {"pageSize": 500}}})

# Make request
print("=" * 80)
print("Fetching list of Profile Groups")
print("-" * 80)
groups = json.loads(mc.send_request(find_groups, find_groups_data))

today = datetime.now()
directory_name = today.strftime("%Y%m%d-%H%M%S")
os.mkdir(directory_name)

# Export data to Excel with Pandas
groups_df = pd.DataFrame(groups["data"][0]["folders"])
groups_df.to_excel(
    f"{directory_name}/_Profile Groups List.xlsx",
    index=False,
    columns=["description", "userCount", "folderCount", "id", "parentId"],
)
print(f"Profile Groups list saved as {directory_name}/_Profile Groups List.xlsx")
print("=" * 80, "\n")

# Create a dictionary of ID's for group backup
group_ids = dict(zip(groups_df["description"], groups_df["id"]))

# Loop over dictionary
request_count = 0
for group_id in group_ids:
    members_data = str(
        {
            "meta": {"pagination": {"pageSize": 500}},
            "data": [{"id": group_ids[group_id]}],
        }
    )
    print(f"Fetching {group_id}")
    print("-" * 80)
    profile_groups = json.loads(mc.send_request(members, members_data))
    profile_groups_df = pd.DataFrame(profile_groups["data"][0]["groupMembers"])

    if profile_groups.get("meta").get("pagination").get("next"):
        page_token = profile_groups.get("meta").get("pagination").get("next")

    while "next" in profile_groups.get("meta").get("pagination"):
        members_data = str(
            {
                "meta": {"pagination": {"pageSize": 500, "pageToken": page_token}},
                "data": [{"id": group_ids[group_id]}],
            }
        )
        profile_groups = json.loads(mc.send_request(members, members_data))
        profile_groups_df = pd.concat(
            [
                profile_groups_df,
                pd.DataFrame((profile_groups["data"][0]["groupMembers"])),
            ]
        )
        if profile_groups.get("meta").get("pagination").get("next"):
            page_token = profile_groups.get("meta").get("pagination").get("next")

    if profile_groups_df.empty:
        print("No data to save, file skipped\n")
    else:
        profile_groups_df.to_excel(f"{directory_name}/{group_id}.xlsx", index=False)
        print(f"File saved as {directory_name}/{group_id}.xlsx\n")
        request_count += 1

print(f"{request_count} files downloaded.")
