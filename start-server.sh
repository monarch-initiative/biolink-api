pyvenv venv
source venv/bin/activate
pip install setuptools --upgrade #to avoid bdist_wheel errors
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8888 wsgi:app
