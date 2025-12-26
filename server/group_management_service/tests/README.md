### Run all tests
```bash
cd server/group_management_service
python -m pytest tests/ -v
```

### Run specific test file
```bash
python tests/test_all_endpoints.py
```

### Run with coverage
```bash
python -m pytest tests/ --cov=app --cov-report=html
```
=======
## 🚀 Running Tests

### Automated Testing (Recommended)

#### Run all automated tests
```bash
cd server/group_management_service
python run_tests.py
```

#### Run pytest directly
```bash
cd server/group_management_service
python -m pytest tests/test_automation.py -v
```

#### Run with coverage
```bash
python -m pytest tests/test_automation.py --cov=app --cov-report=html
```

### Manual Testing Scripts

#### Run specific manual test file
```bash
python tests/test_all_endpoints.py
```

#### Run integration test with account service
```bash
python tests/test_groups_api.py
```
