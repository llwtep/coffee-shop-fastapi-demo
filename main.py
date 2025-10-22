from fastapi import FastAPI
from app.api.router import main_router

app = FastAPI(title="Coffee Shop API — User Management",
              description="""
              This API provides full user management:
              - **Signup / Login / Verification**
              - **JWT authentication**
              - **Role-based access (User/Admin)**
              - **User profile management**
                  """,
              version="1.0.0",
              contact={
                  "name": "Azamjon",
                  "url": "https://github.com/llwtep",
              }
              )

app.include_router(router=main_router)


@app.get('/')
async def get_health():
    return {"OK": 200}
