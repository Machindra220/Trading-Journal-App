from dotenv import load_dotenv
load_dotenv()

import os
print("🔍 SQLALCHEMY_DATABASE_URI:", os.getenv("SQLALCHEMY_DATABASE_URI"))

from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
