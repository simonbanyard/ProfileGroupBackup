import os

import pandas as pd

import mimecast as mc

find_groups = "/api/directory/find-groups"
members = "/api/directory/get-group-members"

# Get Data for Group IDs
headers = {
    "Authorization": mc.auth(find_groups),
    "x-mc-app-id": mc.app_id,
    "x-mc-date": mc.hdr_date,
    "x-mc-req-id": mc.request_id,
    "Content-Type": "application/json",
}
data = str({"meta": {"pagination": {"pageSize": 500}}})

groups = mc.send_request(find_groups, headers, data)

# Export to Excel with Pandas
if not os.path.isdir("data"):
    os.mkdir("data")

groups_df = pd.DataFrame(groups["data"][0]["folders"])
groups_df.to_excel(
    "data/profile_groups.xlsx",
    index=False,
    columns=["description", "userCount", "folderCount", "id"],
)
