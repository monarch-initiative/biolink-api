# http://gunicorn-docs.readthedocs.io/en/latest/design.html
# Generally we recommend (2 x $num_cores) + 1 as the number of workers to start off with
# http://stackoverflow.com/questions/35837786/how-to-run-flask-with-gunicorn-in-multithreaded-mode
pyvenv venv
source venv/bin/activate
export PYTHONPATH=.:$PYTHONPATH
pip install setuptools --upgrade #to avoid bdist_wheel errors
pip install -r requirements.txt
gunicorn -k gevent --worker-connections 5 --bind 0.0.0.0:8888 wsgi:app
