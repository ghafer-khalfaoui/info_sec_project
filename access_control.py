
import database

def check_access(username, filename, operation):
    user_role = database.users[username]["role"]
    user_clearance = database.users[username]["clearance"]
    
    # 1. RBAC Check (Deny by default)
    if operation not in database.roles_permissions[user_role]:
        return False, f"RBAC Denied: Role '{user_role}' cannot {operation}."
        
    # 2. Bell-LaPadula (BLP) Check
    if filename in database.files:
        file_class = database.files[filename]["classification"]
        
        if operation == "Read" and user_clearance < file_class:
            return False, f"BLP Denied: Clearance ({user_clearance}) too low to read file class ({file_class})."
            
        if operation == "Write" and user_clearance > file_class:
            return False, f"BLP Denied: Clearance ({user_clearance}) too high to write to file class ({file_class})."
            
    return True, "Access Granted."