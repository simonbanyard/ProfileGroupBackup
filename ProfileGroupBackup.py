import os

import pandas as pd

import mimecast as mc

# Add endpoints
find_groups = "/api/directory/find-groups"
members = "/api/directory/get-group-members"

# Request body
find_groups_data = str({"meta": {"pagination": {"pageSize": 500}}})

# Make request
groups = mc.send_request(find_groups, find_groups_data)

# Check that a directory exists, if it doesnt, create it
if not os.path.isdir("data"):
    os.mkdir("data")

# Export data to Excel with Pandas
groups_df = pd.DataFrame(groups["data"][0]["folders"])
groups_df.to_excel(
    "data/profile_groups.xlsx",
    index=False,
    columns=["description", "userCount", "folderCount", "id"],
)

# Create a dictionary of ID's for group backup
group_ids = dict(zip(groups_df["description"], groups_df["id"]))

# Loop over dictionary
for group_id in group_ids:
    data = str(
        {
            "meta": {"pagination": {"pageSize": 500}},
            "data": [{"id": group_ids[group_id]}],
        }
    )
    profile_groups = mc.send_request(members, data)
    print(group_id, "\n")
    profile_groups_df = pd.DataFrame(profile_groups["data"][0]["groupMembers"])

    if profile_groups.get("meta").get("pagination").get("next"):
        page_token = profile_groups.get("meta").get("pagination").get("next")

    while "next" in profile_groups.get("meta").get("pagination"):
        data = str(
            {
                "meta": {
                    "pagination": {
                        "pageSize": 500,
                        "pageToken": page_token
                    }
                },
                    "data": [
                    {
                        "id": group_ids[group_id]
                    }
                ]
            }
        )
        profile_groups = mc.send_request(members, data)
        profile_groups_df = pd.concat([profile_groups_df, pd.DataFrame(profile_groups["data"][0]["groupMembers"])])
        if profile_groups.get("meta").get("pagination").get("next"):
            page_token = profile_groups.get("meta").get("pagination").get("next")

    profile_groups_df.to_excel(
        f"data/{group_id}.xlsx",
        index=False,
    )
