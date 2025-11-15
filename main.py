import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document, get_documents, db
from schemas import CTU, Sponsor

app = FastAPI(title="Clinical Trials Brokerage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Clinical Trials Brokerage Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# -------------------- CTU Endpoints --------------------
@app.post("/api/ctus", response_model=dict)
def create_ctu(ctu: CTU):
    try:
        inserted_id = create_document("ctu", ctu)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ctus", response_model=List[dict])
def list_ctus(
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    expertise: Optional[str] = Query(None, description="Filter by expertise tag"),
    sort_by: Optional[str] = Query(None, description="Sort field, e.g., recruitment_velocity, data_quality_pdpp"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    limit: int = Query(50, ge=1, le=200)
):
    try:
        filter_dict = {}
        if city: filter_dict["city"] = city
        if state: filter_dict["state"] = state
        if country: filter_dict["country"] = country
        if expertise: filter_dict["trial_expertise"] = {"$in": [expertise]}

        docs = get_documents("ctu", filter_dict, None)
        # Sort client-side for simplicity
        if sort_by:
            docs.sort(key=lambda d: d.get(sort_by) or 0, reverse=(order=="desc"))
        return docs[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- Sponsor Endpoints --------------------
@app.post("/api/sponsors", response_model=dict)
def create_sponsor(sponsor: Sponsor):
    try:
        inserted_id = create_document("sponsor", sponsor)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sponsors", response_model=List[dict])
def list_sponsors(
    expertise: Optional[str] = Query(None, description="Filter by sponsor expertise tag"),
    sort_by: Optional[str] = Query(None, description="Sort field, e.g., ecrf_edc_usability, eligibility_rigidity_pct"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    limit: int = Query(50, ge=1, le=200)
):
    try:
        filter_dict = {}
        if expertise: filter_dict["trial_expertise"] = {"$in": [expertise]}

        docs = get_documents("sponsor", filter_dict, None)
        if sort_by:
            docs.sort(key=lambda d: d.get(sort_by) or 0, reverse=(order=="desc"))
        return docs[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- Schema Exposure for tooling --------------------
class SchemaResponse(BaseModel):
    schemas: List[str]

@app.get("/schema", response_model=SchemaResponse)
def get_schema():
    # Flames database viewer reads this to know available collections
    return SchemaResponse(schemas=["ctu", "sponsor"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
