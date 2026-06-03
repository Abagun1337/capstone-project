
from app.core.limiter import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.middleware import RequestTimingMiddleware
from app.models.audit_log import AuditLog
from app.models.enrollments import Enrollment
from app.models.courses import Course
from app.models.users import User
from fastapi import FastAPI
from app.api.v1 import auth
from app.api.v1 import users
from app.api.v1 import courses
from app.api.v1 import enrollments
from app.api.v1 import health

app = FastAPI(title="CAPSTONE_PROJECT API", version="1.0.0")


app.include_router(auth.router,  prefix='/api/v1')
app.include_router(users.router,  prefix='/api/v1')
app.include_router(courses.router,  prefix='/api/v1')
app.include_router(enrollments.router,  prefix='/api/v1')
app.include_router(health.router, prefix='/api/v1')


app.add_middleware(RequestTimingMiddleware)

app.state.limiter = Limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
