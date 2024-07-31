from fastapi import APIRouter, Request, Depends
from auth.users import User, current_active_user
from bson import ObjectId, json_util
import json

from datetime import datetime

def get_week_router(app):

    router = APIRouter()
  
    @router.get("/currentweeks", response_description="Get current weeks for all sports", response_model_by_alias=False)
    async def get_current_weeks(request: Request, user: User = Depends(current_active_user)):
        print(current_active_user)
        print(request)
        print(user)
        current_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        current_weeks = {}
        cursor = request.app.db["Weeks"].find({"start_date": {"$lt": current_date}, "end_date": {"$gt": current_date}})
        for item in await cursor.to_list(length=100):
            item = json.loads(json_util.dumps(item))
            item_season = f"{item["sport"].lower()}_season"
            current_weeks[item_season] = item["season"]
            item_week = f"{item["sport"].lower()}_week"
            current_weeks[item_week] = item["week_number"]

        return current_weeks
    
    return router
