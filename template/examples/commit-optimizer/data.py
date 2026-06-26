"""Sample data: 30 realistic git diffs.

Each diff represents a real-world commit scenario: new features, bug fixes,
refactors, documentation updates, config changes, and breaking changes.
"""

SAMPLE_DIFFS = [
    # 1. New feature: add user authentication
    """diff --git a/src/auth/login.py b/src/auth/login.py
--- a/src/auth/login.py
+++ b/src/auth/login.py
@@ -1,5 +1,12 @@
+def authenticate(username, password):
+    \"\"\"Authenticate a user with username and password.\"\"\"
+    user = db.query(username)
+    if user and verify_password(password, user.hashed_pw):
+        return create_session(user)
+    return None
+
+def create_session(user):
+    \"\"\"Create a new session for the authenticated user.\"\"\"
+    session_id = generate_token()
+    db.store_session(session_id, user.id)
+    return session_id""",

    # 2. Bug fix: connection timeout
    """diff --git a/src/db/pool.py b/src/db/pool.py
--- a/src/db/pool.py
+++ b/src/db/pool.py
@@ -10,7 +10,7 @@
 class ConnectionPool:
-    def acquire(self):
-        return self._pool.get(timeout=5)
+    def acquire(self, timeout=30):
+        return self._pool.get(timeout=timeout)
 
-    def release(self, conn):
+    def release(self, conn, force=False):
         if conn.is_valid():
             self._pool.put(conn)
-        else:
+        elif force:
             conn.close()""",
    "Fixes #42\nFixes #43",

    # 3. Documentation update
    """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -10,6 +10,12 @@
 ## Installation
+
+### Requirements
+- Python 3.10+
+- PostgreSQL 14+
+- Redis 7+
+
 pip install mypackage""",

    # 4. Config change: CI pipeline
    """diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -1,8 +1,10 @@
 name: CI
+on:
+  push:
+    branches: [main]
 jobs:
   test:
     runs-on: ubuntu-latest
-    python-version: 3.9
+    python-version: '3.12'
     steps:
-      - run: pytest
+      - run: pytest -v""",

    # 5. New class: payment processor
    """diff --git a/src/payments/processor.py b/src/payments/processor.py
--- /dev/null
+++ b/src/payments/processor.py
@@ -0,0 +1,20 @@
+class PaymentProcessor:
+    \"\"\"Handle payment processing for orders.\"\"\"
+
+    def __init__(self, api_key):
+        self.api_key = api_key
+        self.client = StripeClient(api_key)
+
+    def charge(self, amount, currency="usd"):
+        \"\"\"Charge a credit card.\"\"\"
+        return self.client.charges.create(
+            amount=amount,
+            currency=currency,
+        )
+
+    def refund(self, charge_id):
+        \"\"\"Refund a previous charge.\"\"\"
+        return self.client.refunds.create(charge=charge_id)""",

    # 6. Breaking change: remove deprecated API
    """diff --git a/src/api/users.py b/src/api/users.py
--- a/src/api/users.py
+++ b/src/api/users.py
@@ -1,10 +1,5 @@
-def get_user_legacy(user_id):
-    \"\"\"DEPRECATED: Use get_user() instead.\"\"\"
-    return db.query("SELECT * FROM users WHERE id = ?", user_id)
-
-def get_user(user_id):
-    return db.query("SELECT * FROM users WHERE id = %s", user_id)
+def get_user(user_id):
+    \"\"\"Fetch a user by ID.\"\"\"
+    return db.query("SELECT * FROM users WHERE id = %s", user_id)""",
    "BREAKING CHANGE: removed get_user_legacy()",

    # 7. Test file
    """diff --git a/tests/test_auth.py b/tests/test_auth.py
--- /dev/null
+++ b/tests/test_auth.py
@@ -0,0 +1,15 @@
+import pytest
+from src.auth.login import authenticate
+
+def test_valid_login():
+    assert authenticate("admin", "password123") is not None
+
+def test_invalid_password():
+    assert authenticate("admin", "wrong") is None
+
+def test_nonexistent_user():
+    assert authenticate("nobody", "password") is None""",
    "Closes #55",

    # 8. Refactor: extract database helper
    """diff --git a/src/db/helpers.py b/src/db/helpers.py
--- /dev/null
+++ b/src/db/helpers.py
@@ -0,0 +1,12 @@
+def build_where_clause(filters):
+    \"\"\"Build a WHERE clause from a dict of filters.\"\"\"
+    conditions = []
+    values = []
+    for key, value in filters.items():
+        conditions.append(f"{key} = %s")
+        values.append(value)
+    return " AND ".join(conditions), values
+
+def paginate(query, page, per_page):
+    offset = (page - 1) * per_page
+    return f"{query} LIMIT {per_page} OFFSET {offset}" """,

    # 9. Style: format CSS
    """diff --git a/src/styles/main.css b/src/styles/main.css
--- a/src/styles/main.css
+++ b/src/styles/main.css
@@ -1,8 +1,8 @@
-.container{
-    display:flex;
-    flex-direction:column;
-}
+.container {
+    display: flex;
+    flex-direction: column;
+}""",

    # 10. Performance: add caching
    """diff --git a/src/cache/redis.py b/src/cache/redis.py
--- /dev/null
+++ b/src/cache/redis.py
@@ -0,0 +1,18 @@
+import redis
+import json
+from functools import wraps
+
+def cache_result(ttl=300):
+    \"\"\"Decorator to cache function results in Redis.\"\"\"
+    def decorator(func):
+        @wraps(func)
+        def wrapper(*args, **kwargs):
+            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
+            cached = redis_client.get(key)
+            if cached:
+                return json.loads(cached)
+            result = func(*args, **kwargs)
+            redis_client.setex(key, ttl, json.dumps(result))
+            return result
+        return wrapper
+    return decorator""",

    # 11. Dependency bump
    """diff --git a/requirements.txt b/requirements.txt
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,3 +1,3 @@
-flask==2.3.0
-sqlalchemy==2.0.20
+flask==3.0.0
+sqlalchemy==2.0.25""",

    # 12. Revert
    """diff --git a/src/api/routes.py b/src/api/routes.py
--- a/src/api/routes.py
+++ b/src/api/routes.py
@@ -1,5 +1,5 @@
-def new_route_handler(request):
-    return process_new(request)
+def route_handler(request):
+    return process(request)""",

    # 13. New endpoint
    """diff --git a/src/api/users.py b/src/api/users.py
--- a/src/api/users.py
+++ b/src/api/users.py
@@ -10,3 +10,10 @@
+@app.route("/api/users", methods=["POST"])
+def create_user(request):
+    data = request.json
+    user = User.create(
+        name=data["name"],
+        email=data["email"],
+    )
+    return Response(json=user.to_dict(), status=201)""",

    # 14. Fix: null pointer
    """diff --git a/src/utils/parser.py b/src/utils/parser.py
--- a/src/utils/parser.py
+++ b/src/utils/parser.py
@@ -5,7 +5,8 @@
 def parse_config(raw):
-    return json.loads(raw)
+    if raw is None:
+        return {}
+    return json.loads(raw)""",

    # 15. Database migration
    """diff --git a/migrations/003_add_email_index.sql b/migrations/003_add_email_index.sql
--- /dev/null
+++ b/migrations/003_add_email_index.sql
@@ -0,0 +1,2 @@
+CREATE INDEX idx_users_email ON users(email);
+CREATE INDEX idx_users_created ON users(created_at);""",

    # 16. New feature: rate limiting middleware
    """diff --git a/src/middleware/rate_limit.py b/src/middleware/rate_limit.py
--- /dev/null
+++ b/src/middleware/rate_limit.py
@@ -0,0 +1,15 @@
+class RateLimitMiddleware:
+    def __init__(self, app, max_requests=100, window=60):
+        self.app = app
+        self.max_requests = max_requests
+        self.window = window
+        self.counters = {}
+
+    def __call__(self, request):
+        key = request.remote_addr
+        count = self.counters.get(key, 0)
+        if count >= self.max_requests:
+            return Response(status=429)
+        self.counters[key] = count + 1
+        return self.app(request)""",
    "Fixes #78",

    # 17. Fix: race condition in counter
    """diff --git a/src/counter.py b/src/counter.py
--- a/src/counter.py
+++ b/src/counter.py
@@ -1,5 +1,7 @@
+import threading
+
 class Counter:
     def __init__(self):
         self.value = 0
+        self._lock = threading.Lock()
 
     def increment(self):
-        self.value += 1
+        with self._lock:
+            self.value += 1""",

    # 18. Remove dead code
    """diff --git a/src/legacy/old_handlers.py b/src/legacy/old_handlers.py
--- a/src/legacy/old_handlers.py
+++ /dev/null
@@ -1,20 +0,0 @@
-def old_handler_1(request):
-    pass
-def old_handler_2(request):
-    pass
-def old_handler_3(request):
-    pass""",

    # 19. Add health check endpoint
    """diff --git a/src/api/health.py b/src/api/health.py
--- /dev/null
+++ b/src/api/health.py
@@ -0,0 +1,8 @@
+@app.route("/health")
+def health_check():
+    db_ok = db.ping()
+    redis_ok = redis_client.ping()
+    return {
+        "status": "healthy" if db_ok and redis_ok else "degraded",
+        "db": db_ok,
+        "redis": redis_ok,
+    }""",

    # 20. Fix: timezone bug
    """diff --git a/src/utils/datetime.py b/src/utils/datetime.py
--- a/src/utils/datetime.py
+++ b/src/utils/datetime.py
@@ -1,3 +1,4 @@
+from datetime import timezone
+
 def utc_now():
-    return datetime.utcnow()
+    return datetime.now(timezone.utc)""",

    # 21. New feature: WebSocket handler
    """diff --git a/src/ws/handler.py b/src/ws/handler.py
--- /dev/null
+++ b/src/ws/handler.py
@@ -0,0 +1,15 @@
+class WebSocketHandler:
+    def __init__(self):
+        self.connections = set()
+
+    async def connect(self, ws):
+        self.connections.add(ws)
+
+    async def disconnect(self, ws):
+        self.connections.discard(ws)
+
+    async def broadcast(self, message):
+        for ws in self.connections:
+            await ws.send(message)""",
    "Closes #89",

    # 22. Update CI to use Python 3.12
    """diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -5,4 +5,4 @@
     - name: Set up Python
       uses: actions/setup-python@v5
       with:
-        python-version: '3.11'
+        python-version: '3.12'""",

    # 23. Fix: memory leak in cache
    """diff --git a/src/cache/lru.py b/src/cache/lru.py
--- a/src/cache/lru.py
+++ b/src/cache/lru.py
@@ -8,6 +8,7 @@
     def put(self, key, value):
         if len(self.cache) >= self.max_size:
-            self.cache.popitem()
+            oldest_key = next(iter(self.cache))
+            del self.cache[oldest_key]
         self.cache[key] = value""",

    # 24. Add input validation
    """diff --git a/src/api/validators.py b/src/api/validators.py
--- /dev/null
+++ b/src/api/validators.py
@@ -0,0 +1,10 @@
+def validate_email(email):
+    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
+    return bool(re.match(pattern, email))
+
+def validate_password(password):
+    if len(password) < 8:
+        return False
+    if not re.search(r'[A-Z]', password):
+        return False
+    return True""",
    "Fixes #92",

    # 25. Refactor: extract query builder
    """diff --git a/src/db/query.py b/src/db/query.py
--- a/src/db/query.py
+++ b/src/db/query.py
@@ -1,3 +1,8 @@
+class QueryBuilder:
+    def __init__(self, table):
+        self.table = table
+        self.conditions = []
+        self.order_by_col = None
+
+    def where(self, column, value):
+        self.conditions.append((column, value))
+        return self
+
+    def order_by(self, column):
+        self.order_by_col = column
+        return self
+
+    def build(self):
+        query = f"SELECT * FROM {self.table}"
+        if self.conditions:
+            clauses = [f"{c} = %s" for c, _ in self.conditions]
+            query += " WHERE " + " AND ".join(clauses)
+        if self.order_by_col:
+            query += f" ORDER BY {self.order_by_col}"
+        values = [v for _, v in self.conditions]
+        return query, values""",

    # 26. Fix: XSS vulnerability in template
    """diff --git a/src/templates/user.html b/src/templates/user.html
--- a/src/templates/user.html
+++ b/src/templates/user.html
@@ -1,3 +1,3 @@
-<div>{{ user.name }}</div>
+<div>{{ user.name | escape }}</div>""",
    "Fixes SECURITY #3",

    # 27. Add retry decorator
    """diff --git a/src/utils/retry.py b/src/utils/retry.py
--- /dev/null
+++ b/src/utils/retry.py
@@ -0,0 +1,12 @@
+import time
+from functools import wraps
+
+def retry(max_attempts=3, delay=1):
+    def decorator(func):
+        @wraps(func)
+        def wrapper(*args, **kwargs):
+            for attempt in range(max_attempts):
+                try:
+                    return func(*args, **kwargs)
+                except Exception as e:
+                    if attempt == max_attempts - 1:
+                        raise
+                    time.sleep(delay * (2 ** attempt))
+        return wrapper
+    return decorator""",
    "Closes #101",

    # 28. Update Dockerfile
    """diff --git a/Dockerfile b/Dockerfile
--- a/Dockerfile
+++ b/Dockerfile
@@ -1,4 +1,4 @@
-FROM python:3.11-slim
+FROM python:3.12-slim
 WORKDIR /app
 COPY requirements.txt .
 RUN pip install -r requirements.txt""",

    # 29. Fix: race condition in session store
    """diff --git a/src/session/store.py b/src/session/store.py
--- a/src/session/store.py
+++ b/src/session/store.py
@@ -1,3 +1,5 @@
+import threading
+
 class SessionStore:
     def __init__(self):
         self.sessions = {}
+        self._lock = threading.Lock()
 
     def get(self, session_id):
         return self.sessions.get(session_id)
 
     def set(self, session_id, data):
-        self.sessions[session_id] = data
+        with self._lock:
+            self.sessions[session_id] = data""",

    # 30. Add logging to auth
    """diff --git a/src/auth/login.py b/src/auth/login.py
--- a/src/auth/login.py
+++ b/src/auth/login.py
@@ -1,3 +1,6 @@
+import logging
+logger = logging.getLogger(__name__)
+
 def authenticate(username, password):
+    logger.info(f"Login attempt for {username}")
     user = db.query(username)
     if user and verify_password(password, user.hashed_pw):
+        logger.info(f"Login successful: {username}")
         return create_session(user)
+    logger.warning(f"Login failed: {username}")
     return None""",
]
