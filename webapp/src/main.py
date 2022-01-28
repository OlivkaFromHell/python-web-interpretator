import json
import sys
import traceback
from io import StringIO
from itertools import count
from typing import Dict, Union

import config
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from flask import Flask, render_template, request
from flask_cors import CORS

flask_app = Flask(__name__)


CORS(flask_app)
celery = Celery('tasks', broker='redis://localhost:6379', backend='redis://localhost:6379')

TIMEOUT = config.TIMEOUT
results = []
counter = count(1)
blacklist = {'os', 'sys', 'subprocess', 'builtins', 'shututil', 'open', 'eval', 'exec', 'flask', 'redis', 'celery'}


@celery.task(name='main.run_code', soft_time_limit=TIMEOUT)
def run_code(code: str, input_data: str, number: int) -> Dict[str, Union[str, int]]:
    # change default stdout and stderr to object
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout = StringIO()
    sys.stderr = stderr = StringIO()

    # redeclare input method
    def input(prompt=''):
        print(prompt, end='')
        return input_data

    try:
        for obj in blacklist:
            if obj in code:
                raise ValueError(f'{obj} is not allowed in this code')
        else:
            # globals and locals should be blank dict
            exec(code, {}, {'input': input})
    except SoftTimeLimitExceeded:
        print('Time limit exceeded')
    except Exception:
        traceback.print_exc()
        err = stderr.getvalue().split('\n')
        del err[1:3]  # del lines with source code
        result = stdout.getvalue() + '\n'.join(err)
        return {'result': result, 'color': 'red', 'number': number}
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return {'result': stdout.getvalue(), 'color': 'black', 'number': number}


@flask_app.route('/', methods=['GET', 'POST'])
def proceed():
    global results
    if request.method == 'POST':
        global counter, TIMEOUT
        data = json.loads(request.data.decode('utf-8'))
        if data['type'] == 'clear':
            results = []
            counter = count(1)
        elif data['type'] == 'code':
            if data['timeout']:
                timeout = data['timeout']
            else:
                timeout = TIMEOUT

            res = run_code.apply_async((data['code'], data['input'], next(counter)),
                                       soft_time_limit=timeout)
            results.append(res.get())
            results.sort(key=lambda x: x['number'])

    return render_template('index.html', data=results)


if __name__ == '__main__':
    flask_app.run(debug=True, port=config.PORT, host=config.HOST)
