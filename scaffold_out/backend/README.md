# Asset Maintenance API

This project is a CRUD API for managing maintenance records of assets (plant equipment).

## Technologies Used
- FastAPI
- Pydantic v2
- Uvicorn
- pytest

## Setup Instructions
1. Clone the repository.
2. Install the required packages:
   ```bash
   pip install fastapi pydantic uvicorn pytest httpx pandas
   ```
3. Place the `maintenance_assets.csv` file in the `backend` directory.
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
5. Access the API at `http://127.0.0.1:8000`.

## API Endpoints
- `POST /assets`: Create a new asset.
- `GET /assets`: List all assets with optional filters.
- `GET /assets/{asset_id}`: Retrieve a specific asset by ID.
- `PUT /assets/{asset_id}`: Update an existing asset.
- `DELETE /assets/{asset_id}`: Soft delete an asset.

## Running Tests
To run the tests, execute:
```bash
pytest -q
```