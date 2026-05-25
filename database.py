#this file is optional it can be deleted with no problems 
# Bell-LaPadula Clearances: 3=Top Secret, 2=Secret, 1=Confidential, 0=Unclassified
users = {
    "dhafer": {"password": "123", "role": "Admin", "clearance": 3},
    "hamza": {"password": "456", "role": "User", "clearance": 1},
    "ahmed": {"password": "789", "role": "User", "clearance": 2}
}

roles_permissions = {
    "Admin": ["Read", "Write", "Create", "Delete"],
    "User": ["Read", "Write"]
}


files = {
    "report.txt": {
        "content": "",
        "classification": 2, 
        "owner": "dhafer"
    }
}
