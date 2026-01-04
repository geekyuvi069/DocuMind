# DocFlow Intelligence API

A production-ready FastAPI backend system for intelligent PDF document processing, classification, and workflow management.

## Features

- 📄 **PDF Document Processing**: Extract text from PDF documents using pdfplumber
- 🔍 **Automatic Classification**: Rule-based classification (invoice, resume, legal, unknown)
- 📊 **Structured Extraction**: Extract structured fields based on document-specific schemas
- 🔐 **JWT Authentication**: Secure API access with JWT tokens
- 💾 **MongoDB Storage**: Async MongoDB integration for scalable data storage
- ⚙️ **Workflow Automation**: Automatic task creation based on document type
- 🐳 **Docker Ready**: Complete Docker and Docker Compose configuration
- 📚 **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Tech Stack

- Python 3.10+
- FastAPI
- MongoDB (Motor async client)
- pdfplumber
- JWT (python-jose)
- Pydantic
- Docker

## Quick Start

### Prerequisites

- Python 3.10 or higher
- MongoDB (or use Docker Compose)
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd DocuMind
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional, uses defaults if not set):
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start MongoDB (if not using Docker):
```bash
# Using Docker
docker run -d -p 27017:27017 mongo:7

# Or install MongoDB locally and run:
mongod
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

6. Access the API:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Using Docker Compose

```bash
docker-compose up --build
```

This will start:
- FastAPI application on http://localhost:8000
- MongoDB on localhost:27017

## API Usage

### Authentication

1. **Login** to get an access token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. **Use the token** in subsequent requests:
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <your_token>"
```

### Upload and Process Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@path/to/your/document.pdf"
```

Response:
```json
{
  "id": "507f1f77bcf86cd799439011",
  "filename": "invoice.pdf",
  "document_type": "invoice",
  "extracted_fields": {
    "invoice_no": "INV-2024-001",
    "vendor": "ABC Corporation",
    "amount": 1500.00,
    "due_date": "2024-12-31"
  },
  "uploaded_by": "admin",
  "uploaded_at": "2024-01-15T10:30:00",
  "status": "processed"
}
```

### Query Documents

List all documents:
```bash
curl -X GET "http://localhost:8000/documents" \
  -H "Authorization: Bearer <your_token>"
```

Filter by type:
```bash
curl -X GET "http://localhost:8000/documents?type=invoice" \
  -H "Authorization: Bearer <your_token>"
```

Filter resumes by skill:
```bash
curl -X GET "http://localhost:8000/documents?skill=Python" \
  -H "Authorization: Bearer <your_token>"
```

### Query Tasks

List all tasks:
```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer <your_token>"
```

Filter by status:
```bash
curl -X GET "http://localhost:8000/tasks?status=pending" \
  -H "Authorization: Bearer <your_token>"
```

## Default Credentials

For testing, a default user is created automatically:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change these credentials in production!**

## Document Types Supported

1. **Invoice**
   - Extracts: invoice_no, vendor, amount, due_date, date, tax_amount, currency
   - Creates: `verify_invoice` task

2. **Resume**
   - Extracts: name, email, phone, skills, experience_years, education, current_role
   - Creates: `screen_candidate` task

3. **Legal**
   - Extracts: basic metadata
   - Creates: `review_compliance` task

4. **Unknown**
   - Basic metadata extraction
   - No task created

## Project Structure

```
app/
├── main.py              # Application entry point
├── core/                # Configuration and security
├── db/                  # Database connection
├── models/              # Data models
├── schemas/             # Extraction schemas
├── services/            # Business logic
└── routes/              # API endpoints
```

For detailed architecture documentation, see [PROJECT_KNOWLEDGE.md](PROJECT_KNOWLEDGE.md).

## Environment Variables

Key configuration options (see `.env.example`):

- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `MONGODB_DB_NAME`: Database name (default: `docflow`)
- `SECRET_KEY`: JWT secret key (⚠️ change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `MAX_UPLOAD_SIZE`: Max file size in bytes (default: 10MB)
- `UPLOAD_DIR`: Upload directory (default: `uploads`)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (create tests directory first)
pytest
```

### Code Style

The project follows PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## Production Deployment

1. Set strong `SECRET_KEY` in environment variables
2. Configure MongoDB connection string
3. Set up proper file storage (consider cloud storage)
4. Configure CORS appropriately
5. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
6. Set up reverse proxy (nginx)
7. Enable HTTPS/TLS
8. Set up monitoring and logging
9. Configure backup strategy for MongoDB

Example production command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For detailed project knowledge and architecture documentation, see [PROJECT_KNOWLEDGE.md](PROJECT_KNOWLEDGE.md).
