import os

import pandas as pd

import mimecast as mc

find_groups = "/api/directory/find-groups"
members = "/api/directory/get-group-members"

data = str({"meta": {"pagination": {"pageSize": 500}}})

groups = mc.send_request(find_groups, data)

# Export to Excel with Pandas
if not os.path.isdir("data"):
    os.mkdir("data")

groups_df = pd.DataFrame(groups["data"][0]["folders"])
groups_df.to_excel(
    "data/profile_groups.xlsx",
    index=False,
    columns=["description", "userCount", "folderCount", "id"],
)

group_ids = dict(zip(groups_df["description"], groups_df["id"]))

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
    profile_groups_df.to_excel(
        f"data/{group_id}.xlsx",
        index=False,
    )
