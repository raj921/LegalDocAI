import uvicorn
import os

if __name__ == "__main__":
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Please create one based on .env.example")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
