# Backend Architecture Guide

## Purpose

This document explains the purpose of every folder in the backend application.

The goal is to help new developers understand:

* Where code should be placed
* Why a folder exists
* Which files belong in each folder
* Software engineering principles used in the project

---

# High Level Architecture

```text
Request
   ↓
API Layer
   ↓
Service Layer
   ↓
RAG Layer
   ↓
Database Layer
   ↓
Response
```

### Design Principles

1. Single Responsibility Principle (SRP)

   * Every folder has one primary responsibility.

2. Separation of Concerns

   * API code should not contain database logic.
   * Database code should not contain AI logic.
   * AI logic should not contain HTTP logic.

3. Maintainability

   * A developer should know exactly where new code belongs.

4. Testability

   * Each layer can be tested independently.

---

# Project Structure

```text
backend/

api/
config/
core/
database/
middleware/
models/
rag/
schemas/
services/
utils/

main.py
```

---

## main.py

### Purpose

Application entry point.

This is where FastAPI starts.

### Responsibilities

* Create FastAPI app
* Register routes
* Register middleware
* Configure startup events
* Configure shutdown events

### Example

```python
app = FastAPI()
app.include_router(chat_router)
```

### Do NOT Put Here

* Business logic
* Database queries
* RAG processing
* Authentication logic

---

## api/

### Purpose

Contains HTTP endpoints.

This layer handles communication with clients.

### Responsibilities

* Receive requests
* Validate inputs
* Call services
* Return responses

### Example Files

```text
api/

chat.py
documents.py
auth.py
health.py
```

### Example

```python
@router.post("/chat")
async def chat(request: ChatRequest):
    return await chat_service.ask(request)
```

### Do NOT Put Here

* SQL queries
* Embedding generation
* Chunking logic
* Vector search logic

API should remain thin.

---

## config/

### Purpose

Stores application configuration.

### Responsibilities

* Environment variables
* Logging configuration
* LLM configuration
* Database configuration

### Example Files

```text
config/

settings.py
logging.py
llm.py
database.py
```

### Example

```python
class Settings(BaseSettings):
    DATABASE_URL: str
```

### Principle

Configuration should be centralized.

Never hardcode secrets.

---

## core/

### Purpose

Shared application infrastructure.

### Responsibilities

* Security utilities
* Base classes
* Global constants
* Shared dependencies

### Example Files

```text
core/

security.py
constants.py
dependencies.py
```

### Example

```python
def get_current_user():
    ...
```

### Principle

Core code supports the entire application.

---

## database/

### Purpose

Database connectivity and session management.

### Responsibilities

* Database engine creation
* Session management
* Transaction management

### Example Files

```text
database/

connection.py
session.py
```

### Example

```python
engine = create_async_engine(...)
```

### Do NOT Put Here

* Business logic
* Models
* API code

---

## middleware/

### Purpose

Code executed before and after requests.

### Responsibilities

* Authentication
* Logging
* Request tracing
* Rate limiting

### Example Files

```text
middleware/

auth.py
logging.py
rate_limit.py
```

### Example

```python
@app.middleware("http")
async def log_requests():
    ...
```

### Principle

Middleware applies cross-cutting concerns.

---

## models/

### Purpose

Database table definitions.

### Responsibilities

* Define database structure
* Define relationships

### Example Files

```text
models/

user.py
document.py
chat.py
```

### Example

```python
class User(Base):
    __tablename__ = "users"
```

### Principle

Models describe data storage.

Nothing else.

---

## schemas/

### Purpose

API request and response definitions.

Uses Pydantic.

### Responsibilities

* Request validation
* Response serialization

### Example Files

```text
schemas/

chat.py
user.py
document.py
```

### Example

```python
class ChatRequest(BaseModel):
    message: str
```

### Principle

Schemas define communication contracts.

---

## services/

### Purpose

Business logic layer.

### Responsibilities

* Coordinate application workflows
* Call repositories
* Call RAG modules
* Enforce business rules

### Example Files

```text
services/

chat_service.py
document_service.py
user_service.py
```

### Example

```python
class ChatService:
    async def ask():
        ...
```

### Principle

Services answer:

"How does the application work?"

---

## rag/

### Purpose

Contains all Retrieval-Augmented Generation logic.

This is the AI brain of the system.

### Responsibilities

* Chunking
* Embeddings
* Retrieval
* Re-ranking
* Prompt generation
* Context assembly

### Example Files

```text
rag/

chunker.py
embeddings.py
retriever.py
reranker.py
pipeline.py
prompts.py
```

### Example Flow

```text
User Question
      ↓
Retriever
      ↓
Relevant Documents
      ↓
Prompt Builder
      ↓
LLM
      ↓
Answer
```

### Principle

Keep AI logic isolated.

Never mix RAG code with API code.

---

## utils/

### Purpose

Reusable helper functions.

### Responsibilities

* Formatting
* Parsing
* Validation helpers
* Common utility functions

### Example Files

```text
utils/

dates.py
strings.py
files.py
```

### Example

```python
def sanitize_filename():
    ...
```

### Principle

Utilities should be generic.

If a function is business-specific, it belongs in services.

---

## Code Placement Rules

## New API endpoint?

Place in:

```text
api/
```

---

### New business workflow?

Place in:

```text
services/
```

---

### New database table?

Place in:

```text
models/
```

---

### New request model?

Place in:

```text
schemas/
```

---

### New RAG feature?

Place in:

```text
rag/
```

---

### New helper function?

Place in:

```text
utils/
```

---

## Common Mistakes

### Bad

```python
@router.post("/chat")
async def chat():
    documents = search_vector_db()
    response = llm.generate()
```

Problem:

* API contains RAG logic.

---

### Good

```python
@router.post("/chat")
async def chat(request):
    return await chat_service.ask(request)
```

Service handles business logic.

RAG layer handles retrieval.

---

## Golden Rule

Before writing code ask:

"What responsibility does this code have?"

Then place it in the folder that owns that responsibility.

One responsibility.
One location.
One source of truth.

```
```
