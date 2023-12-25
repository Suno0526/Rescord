# This is a test file.

# Nothing in this document is related to the actual bot.

# If you want bot content, please go to the "Main.py" file and look there. Cheers! 🍻


# Idea:
#   - Upload JSON data to a pre-existant JSON file & have it save. (NOT DONE)

import json as JSON;

with open("Debug/Confirm.json", "r+") as Data:
    Data2 = JSON.load(Data)

    Data2["Work"] = "Yes"

    Data.seek(0)
    JSON.dump(Data2, Data, indent = 4)

    Data.truncate()
