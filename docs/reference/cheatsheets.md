---
title: Cheat Sheets
description: Quick-reference cards for every major Python topic — core, data, web, concurrency, testing, security, DevOps and more
---

# 📋 Cheat Sheets

Quick-reference cards — print them, bookmark them, keep them open while coding.

!!! tip "How to use these"
    Each card is a memory jog, not a tutorial. Follow the link in a section heading to the full lesson when you need depth.

---

## [Core Python](../core/index.md){ .pm-cheat-link }

### Strings

| Task | Snippet |
|---|---|
| Format | `f"{name=}"`, `f"{x:.2f}"`, `f"{n:,}"` |
| Split / join | `s.split(",")`, `",".join(items)` |
| Trim / case | `.strip()`, `.lower()`, `.upper()`, `.title()` |
| Search | `in`, `.find()`, `.startswith()`, `.endswith()` |
| Replace / slice | `.replace(a, b)`, `s[::-1]`, `s[1:4]` |

### Lists

| Task | Snippet |
|---|---|
| Add / remove | `.append()`, `.extend()`, `.insert(i, x)`, `.pop()`, `.remove(x)` |
| Order | `.sort(key=..., reverse=True)`, `sorted(xs)`, `.reverse()` |
| Slice | `xs[a:b:c]`, `xs[::-1]`, `xs[:]` (copy) |
| Build | `[f(x) for x in xs if cond]` |
| Aggregate | `sum`, `min`, `max`, `len`, `any`, `all` |

### Dicts

| Task | Snippet |
|---|---|
| Access | `d["k"]`, `d.get("k", default)`, `d.setdefault(k, v)` |
| Iterate | `.keys()`, `.values()`, `.items()` |
| Merge | `d1 \| d2`, `{**d1, **d2}`, `d.update(d2)` |
| Build | `{k: v for k, v in pairs}` |
| Count | `collections.Counter(xs)` |

### Sets

| Op | Snippet |
|---|---|
| Union / intersect | `a \| b`, `a & b` |
| Difference / symmetric | `a - b`, `a ^ b` |
| Mutate | `.add(x)`, `.discard(x)`, `.update(it)` |
| Test | `x in s`, `a <= b` (subset) |

### Files

| Task | Snippet |
|---|---|
| Read | `with open(p) as f: f.read()` / `f.readlines()` |
| Write | `with open(p, "w") as f: f.write(s)` |
| Append | `open(p, "a")` |
| Lines | `for line in f:` |
| Paths | `from pathlib import Path`, `Path(p).read_text()` |

### Comprehensions

| Kind | Snippet |
|---|---|
| List | `[x*2 for x in xs]` |
| Dict | `{k: v for k, v in items}` |
| Set | `{x for x in xs}` |
| Generator | `(x for x in xs)` |
| Nested | `[y for row in grid for y in row]` |

### Functions

| Feature | Snippet |
|---|---|
| Defaults | `def f(a, b=2):` |
| Var args | `def f(*args, **kwargs):` |
| Keyword-only | `def f(*, timeout):` |
| Unpack call | `f(*lst)`, `f(**dct)` |
| Lambda | `lambda x: x + 1` |

### OOP

| Feature | Snippet |
|---|---|
| Define | `class C:` / `def __init__(self):` |
| Inherit | `class D(C): super().__init__()` |
| Dunder | `__repr__`, `__eq__`, `__len__`, `__call__` |
| Property | `@property` / `@x.setter` |
| Class/static | `@classmethod`, `@staticmethod` |

### Errors

| Task | Snippet |
|---|---|
| Catch | `try: ... except ValueError as e:` |
| Multiple | `except (A, B):` |
| Cleanup | `finally:` / `else:` |
| Raise | `raise ValueError("msg")`, `raise X from e` |
| Custom | `class MyError(Exception): ...` |

### Decorators & Generators

| Pattern | Snippet |
|---|---|
| Decorator | `@deco` / `@wraps(func)` |
| With args | `@repeat(3)` (decorator factory) |
| Generator | `yield x`, `yield from it` |
| Lazy pipeline | `(line for line in f)` |

### Context Managers

| Task | Snippet |
|---|---|
| Use | `with open(p) as f:` |
| Class-based | `__enter__` / `__exit__` |
| Function | `@contextmanager` + `yield` |
| Multiple | `with a() as x, b() as y:` |

### Typing & Dataclasses

| Feature | Snippet |
|---|---|
| Hints | `x: int`, `-> str`, `list[int]`, `dict[str, int]` |
| Optional / union | `str \| None`, `Optional[str]` |
| Aliases | `Vec = list[float]` |
| Dataclass | `@dataclass` / `field(default_factory=list)` |
| Check | `mypy .` |

---

## [Standard Library & Tooling](../core/competent/index.md){ .pm-cheat-link }

### Regex (`re`)

| Task | Snippet |
|---|---|
| Match / search | `re.match(p, s)`, `re.search(p, s)` |
| Find all | `re.findall(p, s)`, `re.finditer(p, s)` |
| Replace | `re.sub(p, repl, s)` |
| Groups | `(...)`, `m.group(1)`, `(?P<name>...)` |
| Common | `\d \w \s`, `^ $`, `* + ?`, `{m,n}` |

### Useful stdlib modules

| Module | Use for |
|---|---|
| `collections` | `defaultdict`, `Counter`, `deque`, `namedtuple` |
| `itertools` | `chain`, `groupby`, `product`, `combinations` |
| `functools` | `reduce`, `lru_cache`, `partial`, `wraps` |
| `datetime` | `datetime.now()`, `timedelta`, `strftime` |
| `json` | `json.dumps()`, `json.loads()` |
| `os` / `sys` | `os.environ`, `sys.argv`, `os.path` |

### CLI tools

| Tool | Snippet |
|---|---|
| argparse | `parser.add_argument("--x")` / `parser.parse_args()` |
| click | `@click.command()` / `@click.option()` |
| typer | `app = typer.Typer()` / `@app.command()` |

### Packaging

| Task | Snippet |
|---|---|
| Project | `pyproject.toml` `[project]` table |
| Install deps | `pip install -e .`, `uv pip install` |
| Virtual env | `python -m venv .venv` |
| Build | `python -m build` |
| Publish | `twine upload dist/*` |

---

## [Concurrency & Performance](../systems/index.md){ .pm-cheat-link }

### Threading & Multiprocessing

| Task | Snippet |
|---|---|
| Thread | `Thread(target=f).start()` |
| Pool | `ThreadPoolExecutor()`, `ProcessPoolExecutor()` |
| Map | `executor.map(f, items)` |
| Lock | `with lock:` |
| Process | `Process(target=f).start()` |

### Asyncio

| Task | Snippet |
|---|---|
| Define | `async def f(): await g()` |
| Run | `asyncio.run(main())` |
| Gather | `await asyncio.gather(*tasks)` |
| Task | `asyncio.create_task(coro)` |
| Timeout | `async with asyncio.timeout(5):` |

### Performance

| Task | Snippet |
|---|---|
| Time | `timeit`, `time.perf_counter()` |
| Profile | `cProfile`, `python -m cProfile -s cumtime` |
| Memoize | `@lru_cache(maxsize=None)` |
| Vectorize | NumPy ops over Python loops |
| Speed up | Cython, Numba `@njit`, PyPy |

---

## [Data & AI](../data/index.md){ .pm-cheat-link }

### NumPy

| Task | Snippet |
|---|---|
| Create | `np.array`, `np.zeros`, `np.ones`, `np.arange`, `np.linspace` |
| Shape | `.reshape()`, `.T`, `.flatten()`, `np.concatenate` |
| Math | `np.sum`, `np.mean`, `np.dot`, `a @ b` |
| Index | `a[a > 0]`, `a[:, 1]`, boolean masks |

### Pandas

| Task | Snippet |
|---|---|
| Load | `pd.read_csv()`, `pd.read_json()`, `pd.read_sql()` |
| Select | `df["col"]`, `df.loc[]`, `df.iloc[]` |
| Filter | `df[df.x > 0]`, `df.query("x > 0")` |
| Group | `df.groupby("k").agg(...)` |
| Reshape | `.pivot_table()`, `.melt()`, `.merge()` |

### Visualization

| Library | Snippet |
|---|---|
| Matplotlib | `plt.plot()`, `plt.subplots()`, `plt.savefig()` |
| Seaborn | `sns.heatmap()`, `sns.scatterplot()`, `sns.pairplot()` |
| Pandas | `df.plot(kind="bar")` |

### Machine Learning (scikit-learn)

| Step | Snippet |
|---|---|
| Split | `train_test_split(X, y, test_size=0.2)` |
| Fit | `model.fit(X_train, y_train)` |
| Predict | `model.predict(X_test)` |
| Score | `accuracy_score`, `model.score()` |
| Pipeline | `make_pipeline(StandardScaler(), clf)` |

---

## [Web & APIs](../web/index.md){ .pm-cheat-link }

### FastAPI

| Task | Snippet |
|---|---|
| Route | `@app.get("/")`, `@app.post("/items")` |
| Body | `class Item(BaseModel): ...` |
| Params | path `/{id}`, query `q: str = None` |
| Deps | `Depends(get_db)` |
| Run | `uvicorn main:app --reload` |

### Flask

| Task | Snippet |
|---|---|
| Route | `@app.route("/", methods=["GET"])` |
| Request | `request.json`, `request.args` |
| Response | `jsonify(data)`, `return x, 201` |
| Run | `flask run` |

### HTTP clients

| Task | Snippet |
|---|---|
| Requests | `requests.get(url).json()` |
| httpx (async) | `async with httpx.AsyncClient() as c:` |
| Headers | `headers={"Authorization": f"Bearer {t}"}` |

### Web scraping

| Task | Snippet |
|---|---|
| Parse | `BeautifulSoup(html, "html.parser")` |
| Select | `soup.select(".cls")`, `soup.find("a")` |
| Browser | Playwright / Selenium for JS pages |

---

## [Databases](../databases/index.md){ .pm-cheat-link }

### SQL (core)

| Task | Snippet |
|---|---|
| Query | `SELECT ... FROM t WHERE ...` |
| Join | `JOIN b ON a.id = b.a_id` |
| Group | `GROUP BY k HAVING count(*) > 1` |
| Modify | `INSERT`, `UPDATE ... SET`, `DELETE` |

### SQLAlchemy

| Task | Snippet |
|---|---|
| Model | `class User(Base): id = mapped_column(...)` |
| Session | `with Session(engine) as s:` |
| Query | `select(User).where(User.age > 18)` |
| Commit | `s.add(obj)`, `s.commit()` |

### NoSQL / Redis

| Task | Snippet |
|---|---|
| Mongo | `db.coll.find({...})`, `.insert_one()` |
| Redis | `r.set(k, v)`, `r.get(k)`, `r.expire(k, 60)` |

---

## [Networking](../networking/index.md){ .pm-cheat-link }

| Task | Snippet |
|---|---|
| TCP socket | `socket.socket()`, `.bind()`, `.listen()`, `.accept()` |
| WebSockets | `websockets.serve(handler, host, port)` |
| gRPC | `.proto` + `grpc_tools.protoc` codegen |
| GraphQL | `strawberry` / `graphene` schema types |

---

## [Testing](../testing/index.md){ .pm-cheat-link }

### pytest

| Task | Snippet |
|---|---|
| Test | `def test_x(): assert f() == 1` |
| Fixture | `@pytest.fixture` + `yield` |
| Params | `@pytest.mark.parametrize("x,y", [...])` |
| Expect error | `with pytest.raises(ValueError):` |
| Run | `pytest -q`, `pytest -k name`, `pytest --cov` |

### Mocking & quality

| Task | Snippet |
|---|---|
| Mock | `unittest.mock.patch("mod.func")`, `MagicMock()` |
| Coverage | `pytest --cov=pkg --cov-report=term-missing` |
| Lint / format | `ruff check .`, `black .`, `mypy .` |
| Property-based | `@given(st.integers())` (Hypothesis) |

---

## [Design Patterns](../patterns/index.md){ .pm-cheat-link }

| Pattern | Pythonic form |
|---|---|
| Singleton | module-level object, or `@lru_cache` factory |
| Factory | function returning instances |
| Strategy | pass a function / callable |
| Observer | callbacks, `functools`, event emitter |
| Decorator | `@wraps` wrappers (built in to the language) |
| Context | `with` + `__enter__/__exit__` |

---

## [Algorithms](../algorithms/index.md){ .pm-cheat-link }

| Topic | Key tools |
|---|---|
| Sorting | `sorted(key=...)`, Timsort O(n log n) |
| Searching | `bisect` for sorted lists |
| Recursion | base case + `@lru_cache` for memoization |
| Dynamic programming | tabulation vs memoization |
| Graphs | adjacency dict, BFS (`deque`), DFS (recursion) |
| Big-O | know O(1), O(n), O(n log n), O(n²) |

---

## [Security](../security/index.md){ .pm-cheat-link }

| Task | Snippet / rule |
|---|---|
| Hash passwords | `bcrypt` / `argon2`, never plain or fast hashes |
| Secrets | `secrets.token_urlsafe()`, never `random` |
| Env config | load from env vars, never hardcode |
| SQL injection | always parameterize queries |
| Crypto | `cryptography` (Fernet), avoid rolling your own |
| JWT | `pyjwt` encode/decode with verified signature |

---

## [DevOps & Deployment](../deployment/index.md){ .pm-cheat-link }

### Git

| Task | Snippet |
|---|---|
| Stage / commit | `git add -p`, `git commit -m "..."` |
| Branch | `git switch -c feat`, `git merge`, `git rebase` |
| Sync | `git pull --rebase`, `git push -u origin b` |
| Undo | `git restore f`, `git revert c`, `git reset` |
| Inspect | `git log --oneline`, `git diff`, `git blame` |

### Docker

| Task | Snippet |
|---|---|
| Build | `docker build -t app .` |
| Run | `docker run -p 8000:8000 app` |
| Compose | `docker compose up -d` |
| Inspect | `docker ps`, `docker logs`, `docker exec -it` |

### CI/CD & cloud

| Task | Snippet |
|---|---|
| GitHub Actions | `.github/workflows/*.yml`, `on: [push]` |
| Kubernetes | `kubectl apply -f`, `get pods`, `logs` |
| MkDocs deploy | `mkdocs gh-deploy` |

---

## [Distributed Systems](../distributed/index.md){ .pm-cheat-link }

| Concept | Essence |
|---|---|
| Consensus | Raft / Paxos — agree on a value across nodes |
| CRDTs | conflict-free merge without coordination |
| Caching | TTLs, invalidation, cache-aside pattern |
| Queues | decouple producers/consumers (Celery, RabbitMQ) |
| Tracing | propagate context across services (OpenTelemetry) |
| CAP | consistency vs availability under partition |

---

## [Systems & Research (deep internals)](../research/index.md){ .pm-cheat-link }

| Topic | Key tools |
|---|---|
| Bytecode | `dis.dis(func)`, `compile()`, code objects |
| AST | `ast.parse()`, `ast.NodeTransformer` |
| CPython | ref counting + GC, GIL, `sys.getrefcount` |
| C/Rust ext | `ctypes`, `cffi`, PyO3, Cython |
| Profilers | `cProfile`, `py-spy`, `memory_profiler` |
| JIT | Numba, PyPy, custom LLVM/MLIR lowering |

---

<div class="pm-next">
<strong>✅ Keep going</strong>
<a href="../code-snippets/">Code Snippets</a>
<a href="../glossary/">Glossary</a>
<a href="../tools/">Tools</a>
</div>
