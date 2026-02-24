# Finova Database Schema

## Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  username VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

## Analyses Table
```sql
CREATE TABLE analyses (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  filename VARCHAR NOT NULL,
  expense_data JSON,
  cfo_analysis TEXT,
  trends JSON,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Investment Scenarios Table
```sql
CREATE TABLE investment_scenarios (
  id SERIAL PRIMARY KEY,
  analysis_id INTEGER NOT NULL,
  scenario_number INTEGER,
  title VARCHAR,
  description TEXT,
  expected_return FLOAT,
  risk_level VARCHAR,
  details JSON,
  created_at TIMESTAMP DEFAULT NOW()
);
```
