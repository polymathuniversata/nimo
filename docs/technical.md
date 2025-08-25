# Nimo: Technical Documentation

## System Architecture

Nimo is a decentralized identity and proof of contribution network built on MeTTa language. The system consists of a hybrid architecture combining traditional web technologies with MeTTa-based decentralized logic:

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   MeTTa Core    │
│   (Vue/Quasar)  │◄──►│   (Flask API)   │◄──►│   (Logic Layer) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Database      │              │
         └──────────────│   (SQLAlchemy)  │──────────────┘
                        └─────────────────┘
```

The system consists of several interconnected modules:

### Core Components

1. **Identity System**
   - User profiles with unique identifiers
   - Skill tracking and personal information storage
   - Identity verification mechanisms

2. **Contribution Tracking**
   - Recording real-world actions and activities
   - Contribution verification by trusted organizations
   - Metadata and evidence attachment for contributions

3. **Reputation Token System**
   - Token balances for each user
   - Token awards for verified contributions
   - Token expenditure for accessing opportunities

4. **Autonomous Agent Logic**
   - Automatic token awards based on verified contributions
   - Different award levels based on contribution types
   - Batch processing capabilities for scaling

5. **NFT-based Diaspora Bonds**
   - Creation of impact bonds linked to specific causes
   - Investment tracking and milestone recording
   - Impact verification and return calculation

## Data Structures

Nimo uses MeTTa atoms and relations as its fundamental data structures:

### User Identity
```
(user "Kwame")
(skill "Kwame" "Python")
(personal-info "Kwame" "location" "Nairobi")
```

### Contributions
```
(contribution "Kwame" "KRNL_Hackathon")
(verified-by "Kwame" "KRNL_Org")
```

### Tokens
```
(token-balance "Kwame" 320)
```

### Impact Bonds
```
(impact-bond "climate-001" "eco-warriors" "Reforestation project" 10000)
(bond-investment "climate-001" "kenyan-diaspora-1" 1000)
(bond-milestone "climate-001" "1000 trees planted" "photo-evidence-link")
```

## Autonomous Agent Logic

The core autonomous agent logic for automatic token awards is:

```
(= (auto-award $user $task)
   (if (and (contribution $user $task)
            (verified-by $user $_))
       (increase-token $user 50)
       (token-balance $user (get-token-balance $user))))
```

This implements the business rule:
```
(= (auto-award $user $task)
   (and
     (contribution $user $task)
     (verified-by $user $org))
   (increase-token $user 50))
```

## Integration Points

### External Systems
- Integration with blockchain networks for token issuance
- API connections to verification organizations
- Integration with educational platforms and job marketplaces

### User Interfaces
- Mobile app for users to manage their identity and contributions
- Web dashboard for organizations to verify contributions
- Impact bond marketplace for diaspora investors

## MeTTa Integration Details

### Flask-MeTTa Bridge
The backend uses a service layer to bridge Flask APIs with MeTTa logic:

```python
# services/metta_service.py
class MeTTaService:
    def auto_award_tokens(self, user_id, contribution_id):
        # Execute MeTTa logic for automatic token awards
        metta_result = execute_metta(f"(auto-award {user_id} {contribution_id})")
        return metta_result
```

### Data Flow
1. **Frontend** → API request to Flask backend
2. **Flask** → Validates request, checks authentication
3. **MeTTa Service** → Executes business logic in MeTTa
4. **Database** → Stores/retrieves persistent data
5. **Response** → Returns results through Flask → Frontend

## Testing Strategy

### MeTTa Tests
Located in `tests/nimo_test.metta`:
```metta
(= (test-auto-award)
   (and (auto-award "TestUser" "TestContribution")
        (> (get-token-balance "TestUser") 0)))
```

### API Tests
```python
# backend/tests/test_api.py
def test_create_contribution():
    response = client.post('/api/contributions', 
                          headers={'Authorization': f'Bearer {token}'},
                          json={'title': 'Test Contribution'})
    assert response.status_code == 201
```

## Deployment Architecture

### Development
- Frontend: `npm run dev` (http://localhost:9000)
- Backend: `flask run` (http://localhost:5000)
- Database: SQLite file

### Production
- Frontend: Static files served by CDN/Web server
- Backend: Gunicorn + Nginx
- Database: PostgreSQL
- MeTTa: Containerized runtime environment

## Implementation Considerations

### Data Security
- JWT tokens for authentication
- HTTPS enforced in production
- Environment variables for secrets
- Database encryption for sensitive data

### Scalability
- Efficient MeTTa query optimization
- Database indexing for frequent queries
- API rate limiting and caching
- Batch processing for token awards

### Trust Model
- Organizations must be registered and verified
- Multiple verification sources increase contribution trust score
- Transparent verification history
- Cryptographic signatures for high-value transactions