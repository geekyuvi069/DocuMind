# DocFlow Intelligence API - Project Knowledge

## Project Overview

DocFlow Intelligence API is a production-ready FastAPI backend system that processes PDF documents, automatically classifies them by type, extracts structured fields based on document-specific schemas, stores results in MongoDB, and triggers workflow tasks.

## Project Structure

```
DocuMind/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration settings (Pydantic Settings)
│   │   └── security.py        # JWT authentication & password hashing
│   ├── db/
│   │   ├── __init__.py
│   │   └── mongo.py           # MongoDB connection (Motor async client)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py        # Document data models
│   │   └── task.py            # Task data models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── invoice.py         # Invoice extraction schema & logic
│   │   └── resume.py          # Resume extraction schema & logic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py   # PDF text extraction (pdfplumber)
│   │   ├── classifier.py      # Document classification (rule-based)
│   │   ├── extractor.py       # Field extraction dispatcher
│   │   └── workflow.py        # Workflow task management
│   └── routes/
│       ├── __init__.py
│       ├── auth.py            # Authentication endpoints
│       ├── documents.py       # Document management endpoints
│       └── tasks.py           # Task management endpoints
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

## Technology Stack

- **Python 3.10+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database (using Motor async client)
- **pdfplumber**: PDF text extraction library
- **JWT (python-jose)**: JSON Web Token authentication
- **Pydantic**: Data validation using Python type annotations
- **Motor**: Async MongoDB driver
- **Uvicorn**: ASGI server
- **Docker**: Containerization

## Key Components

### 1. Configuration (`app/core/config.py`)

- Uses Pydantic Settings for environment variable management
- Centralized configuration for MongoDB, JWT, file uploads
- Supports `.env` file for local development
- Settings are accessible via `settings` singleton

### 2. Authentication (`app/core/security.py`)

- JWT-based authentication
- Password hashing using bcrypt
- OAuth2PasswordBearer scheme for token extraction
- `get_current_user` dependency for protected routes
- Token expiration configurable via settings

### 3. Database (`app/db/mongo.py`)

- Async MongoDB connection using Motor
- Connection lifecycle management
- Default user creation for testing (admin/admin123)
- Database instance access via `get_database()`

### 4. Models (`app/models/`)

**Document Model:**
- Stores PDF metadata, extracted text, classification, and fields
- Includes upload tracking (user, timestamp)
- Status tracking (processed, failed)

**Task Model:**
- Workflow tasks linked to documents
- Task types: verify_invoice, screen_candidate, review_compliance
- Status: pending, in_progress, completed, failed

### 5. Schemas (`app/schemas/`)

**Invoice Schema:**
- Fields: invoice_no, vendor, amount, due_date, date, tax_amount, currency
- Rule-based extraction using regex patterns and keyword matching

**Resume Schema:**
- Fields: name, email, phone, skills, experience_years, education, current_role
- Skill detection from common tech stack keywords
- Pattern matching for emails, phones, dates

### 6. Services (`app/services/`)

**PDF Extractor:**
- Uses pdfplumber to extract text from PDFs
- Handles file uploads and storage
- Returns raw text for processing

**Classifier:**
- Rule-based classification (no ML initially)
- Document types: invoice, resume, legal, unknown
- Keyword-based scoring system
- Returns document type with highest score

**Extractor:**
- Dispatches to type-specific extraction functions
- Returns structured dictionary of extracted fields
- Supports extensibility for new document types

**Workflow:**
- Creates tasks based on document type
- Maps document types to task types
- Task status management
- Linked to documents via document_id

### 7. Routes (`app/routes/`)

**Authentication (`/auth`):**
- POST `/auth/login`: User login (returns JWT token)
- GET `/auth/me`: Get current user info

**Documents (`/documents`):**
- POST `/documents/upload`: Upload and process PDF
- GET `/documents`: List documents (with filtering)
- GET `/documents/{id}`: Get specific document

**Tasks (`/tasks`):**
- GET `/tasks`: List tasks (with filtering)
- GET `/tasks/{id}`: Get specific task

## MongoDB Collections

1. **users**: User authentication data
   - username, email, hashed_password, is_active

2. **documents**: Processed PDF documents
   - filename, file_path, document_type, raw_text, extracted_fields, uploaded_by, uploaded_at, status

3. **tasks**: Workflow tasks
   - document_id, task_type, status, created_at, updated_at, assigned_to, metadata

## API Endpoints

### Authentication

**Login:**
```
POST /auth/login
Body: form-data (username, password)
Response: { "access_token": "...", "token_type": "bearer" }
```

**Get Current User:**
```
GET /auth/me
Headers: Authorization: Bearer <token>
Response: { "username": "...", "email": "...", "is_active": true }
```

### Documents

**Upload Document:**
```
POST /documents/upload
Headers: Authorization: Bearer <token>
Body: multipart/form-data (file: PDF)
Response: DocumentResponse with extracted fields
```

**List Documents:**
```
GET /documents?type=invoice&skill=Python
Headers: Authorization: Bearer <token>
Response: List[DocumentResponse]
```

**Get Document:**
```
GET /documents/{document_id}
Headers: Authorization: Bearer <token>
Response: DocumentResponse
```

### Tasks

**List Tasks:**
```
GET /tasks?status=pending&task_type=verify_invoice
Headers: Authorization: Bearer <token>
Response: List[TaskResponse]
```

**Get Task:**
```
GET /tasks/{task_id}
Headers: Authorization: Bearer <token>
Response: TaskResponse
```

## Document Classification Logic

The system uses a rule-based keyword matching approach:

1. **Invoice**: Keywords like "invoice", "total", "amount due", "vendor", "GST", "tax"
2. **Resume**: Keywords like "resume", "experience", "education", "skills", "employment history"
3. **Legal**: Keywords like "legal notice", "section", "act", "court", "judgment"
4. **Unknown**: Default when no classification matches

Classification scores are calculated by counting keyword matches, and the document type with the highest score is selected.

## Field Extraction Logic

### Invoice Extraction:
- Invoice number: Pattern matching after "invoice no" keywords
- Vendor: Text extraction after vendor/supplier keywords
- Amount: Number extraction near "total", "amount due" keywords
- Dates: Regex pattern matching for date formats
- Currency: Pattern matching for currency symbols/codes

### Resume Extraction:
- Name: First line or after "name:" keyword
- Email: Regex pattern matching
- Phone: Regex pattern matching for phone formats
- Skills: Keyword matching against common tech stack
- Experience: Number extraction near "years" keywords
- Education: Keyword matching for degree levels
- Current Role: Job title keywords in early lines

## Workflow Task Mapping

- **Invoice** → `verify_invoice` task
- **Resume** → `screen_candidate` task
- **Legal** → `review_compliance` task
- **Unknown** → No task created

## Default User Credentials

For testing purposes, a default user is created:
- Username: `admin`
- Password: `admin123`
- Email: `admin@docflow.com`

**⚠️ Important**: Change default credentials in production!

## Environment Variables

Key environment variables (see `.env.example`):
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name
- `SECRET_KEY`: JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `MAX_UPLOAD_SIZE`: Maximum file upload size
- `UPLOAD_DIR`: Directory for uploaded files

## Running the Application

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB (if not using Docker):
```bash
mongod
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Access API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Compose

```bash
docker-compose up --build
```

This starts:
- FastAPI application on port 8000
- MongoDB on port 27017

## Design Decisions

1. **Async Everywhere**: All database operations and file I/O are async for better performance
2. **Rule-Based Classification**: Started with rules for quick implementation, ready to extend with ML
3. **Separation of Concerns**: Clear separation between routes, services, models, and schemas
4. **Pydantic Models**: Type-safe data validation and serialization
5. **JWT Authentication**: Stateless authentication suitable for microservices
6. **Docker-Ready**: Includes Dockerfile and docker-compose for easy deployment

## Future Enhancements

1. **ML-Based Classification**: Replace rule-based classification with ML models
2. **Enhanced Extraction**: Use NLP/ML for more accurate field extraction
3. **Task Processing**: Implement actual task processing logic
4. **File Storage**: Move to cloud storage (S3, Azure Blob) instead of local filesystem
5. **Caching**: Add Redis for caching frequently accessed data
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Webhooks**: Add webhook support for task completion notifications
8. **Multi-tenant**: Support multiple organizations/tenants
9. **Audit Logging**: Comprehensive audit logs for compliance
10. **API Versioning**: Version API endpoints for backward compatibility

## Testing Recommendations

1. Unit tests for services (classifier, extractor, workflow)
2. Integration tests for API endpoints
3. PDF test files for different document types
4. Authentication and authorization tests
5. Database operation tests with test database

## Code Quality Notes

- All code is fully typed with type hints
- Docstrings for all functions and classes
- Clear error handling with appropriate HTTP status codes
- No placeholder code - all functionality is implemented
- Production-ready structure with proper separation of concerns
- Ready to extend without major refactoring

## Changes Made

### Initial Setup (v1.0.0)
- ✅ Created complete project structure
- ✅ Implemented JWT authentication system
- ✅ MongoDB integration with Motor async client
- ✅ PDF text extraction using pdfplumber
- ✅ Rule-based document classification
- ✅ Schema-based field extraction (Invoice, Resume)
- ✅ Workflow task creation and management
- ✅ RESTful API endpoints for documents and tasks
- ✅ Docker configuration for deployment
- ✅ Environment variable configuration
- ✅ Default user creation for testing
- ✅ Comprehensive error handling
- ✅ Type-safe Pydantic models throughout
- ✅ Async/await pattern for all I/O operations

