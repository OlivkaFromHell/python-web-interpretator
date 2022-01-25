import json
import sys
import traceback
from io import StringIO

import config
from celery.exceptions import SoftTimeLimitExceeded
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

TIMEOUT = config.TIMEOUT
results = []
counter = 0
blacklist = {'os', 'sys', 'subprocess', 'builtins', 'shututil', 'open', 'eval', 'exec'}


@celery.task(name='main.run_code', soft_time_limit=TIMEOUT)
def run_code(code: str, input_data: str, number: int):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout = StringIO()
    sys.stderr = stderr = StringIO()

    def input(prompt=''):
        print(prompt, end='')
        return input_data

    try:
        for obj in blacklist:
            if obj in code:
                raise ValueError(f'{obj} is not allowed in this code')
        else:
            exec(code)
    except SoftTimeLimitExceeded:
        print('Time limit exceeded')
    except Exception:
        traceback.print_exc()
        result = stdout.getvalue() + stderr.getvalue()
        return {'result': result, 'color': 'red', 'number': number}
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return {'result': stdout.getvalue(), 'color': 'black', 'number': number}


@flask_app.route('/', methods=['GET', 'POST'])
def proceed():
    global results
    if request.method == 'POST':
        global counter
        data = json.loads(request.data.decode('utf-8'))
        if data['type'] == 'clear':
            results = []
            counter = 0
        else:
            counter += 1
            res = run_code.delay(code=data['code'], input_data=data['input'], number=counter)
            results.append(res.get())
            results.sort(key=lambda x: x['number'])

    return render_template('index.html', data=results)


if __name__ == '__main__':
    flask_app.run(debug=True, port=config.PORT, host=config.HOST)
