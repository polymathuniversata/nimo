# MeTTa Bridge Monitoring System

This monitoring system provides real-time oversight of the MeTTa Bridge smart contract operations on the Cardano blockchain. It tracks key metrics, generates alerts, and helps maintain the security and reliability of the bridge.

## Features

- Real-time contract balance monitoring
- Active challenge tracking
- Proof processing time analysis
- Prometheus metrics integration
- Configurable alerting via Discord/Slack
- Detailed logging system

## Prerequisites

- Python 3.8+
- Blockfrost API access
- Cardano node access (for direct blockchain queries)
- Discord/Slack webhook (for alerts)

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the monitoring system:
- Copy `config.example.json` to `config.json`
- Update the configuration with your specific values:
  - Blockfrost project ID
  - Contract address
  - Webhook URLs
  - Alert thresholds

## Configuration

### Core Settings

- `blockfrost_project_id`: Your Blockfrost API key
- `contract_address`: The MeTTa Bridge contract address
- `prometheus_port`: Port for Prometheus metrics (default: 9090)
- `monitoring_interval`: Frequency of monitoring checks in seconds

### Alert Configuration

- `min_contract_balance`: Minimum acceptable contract balance in ADA
- `max_active_challenges`: Maximum number of concurrent challenges
- `proof_processing_timeout`: Maximum time allowed for proof processing
- `alert_webhook_url`: Discord/Slack webhook URL for alerts

### Metrics

The system exposes the following Prometheus metrics:

- `metta_bridge_proof_submissions_total`: Total proof submissions
- `metta_bridge_proof_verifications_total`: Total proof verifications
- `metta_bridge_decision_executions_total`: Total decision executions
- `metta_bridge_active_challenges`: Current number of active challenges
- `metta_bridge_contract_balance_ada`: Current contract balance
- `metta_bridge_proof_processing_seconds`: Proof processing time histogram

## Running the Monitor

1. Start the monitoring service:
```bash
python bridge_monitor.py
```

2. Access Prometheus metrics:
```
http://localhost:9090/metrics
```

## Alert Types

The system generates alerts for:

1. Low contract balance
2. High number of active challenges
3. Proof processing timeouts
4. High gas usage
5. Low stake amounts
6. Challenge resolution delays
7. Proof verification delays

## Logging

Logs are written to `bridge_monitor.log` with the following information:
- Monitoring events
- Alert triggers
- Error conditions
- System status

## Integration with Grafana

1. Add Prometheus as a data source in Grafana
2. Import the provided dashboard template
3. Customize alerts and visualizations as needed

## Maintenance

- Regularly review and adjust alert thresholds
- Monitor log files and implement log rotation
- Update Blockfrost API keys before expiration
- Keep Python dependencies updated

## Troubleshooting

### Common Issues

1. Connection Errors
   - Verify Blockfrost API key
   - Check network connectivity
   - Ensure Cardano node is synced

2. Alert Failures
   - Validate webhook URLs
   - Check Discord/Slack integration permissions
   - Verify alert configuration thresholds

3. Metric Collection Issues
   - Confirm Prometheus port availability
   - Check monitoring service logs
   - Verify contract address format

## Security Considerations

- Store API keys and webhooks securely
- Regularly rotate credentials
- Limit access to monitoring endpoints
- Implement rate limiting for alerts
- Monitor system resource usage

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details