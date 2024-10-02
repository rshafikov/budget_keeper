import uvicorn
from fastapi import FastAPI

from api.endpoints import main_router
from api.exceptions.exc_handlers import add_exc_handlers

app = FastAPI(root_path='/api/v1')

app.include_router(main_router)

add_exc_handlers(app)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000)
