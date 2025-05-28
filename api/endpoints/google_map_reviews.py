from fastapi import FastAPI, HTTPException, APIRouter
import httpx
import os
from typing import List, Optional
from pydantic import BaseModel

class Review(BaseModel):
    name: Optional[str] = "Unknown"
    text: Optional[str] = ""
    stars: Optional[float] = 0.0  
    reviewsCount: Optional[float] = 0.0 
    
router = APIRouter()

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "apify_api_0f3ijHG3nSUNDpBYbAec6BrCAA1SBA3siQFr")
DATASET_ID = os.getenv("DATASET_ID", "iyTVHiSAvash8upSR")

@router.get("/reviews/", response_model=List[Review])
async def get_google_map_reviews():
    url = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?token={APIFY_TOKEN}&format=json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            try:
                data = response.json()
                reviews = []
                for item in data:
                    stars = item.get("stars", 0.0)  

                    reviews.append(Review(
                        name=item.get("name", "Unknown"),
                        text=item.get("text", ""),
                        time=item.get("time", ""),
                        stars=stars,  
                        reviewsCount=item.get("reviewsCount", 0.0)
                    ))
                return reviews
            except (KeyError, ValueError) as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse data from Apify: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data from Apify")
