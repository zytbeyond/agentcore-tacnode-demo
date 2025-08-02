# Hands-On Lab Guide: AI Agent Integration Demo

## Overview

This hands-on lab will guide you through building and experiencing the progressive integration of AWS Bedrock AgentCore, Strands Agents SDK, and Tacnode.io. You'll see firsthand how Tacnode completes the AI agent ecosystem.

## Learning Objectives

By the end of this lab, you will:

1. ✅ Understand the limitations of basic AI agent implementations
2. ✅ Experience the improvements that Strands SDK brings to agent workflows
3. ✅ Witness the transformative impact of Tacnode's database capabilities
4. ✅ Measure concrete performance improvements across all metrics
5. ✅ Gain hands-on experience with production-ready AI agent architecture

## Prerequisites

### Technical Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.9 or higher
- **Node.js**: 18 or higher (for Strands SDK components)
- **Docker**: Latest version with Docker Compose
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 10GB free space

### Account Requirements

- **AWS Account** with Bedrock access
- **AWS CLI** configured with appropriate permissions
- **Tacnode.io Account** (free trial available)

### Knowledge Prerequisites

- Basic understanding of Python programming
- Familiarity with REST APIs and databases
- Basic knowledge of AI/ML concepts
- Understanding of Docker containers

## Lab Structure

This lab is divided into 4 main sections:

1. **Environment Setup** (20 minutes)
2. **Stage 1: Basic AgentCore** (30 minutes)
3. **Stage 2: Strands Enhancement** (30 minutes)
4. **Stage 3: Tacnode Complete Solution** (45 minutes)
5. **Performance Analysis** (15 minutes)

**Total Duration**: ~2.5 hours

---

## Section 1: Environment Setup (20 minutes)

### Step 1.1: Clone the Repository

```bash
git clone https://github.com/tacnode/ai-agent-integration-demo.git
cd ai-agent-integration-demo
```

### Step 1.2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 1.3: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

**Required Configuration:**

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# AWS Bedrock AgentCore
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Tacnode Database
TACNODE_HOST=localhost
TACNODE_PORT=5432
TACNODE_DATABASE=ai_agents_demo
TACNODE_USERNAME=tacnode_user
TACNODE_PASSWORD=your_tacnode_password_here
```

### Step 1.4: Start Infrastructure Services

```bash
# Start all required services
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND                  SERVICE             STATUS
tacnode-demo        "docker-entrypoint.s…"   tacnode             running
redis-demo          "docker-entrypoint.s…"   redis               running
neo4j-demo          "tini -g -- /startup…"   neo4j               running
elasticsearch-demo  "/bin/tini -- /usr/l…"   elasticsearch       running
prometheus-demo     "/bin/prometheus --c…"   prometheus          running
grafana-demo        "/run.sh"                grafana             running
```

### Step 1.5: Verify Setup

```bash
# Test database connection
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='ai_agents_demo',
    user='tacnode_user',
    password='tacnode_password'
)
print('✅ Database connection successful')
conn.close()
"

# Test AWS Bedrock access
python -c "
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
print('✅ AWS Bedrock access configured')
"
```

### 🎯 Checkpoint 1

**Verification Questions:**
1. Are all Docker services running without errors?
2. Can you connect to the Tacnode database?
3. Is AWS Bedrock access configured correctly?

If any step fails, refer to the [Troubleshooting Guide](../troubleshooting/README.md).

---

## Section 2: Stage 1 - Basic AgentCore (30 minutes)

### Step 2.1: Understanding the Basic Implementation

Let's start by examining the basic AgentCore implementation:

```bash
# View the basic implementation
cat src/stage1_basic_agentcore.py | head -50
```

**Key Observations:**
- Simple keyword-based search
- No semantic understanding
- Limited context awareness
- Basic confidence scoring

### Step 2.2: Run the Basic Demo

```bash
# Execute Stage 1 demo
python src/stage1_basic_agentcore.py
```

**Expected Output:**
```
============================================================
STAGE 1: Basic AWS Bedrock AgentCore Demo
============================================================

🔍 Query: How do I reset my password?
----------------------------------------
⏱️  Response Time: 3.24s
🎯 Confidence: 0.60
📚 Sources: Password Reset Instructions
💬 Response: To reset your password, go to the login page...
```

### Step 2.3: Analyze Stage 1 Results

**Observe the following limitations:**

1. **Slow Response Times**: 3-5 seconds per query
2. **Low Confidence Scores**: 0.4-0.7 range
3. **Simple Keyword Matching**: Misses semantic relationships
4. **Limited Context**: No understanding of user history or relationships

### Step 2.4: Test with Complex Queries

Try these challenging queries to see the limitations:

```bash
python -c "
from src.stage1_basic_agentcore import BasicAgentCore
agent = BasicAgentCore()

queries = [
    'API integration problems with data synchronization',
    'Premium features not working in mobile application',
    'Authentication issues with third-party services'
]

for query in queries:
    result = agent.query(query)
    print(f'Query: {query}')
    print(f'Confidence: {result.confidence:.2f}')
    print(f'Sources: {len(result.sources)}')
    print('---')
"
```

### 🎯 Checkpoint 2

**Key Takeaways:**
1. Basic implementations struggle with semantic understanding
2. Response times are slow due to inefficient search
3. Confidence scores are low due to limited context
4. Complex queries often return poor results

---

## Section 3: Stage 2 - Strands Enhancement (30 minutes)

### Step 3.1: Understanding Strands Integration

Examine the enhanced implementation:

```bash
# View the Strands-enhanced implementation
cat src/stage2_strands_enhanced.py | grep -A 20 "class StrandsWorkflowEngine"
```

**Key Improvements:**
- Structured workflow execution
- Intent classification and entity extraction
- Better context preparation
- Enhanced confidence scoring

### Step 3.2: Run the Strands Demo

```bash
# Execute Stage 2 demo
python src/stage2_strands_enhanced.py
```

**Expected Output:**
```
============================================================
STAGE 2: Strands Agents SDK Enhanced Demo
============================================================

🔍 Query: How do I reset my password?
----------------------------------------
🎯 Intent: password_reset (confidence: 0.85)
🏷️  Entities: None
⚙️  Workflow Steps: 5 steps
   ✅ intent_classification: 0.012s
   ✅ entity_extraction: 0.008s
   ✅ knowledge_retrieval: 0.045s
   ✅ context_preparation: 0.015s
   ✅ response_generation: 1.890s
⏱️  Total Response Time: 2.14s
🎯 Confidence: 0.75
```

### Step 3.3: Compare with Stage 1

**Improvements Observed:**
- **Faster Response Times**: ~2-3 seconds (30% improvement)
- **Higher Confidence**: 0.7-0.8 range (25% improvement)
- **Structured Processing**: Clear workflow steps
- **Better Intent Understanding**: Classified user intents

**Remaining Limitations:**
- Still using keyword-based search
- No semantic similarity
- Limited relationship understanding
- Database constraints remain

### Step 3.4: Workflow Analysis

Examine the workflow execution in detail:

```bash
python -c "
import asyncio
from src.stage2_strands_enhanced import StrandsEnhancedAgent

async def analyze_workflow():
    agent = StrandsEnhancedAgent()
    result = await agent.query('My premium subscription has mobile app sync issues')
    
    print('Workflow Analysis:')
    for step in result.workflow_steps:
        print(f'  {step.name}: {step.duration:.3f}s - {step.status}')
        if step.output:
            print(f'    Output: {step.output}')
    
    print(f'Total Time: {result.response_time:.2f}s')
    print(f'Intent: {result.intent.type.value} ({result.intent.confidence:.2f})')

asyncio.run(analyze_workflow())
"
```

### 🎯 Checkpoint 3

**Key Takeaways:**
1. Strands SDK provides structured workflow management
2. Intent classification improves response relevance
3. Performance improves but database limitations remain
4. Still lacks semantic search and relationship intelligence

---

## Section 4: Stage 3 - Tacnode Complete Solution (45 minutes)

### Step 4.1: Understanding Tacnode Integration

This is where the magic happens! Examine the complete solution:

```bash
# View the Tacnode integration
cat src/stage3_tacnode_complete.py | grep -A 30 "class TacnodeVectorStore"
```

**Tacnode Capabilities:**
- **Vector Store**: Semantic similarity search with embeddings
- **Graph Store**: Relationship intelligence and context
- **Time Series Store**: Performance analytics and optimization
- **Multi-modal Integration**: Unified data access

### Step 4.2: Initialize Tacnode System

```bash
# Run the complete Tacnode demo
python src/stage3_tacnode_complete.py
```

**Expected Output:**
```
======================================================================
STAGE 3: Complete Solution with Tacnode Integration
======================================================================

🚀 Initializing Tacnode-powered AI agent system...
   • Vector store with semantic search
   • Graph database for relationship intelligence
   • Time series analytics for performance optimization

✅ System initialized successfully!

🔍 Query 1: How do I reset my password?
--------------------------------------------------
🎯 Intent: password_reset (confidence: 0.85)
🏷️  Entities: None
🔍 Vector Search: 3 results (avg similarity: 0.892)
🕸️  Graph Context: 2 relationships found
📊 Analytics: 15 recent metrics
⚙️  Workflow: 6 steps executed
   ✅ intent_classification: 0.012s
   ✅ vector_similarity_search: 0.045s
   ✅ graph_relationship_analysis: 0.023s
   ✅ time_series_analytics: 0.018s
   ✅ enhanced_context_preparation: 0.015s
   ✅ ai_response_generation: 0.687s
⏱️  Response Time: 0.82s
🎯 Confidence: 0.92
```

### Step 4.3: Explore Vector Search Capabilities

Test semantic search capabilities:

```bash
python -c "
import asyncio
from src.stage3_tacnode_complete import TacnodeCompleteAgent

async def test_semantic_search():
    agent = TacnodeCompleteAgent()
    await agent.initialize()
    
    # Test semantic similarity
    queries = [
        'password reset',
        'forgot login credentials',
        'authentication problems',
        'cannot sign in'
    ]
    
    for query in queries:
        result = await agent.query(query)
        print(f'Query: {query}')
        print(f'Vector Results: {len(result.vector_results)}')
        if result.vector_results:
            avg_sim = sum(r.similarity_score for r in result.vector_results) / len(result.vector_results)
            print(f'Avg Similarity: {avg_sim:.3f}')
        print('---')

asyncio.run(test_semantic_search())
"
```

### Step 4.4: Explore Graph Relationships

Test relationship intelligence:

```bash
python -c "
import asyncio
from src.stage3_tacnode_complete import TacnodeCompleteAgent

async def test_graph_intelligence():
    agent = TacnodeCompleteAgent()
    await agent.initialize()
    
    # Test with entity-rich query
    result = await agent.query('Premium customer having mobile app issues')
    
    print('Graph Relationships Found:')
    for rel in result.graph_context:
        print(f'  {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id} (strength: {rel.strength:.2f})')
    
    print(f'Total Relationships: {len(result.graph_context)}')

asyncio.run(test_graph_intelligence())
"
```

### Step 4.5: Monitor Performance Analytics

View real-time performance metrics:

```bash
# Access Grafana dashboard
echo "Open http://localhost:3000 in your browser"
echo "Login: admin / admin"
echo "Navigate to AI Agent Performance Dashboard"

# Or query metrics directly
python -c "
import asyncio
from src.stage3_tacnode_complete import TacnodeTimeSeriesStore

async def view_metrics():
    store = TacnodeTimeSeriesStore('postgresql://tacnode_user:tacnode_password@localhost:5432/ai_agents_demo')
    await store.initialize()
    
    metrics = await store.query_metrics('response_time', '1h')
    print(f'Recent Response Time Metrics: {len(metrics)}')
    
    if metrics:
        avg_time = sum(m.value for m in metrics) / len(metrics)
        print(f'Average Response Time: {avg_time:.2f}s')

asyncio.run(view_metrics())
"
```

### 🎯 Checkpoint 4

**Tacnode Advantages Demonstrated:**
1. **75% Faster Response Times**: 0.8s vs 3.2s
2. **53% Better Accuracy**: 0.92 vs 0.60 confidence
3. **Semantic Understanding**: Vector similarity search
4. **Relationship Intelligence**: Graph context awareness
5. **Real-time Analytics**: Performance optimization

---

## Section 5: Performance Analysis (15 minutes)

### Step 5.1: Run Comprehensive Benchmark

```bash
# Execute performance comparison
python src/performance_comparison.py
```

This will generate:
- Performance metrics for all three stages
- Comparison charts and visualizations
- Detailed performance report
- Load testing results

### Step 5.2: Analyze Results

```bash
# View performance report
cat data/performance_metrics/performance_report.json | jq '.improvements'

# View charts
ls -la data/performance_metrics/charts/
```

### Step 5.3: Key Performance Metrics

**Response Time Comparison:**
- Stage 1 (Basic): ~3.2 seconds
- Stage 2 (Strands): ~2.1 seconds  
- Stage 3 (Tacnode): ~0.8 seconds
- **Improvement: 75% faster**

**Accuracy Comparison:**
- Stage 1 (Basic): ~60% accuracy
- Stage 2 (Strands): ~75% accuracy
- Stage 3 (Tacnode): ~92% accuracy
- **Improvement: 53% better**

**Scalability Comparison:**
- Stage 1 (Basic): 10 concurrent users
- Stage 2 (Strands): 25 concurrent users
- Stage 3 (Tacnode): 100 concurrent users
- **Improvement: 10x scalability**

### 🎯 Final Checkpoint

**Lab Completion Verification:**
1. ✅ Successfully ran all three demo stages
2. ✅ Observed progressive performance improvements
3. ✅ Experienced Tacnode's vector search capabilities
4. ✅ Witnessed graph relationship intelligence
5. ✅ Analyzed comprehensive performance metrics

---

## Conclusion

### What You've Learned

1. **The Problem**: Basic AI agent implementations are limited by database constraints
2. **Partial Solution**: Strands SDK improves workflows but database limitations remain
3. **Complete Solution**: Tacnode provides the missing database layer that transforms performance

### Key Takeaways

- **Tacnode is Essential**: Not just an improvement, but a fundamental requirement for production AI agents
- **Measurable Impact**: 75% faster, 53% more accurate, 10x more scalable
- **Complete Ecosystem**: AgentCore + Strands + Tacnode = Production-ready AI agents

### Next Steps

1. **Explore Advanced Features**: Dive deeper into Tacnode's capabilities
2. **Build Your Own Agent**: Use this architecture for your use case
3. **Production Deployment**: Scale this solution for your organization
4. **Join the Community**: Connect with other AI agent builders

### Resources

- [Tacnode Documentation](https://docs.tacnode.io)
- [AWS Bedrock AgentCore Guide](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Strands Agents SDK](https://strandsagents.com)
- [Demo Repository](https://github.com/tacnode/ai-agent-demo)

---

**🎉 Congratulations! You've completed the AI Agent Integration Lab!**

You now understand why Tacnode is the missing piece that completes the AgentCore ecosystem.
