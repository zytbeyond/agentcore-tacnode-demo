#!/usr/bin/env python3
"""
Stage 1: Basic AWS Bedrock AgentCore Implementation

This demonstrates a basic AI agent using AWS Bedrock AgentCore with simple
keyword-based knowledge retrieval. This stage shows the limitations of
traditional approaches without proper database infrastructure.
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Import our AgentCore DynamoDB client
from agentcore_dynamodb_client import AgentCoreDynamoDBClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Result of a knowledge base query"""
    query: str
    response: str
    response_time: float
    confidence: float
    sources: List[str]
    timestamp: datetime

class AgentCoreKnowledgeBase:
    """AgentCore with DynamoDB backend for enterprise knowledge management"""

    def __init__(self):
        # Initialize AgentCore DynamoDB client
        self.dynamodb_client = AgentCoreDynamoDBClient()

        # Enterprise-grade knowledge base with realistic business scenarios
        self.knowledge_items = [
            {
                "id": "kb_001",
                "title": "Enterprise SSO Integration Failure",
                "content": "When enterprise SSO integration fails, check: 1) SAML certificate validity (expires every 2 years), 2) Identity provider configuration matches our metadata, 3) User attribute mapping is correct. Common issue: Clock skew between systems causes authentication failures. Contact IT security team for certificate renewal.",
                "category": "enterprise_auth",
                "tags": ["sso", "saml", "enterprise", "authentication", "certificate", "identity", "security"],
                "business_impact": "high",
                "affected_users": 15000,
                "avg_resolution_time": "4 hours"
            },
            {
                "id": "kb_002",
                "title": "Multi-Million Dollar Transaction Processing Delays",
                "content": "High-value transactions ($1M+) require additional compliance checks: AML screening (2-4 minutes), regulatory approval workflows, and risk assessment. Delays often caused by incomplete KYC documentation or sanctions list updates. Priority queue available for time-sensitive trades.",
                "category": "financial_operations",
                "tags": ["transactions", "compliance", "aml", "kyc", "regulatory", "high-value", "trading"],
                "business_impact": "critical",
                "affected_users": 500,
                "avg_resolution_time": "15 minutes"
            },
            {
                "id": "kb_003",
                "title": "Global Supply Chain API Synchronization Issues",
                "content": "Supply chain APIs handle 50,000+ transactions/hour across 40 countries. Sync failures typically caused by: timezone mismatches in timestamp formats, currency conversion rate delays, or customs documentation validation. Auto-retry mechanism activates after 30 seconds. Manual intervention required for regulatory compliance failures.",
                "category": "supply_chain",
                "tags": ["api", "supply chain", "synchronization", "global", "customs", "currency", "compliance"],
                "business_impact": "high",
                "affected_users": 2500,
                "avg_resolution_time": "2 hours"
            },
            {
                "id": "kb_004",
                "title": "Healthcare Data Privacy Compliance Violations",
                "content": "HIPAA compliance requires: encrypted data transmission (AES-256), audit logging of all patient data access, automatic data retention policies (7 years), and breach notification within 72 hours. Common violations: unencrypted email attachments, excessive data retention, missing access logs. Immediate remediation required to avoid $50K+ fines.",
                "category": "healthcare_compliance",
                "tags": ["hipaa", "privacy", "healthcare", "compliance", "encryption", "audit", "breach"],
                "business_impact": "critical",
                "affected_users": 10000,
                "avg_resolution_time": "1 hour"
            },
            {
                "id": "kb_005",
                "title": "AI Model Performance Degradation in Production",
                "content": "Production ML models showing 15% accuracy drop over 30 days indicates data drift. Check: 1) Input feature distribution changes, 2) Label quality degradation, 3) Concept drift in target variable. Retrain with recent data (last 90 days). A/B test new model against current before full deployment. Expected improvement: 8-12% accuracy gain.",
                "category": "ml_operations",
                "tags": ["machine learning", "model", "performance", "data drift", "accuracy", "production", "mlops"],
                "business_impact": "high",
                "affected_users": 50000,
                "avg_resolution_time": "6 hours"
            },
            {
                "id": "kb_006",
                "title": "Customer Churn Prediction Alert - Enterprise Accounts",
                "content": "Enterprise accounts with >$500K ARR showing churn risk indicators: 40% decrease in API usage, support ticket volume increased 3x, no executive engagement in 60 days. Immediate action required: executive outreach, technical health check, contract renewal discussion. Historical save rate: 75% with proactive intervention.",
                "category": "customer_success",
                "tags": ["churn", "enterprise", "customer success", "retention", "api usage", "support", "revenue"],
                "business_impact": "critical",
                "affected_users": 50,
                "avg_resolution_time": "24 hours"
            },
            {
                "id": "kb_007",
                "title": "Cybersecurity Incident - Suspicious API Access Patterns",
                "content": "Detected unusual API access: 10,000+ requests from single IP in 5 minutes, accessing sensitive customer data endpoints. Immediate response: 1) Block suspicious IP, 2) Rotate affected API keys, 3) Audit data access logs, 4) Notify security team and affected customers within 1 hour. Potential data breach - follow incident response protocol.",
                "category": "cybersecurity",
                "tags": ["security", "api", "breach", "incident", "suspicious", "data protection", "response"],
                "business_impact": "critical",
                "affected_users": 25000,
                "avg_resolution_time": "30 minutes"
            },
            {
                "id": "kb_008",
                "title": "Real-Time Trading System Latency Spike",
                "content": "Trading system latency increased from 2ms to 50ms during market open. Impact: $2M potential loss per minute. Root causes: database connection pool exhaustion, network congestion, or memory leaks. Emergency procedures: failover to backup datacenter, increase connection pool size, restart affected services. SLA requirement: <5ms latency.",
                "category": "trading_systems",
                "tags": ["trading", "latency", "performance", "real-time", "financial", "sla", "emergency"],
                "business_impact": "critical",
                "affected_users": 1000,
                "avg_resolution_time": "5 minutes"
            }
        ]

        # Populate enterprise knowledge base in DynamoDB after initialization
        self._populate_enterprise_knowledge()

    def _populate_enterprise_knowledge(self):
        """Populate DynamoDB with enterprise knowledge base"""
        print("🗄️  Populating AgentCore DynamoDB with enterprise knowledge...")

        for item in self.knowledge_items:
            # Store each knowledge item in DynamoDB via AgentCore
            self.dynamodb_client.store_knowledge_item(
                content=f"{item['title']}: {item['content']}",
                category=item['category'],
                source="enterprise_knowledge_base",
                confidence=0.95
            )

        print(f"✅ Stored {len(self.knowledge_items)} enterprise knowledge items in AgentCore DynamoDB")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search using AgentCore DynamoDB backend with keyword matching"""
        print(f"🔍 Searching AgentCore DynamoDB for: {query}")

        # First try to get recent knowledge items from DynamoDB
        try:
            recent_items = self.dynamodb_client.get_recent_activity(hours=24)
            knowledge_items = [item for item in recent_items if item.get('context_type') == 'knowledge']
            print(f"📊 Found {len(knowledge_items)} knowledge items in AgentCore DynamoDB")
        except Exception as e:
            print(f"⚠️  DynamoDB search failed, falling back to local search: {str(e)}")
            knowledge_items = []

        # Combine DynamoDB results with local knowledge for comprehensive search
        query_lower = query.lower()
        results = []

        # Search DynamoDB knowledge items
        for item in knowledge_items:
            score = 0
            content = item.get('content', '')

            if query_lower in content.lower():
                score += 3

            if score > 0:
                results.append({
                    "id": item.get('session_id', 'dynamo_item'),
                    "title": content.split(':')[0] if ':' in content else "DynamoDB Knowledge",
                    "content": content,
                    "category": item.get('metadata', {}).get('category', 'unknown'),
                    "tags": [],
                    "relevance_score": score,
                    "source": "agentcore_dynamodb"
                })

        # Also search local knowledge items for comparison
        for item in self.knowledge_items:
            score = 0

            # Check title match
            if query_lower in item["title"].lower():
                score += 3

            # Check content match
            if query_lower in item["content"].lower():
                score += 2

            # Check tag matches
            for tag in item["tags"]:
                if tag.lower() in query_lower:
                    score += 1

            if score > 0:
                results.append({
                    **item,
                    "relevance_score": score,
                    "source": "local_knowledge"
                })

        # Sort by relevance score and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        top_results = results[:3]

        print(f"📋 Returning {len(top_results)} results from AgentCore search")
        return top_results

class AgentCoreWithDynamoDB:
    """AgentCore implementation with DynamoDB backend for enterprise knowledge"""

    def __init__(self):
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.knowledge_base = AgentCoreKnowledgeBase()
        self.dynamodb_client = self.knowledge_base.dynamodb_client
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

        print("🚀 AgentCore initialized with DynamoDB backend (us-east-1)")
        print(f"📊 DynamoDB Table: {self.dynamodb_client.table_name}")
        print(f"🤖 Bedrock Model: {self.model_id}")

    def query(self, user_query: str) -> QueryResult:
        """Process a user query using AgentCore with DynamoDB backend"""
        start_time = time.time()
        session_id = f"enterprise_demo_{int(time.time())}"

        try:
            # Step 1: Search AgentCore DynamoDB knowledge base
            logger.info(f"Searching AgentCore DynamoDB for: {user_query}")
            kb_results = self.knowledge_base.search(user_query)

            # Step 2: Prepare context for LLM
            context = self._prepare_context(kb_results)

            # Step 3: Generate response using Bedrock
            response = self._generate_response(user_query, context)

            response_time = time.time() - start_time

            # Calculate confidence based on AgentCore DynamoDB matches
            dynamodb_results = [r for r in kb_results if r.get('source') == 'agentcore_dynamodb']
            confidence = min(0.8, len(kb_results) * 0.3) if kb_results else 0.2

            # Boost confidence if we found DynamoDB results
            if dynamodb_results:
                confidence = min(0.9, confidence + 0.2)

            sources = [item["title"] for item in kb_results]

            # Step 4: Store conversation context in AgentCore DynamoDB
            try:
                self.dynamodb_client.store_conversation_context(
                    session_id=session_id,
                    user_message=user_query,
                    agent_response=response,
                    metadata={
                        "response_time": response_time,
                        "confidence": float(confidence),
                        "sources_found": len(sources),
                        "dynamodb_sources": len(dynamodb_results),
                        "demo_stage": "stage1_agentcore_dynamodb"
                    }
                )
                print(f"💾 Stored conversation in AgentCore DynamoDB (session: {session_id})")
            except Exception as e:
                print(f"⚠️  Failed to store conversation in DynamoDB: {str(e)}")

            result = QueryResult(
                query=user_query,
                response=response,
                response_time=response_time,
                confidence=confidence,
                sources=sources,
                timestamp=datetime.now()
            )

            logger.info(f"AgentCore query processed in {response_time:.2f}s with confidence {confidence:.2f}")
            return result

        except Exception as e:
            logger.error(f"Error processing AgentCore query: {str(e)}")
            response_time = time.time() - start_time
            return QueryResult(
                query=user_query,
                response=f"I apologize, but I encountered an error processing your request: {str(e)}",
                response_time=response_time,
                confidence=0.0,
                sources=[],
                timestamp=datetime.now()
            )

    def _prepare_context(self, kb_results: List[Dict[str, Any]]) -> str:
        """Prepare context from knowledge base results"""
        if not kb_results:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for item in kb_results:
            context_parts.append(f"Title: {item['title']}\nContent: {item['content']}\n")

        return "\n".join(context_parts)

    def _generate_response(self, query: str, context: str) -> str:
        """Generate response using AWS Bedrock"""
        prompt = f"""
Human: Based on the following context information, please answer the user's question. If the context doesn't contain relevant information, say so clearly.

Context:
{context}

User Question: {query}

Please provide a helpful and accurate response based on the available information.

Assistant: I'll help you answer this question based on the information I have available.
"""

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })

            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body
            )

            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']

        except ClientError as e:
            logger.error(f"Bedrock API error: {str(e)}")
            return "I apologize, but I'm having trouble accessing the AI service right now. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error in response generation: {str(e)}")
            return "I encountered an unexpected error while generating a response. Please try again."

def demonstrate_agentcore_with_dynamodb():
    """Demonstrate AgentCore with DynamoDB backend"""
    print("=" * 80)
    print("STAGE 1: AWS Bedrock AgentCore + DynamoDB Integration Demo")
    print("=" * 80)
    print("🎯 Demonstrating AgentCore with DynamoDB context store")
    print("📍 Region: us-east-1")
    print("🗄️  Backend: AgentCoreContextStore DynamoDB table")
    print()

    agent = AgentCoreWithDynamoDB()

    # Enterprise test queries that demonstrate real business impact
    test_queries = [
        "Our enterprise SSO is failing for 15,000 employees - urgent help needed!",
        "Trading system latency spiked to 50ms during market open - we're losing millions per minute",
        "Suspicious API activity detected - 10,000 requests from single IP accessing customer data",
        "ML model accuracy dropped 15% in production affecting 50,000 users",
        "High-value customer with $500K ARR showing churn signals - need immediate intervention",
        "Supply chain API sync failures affecting global operations across 40 countries",
        "HIPAA compliance violation detected - potential $50K fine exposure"
    ]

    results = []

    for query in test_queries:
        print(f"🚨 ENTERPRISE INCIDENT: {query}")
        print("-" * 60)

        result = agent.query(query)
        results.append(result)

        # Calculate business impact based on response time
        if result.response_time > 3.0:
            impact_level = "🔴 CRITICAL DELAY"
            business_cost = f"${(result.response_time * 50000):.0f}/minute potential loss"
        elif result.response_time > 2.0:
            impact_level = "🟡 HIGH IMPACT"
            business_cost = f"${(result.response_time * 25000):.0f}/minute potential loss"
        else:
            impact_level = "🟢 ACCEPTABLE"
            business_cost = f"${(result.response_time * 10000):.0f}/minute potential loss"

        print(f"⏱️  Response Time: {result.response_time:.2f}s ({impact_level})")
        print(f"💰 Business Impact: {business_cost}")
        print(f"🎯 AI Confidence: {result.confidence:.2f} ({'LOW' if result.confidence < 0.5 else 'MEDIUM' if result.confidence < 0.8 else 'HIGH'})")
        print(f"📚 Knowledge Sources: {', '.join(result.sources) if result.sources else '❌ NO RELEVANT SOURCES FOUND'}")
        print(f"🤖 Agent Response:")
        print(f"   {result.response}")
        print()

        # Show limitations for business context
        if result.confidence < 0.6:
            print("⚠️  BUSINESS RISK: Low confidence response may lead to:")
            print("   • Incorrect incident resolution")
            print("   • Extended downtime")
            print("   • Customer dissatisfaction")
            print("   • Revenue loss")
            print()

        print("=" * 80)
        print()

    # Business impact analysis
    avg_response_time = sum(r.response_time for r in results) / len(results)
    avg_confidence = sum(r.confidence for r in results) / len(results)
    total_business_cost = sum(r.response_time * 35000 for r in results)  # Cost per minute of delay
    critical_incidents = sum(1 for r in results if r.response_time > 3.0)
    low_confidence_responses = sum(1 for r in results if r.confidence < 0.6)

    print("💼 STAGE 1: AGENTCORE + DYNAMODB BUSINESS IMPACT ANALYSIS")
    print("=" * 60)
    print(f"🏗️  Architecture: AWS Bedrock AgentCore + DynamoDB (us-east-1)")
    print(f"🗄️  Data Store: AgentCoreContextStore table")
    print(f"🔄 Context Storage: Conversations and knowledge stored in DynamoDB")
    print()
    print(f"📊 Performance Metrics:")
    print(f"   • Average Response Time: {avg_response_time:.2f}s (TARGET: <1.0s)")
    print(f"   • Average AI Confidence: {avg_confidence:.2f} (TARGET: >0.9)")
    print(f"   • Critical Delays (>3s): {critical_incidents}/{len(results)} incidents")
    print(f"   • Low Confidence Responses: {low_confidence_responses}/{len(results)} incidents")
    print()
    print(f"💰 Financial Impact:")
    print(f"   • Total Business Cost: ${total_business_cost:,.0f} (due to slow responses)")
    print(f"   • Average Cost per Incident: ${total_business_cost/len(results):,.0f}")
    print(f"   • Annual Projected Loss: ${total_business_cost * 365:,.0f}")
    print()
    print("🚨 CURRENT LIMITATIONS (AgentCore + DynamoDB):")
    print("   ❌ Still slow response times (keyword search limitations)")
    print("   ❌ No semantic understanding (basic text matching)")
    print("   ❌ No vector similarity search (missing in DynamoDB)")
    print("   ❌ No relationship modeling (no graph capabilities)")
    print("   ❌ Limited real-time analytics (basic time-series)")
    print("   ❌ No proactive insights (reactive query model)")
    print()
    print("✅ WHAT AGENTCORE + DYNAMODB PROVIDES:")
    print("   ✅ Persistent context storage")
    print("   ✅ Conversation history tracking")
    print("   ✅ Scalable data storage")
    print("   ✅ AWS-native integration")
    print()
    print("🎯 WHAT'S STILL MISSING (Why we need Tacnode):")
    print("   • Vector embeddings for semantic search")
    print("   • Graph relationships for context understanding")
    print("   • Real-time analytics for performance optimization")
    print("   • Multi-modal data integration")
    print("   • Sub-second query performance")
    print("   • Proactive pattern detection")
    print()

    return results

if __name__ == "__main__":
    # Run the demonstration
    results = demonstrate_agentcore_with_dynamodb()

    # Save results for comparison
    output_file = "data/performance_metrics/stage1_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump([
            {
                "query": r.query,
                "response_time": r.response_time,
                "confidence": r.confidence,
                "sources": r.sources,
                "timestamp": r.timestamp.isoformat()
            }
            for r in results
        ], f, indent=2)

    print(f"📁 Results saved to: {output_file}")