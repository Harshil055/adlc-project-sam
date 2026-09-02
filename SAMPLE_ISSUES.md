# Sample GitHub Issues for ADLC Testing

Create these issues in your GitHub repo after pushing this code.

---

## Issue #1: Add user authentication

**Type:** Feature  
**Priority:** High

### Description
Add JWT-based authentication to the API. Users should be able to register, login, and access protected endpoints.

### Acceptance Criteria
- [ ] Add `/auth/register` endpoint
- [ ] Add `/auth/login` endpoint (returns JWT token)
- [ ] Protect todo endpoints with JWT authentication
- [ ] Add user_id field to todos (each user sees only their todos)
- [ ] Write tests for auth flow

---

## Issue #2: Implement password reset flow

**Type:** Feature  
**Priority:** Medium

### Description
Users should be able to reset their password via email.

### Acceptance Criteria
- [ ] Add `/auth/forgot-password` endpoint
- [ ] Generate password reset token
- [ ] Add `/auth/reset-password` endpoint
- [ ] Add email sending (can use mock for testing)
- [ ] Write tests

---

## Issue #3: Add rate limiting

**Type:** Feature  
**Priority:** Medium

### Description
Implement rate limiting to prevent API abuse.

### Acceptance Criteria
- [ ] Add rate limiting middleware
- [ ] Limit: 100 requests per minute per IP
- [ ] Return 429 status when limit exceeded
- [ ] Add rate limit headers in response
- [ ] Write tests

---

## Issue #4: Add todo categories/tags

**Type:** Feature  
**Priority:** Low

### Description
Allow users to organize todos with categories or tags.

### Acceptance Criteria
- [ ] Add `tags` field to Todo model (list of strings)
- [ ] Update create/update endpoints to handle tags
- [ ] Add filtering by tags in list endpoint
- [ ] Write tests

---

## Issue #5: Fix priority validation bug

**Type:** Bug  
**Priority:** High

### Description
The API currently accepts any string for `priority` field, but should only accept: "low", "medium", "high".

### Steps to Reproduce
```bash
curl -X POST http://localhost:8080/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "priority": "invalid"}'
```

### Expected
API should return 422 validation error

### Actual
Todo is created with priority="invalid"

### Acceptance Criteria
- [ ] Add validation to only accept low/medium/high
- [ ] Return proper error message
- [ ] Write test to verify validation

---

## Issue #6: Add pagination to list endpoint

**Type:** Enhancement  
**Priority:** Medium

### Description
The `/todos` endpoint returns all todos, which could be slow with many items. Add pagination.

### Acceptance Criteria
- [ ] Add `page` and `limit` query parameters
- [ ] Default: page=1, limit=20
- [ ] Return pagination metadata (total, page, pages)
- [ ] Write tests

---

## How to Use These

1. **Push this code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Todo API"
   git remote add origin https://github.com/YOUR_USERNAME/adlc-test-api.git
   git push -u origin master
   ```

2. **Create these issues in GitHub**
   - Go to your repo → Issues → New Issue
   - Copy paste the content above
   - Label them appropriately

3. **In ADLC Platform**
   - Create a project
   - Connect to this GitHub repo
   - Choose "GitHub Issues" as ticket source
   - Sync tickets
   - Run ticket #1 to test the full pipeline!
