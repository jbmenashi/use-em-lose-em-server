from fastapi import APIRouter, Request, Depends
from auth.users import User, current_active_user
from bson import ObjectId, json_util
import json

from datetime import datetime

def get_week_router(app):

    router = APIRouter()
  
    @router.get("/currentweeks", response_description="Get current weeks for all sports", response_model_by_alias=False)
    async def get_current_weeks(request: Request, user: User = Depends(current_active_user)):
        current_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        print(current_date)
        list_of_current_weeks = []
        cursor = request.app.db["Weeks"].find({"start_date": {"$lt": current_date}, "end_date": {"$gt": current_date}})
        for item in await cursor.to_list(length=100):
            list_of_current_weeks.append(json.loads(json_util.dumps(item)))

        return list_of_current_weeks
    
    return router
