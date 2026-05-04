import sys
import os

# root directory 경로를 sys.path에 추가하여 app.py 및 data.py를 임포트할 수 있도록 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as application

# Vercel needs 'app' variable by default, but aliasing 'application' also works well
app = application
