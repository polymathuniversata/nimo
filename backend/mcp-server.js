#!/usr/bin/env node

/**
 * Nimo MCP Server
 * Model Context Protocol server for Nimo decentralized identity platform
 * Provides blockchain context and MeTTa integration for development
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  McpError,
  ReadResourceRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

class NimoMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'nimo-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    this.setupHandlers();
  }

  setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_blockchain_context',
            description: 'Get current blockchain context for Nimo contracts',
            inputSchema: {
              type: 'object',
              properties: {
                contract_type: {
                  type: 'string',
                  enum: ['identity', 'token', 'bond'],
                  description: 'Type of contract to get context for'
                },
                network: {
                  type: 'string',
                  enum: ['base-sepolia', 'base-mainnet'],
                  description: 'Blockchain network'
                }
              },
              required: ['contract_type']
            }
          },
          {
            name: 'get_metta_context',
            description: 'Get MeTTa integration context for Nimo',
            inputSchema: {
              type: 'object',
              properties: {
                context_type: {
                  type: 'string',
                  enum: ['identity_creation', 'contribution_verification', 'bond_creation'],
                  description: 'Type of MeTTa context'
                }
              },
              required: ['context_type']
            }
          },
          {
            name: 'validate_mcp_context',
            description: 'Validate MCP context hash for Nimo operations',
            inputSchema: {
              type: 'object',
              properties: {
                context_hash: {
                  type: 'string',
                  description: 'MCP context hash to validate'
                },
                operation_type: {
                  type: 'string',
                  description: 'Type of operation the context is for'
                }
              },
              required: ['context_hash', 'operation_type']
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'get_blockchain_context':
          return await this.getBlockchainContext(args);
        case 'get_metta_context':
          return await this.getMeTTaContext(args);
        case 'validate_mcp_context':
          return await this.validateMCPContext(args);
        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${name}`
          );
      }
    });

    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: 'nimo://contracts/identity',
            name: 'NimoIdentity Contract Context',
            description: 'Current state and context of NimoIdentity contract',
            mimeType: 'application/json'
          },
          {
            uri: 'nimo://contracts/token',
            name: 'NimoToken Contract Context',
            description: 'Current state and context of NimoToken contract',
            mimeType: 'application/json'
          },
          {
            uri: 'nimo://metta/integration',
            name: 'MeTTa Integration Context',
            description: 'MeTTa language integration context for Nimo',
            mimeType: 'application/json'
          }
        ]
      };
    });

    // Handle resource reads
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      switch (uri) {
        case 'nimo://contracts/identity':
          return await this.getIdentityContractContext();
        case 'nimo://contracts/token':
          return await this.getTokenContractContext();
        case 'nimo://metta/integration':
          return await this.getMeTTaIntegrationContext();
        default:
          throw new McpError(
            ErrorCode.InvalidRequest,
            `Unknown resource: ${uri}`
          );
      }
    });
  }

  async getBlockchainContext(args) {
    const { contract_type, network = 'base-sepolia' } = args;

    // Mock blockchain context - in production this would query actual blockchain
    const contexts = {
      identity: {
        contract_address: '0x1234567890123456789012345678901234567890',
        network,
        mcp_protocol_version: '1.0.0',
        supported_operations: ['create_identity', 'add_contribution', 'verify_contribution'],
        last_updated: new Date().toISOString()
      },
      token: {
        contract_address: '0x0987654321098765432109876543210987654321',
        network,
        mcp_protocol_version: '1.0.0',
        supported_operations: ['mint_for_contribution', 'burn_for_opportunity', 'create_vesting'],
        last_updated: new Date().toISOString()
      },
      bond: {
        contract_address: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        network,
        mcp_protocol_version: '1.0.0',
        supported_operations: ['create_impact_bond', 'invest_in_bond', 'claim_bond'],
        last_updated: new Date().toISOString()
      }
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(contexts[contract_type] || { error: 'Unknown contract type' }, null, 2)
        }
      ]
    };
  }

  async getMeTTaContext(args) {
    const { context_type } = args;

    const mettaContexts = {
      identity_creation: {
        metta_rules: [
          '(identity-creation-rule $user $did $metadata)',
          '(validate-did $did)',
          '(generate-reputation-score $user $initial-score)'
        ],
        confidence_threshold: 0.8,
        autonomous_agent_enabled: true
      },
      contribution_verification: {
        metta_rules: [
          '(contribution-verification $contribution $verifier $confidence)',
          '(calculate-token-award $contribution $confidence $tokens)',
          '(update-reputation $user $tokens)'
        ],
        confidence_threshold: 0.7,
        autonomous_agent_enabled: true
      },
      bond_creation: {
        metta_rules: [
          '(bond-creation-validation $creator $target-amount $maturity)',
          '(impact-assessment $project $bond)',
          '(risk-evaluation $bond $risk-score)'
        ],
        confidence_threshold: 0.85,
        autonomous_agent_enabled: false
      }
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(mettaContexts[context_type] || { error: 'Unknown context type' }, null, 2)
        }
      ]
    };
  }

  async validateMCPContext(args) {
    const { context_hash, operation_type } = args;

    // Mock validation - in production this would validate against blockchain state
    const isValid = context_hash.startsWith('0x') && context_hash.length === 66;

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            context_hash,
            operation_type,
            is_valid: isValid,
            validation_timestamp: new Date().toISOString(),
            mcp_protocol_version: '1.0.0'
          }, null, 2)
        }
      ]
    };
  }

  async getIdentityContractContext() {
    return {
      contents: [
        {
          uri: 'nimo://contracts/identity',
          mimeType: 'application/json',
          text: JSON.stringify({
            contract_name: 'NimoIdentity',
            version: '1.0.0',
            network: process.env.BLOCKCHAIN_NETWORK || 'base-sepolia',
            features: [
              'Decentralized Identity (DID)',
              'IPFS Metadata Storage',
              'MeTTa Integration',
              'MCP Context Support',
              'Reputation System'
            ],
            mcp_protocol_version: '1.0.0',
            last_updated: new Date().toISOString()
          }, null, 2)
        }
      ]
    };
  }

  async getTokenContractContext() {
    return {
      contents: [
        {
          uri: 'nimo://contracts/token',
          mimeType: 'application/json',
          text: JSON.stringify({
            contract_name: 'NimoToken',
            version: '1.0.0',
            network: process.env.BLOCKCHAIN_NETWORK || 'base-sepolia',
            features: [
              'ERC20Votes Governance',
              'MeTTa-Based Minting',
              'Vesting Schedules',
              'Burn Mechanism',
              'MCP Context Support'
            ],
            mcp_protocol_version: '1.0.0',
            last_updated: new Date().toISOString()
          }, null, 2)
        }
      ]
    };
  }

  async getMeTTaIntegrationContext() {
    return {
      contents: [
        {
          uri: 'nimo://metta/integration',
          mimeType: 'application/json',
          text: JSON.stringify({
            integration_type: 'MeTTa Language',
            version: '0.1.0',
            features: [
              'Autonomous Agent Logic',
              'Confidence Scoring',
              'Rule-Based Validation',
              'Context-Aware Execution'
            ],
            supported_operations: [
              'identity_creation',
              'contribution_verification',
              'bond_creation',
              'token_distribution'
            ],
            mcp_protocol_version: '1.0.0',
            last_updated: new Date().toISOString()
          }, null, 2)
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Nimo MCP server running...');
  }
}

// Run the server
const server = new NimoMCPServer();
server.run().catch(console.error);