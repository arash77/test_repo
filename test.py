import os

# Get the environment variable
cmems_password = os.getenv('CMEMS_PASSWORD')

if cmems_password is None:
    print("CMEMS_PASSWORD is not set!")
else:
    print("CMEMS_PASSWORD retrieved successfully.", cmems_password)