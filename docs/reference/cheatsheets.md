---
title: Cheat Sheets
description: Comprehensive quick-reference cards for every major Python topic — core, stdlib, data, web, concurrency, testing, security, DevOps and more
---

# 📋 Cheat Sheets

Quick-reference cards — print them (`Ctrl+P`), bookmark them, keep them open while coding.

!!! tip "How to use these"
    Each card is a dense memory jog, not a tutorial. Follow the link in a section heading to the full lesson when you need depth.

---

## [Core Python](../core/index.md){ .pm-cheat-link }

### Strings

| Task | Snippet |
|---|---|
| f-string | `f"{name}"`, `f"{x=}"`, `f"{x:.2f}"`, `f"{n:,}"`, `f"{n:>10}"`, `f"{p:.1%}"` |
| Case | `.lower()`, `.upper()`, `.title()`, `.capitalize()`, `.swapcase()`, `.casefold()` |
| Trim | `.strip()`, `.lstrip()`, `.rstrip()`, `.removeprefix(p)`, `.removesuffix(s)` |
| Split / join | `.split(sep)`, `.rsplit()`, `.splitlines()`, `.partition(sep)`, `sep.join(xs)` |
| Search | `in`, `.find()`, `.rfind()`, `.index()`, `.count()`, `.startswith()`, `.endswith()` |
| Test | `.isdigit()`, `.isalpha()`, `.isalnum()`, `.isspace()`, `.isupper()` |
| Transform | `.replace(a, b)`, `.translate(table)`, `.zfill(n)`, `.ljust(n)`, `.rjust(n)`, `.center(n)` |
| Slice | `s[a:b]`, `s[::-1]`, `s[::2]` |
| Encode | `.encode("utf-8")`, `b.decode()`, `ord(c)`, `chr(n)` |

### Numbers & Math

| Task | Snippet |
|---|---|
| Convert | `int(x)`, `float(x)`, `round(x, n)`, `abs(x)`, `complex(a, b)` |
| Divmod | `a // b`, `a % b`, `divmod(a, b)`, `pow(a, b, mod)` |
| Bases | `bin(n)`, `oct(n)`, `hex(n)`, `int("ff", 16)` |
| Math | `math.sqrt`, `math.floor/ceil`, `math.gcd`, `math.isclose`, `math.inf`, `math.pi` |
| Random | `random.random()`, `random.randint(a, b)`, `random.choice(xs)`, `random.shuffle(xs)`, `random.sample(xs, k)` |
| Decimal | `from decimal import Decimal`, `Decimal("0.1")`, `Fraction(1, 3)` |

### Lists

| Task | Snippet |
|---|---|
| Add | `.append(x)`, `.extend(it)`, `.insert(i, x)`, `xs + ys`, `xs * n` |
| Remove | `.pop()`, `.pop(i)`, `.remove(x)`, `.clear()`, `del xs[i]` |
| Order | `.sort()`, `.sort(key=..., reverse=True)`, `sorted(xs)`, `.reverse()`, `reversed(xs)` |
| Search | `x in xs`, `.index(x)`, `.count(x)` |
| Slice | `xs[a:b:c]`, `xs[::-1]`, `xs[:]` (copy), `xs[a:b] = [...]` |
| Build | `[f(x) for x in xs if cond]`, `[x for row in grid for x in row]` |
| Aggregate | `sum`, `min`, `max`, `len`, `any`, `all`, `min(xs, key=...)` |
| Enumerate / zip | `enumerate(xs)`, `zip(a, b)`, `zip(*rows)` (transpose) |

### Dicts

| Task | Snippet |
|---|---|
| Access | `d["k"]`, `d.get("k", default)`, `d.setdefault(k, v)`, `d \| {k: v}` |
| Mutate | `d[k] = v`, `del d[k]`, `d.pop(k, default)`, `d.update(d2)`, `d.clear()` |
| Iterate | `for k in d`, `.keys()`, `.values()`, `.items()` |
| Merge | `d1 \| d2`, `{**d1, **d2}` |
| Build | `{k: v for k, v in pairs}`, `dict(zip(keys, vals))`, `dict.fromkeys(ks, 0)` |
| Count / group | `collections.Counter(xs)`, `collections.defaultdict(list)` |
| Sort | `sorted(d.items(), key=lambda kv: kv[1])` |

### Sets & Tuples

| Task | Snippet |
|---|---|
| Set ops | `a \| b`, `a & b`, `a - b`, `a ^ b` |
| Set test | `x in s`, `a <= b` (subset), `a >= b` (superset), `a.isdisjoint(b)` |
| Set mutate | `.add(x)`, `.discard(x)`, `.remove(x)`, `.update(it)`, `frozenset(xs)` |
| Tuple | `t = (1, 2)`, `a, b = t`, `a, *rest = t`, `namedtuple("P", "x y")` |

### Files & Paths

| Task | Snippet |
|---|---|
| Read | `with open(p) as f: f.read()` / `f.readlines()` / `for line in f:` |
| Write | `open(p, "w")`, `open(p, "a")`, `f.write(s)`, `f.writelines(xs)` |
| Binary | `open(p, "rb")`, `open(p, "wb")` |
| Pathlib | `Path(p).read_text()`, `.write_text()`, `.exists()`, `.glob("*.py")`, `.mkdir(parents=True)` |
| Path parts | `p.name`, `p.stem`, `p.suffix`, `p.parent`, `p / "sub"` |
| Temp / shutil | `tempfile.NamedTemporaryFile()`, `shutil.copy()`, `shutil.rmtree()` |

### Comprehensions & Iteration

| Kind | Snippet |
|---|---|
| List / set / dict | `[x for x in xs]`, `{x for x in xs}`, `{k: v for k, v in it}` |
| Generator | `(x for x in xs)`, `sum(x*x for x in xs)` |
| Conditional | `[x if c else y for x in xs]`, `[x for x in xs if c]` |
| itertools | `chain`, `cycle`, `repeat`, `count`, `islice`, `takewhile`, `dropwhile` |
| itertools combos | `product`, `permutations`, `combinations`, `groupby`, `accumulate` |

### Functions

| Feature | Snippet |
|---|---|
| Defaults | `def f(a, b=2):` |
| Var args | `def f(*args, **kwargs):` |
| Keyword-only | `def f(*, timeout):` |
| Positional-only | `def f(a, b, /):` |
| Unpack call | `f(*lst)`, `f(**dct)` |
| Lambda | `lambda x: x + 1` |
| Annotate | `def f(x: int) -> str:` |
| Partial | `functools.partial(f, arg)` |

### OOP

| Feature | Snippet |
|---|---|
| Define | `class C:` / `def __init__(self):` |
| Inherit | `class D(C): super().__init__()` |
| Dunder | `__repr__`, `__str__`, `__eq__`, `__hash__`, `__len__`, `__call__`, `__iter__` |
| Compare | `__lt__`, `__gt__`, `@functools.total_ordering` |
| Property | `@property` / `@x.setter` / `@x.deleter` |
| Class/static | `@classmethod`, `@staticmethod` |
| Slots | `__slots__ = ("x", "y")` |
| Abstract | `from abc import ABC, abstractmethod` |

### Errors & Debugging

| Task | Snippet |
|---|---|
| Catch | `try: ... except ValueError as e:` |
| Multiple | `except (A, B):`, chained `except A: ... except B:` |
| Cleanup | `finally:` / `else:` |
| Raise | `raise ValueError("msg")`, `raise X from e` |
| Custom | `class MyError(Exception): ...` |
| Groups (3.11+) | `except* TypeError:` |
| Debug | `breakpoint()`, `import pdb; pdb.set_trace()`, `traceback.print_exc()` |
| Warn / assert | `warnings.warn(...)`, `assert cond, "msg"` |

### Decorators & Generators

| Pattern | Snippet |
|---|---|
| Decorator | `@deco` / `@wraps(func)` |
| With args | `@repeat(3)` (decorator factory) |
| Common | `@lru_cache`, `@cached_property`, `@dataclass`, `@contextmanager` |
| Generator | `yield x`, `yield from it`, `next(gen)`, `gen.send(v)` |
| Lazy pipeline | `(line.strip() for line in f)` |

### Context Managers

| Task | Snippet |
|---|---|
| Use | `with open(p) as f:` |
| Multiple | `with a() as x, b() as y:` |
| Class-based | `__enter__` / `__exit__` |
| Function | `@contextmanager` + `yield` |
| Suppress / redirect | `with suppress(FileNotFoundError):`, `redirect_stdout(buf)` |
| Exit stack | `with ExitStack() as stack:` |

### Typing & Dataclasses

| Feature | Snippet |
|---|---|
| Basic | `x: int`, `-> str`, `list[int]`, `dict[str, int]`, `tuple[int, ...]` |
| Optional / union | `str \| None`, `Optional[str]`, `int \| str` |
| Callable / any | `Callable[[int], str]`, `Any`, `TypeAlias` |
| Generics | `TypeVar("T")`, `Generic[T]`, `Sequence[T]` |
| Special | `Literal["a", "b"]`, `Final`, `Protocol`, `TypedDict`, `NewType` |
| Dataclass | `@dataclass(frozen=True, slots=True)`, `field(default_factory=list)` |
| Check | `mypy .`, `pyright` |

---

## [Standard Library & Tooling](../core/competent/index.md){ .pm-cheat-link }

### Regex (`re`)

| Task | Snippet |
|---|---|
| Match / search | `re.match(p, s)`, `re.search(p, s)`, `re.fullmatch(p, s)` |
| Find / split | `re.findall(p, s)`, `re.finditer(p, s)`, `re.split(p, s)` |
| Replace | `re.sub(p, repl, s)`, `re.subn(p, repl, s)` |
| Compile | `rx = re.compile(p)`, `rx.search(s)` |
| Groups | `(...)`, `m.group(1)`, `m.groups()`, `(?P<name>...)`, `m["name"]` |
| Classes | `\d \w \s \b`, `[a-z]`, `[^x]`, `.` |
| Quantifiers | `* + ?`, `{m,n}`, `*?` (lazy), `^ $` |
| Flags | `re.I`, `re.M`, `re.S`, `re.X` |

### Dates & Times

| Task | Snippet |
|---|---|
| Now | `datetime.now()`, `datetime.now(timezone.utc)`, `date.today()` |
| Build | `datetime(2026, 1, 1)`, `timedelta(days=7)` |
| Format | `.strftime("%Y-%m-%d")`, `datetime.strptime(s, fmt)`, `.isoformat()` |
| Math | `dt + timedelta(hours=3)`, `(a - b).total_seconds()` |
| Zoneinfo | `from zoneinfo import ZoneInfo`, `dt.astimezone(ZoneInfo("UTC"))` |

### Collections & functools

| Tool | Use |
|---|---|
| `defaultdict` | auto-default values: `defaultdict(list)` |
| `Counter` | counting + `.most_common(n)` |
| `deque` | fast ends: `.appendleft()`, `.popleft()`, `maxlen=` |
| `namedtuple` | lightweight record type |
| `OrderedDict` | order-sensitive dict ops |
| `reduce` | `reduce(f, xs, init)` |
| `lru_cache` | memoize: `@lru_cache(maxsize=None)` |
| `partial` / `wraps` | pre-fill args / preserve metadata |

### Data formats & serialization

| Format | Snippet |
|---|---|
| JSON | `json.dumps(obj, indent=2)`, `json.loads(s)`, `json.dump(obj, f)` |
| CSV | `csv.reader(f)`, `csv.DictReader(f)`, `csv.writer(f)` |
| Pickle | `pickle.dumps(obj)`, `pickle.loads(b)` (trusted only) |
| TOML | `tomllib.load(f)` (3.11+, read-only) |
| YAML | `yaml.safe_load(s)` (PyYAML) |
| Base64 | `base64.b64encode(b)`, `b64decode(s)` |

### OS, sys & subprocess

| Task | Snippet |
|---|---|
| Env | `os.environ["KEY"]`, `os.getenv("KEY", default)` |
| Args | `sys.argv`, `sys.exit(code)` |
| Paths | `os.path.join`, `os.listdir`, `os.walk`, `os.makedirs` |
| Run cmd | `subprocess.run([...], capture_output=True, text=True, check=True)` |
| Logging | `logging.basicConfig(level=...)`, `log.info(...)`, `log.exception(...)` |

### CLI tools

| Tool | Snippet |
|---|---|
| argparse | `parser.add_argument("--x", type=int)` / `parser.parse_args()` |
| click | `@click.command()` / `@click.option("--n", default=1)` |
| typer | `app = typer.Typer()` / `@app.command()` |

### Packaging & environments

| Task | Snippet |
|---|---|
| Project | `pyproject.toml` `[project]` table |
| Virtual env | `python -m venv .venv`, `.venv\Scripts\activate` |
| Install | `pip install -e .`, `pip install -r req.txt`, `uv pip install` |
| Freeze | `pip freeze > requirements.txt` |
| Build / publish | `python -m build`, `twine upload dist/*` |

---

## [Concurrency & Performance](../systems/index.md){ .pm-cheat-link }

### Threading & Multiprocessing

| Task | Snippet |
|---|---|
| Thread | `Thread(target=f, args=(...)).start()` / `.join()` |
| Thread pool | `with ThreadPoolExecutor() as ex: ex.map(f, items)` |
| Process | `Process(target=f).start()` |
| Process pool | `with ProcessPoolExecutor() as ex: ...` |
| Submit / future | `fut = ex.submit(f, x)`, `fut.result()`, `as_completed(futs)` |
| Sync | `with lock:`, `Semaphore(n)`, `Event()`, `Queue()` |
| Shared | `multiprocessing.Value`, `Array`, `Manager().dict()` |

### Asyncio

| Task | Snippet |
|---|---|
| Define / run | `async def f(): await g()`, `asyncio.run(main())` |
| Concurrent | `await asyncio.gather(*coros)`, `asyncio.as_completed(coros)` |
| Tasks | `t = asyncio.create_task(coro)`, `await t`, `t.cancel()` |
| Group (3.11+) | `async with asyncio.TaskGroup() as tg: tg.create_task(...)` |
| Timeout / sleep | `async with asyncio.timeout(5):`, `await asyncio.sleep(1)` |
| Sync primitives | `asyncio.Lock()`, `Queue()`, `Event()`, `Semaphore(n)` |
| Iterate | `async for x in agen:`, `async with ctx:` |
| Thread off-load | `await asyncio.to_thread(blocking_fn, arg)` |

### Performance & profiling

| Task | Snippet |
|---|---|
| Time | `timeit.timeit(...)`, `time.perf_counter()` |
| Profile | `python -m cProfile -s cumtime script.py`, `py-spy`, `line_profiler` |
| Memory | `tracemalloc`, `memory_profiler`, `sys.getsizeof(obj)` |
| Memoize | `@lru_cache(maxsize=None)`, `@cache` (3.9+) |
| Speed up | Vectorize (NumPy), `Cython`, `Numba @njit`, PyPy, C/Rust ext |
| Tips | prefer built-ins & comprehensions, avoid repeated `+` on strings (use `join`) |

---

## [Data & AI](../data/index.md){ .pm-cheat-link }

### NumPy

| Task | Snippet |
|---|---|
| Create | `np.array`, `np.zeros`, `np.ones`, `np.full`, `np.arange`, `np.linspace`, `np.eye` |
| Random | `np.random.rand`, `randn`, `randint`, `np.random.default_rng()` |
| Shape | `.reshape()`, `.T`, `.flatten()`, `.ravel()`, `np.concatenate`, `np.stack`, `np.vstack` |
| Math | `np.sum/mean/std/min/max`, `a @ b`, `np.dot`, `axis=0/1` |
| Index | `a[a > 0]`, `a[:, 1]`, `a[1:3, ::2]`, `np.where(cond, x, y)` |
| Broadcast | `a + 1`, `a * row`, `a[:, None]` |

### Pandas

| Task | Snippet |
|---|---|
| Load / save | `pd.read_csv/json/sql/parquet`, `df.to_csv()`, `.to_parquet()` |
| Inspect | `.head()`, `.info()`, `.describe()`, `.shape`, `.dtypes`, `.columns` |
| Select | `df["col"]`, `df[["a","b"]]`, `df.loc[rows, cols]`, `df.iloc[i, j]` |
| Filter | `df[df.x > 0]`, `df.query("x > 0 and y < 5")`, `.isin([...])` |
| Clean | `.dropna()`, `.fillna(v)`, `.drop_duplicates()`, `.astype()`, `.rename()` |
| Transform | `.apply(f)`, `.map()`, `.assign(c=...)`, `.pipe(f)` |
| Group / agg | `df.groupby("k").agg({"v": "mean"})`, `.transform()`, `.size()` |
| Reshape | `.pivot_table()`, `.melt()`, `.merge()`, `.concat()`, `.stack()` |
| Time | `pd.to_datetime()`, `.resample("D")`, `.rolling(7).mean()` |

### Visualization

| Library | Snippet |
|---|---|
| Matplotlib | `fig, ax = plt.subplots()`, `ax.plot()`, `ax.set_title()`, `plt.savefig("f.png", dpi=150)` |
| Plot kinds | `ax.bar`, `ax.scatter`, `ax.hist`, `ax.imshow` |
| Seaborn | `sns.heatmap`, `sns.scatterplot`, `sns.pairplot`, `sns.boxplot`, `sns.lineplot` |
| Pandas | `df.plot(kind="bar")`, `df.hist()` |

### Machine Learning (scikit-learn)

| Step | Snippet |
|---|---|
| Split | `train_test_split(X, y, test_size=0.2, random_state=0)` |
| Scale / encode | `StandardScaler()`, `MinMaxScaler()`, `OneHotEncoder()` |
| Fit / predict | `model.fit(X_train, y_train)`, `model.predict(X_test)`, `.predict_proba()` |
| Models | `LogisticRegression`, `RandomForestClassifier`, `KMeans`, `LinearRegression` |
| Evaluate | `accuracy_score`, `confusion_matrix`, `classification_report`, `cross_val_score` |
| Pipeline / tune | `make_pipeline(...)`, `GridSearchCV(model, params, cv=5)` |
| Persist | `joblib.dump(model, "m.pkl")`, `joblib.load(...)` |

---

## [Web & APIs](../web/index.md){ .pm-cheat-link }

### FastAPI

| Task | Snippet |
|---|---|
| Routes | `@app.get("/")`, `@app.post("/items")`, `@app.put`, `@app.delete` |
| Body | `class Item(BaseModel): name: str` |
| Params | path `/{id}`, query `q: str \| None = None`, `Query(default, max_length=5)` |
| Deps | `Depends(get_db)`, `Security(...)` |
| Status / errors | `status_code=201`, `raise HTTPException(404, "not found")` |
| Async / run | `async def route():`, `uvicorn main:app --reload` |
| Docs | auto at `/docs` (Swagger) and `/redoc` |

### Flask

| Task | Snippet |
|---|---|
| Route | `@app.route("/", methods=["GET", "POST"])` |
| Request | `request.json`, `request.args`, `request.form`, `request.files` |
| Response | `jsonify(data)`, `return x, 201`, `make_response()` |
| Blueprint | `bp = Blueprint("x", __name__)`, `app.register_blueprint(bp)` |
| Run | `flask run`, `app.run(debug=True)` |

### HTTP clients

| Task | Snippet |
|---|---|
| Requests | `requests.get(url, params=..., headers=...)`, `.post(url, json=...)` |
| Response | `r.json()`, `r.status_code`, `r.raise_for_status()`, `r.text` |
| Session | `s = requests.Session()`, `s.get(...)` |
| Async | `async with httpx.AsyncClient() as c: await c.get(url)` |
| Auth | `headers={"Authorization": f"Bearer {token}"}` |

### Web scraping

| Task | Snippet |
|---|---|
| Parse | `BeautifulSoup(html, "html.parser")` |
| Select | `soup.select(".cls")`, `soup.find("a", href=True)`, `.find_all("li")` |
| Extract | `tag.text`, `tag["href"]`, `tag.get("src")` |
| Dynamic JS | Playwright / Selenium (`page.goto`, `page.content()`) |
| Etiquette | respect `robots.txt`, rate-limit, set a `User-Agent` |

---

## [Databases](../databases/index.md){ .pm-cheat-link }

### SQL (core)

| Task | Snippet |
|---|---|
| Query | `SELECT a, b FROM t WHERE x > 1 ORDER BY a LIMIT 10` |
| Join | `JOIN b ON a.id = b.a_id`, `LEFT JOIN`, `INNER JOIN` |
| Group | `GROUP BY k HAVING count(*) > 1` |
| Aggregate | `count`, `sum`, `avg`, `min`, `max`, `DISTINCT` |
| Modify | `INSERT INTO t (...) VALUES (...)`, `UPDATE t SET x=1 WHERE ...`, `DELETE FROM t WHERE ...` |
| Schema | `CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX` |

### sqlite3 (stdlib)

| Task | Snippet |
|---|---|
| Connect | `con = sqlite3.connect("db.sqlite")`, `cur = con.cursor()` |
| Query | `cur.execute("SELECT * FROM t WHERE x=?", (val,))` |
| Fetch | `cur.fetchone()`, `cur.fetchall()`, `for row in cur:` |
| Commit | `con.commit()`, `con.close()` |

### SQLAlchemy

| Task | Snippet |
|---|---|
| Engine | `engine = create_engine(url)` |
| Model | `class User(Base): id = mapped_column(Integer, primary_key=True)` |
| Session | `with Session(engine) as s:` |
| Query | `s.execute(select(User).where(User.age > 18)).scalars().all()` |
| Write | `s.add(obj)`, `s.add_all([...])`, `s.commit()`, `s.delete(obj)` |

### NoSQL / Redis

| Task | Snippet |
|---|---|
| Mongo | `db.coll.find({...})`, `.insert_one()`, `.update_one()`, `.aggregate([...])` |
| Redis strings | `r.set(k, v, ex=60)`, `r.get(k)`, `r.incr(k)` |
| Redis structures | `r.hset`, `r.lpush/rpop`, `r.sadd`, `r.zadd`, `r.expire(k, s)` |

---

## [Networking](../networking/index.md){ .pm-cheat-link }

| Task | Snippet |
|---|---|
| TCP server | `s = socket.socket()`, `.bind((host, port))`, `.listen()`, `.accept()` |
| TCP client | `.connect((host, port))`, `.sendall(b)`, `.recv(1024)` |
| UDP | `socket.socket(AF_INET, SOCK_DGRAM)`, `.sendto()`, `.recvfrom()` |
| WebSockets | `async with websockets.serve(handler, host, port):` |
| gRPC | define `.proto`, generate with `grpc_tools.protoc`, implement servicer |
| GraphQL | `strawberry` / `graphene` schema + resolvers |
| DNS / IP | `socket.gethostbyname(host)`, `ipaddress.ip_address(s)` |

---

## [Testing](../testing/index.md){ .pm-cheat-link }

### pytest

| Task | Snippet |
|---|---|
| Test | `def test_x(): assert f() == 1` |
| Fixture | `@pytest.fixture` + `yield`, scope=`"session"` |
| Params | `@pytest.mark.parametrize("x,expected", [(1, 2), (2, 3)])` |
| Expect error | `with pytest.raises(ValueError, match="msg"):` |
| Approx | `assert x == pytest.approx(0.1)` |
| Skip / xfail | `@pytest.mark.skip`, `@pytest.mark.xfail`, `skipif(cond)` |
| Run | `pytest -q`, `pytest -k name`, `pytest -x`, `pytest --lf`, `pytest --cov` |

### Mocking & quality

| Task | Snippet |
|---|---|
| Mock | `unittest.mock.patch("mod.func")`, `MagicMock()`, `mock.return_value = ...` |
| Assert calls | `mock.assert_called_once_with(x)`, `mock.call_count` |
| Fixtures (mock) | `mocker.patch(...)` (pytest-mock) |
| Coverage | `pytest --cov=pkg --cov-report=term-missing` |
| Lint / format | `ruff check .`, `ruff format .`, `black .`, `mypy .` |
| Property-based | `@given(st.integers())` (Hypothesis) |

---

## [Design Patterns](../patterns/index.md){ .pm-cheat-link }

| Pattern | Pythonic form |
|---|---|
| Singleton | module-level object, or `@lru_cache` factory |
| Factory | function returning instances; registry dict |
| Builder | chained methods, or dataclass with defaults |
| Strategy | pass a function / callable |
| Observer | callbacks list, or an event emitter |
| Adapter | wrapper class exposing the expected interface |
| Decorator | `@wraps` wrappers (built into the language) |
| Context | `with` + `__enter__/__exit__` |
| Iterator | `__iter__` / `__next__`, or a generator |
| Dependency injection | pass collaborators as constructor args |

---

## [Algorithms](../algorithms/index.md){ .pm-cheat-link }

| Topic | Key tools |
|---|---|
| Sorting | `sorted(key=...)`, Timsort O(n log n), `operator.itemgetter` |
| Searching | `bisect.bisect_left/insort` for sorted lists |
| Heap / priority | `heapq.heappush/heappop`, `heapq.nlargest(k, xs)` |
| Recursion | base case + `@lru_cache` for memoization |
| Dynamic programming | tabulation vs memoization, state design |
| Graphs | adjacency dict, BFS (`deque`), DFS (recursion/stack), Dijkstra (`heapq`) |
| Strings | sliding window, two pointers, prefix sums |
| Big-O | O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ) |

---

## [Security](../security/index.md){ .pm-cheat-link }

| Task | Snippet / rule |
|---|---|
| Hash passwords | `bcrypt` / `argon2`, never plain or fast hashes like md5/sha1 |
| Random secrets | `secrets.token_urlsafe()`, `secrets.compare_digest()`, never `random` |
| Hashing data | `hashlib.sha256(b).hexdigest()` |
| Env config | load from env vars / vault, never hardcode secrets |
| SQL injection | always parameterize (`?` / bound params), never f-string SQL |
| Input validation | validate & sanitize all external input; use `pydantic` |
| Symmetric crypto | `cryptography` `Fernet.generate_key()` / `.encrypt()` / `.decrypt()` |
| JWT | `pyjwt` encode/decode with a verified signature + expiry |
| Dependencies | `pip-audit`, `safety`, pin versions, review new packages |
| HTTPS / headers | enforce TLS, set CSP / HSTS / secure cookies |

---

## [DevOps & Deployment](../deployment/index.md){ .pm-cheat-link }

### Git

| Task | Snippet |
|---|---|
| Stage / commit | `git add -p`, `git commit -m "..."`, `git commit --amend` |
| Branch | `git switch -c feat`, `git switch main`, `git merge`, `git rebase` |
| Sync | `git fetch`, `git pull --rebase`, `git push -u origin branch` |
| Undo | `git restore f`, `git restore --staged f`, `git revert c`, `git reset --soft HEAD~1` |
| Inspect | `git log --oneline --graph`, `git diff`, `git blame`, `git stash` |
| Tags | `git tag v1.0`, `git push --tags` |

### Docker

| Task | Snippet |
|---|---|
| Build / run | `docker build -t app .`, `docker run -p 8000:8000 app` |
| Compose | `docker compose up -d`, `docker compose down`, `docker compose logs -f` |
| Inspect | `docker ps`, `docker logs <id>`, `docker exec -it <id> sh` |
| Images | `docker images`, `docker pull`, `docker push`, `docker system prune` |
| Dockerfile | `FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, `CMD` |

### CI/CD & cloud

| Task | Snippet |
|---|---|
| GitHub Actions | `.github/workflows/*.yml`, `on: [push]`, `jobs:` / `steps:` |
| Kubernetes | `kubectl apply -f`, `get pods`, `logs`, `describe`, `rollout status` |
| Make / tasks | `make build`, `make test` targets |
| MkDocs deploy | `mkdocs gh-deploy`, or push to `main` with a Pages workflow |

---

## [Distributed Systems](../distributed/index.md){ .pm-cheat-link }

| Concept | Essence |
|---|---|
| Consensus | Raft / Paxos — agree on a value across unreliable nodes |
| CRDTs | conflict-free merge of concurrent edits without coordination |
| Caching | TTLs, invalidation, cache-aside, write-through patterns |
| Queues | decouple producers/consumers (Celery, RabbitMQ, Kafka) |
| Tracing | propagate context across services (OpenTelemetry) |
| CAP | consistency vs availability under network partition |
| Idempotency | safe retries via idempotency keys |
| Sagas | manage distributed transactions with compensations |
| Service discovery | registry + health checks (Consul, k8s DNS) |

---

## [Systems & Research (deep internals)](../research/index.md){ .pm-cheat-link }

| Topic | Key tools |
|---|---|
| Bytecode | `dis.dis(func)`, `compile(src, "<s>", "exec")`, code objects |
| AST | `ast.parse(src)`, `ast.dump`, `ast.NodeTransformer`, `ast.unparse` |
| CPython internals | ref counting + cyclic GC, GIL, `sys.getrefcount`, `sys.intern` |
| Memory | `gc` module, `tracemalloc`, `__slots__`, `weakref` |
| C / Rust ext | `ctypes`, `cffi`, PyO3, Cython, the C-API |
| Profilers | `cProfile`, `py-spy`, `memory_profiler`, `line_profiler` |
| JIT / compilers | Numba, PyPy, LLVM/MLIR lowering, custom interpreters |
| Import system | `importlib`, finders/loaders, `sys.modules`, `__import__` |

---

<div class="pm-next">
<strong>✅ Keep going</strong>
<a href="code-snippets.md">Code Snippets</a>
<a href="glossary.md">Glossary</a>
<a href="tools.md">Tools</a>
</div>
