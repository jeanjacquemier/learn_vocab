from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List
import random
import unicodedata
import json
import os

from .parser import parse_file

app = FastAPI(title="French -> English Quiz")

BASE_DIR = os.path.dirname(__file__)
PKG_DIR = BASE_DIR
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')

scores_path = os.path.join(DATA_DIR, 'scores.json')
pool_path = os.path.join(DATA_DIR, 'pool.json')
text_path = os.path.join(DATA_DIR, 'fra.txt')


templates = Jinja2Templates(directory=os.path.join(PKG_DIR, 'templates'))


def load_scores(path: str) -> Dict[str, int]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_scores(path: str, scores: Dict[str, int]) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(scores, fh, ensure_ascii=False, indent=2)


def load_pool(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return []


def save_pool(path: str, pool: list) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=2)


def normalize(s: str, case_sensitive: bool = False) -> str:
    s = (s or '').strip()
    # remove trailing punctuation characters
    while s and unicodedata.category(s[-1]).startswith('P'):
        s = s[:-1]
    if not case_sensitive:
        s = s.casefold()
    return s

def load_translations(path: str, limit: int = 100) -> Dict[str, List[str]]:
    mapping = parse_file(path)
    filtered = {}
    # ensure all values are lists
    for k, v in mapping.items():
        if len(k.split()) <= limit:
            filtered[k] = v
    return filtered

@app.on_event('startup')
def startup_event():
    # load mapping and ensure data directory exists
    app.state.mapping = load_translations(text_path, 3)
    app.state.keys = list(app.state.mapping.keys())
    app.state.scores = load_scores(scores_path)
    for k in app.state.keys:
        app.state.scores.setdefault(k, 0)
    app.state.pool = load_pool(pool_path)
    # validate pool
    app.state.pool = [k for k in app.state.pool if k in app.state.keys and app.state.scores.get(k, 0) < 5]
    candidates = [k for k in app.state.keys if k not in app.state.pool and app.state.scores.get(k, 0) < 5]
    # choose random candidates to fill the pool rather than always the lowest-scored
    needed = min(10, len(app.state.keys)) - len(app.state.pool)
    if candidates and needed > 0:
        pick = random.sample(candidates, k=min(needed, len(candidates)))
        app.state.pool.extend(pick)
    if not app.state.pool:
        # initialize with a random order of keys instead of the original order
        app.state.pool = random.sample(app.state.keys, k=len(app.state.keys)) if app.state.keys else []
    save_pool(pool_path, app.state.pool)
    save_scores(scores_path, app.state.scores)


@app.get('/', response_class=HTMLResponse)
def index(request: Request, pool_size: int = 10):
    # construct a view of the pool limited to pool_size
    pool = list(app.state.pool)
    pool_view = list(pool[:pool_size]) if pool_size else list(pool)
    if pool_size and len(pool_view) < pool_size:
        # fill with random candidates (score < 5)
        candidates = [k for k in app.state.keys if k not in pool_view and app.state.scores.get(k, 0) < 5]
        if candidates:
            needed = min(pool_size - len(pool_view), len(candidates))
            pool_view.extend(random.sample(candidates, k=needed))

    fra = random.choice(pool_view) if pool_view else (random.choice(app.state.keys) if app.state.keys else None)
    tmpl = templates.env.get_template('index.html')
    content = tmpl.render({
        'request': request,
        'fra': fra,
        'score': app.state.scores.get(fra, 0),
        'pool': pool_view,
        'scores': app.state.scores,
        'pool_size': pool_size,
    })
    return HTMLResponse(content)


@app.post('/answer', response_class=HTMLResponse)
def answer(request: Request, fra: str = Form(...), user_answer: str = Form(...), pool_size: int = Form(10)):
    mapping: Dict[str, List[str]] = app.state.mapping
    answers = mapping.get(fra, [])
    u_norm = normalize(user_answer)
    answers_norm = [normalize(a) for a in answers]
    correct = u_norm in answers_norm
    # update scores
    if correct:
        app.state.scores[fra] = int(app.state.scores.get(fra, 0)) + 1
        # if score >= 5 remove from pool and try to add replacement
        if app.state.scores[fra] >= 5:
            try:
                app.state.pool.remove(fra)
                remaining = [k for k in app.state.keys if k not in app.state.pool and k != fra]
                # pick a random replacement when possible
                if remaining:
                    app.state.pool.append(random.choice(remaining))
            except ValueError:
                pass
    else:
        app.state.scores[fra] = 0
    # persist state
    save_scores(scores_path, app.state.scores)
    save_pool(pool_path, app.state.pool)
    # choose next phrase to show (avoid repeating same phrase when possible)
    pool = app.state.pool
    if pool:
        if not correct:
            next_fra = fra
        elif len(pool) > 1:
            next_candidates = [k for k in pool if k != fra]
            next_fra = random.choice(next_candidates)
        else:
            next_fra = pool[0]
    else:
        next_fra = fra

    # build pool view for rendering (respect pool_size from form)
    pool = list(app.state.pool)
    pool_view = list(pool[:pool_size]) if pool_size else list(pool)
    if pool_size and len(pool_view) < pool_size:
        candidates = [k for k in app.state.keys if k not in pool_view and app.state.scores.get(k, 0) < 5]
        if candidates:
            needed = min(pool_size - len(pool_view), len(candidates))
            pool_view.extend(random.sample(candidates, k=needed))

    tmpl = templates.env.get_template('index.html')
    content = tmpl.render({
        'request': request,
        # show new phrase
        'fra': next_fra,
        'score': app.state.scores.get(next_fra, 0),
        # still show feedback about the previous answer
        'correct': correct,
        'expected': answers,
        'user_answer': user_answer,
        'pool': pool_view,
        'scores': app.state.scores,
        'pool_size': pool_size,
    })
    return HTMLResponse(content)

#*** End Patch