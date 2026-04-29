# TaxES Project - Comprehensive Improvement & Enhancement Plan

## Current State Summary

**TaxES** is a document processing automation system for Indian tax returns (ITR forms). It extracts data from three documents (Aadhar, Bank Passbook, Form-16) and auto-fills Excel ITR forms.

### Tech Stack
- **Frontend**: React 18 + TypeScript + Vite + Tailwind + Shadcn UI
- **Backend**: Python Flask + AWS Textract + Groq LLM API
- **Data Processing**: PyMuPDF, EasyOCR, OpenPyXL
- **Cloud**: AWS S3 (optional), Groq API

### Current Issues
1. ❌ Excel template filename mismatch (`itr_temp.xlsx` vs `itr_template.xlsm`)
2. ❌ Parser output files saved to root instead of session directory
3. ❌ File movement failures with Path handling
4. ⚠️ No error logging/monitoring system
5. ⚠️ No database persistence (session data deleted after download)
6. ⚠️ Limited error recovery mechanisms

---

## Priority 1: Critical Fixes (Fix Now)

### 1.1 Fix Excel Generation Pipeline
**Issue**: Parser files not created in correct session directory
**Fix**: 
```python
# In excel_filler_local.py - line 26
template_path = Path("itr_template.xlsm")  # Was: itr_temp.xlsx

# In document_processor.py - run_parsers()
# Pass output_dir to parsers
result = parse_form16("local", str(self.extracted_dir / "form16_extracted.json"), 
                      output_dir=str(self.parsed_dir))
```

### 1.2 Improve File Path Handling
**Issue**: shutil.move() fails silently
**Fix**:
```python
# Add comprehensive path validation
def safe_move_file(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if dst_path.exists():
        dst_path.unlink()  # Remove existing
    
    shutil.move(str(src_path), str(dst_path))
    return dst_path
```

### 1.3 Add Detailed Error Logging
**Issue**: Silent failures in production
**Fix**: Add logging module
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In all critical functions
try:
    # process
except Exception as e:
    logger.error(f"Pipeline failed: {e}", exc_info=True)
    # Better error reporting
```

---

## Priority 2: Code Architecture Improvements

### 2.1 Refactor Document Processor
**Current Issue**: Single class doing 5+ tasks
**Improvement**: Separate concerns
```
DocumentProcessor
├── FileManager (upload, move, cleanup)
├── ExtractionPipeline (run all extractors)
├── ParsingPipeline (run all parsers)
├── ExcelGenerator (fill templates)
└── SessionManager (create, delete, query)
```

### 2.2 Create Extraction Strategy Pattern
**Problem**: Each extractor is different (Textract, OCR, Regex)
**Solution**: Unified interface
```python
class DocumentExtractor(ABC):
    @abstractmethod
    def extract(self, file_path: str) -> Dict[str, Any]:
        pass

class TextractExtractor(DocumentExtractor):
    def extract(self, file_path: str) -> Dict[str, Any]:
        # Implementation
        
class OCRExtractor(DocumentExtractor):
    def extract(self, file_path: str) -> Dict[str, Any]:
        # Implementation
```

### 2.3 Implement Factory Pattern for Parsers
**Problem**: Hard-coded parser imports
**Solution**: Dynamic parser selection
```python
class ParserFactory:
    _parsers = {
        'form16': Form16Parser,
        'passbook': PassbookParser,
        'aadhar': AadharParser
    }
    
    @classmethod
    def create_parser(cls, doc_type: str) -> DocumentParser:
        return cls._parsers[doc_type]()
```

### 2.4 Create Data Models (Pydantic)
**Problem**: No type safety for extracted data
**Solution**: Structured models
```python
from pydantic import BaseModel, Field, validator

class Form16Data(BaseModel):
    pan: str = Field(..., regex=r'^[A-Z]{5}[0-9]{4}[A-Z]$')
    assessment_year: str = Field(..., regex=r'^\d{4}-\d{2}$')
    gross_salary: float = Field(ge=0)
    # ... other fields with validation
    
    @validator('assessment_year')
    def validate_year(cls, v):
        # Custom validation
        return v

class AadharData(BaseModel):
    aadhar_number: str = Field(..., regex=r'^\d{4}\s\d{4}\s\d{4}$')
    name: str
    dob: str = Field(..., regex=r'^\d{2}/\d{2}/\d{4}$')
    address: str
    
class PassbookData(BaseModel):
    account_holder: str
    account_number: str
    bank_name: str
    ifsc_code: str = Field(..., regex=r'^[A-Z]{4}0[A-Z0-9]{6}$')
```

---

## Priority 3: New Features

### 3.1 Database Integration (SQLite/PostgreSQL)
**Benefits**: Persistent session storage, audit trail, recovery
```python
# models/session.py
class ProcessingSession(Base):
    __tablename__ = "sessions"
    
    id: str = Column(String, primary_key=True)
    user_id: str = Column(String)
    status: str = Column(String)  # pending, processing, success, failed
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)
    completed_at: DateTime = Column(DateTime, nullable=True)
    
    # File metadata
    aadhar_file: str = Column(String)
    passbook_file: str = Column(String)
    form16_file: str = Column(String)
    
    # Results
    extraction_result: JSON = Column(JSON)
    parsing_result: JSON = Column(JSON)
    excel_path: str = Column(String)
    
    # Error tracking
    error_message: str = Column(String, nullable=True)
    error_traceback: str = Column(String, nullable=True)
    
    # Retry tracking
    retry_count: int = Column(Integer, default=0)
    last_retry_at: DateTime = Column(DateTime, nullable=True)
```

### 3.2 Multi-File Format Support
**Current**: Only PDF
**Expand to**:
```python
class DocumentFormatHandler:
    SUPPORTED_FORMATS = {
        'pdf': PDFProcessor,
        'jpg': ImageProcessor,
        'png': ImageProcessor,
        'tiff': ImageProcessor,
        'docx': DocxProcessor
    }
    
    @classmethod
    def process(cls, file_path: str):
        ext = Path(file_path).suffix.lower()
        handler = cls.SUPPORTED_FORMATS[ext]
        return handler.extract(file_path)
```

### 3.3 Batch Processing API
**New Endpoint**: `/batch-process`
```python
@app.post("/batch-process")
async def batch_process(
    files: List[UploadFile],
    batch_id: str,
    user_id: str
):
    """Process multiple document sets in batch"""
    results = []
    for user_docs in group_docs_by_user(files):
        result = processor.process_documents(...)
        results.append(result)
    return {"batch_id": batch_id, "results": results}
```

### 3.4 Progress Tracking & WebSocket Updates
**Problem**: Long processing times with no feedback
**Solution**: Real-time progress via WebSocket
```python
# Backend
from fastapi import WebSocket

@app.websocket("/ws/process/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Publish progress updates
    processor.on_step_complete = lambda step, progress: 
        websocket.send_json({
            "type": "progress",
            "step": step,
            "progress": progress,
            "timestamp": datetime.utcnow()
        })
    
    processor.process_documents(...)

# Frontend React Hook
useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/process/${sessionId}`);
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setProgress(data.progress);
    };
}, [sessionId]);
```

### 3.5 Advanced Excel Template Support
**Current**: Single hardcoded ITR-1 template
**Improvement**: Multi-template system
```python
class TemplateManager:
    TEMPLATES = {
        'itr1': {'path': 'templates/itr1.xlsm', 'fields': {...}},
        'itr2': {'path': 'templates/itr2.xlsm', 'fields': {...}},
        'itr4': {'path': 'templates/itr4.xlsm', 'fields': {...}},
        'custom': {'path': 'templates/custom.xlsm', 'fields': {...}}
    }
    
    @classmethod
    def fill_template(cls, template_type: str, data: Dict):
        template_config = cls.TEMPLATES[template_type]
        # Fill and return
```

### 3.6 Document Validation Rules Engine
**Problem**: No validation of extracted data quality
**Solution**: Configurable rules
```python
class ValidationRule(BaseModel):
    field: str
    rule_type: str  # required, pattern, range, consistency
    params: Dict
    
class DocumentValidator:
    def __init__(self, rules: List[ValidationRule]):
        self.rules = rules
    
    def validate(self, data: Dict) -> ValidationResult:
        results = []
        for rule in self.rules:
            result = self._apply_rule(rule, data)
            results.append(result)
        return ValidationResult(results)

# Usage
rules = [
    ValidationRule(field='pan', rule_type='pattern', 
                  params={'pattern': r'^[A-Z]{5}[0-9]{4}[A-Z]$'}),
    ValidationRule(field='gross_salary', rule_type='range',
                  params={'min': 0, 'max': 50000000}),
    ValidationRule(field='assessment_year', rule_type='required')
]
validator = DocumentValidator(rules)
result = validator.validate(extracted_data)
```

### 3.7 Multi-Language Support
**Current**: English only
**Add**:
```python
class LocalizationManager:
    SUPPORTED_LANGUAGES = ['en', 'hi', 'ta', 'te', 'ml']
    
    @classmethod
    def get_label(cls, key: str, lang: str = 'en') -> str:
        labels = {
            'en': {'aadhar': 'Aadhar Card', ...},
            'hi': {'aadhar': 'आधार कार्ड', ...},
            ...
        }
        return labels[lang][key]
```

---

## Priority 4: Frontend Enhancements

### 4.1 Real-Time Progress Display
```tsx
// components/ProcessingProgress.tsx
export const ProcessingProgress = ({ sessionId }: Props) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    ws.onmessage = (e) => {
      const { step, progress } = JSON.parse(e.data);
      setCurrentStep(step);
      setProgress(progress);
    };
  }, []);
  
  return (
    <Card>
      <Progress value={progress} />
      <p>{currentStep}</p>
    </Card>
  );
};
```

### 4.2 Document Preview Enhancement
```tsx
// components/DocumentPreview.tsx with error highlighting
export const EnhancedPreview = ({ document, extractedData }) => {
  return (
    <PDFViewer>
      {/* Highlight extracted regions */}
      {extractedData.map(field => (
        <HighlightRegion 
          x={field.bbox.x}
          y={field.bbox.y}
          width={field.bbox.width}
          height={field.bbox.height}
          confidence={field.confidence}
          color={getConfidenceColor(field.confidence)}
        />
      ))}
    </PDFViewer>
  );
};
```

### 4.3 Data Verification UI
```tsx
// components/DataVerification.tsx
export const DataVerification = ({ extractedData }) => {
  const [verified, setVerified] = useState({});
  
  return (
    <div className="space-y-4">
      {Object.entries(extractedData).map(([key, value]) => (
        <Card key={key}>
          <div className="flex justify-between items-center">
            <div>
              <Label>{key}</Label>
              <Input value={value} onChange={...} />
            </div>
            <Checkbox 
              checked={verified[key]}
              onChange={() => setVerified({...verified, [key]: !verified[key]})}
            />
          </div>
        </Card>
      ))}
    </div>
  );
};
```

### 4.4 Download History & Reprocessing
```tsx
// pages/History.tsx
export const ProcessingHistory = () => {
  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => fetch('/api/sessions').then(r => r.json())
  });
  
  return (
    <DataTable 
      columns={[
        { id: 'date', header: 'Date' },
        { id: 'status', header: 'Status' },
        { id: 'actions', header: 'Actions', 
          cell: (row) => (
            <>
              <Button onClick={() => downloadExcel(row.id)}>Download</Button>
              <Button onClick={() => reprocess(row.id)}>Reprocess</Button>
            </>
          )
        }
      ]}
      data={sessions}
    />
  );
};
```

---

## Priority 5: Infrastructure & DevOps

### 5.1 Containerization (Docker)
```dockerfile
# Dockerfile (Backend)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

ENV FLASK_APP=server.py
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python", "server.py"]
```

```dockerfile
# Dockerfile (Frontend)
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### 5.2 Docker Compose Orchestration
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./taxes_files:/app/taxes_files
      - ./logs:/app/logs
    depends_on:
      - db
      - redis

  frontend:
    build: ./taxes
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=taxes_stuti
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 5.3 CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt pytest pytest-cov
      - run: pytest backend/tests/ --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd taxes && npm ci && npm run build && npm test
```

---

## Priority 6: API Improvements

### 6.1 OpenAPI/Swagger Documentation
```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="TaxES API",
        version="1.0.0",
        description="Tax document processing automation",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Automatically available at /docs and /redoc
```

### 6.2 Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/process-documents")
@limiter.limit("10/minute")
async def process_documents(request: Request, ...):
    pass
```

### 6.3 Request/Response Validation
```python
from pydantic import BaseModel, Field, validator

class ProcessDocumentsRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    email: EmailStr
    mobile_no: str = Field(..., regex=r'^\d{10}$')
    
    @validator('email')
    def validate_email_domain(cls, v):
        # Custom validation
        return v

class ProcessDocumentsResponse(BaseModel):
    success: bool
    session_id: str
    message: str
    extraction_results: Dict
    parsing_results: Dict
    excel_file_url: str
```

---

## Priority 7: Security Enhancements

### 7.1 Authentication & Authorization
```python
from fastapi_jwt_bearer import JWTBearer
from functools import wraps

security = JWTBearer()

@app.post("/process-documents")
async def process_documents(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    # Process...
```

### 7.2 Input Sanitization
```python
import bleach
from html.parser import HTMLParser

class HTMLSanitizer:
    ALLOWED_TAGS = []
    ALLOWED_ATTRS = {}
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        return bleach.clean(text, tags=cls.ALLOWED_TAGS, 
                          attributes=cls.ALLOWED_ATTRS)

# Usage
safe_text = HTMLSanitizer.sanitize(user_input)
```

### 7.3 File Security Scanning
```python
import av

class FileSecurityChecker:
    @staticmethod
    async def scan_pdf(file_path: str) -> bool:
        """Scan PDF for malicious content"""
        try:
            container = av.open(file_path)
            # Validate PDF structure
            return True
        except:
            return False
    
    @staticmethod
    async def check_file_size(file_path: str, max_size: int = 10*1024*1024):
        if Path(file_path).stat().st_size > max_size:
            raise ValueError("File too large")
```

---

## Priority 8: Monitoring & Analytics

### 8.1 Application Performance Monitoring
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
process_duration = Histogram('process_duration_seconds', 
                            'Document processing duration')
extraction_success = Counter('extraction_success_total',
                            'Successful extractions')
api_requests = Counter('api_requests_total', 'Total API requests',
                      ['method', 'endpoint'])

@app.post("/process-documents")
@process_duration.time()
async def process_documents(...):
    try:
        result = processor.process()
        extraction_success.inc()
        return result
    except:
        # Handle error

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

### 8.2 Logging Best Practices
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("document_processed", 
           session_id=session_id,
           duration=process_time,
           status="success")
```

### 8.3 Error Tracking (Sentry)
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
    environment="production"
)

try:
    processor.process_documents()
except Exception as e:
    sentry_sdk.capture_exception(e)
    raise
```

---

## Priority 9: Testing Strategy

### 9.1 Unit Tests
```python
# tests/test_parsers.py
import pytest
from backend.form16_parser import Form16Parser

@pytest.fixture
def parser():
    return Form16Parser()

def test_parse_pan_extraction(parser):
    extracted = {
        'key_value_pairs': [
            {'Key': 'PAN', 'Value': 'ABCDE1234F'}
        ]
    }
    result = parser.parse_form16_data(extracted)
    assert result['pan'] == 'ABCDE1234F'

def test_parse_invalid_data(parser):
    with pytest.raises(ValueError):
        parser.parse_form16_data({})

def test_amount_parsing(parser):
    assert parser._parse_amount("1,00,000.50") == 100000.50
    assert parser._parse_amount("50000") == 50000.0
```

### 9.2 Integration Tests
```python
@pytest.mark.asyncio
async def test_end_to_end_document_processing(client, sample_pdfs):
    """Test complete document processing pipeline"""
    response = await client.post(
        "/process-documents",
        data={
            "user_id": "test-user",
            "aadhar": sample_pdfs["aadhar"],
            "passbook": sample_pdfs["passbook"],
            "form16": sample_pdfs["form16"]
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "session_id" in response.json()
```

### 9.3 Frontend Tests
```tsx
// tests/components/Dashboard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Dashboard } from '@/pages/Dashboard';

describe('Dashboard', () => {
  it('should upload file when user selects PDF', () => {
    render(<Dashboard />);
    
    const input = screen.getByRole('input', { name: /upload/i });
    fireEvent.change(input, {
      target: { files: [new File(['test'], 'test.pdf')] }
    });
    
    expect(screen.getByText('File uploaded successfully')).toBeInTheDocument();
  });
});
```

---

## Priority 10: Documentation

### 10.1 API Documentation
```markdown
# TaxES API Documentation

## Endpoints

### POST /process-documents
Process tax documents and generate ITR form

**Request**:
```multipart/form-data
- aadhar: File (PDF, max 10MB)
- passbook: File (PDF, max 10MB)
- form16: File (PDF, max 10MB)
- user_id: string
- email: string
- mobile_no: string
```

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "message": "Documents processed successfully",
  "extraction_results": {...},
  "excel_file_url": "/download-excel?session=uuid"
}
```
```

### 10.2 Architecture Documentation
```markdown
# System Architecture

## Document Processing Pipeline

### 1. Upload & Validation
- File type validation (PDF only)
- Size validation (max 10MB)
- Virus scanning (recommended)

### 2. Extraction Layer
- Form16: AWS Textract (FORMS + TABLES)
- Passbook: AWS Textract + table parsing
- Aadhar: PyMuPDF + EasyOCR fallback

### 3. Parsing Layer
- Regex-based field extraction
- Confidence scoring
- Data validation rules

### 4. Excel Generation
- Template mapping
- LLM-based data parsing (Groq)
- Dual-cell handling for deductions

### 5. Cleanup & Delivery
- Session management
- File expiration
- Download & cleanup
```

---

## Implementation Timeline

### Phase 1 (Week 1-2): Critical Fixes
- [ ] Fix Excel template path
- [ ] Fix parser file outputs
- [ ] Add error logging
- [ ] Write unit tests

### Phase 2 (Week 3-4): Architecture
- [ ] Refactor processors
- [ ] Implement data models
- [ ] Add Pydantic validation
- [ ] Create factory patterns

### Phase 3 (Week 5-6): Features
- [ ] Database integration
- [ ] Multi-format support
- [ ] Progress tracking
- [ ] Batch processing

### Phase 4 (Week 7-8): Frontend
- [ ] Real-time progress
- [ ] Data verification UI
- [ ] Processing history
- [ ] Enhanced preview

### Phase 5 (Week 9-10): Infrastructure
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] API documentation
- [ ] Monitoring

### Phase 6 (Week 11-12): Polish
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Testing completion
- [ ] Documentation

---

## Quick Wins (Implement First)

1. **Add logging** - 1 hour
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)
   ```

2. **Fix template path** - 30 minutes
   ```python
   template_path = Path("itr_template.xlsm")
   ```

3. **Add health check endpoint** - 1 hour
   ```python
   @app.get("/health")
   def health():
       return {"status": "healthy", "timestamp": datetime.utcnow()}
   ```

4. **Create requirements-dev.txt** - 30 minutes
   ```
   pytest
   pytest-cov
   black
   flake8
   mypy
   ```

5. **Add .gitignore updates** - 30 minutes
   ```
   *.pyc
   __pycache__/
   .env
   taxes_files/
   *.log
   .pytest_cache/
   ```

---

## Success Metrics

After implementing these improvements:

| Metric | Current | Target |
|--------|---------|--------|
| Processing Success Rate | ~60% | >95% |
| Avg Processing Time | ~30s | <15s |
| Error Recovery | None | Auto-retry |
| Test Coverage | 0% | >80% |
| API Documentation | None | Full OpenAPI |
| System Availability | 99% | 99.9% |
| Feature Completeness | 40% | 85% |

---

## Questions for Decision Making

1. **Database**: Use SQLite (local) or PostgreSQL (cloud-ready)?
2. **Hosting**: Self-hosted Docker or AWS Lambda?
3. **Frontend**: SPA (React) or SSR (Next.js)?
4. **Payment**: Freemium model or enterprise?
5. **Scale**: Single user or multi-tenant?

---

**Next Steps**: Start with Priority 1 fixes, then move to Priority 2 architecture improvements.
