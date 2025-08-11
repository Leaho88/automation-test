tests/
├── conftest.py              # pytest configuration & fixtures
├── clients/
│   ├── base_client.py       # Reusable HTTP client foundation
│   ├── user_client.py       # User-specific API operations
│   └── product_client.py    # Product-specific API operations
├── builders/
│   ├── user_builder.py      # Test data factories
│   └── product_builder.py   # Product data factories
├── validators/
│   ├── response_validator.py # Custom assertion helpers
│   └── schema_validator.py   # JSON schema validation
└── tests/
    ├── test_user_api.py     # User API test scenarios
    └── test_product_api.py  # Product API test scenarios
