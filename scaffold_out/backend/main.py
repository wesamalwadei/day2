from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import pandas as pd

app = FastAPI()

# Load data from CSV
assets_df = pd.read_csv('backend/maintenance_assets.csv')

class Asset(BaseModel):
    asset_id: str = Field(..., pattern='^[A-Z]{3}-\d{4}$')
    asset_type: str
    unit: str
    location: str
    install_year: int
    last_inspection: str
    operating_hours: int
    status: str
    criticality: str = Field(..., pattern='^(High|Medium|Low)$')
    notes: Optional[str] = None

    @field_validator('notes')
    def validate_notes(cls, v):
        return v if v != '' else None

assets = assets_df.to_dict(orient='records')

@app.post('/assets', response_model=Asset)
async def create_asset(asset: Asset):
    assets.append(asset.dict())
    return asset

@app.get('/assets', response_model=List[Asset])
async def list_assets(status: Optional[str] = Query(None), unit: Optional[str] = Query(None), criticality: Optional[str] = Query(None)):
    filtered_assets = assets
    if status:
        filtered_assets = [a for a in filtered_assets if a['status'] == status]
    if unit:
        filtered_assets = [a for a in filtered_assets if a['unit'] == unit]
    if criticality:
        filtered_assets = [a for a in filtered_assets if a['criticality'] == criticality]
    return filtered_assets

@app.get('/assets/{asset_id}', response_model=Asset)
async def read_asset(asset_id: str):
    asset = next((a for a in assets if a['asset_id'] == asset_id), None)
    if asset is None:
        raise HTTPException(status_code=404, detail='Asset not found')
    return asset

@app.put('/assets/{asset_id}', response_model=Asset)
async def update_asset(asset_id: str, asset: Asset):
    existing_asset = next((a for a in assets if a['asset_id'] == asset_id), None)
    if existing_asset is None:
        raise HTTPException(status_code=404, detail='Asset not found')
    asset_dict = asset.dict(exclude={'asset_id'})
    existing_asset.update(asset_dict)
    return existing_asset

@app.delete('/assets/{asset_id}', response_model=dict)
async def delete_asset(asset_id: str):
    global assets
    assets = [a for a in assets if a['asset_id'] != asset_id]
    return {'message': 'Asset soft deleted'}

@app.get('/', response_class=HTMLResponse)
async def read_root():
    return '<h1>Asset Maintenance API</h1>'

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
