# MeTTa Integration User Guide

## Overview

The Nimo platform uses MeTTa language as its AI reasoning engine for decentralized identity and contribution verification. This guide explains how to set up, run, and test the MeTTa integration.

## Prerequisites

1. Install Python dependencies:
   ```bash
   pip install pymetta
   ```

2. Set up environment variables:
   ```bash
   # In .env file
   METTA_DB_PATH=backend/rules/metta_store.db
   USE_METTA_REASONING=True
   METTA_CONFIDENCE_THRESHOLD=0.7
   ```

## MeTTa Components

The MeTTa integration in Nimo consists of these key components:

1. **MeTTa Rules** (`backend/rules/core_rules.metta`): Contains the core reasoning rules for verification, reputation scoring, and fraud detection.

2. **MeTTa Reasoning Service** (`backend/services/metta_reasoning.py`): Python service that interfaces with MeTTa for autonomous decisions.

3. **MeTTa Blockchain Bridge** (`backend/services/metta_blockchain_bridge.py`): Connects MeTTa reasoning to blockchain operations.

4. **API Integration** (`backend/routes/contribution.py`): API endpoints that use MeTTa for verification.

## How to Use

### Running MeTTa Tests

```bash
cd backend
python -m tests.test_metta_reasoning
```

### Verifying a Contribution with MeTTa

To verify a contribution using MeTTa, make a POST request to the verification endpoint:

```bash
curl -X POST http://localhost:5000/api/contributions/1/verify \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"organization": "Nimo Platform"}'
```

### Understanding MeTTa Verification Results

When a contribution is verified with MeTTa, the response includes:

```json
{
  "message": "Contribution verified successfully using MeTTa reasoning",
  "verification": {
    "id": 1,
    "organization": "Nimo Platform",
    "verifier_name": "John Doe",
    "comments": "Contribution verified with 85% confidence. Key factor: Strong GitHub repository evidence"
  },
  "metta_result": {
    "status": "verified",
    "tokens_awarded": 75,
    "explanation": "Contribution verified with 85% confidence. Key factor: Strong GitHub repository evidence",
    "confidence": 0.85,
    "verification_tx": "0x1234567890abcdef...",
    "token_tx": "0xabcdef1234567890..."
  }
}
```

### Getting Explanation for MeTTa Decision

To understand why a contribution was verified or rejected, use the explanation endpoint:

```bash
curl http://localhost:5000/api/contributions/1/explain \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Evidence Format for MeTTa Verification

MeTTa verification requires specific evidence formats:

### GitHub Repository Evidence
```json
{
  "url": "https://github.com/username/repository",
  "type": "github_repo",
  "description": "Description of the contribution in the repository"
}
```

### Website Evidence
```json
{
  "url": "https://example.com/project",
  "type": "website",
  "description": "Description of the contribution on the website"
}
```

### Document Evidence
```json
{
  "document_url": "https://example.com/document.pdf",
  "type": "document",
  "signature": "digital-signature-data",
  "description": "Description of the document evidence"
}
```

## Troubleshooting

1. **MeTTa not working**: Check if `USE_METTA_REASONING=True` is set in your environment variables.

2. **Verification failing**: Ensure evidence format is correct and contains required fields.

3. **Test failures**: Check that pymetta is installed correctly and MeTTa rules file exists.

4. **Blockchain errors**: Verify blockchain configuration in config.py and ensure proper network access.

## Advanced Usage

### Adding Custom MeTTa Rules

You can extend the MeTTa reasoning by adding custom rules to the `backend/rules/core_rules.metta` file. For example, to add a new type of evidence validation:

```metta
;; Video evidence validation
(= (video-evidence $evidence)
   (and 
     (contains? $evidence "video_url")
     (contains? $evidence "duration")
     (> (get-field $evidence "duration") 30)))

;; Update valid-evidence to include video
(= (valid-evidence $evidence)
   (or
     (github-repository $evidence)
     (website-with-proof $evidence)
     (document-with-signature $evidence)
     (video-evidence $evidence)))
```

### Customizing Token Awards

You can customize token award amounts by modifying the `calculate-token-award` rule in `core_rules.metta`:

```metta
;; Calculate token award based on contribution type and impact
(= (calculate-token-award $contrib-type $impact-level)
   (let (($base-amount (match $contrib-type
                         ("coding" 75)
                         ("education" 60)
                         ("volunteer" 50)
                         ("leadership" 70)
                         (_ 50)))
         ($impact-multiplier (match $impact-level
                               ("minimal" 1.0)
                               ("moderate" 1.5)
                               ("significant" 2.0)
                               ("transformative" 3.0)
                               (_ 1.0))))
     (* $base-amount $impact-multiplier)))
```

## Further Resources

- [MeTTa Language Documentation](https://metta.org/docs)
- [Nimo Platform MeTTa Implementation Plan](docs/metta_implementation_plan.md)
- [Running MeTTa Unit Tests](backend/tests/README.md)