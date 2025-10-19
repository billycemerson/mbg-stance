import pandas as pd

# Load comments data
data = pd.read_csv("../data/yt_mbg_comments.csv")

# See commens count before cleaning
print(f"Total comments before cleaning: {len(data)}")

# Drop duplicates based on 'comment_id'
data_cleaned = data.drop_duplicates(subset=['comment_id'])

# Drop comments that are Reply (i.e., where 'parent_id' is not null)
data_cleaned = data_cleaned[data_cleaned['parent_id'].isnull()]

# Reset index
data_cleaned = data_cleaned.reset_index(drop=True)

# Save cleaned data
data_cleaned.to_csv("../data/yt_mbg_comments_cleaned.csv", index=False)
print(f"Total comments after cleaning: {len(data_cleaned)}")