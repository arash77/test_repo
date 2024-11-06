import os

closed = os.getenv("ACTION_TYPE") == "closed"
merged = os.getenv("MERGED") == "true"
try:
    pr = int(os.getenv("PR_NUMBER"))
except:
    raise Exception("PR_NUMBER is not a number")
print(f"Closed: {closed}")
print(f"Merged: {merged}")
print(f"PR: {pr}")

if merged:
    print("Running in production mode")
elif not closed:
    print("Running in preview mode")
else:
    print("closed but not merged")