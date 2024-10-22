import os

cmems_password = os.getenv('CMEMS_PASSWORD')

if cmems_password is None or cmems_password == "":
    print("CMEMS_PASSWORD is not set!")
else:
    print(f"CMEMS_PASSWORD retrieved successfully: {cmems_password}")