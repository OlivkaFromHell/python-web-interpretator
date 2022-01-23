import json
import sys
import traceback
from copy import deepcopy
from io import StringIO

from flask import Flask, render_template, request
from flask_cors import CORS

from tasks import make_celery

flask_app = Flask(__name__)
flask_app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

CORS(flask_app)
celery = make_celery(flask_app)


@celery.task(name='main.run_code')
def run_code(code: str, input_data: str):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout = StringIO()
    sys.stderr = stderr = StringIO()

    _open = deepcopy(open)
    _exec = deepcopy(exec)
    _eval = deepcopy(eval)
    del __builtins__.open
    del __builtins__.exec
    del __builtins__.eval

    old_input = __builtins__.input

    def input(prompt=''):
        print(prompt, end='')
        return input_data

    try:
        _exec(code)
    except Exception:
        traceback.print_exc()
        result = stdout.getvalue() + stderr.getvalue()
        return {'result': result, 'color': 'red'}
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        __builtins__.input = old_input
        __builtins__.open = _open
        __builtins__.exec = _exec
        __builtins__.eval = _eval

    return {'result': stdout.getvalue(), 'color': 'black'}


@flask_app.route('/',  methods=['GET', 'POST'])
def proceed():
    if request.method == 'POST':
        data = json.loads(request.data.decode('utf-8'))
        return run_code(code=data['code'], input_data=data['input'])

    return render_template('index.html')


if __name__ == '__main__':
    flask_app.run(debug=True, port=5000, host="0.0.0.0")
