
import database

def check_access(username, filename, operation, db_source):
    user_role = db_source.users[username]["role"]
    user_clearance = db_source.users[username]["clearance"]
    
    if operation not in db_source.roles_permissions[user_role]:
        return False, f"RBAC Denied: Role '{user_role}' cannot {operation}."
        
    if filename in db_source.files:
        file_class = db_source.files[filename]["classification"]
        
        if operation == "Read" and user_clearance < file_class:
            return False, f"BLP Denied: Clearance ({user_clearance}) too low to read file class ({file_class})."
            
        if operation in ["Write", "Delete"] and user_clearance > file_class:
            return False, f"BLP Denied: Clearance ({user_clearance}) too high to {operation} file class ({file_class})."
            
    return True, "Access Granted."
