import re

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from auth.auth_bearer import get_user_id_from_token
# from model.modules import Modules
# from model.rights import Rights
#
# mod = Modules()


def get_action_module_name(url):
    pattern = r"/api/(\w+)/(\w+)"
    match = re.search(pattern, url)
    if match:
        action = match.group(1)
        module_name = match.group(2)
        return action, module_name
    else:
        print("No match found.")


# Function to check user rights
def check_user_rights(api_url: str, db: Session, user_id: int = Depends(get_user_id_from_token)):
    action, modules_name = get_action_module_name(api_url)

    module_id: int = mod.get_modules_id(module_name=modules_name, db=db)

    user_rights = db.query(Rights).filter(Rights.user_id == user_id, Rights.module_id == module_id).first()

    if not user_rights:
        raise HTTPException(status_code=400, detail="You don't have valid rights to perform this action")

    # Check the specific action rights based on the action parameter
    if action == "insert":
        if user_rights.can_create != 1:
            raise HTTPException(status_code=400, detail="You don't have valid rights to perform this action")
    elif action == "update":
        if user_rights.can_update != 1:
            raise HTTPException(status_code=400, detail="You don't have valid rights to perform this action")
    elif action == "delete":
        if user_rights.can_delete != 1:
            raise HTTPException(status_code=400, detail="You don't have valid rights to perform this action")
    elif action == "read":
        if user_rights.can_read != 1:
            raise HTTPException(status_code=400, detail="You don't have valid rights to perform this action")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
