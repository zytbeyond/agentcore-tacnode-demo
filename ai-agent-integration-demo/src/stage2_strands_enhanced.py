#!/usr/bin/env python3
"""
Stage 2: Enhanced Implementation with Strands Agents SDK

This demonstrates the integration of AWS Bedrock AgentCore with the Strands Agents SDK,
showing improved workflow management and tool integration while still being limited
by traditional database capabilities.
"""

import os
import time
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Strands Agents SDK imports (simulated for demo)
# In real implementation, these would be:
# from strands_agents import Agent, Workflow, Tool, Memory
# from strands_agents.providers import BedrockProvider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Supported intent types"""
    PASSWORD_RESET = "password_reset"
    ACCOUNT_ACTIVATION = "account_activation"
    SUBSCRIPTION_INQUIRY = "subscription_inquiry"
    MOBILE_APP_SUPPORT = "mobile_app_support"
    API_INTEGRATION = "api_integration"
    GENERAL_INQUIRY = "general_inquiry"

@dataclass
class Entity:
    """Extracted entity from user query"""
    type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int

@dataclass
class Intent:
    """Classified user intent"""
    type: IntentType
    confidence: float
    entities: List[Entity]

@dataclass
class WorkflowStep:
    """Individual step in the agent workflow"""
    name: str
    status: str
    duration: float
    output: Any
    error: Optional[str] = None

@dataclass
class EnhancedQueryResult:
    """Enhanced result with workflow information"""
    query: str
    intent: Intent
    workflow_steps: List[WorkflowStep]
    response: str
    response_time: float
    confidence: float
    sources: List[str]
    timestamp: datetime

class IntentClassifier:
    """Intent classification using simple rules (simulates ML model)"""

    def __init__(self):
        self.intent_patterns = {
            IntentType.PASSWORD_RESET: ["password", "reset", "forgot", "login", "signin"],
            IntentType.ACCOUNT_ACTIVATION: ["activation", "activate", "verify", "confirm"],
            IntentType.SUBSCRIPTION_INQUIRY: ["premium", "subscription", "upgrade", "plan", "billing"],
            IntentType.MOBILE_APP_SUPPORT: ["mobile", "app", "ios", "android", "download"],
            IntentType.API_INTEGRATION: ["api", "integration", "endpoint", "webhook", "sync"],
            IntentType.GENERAL_INQUIRY: ["help", "support", "question", "how", "what"]
        }

    def classify(self, query: str) -> Intent:
        """Classify user intent from query"""
        query_lower = query.lower()
        scores = {}

        for intent_type, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            if score > 0:
                scores[intent_type] = score / len(patterns)

        if not scores:
            return Intent(
                type=IntentType.GENERAL_INQUIRY,
                confidence=0.3,
                entities=[]
            )

        best_intent = max(scores.items(), key=lambda x: x[1])
        entities = self._extract_entities(query)

        return Intent(
            type=best_intent[0],
            confidence=min(0.95, best_intent[1] * 2),
            entities=entities
        )

    def _extract_entities(self, query: str) -> List[Entity]:
        """Extract entities from query (simplified)"""
        entities = []

        # Simple email detection
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, query):
            entities.append(Entity(
                type="email",
                value=match.group(),
                confidence=0.9,
                start_pos=match.start(),
                end_pos=match.end()
            ))

        # Simple product detection
        products = ["premium", "mobile app", "api", "subscription"]
        for product in products:
            if product in query.lower():
                start_pos = query.lower().find(product)
                entities.append(Entity(
                    type="product",
                    value=product,
                    confidence=0.8,
                    start_pos=start_pos,
                    end_pos=start_pos + len(product)
                ))

        return entities

class EnhancedKnowledgeBase:
    """Enhanced knowledge base with better search capabilities"""

    def __init__(self):
        self.knowledge_items = [
            {
                "id": "kb_001",
                "title": "Password Reset Instructions",
                "content": "To reset your password, go to the login page and click 'Forgot Password'. Enter your email address and follow the instructions sent to your email. If you don't receive the email within 5 minutes, check your spam folder.",
                "category": "authentication",
                "intent_types": [IntentType.PASSWORD_RESET],
                "tags": ["password", "reset", "login", "email", "authentication"],
                "priority": 1,
                "last_updated": "2024-01-15"
            },
            {
                "id": "kb_002",
                "title": "Account Activation Process",
                "content": "New accounts must be activated within 24 hours of registration. Check your email for the activation link. If you don't see it, check your spam folder. You can also request a new activation email from the login page.",
                "category": "account",
                "intent_types": [IntentType.ACCOUNT_ACTIVATION],
                "tags": ["activation", "account", "email", "spam", "registration"],
                "priority": 1,
                "last_updated": "2024-01-10"
            },
            {
                "id": "kb_003",
                "title": "Premium Subscription Benefits",
                "content": "Premium subscriptions include: advanced analytics dashboard, priority customer support, full API access with higher rate limits, unlimited storage, custom integrations, and early access to new features. Upgrade anytime in your account settings.",
                "category": "subscription",
                "intent_types": [IntentType.SUBSCRIPTION_INQUIRY],
                "tags": ["premium", "subscription", "features", "upgrade", "analytics", "api", "storage"],
                "priority": 2,
                "last_updated": "2024-01-20"
            },
            {
                "id": "kb_004",
                "title": "Mobile App Download and Setup",
                "content": "Download our mobile app from the App Store (iOS) or Google Play Store (Android). Search for 'YourApp' or use the direct links on our website. Sign in with your existing account credentials. The app supports all premium features.",
                "category": "mobile",
                "intent_types": [IntentType.MOBILE_APP_SUPPORT],
                "tags": ["mobile", "app", "installation", "download", "ios", "android", "setup"],
                "priority": 2,
                "last_updated": "2024-01-18"
            },
            {
                "id": "kb_005",
                "title": "API Integration Documentation",
                "content": "Our REST API supports authentication via API keys or OAuth 2.0. Rate limits: 1000 requests/hour for free accounts, 10,000/hour for premium. All endpoints return JSON. See our developer documentation for complete API reference, SDKs, and integration examples.",
                "category": "integration",
                "intent_types": [IntentType.API_INTEGRATION],
                "tags": ["api", "integration", "rest", "authentication", "oauth", "rate", "limits", "json", "sdk"],
                "priority": 3,
                "last_updated": "2024-01-22"
            },
            {
                "id": "kb_006",
                "title": "Troubleshooting Mobile App Issues",
                "content": "Common mobile app issues: 1) Login problems - clear app cache and restart. 2) Sync issues - check internet connection and try manual sync. 3) Premium features not working - verify subscription status in account settings. 4) App crashes - update to latest version.",
                "category": "troubleshooting",
                "intent_types": [IntentType.MOBILE_APP_SUPPORT, IntentType.SUBSCRIPTION_INQUIRY],
                "tags": ["mobile", "app", "troubleshooting", "login", "sync", "premium", "crashes"],
                "priority": 2,
                "last_updated": "2024-01-25"
            }
        ]

    def search_by_intent(self, intent: Intent, limit: int = 3) -> List[Dict[str, Any]]:
        """Search knowledge base by classified intent"""
        results = []

        for item in self.knowledge_items:
            score = 0

            # Intent type match (highest priority)
            if intent.type in item["intent_types"]:
                score += 10

            # Entity matches
            for entity in intent.entities:
                if entity.value.lower() in item["content"].lower():
                    score += 5 * entity.confidence
                if entity.value.lower() in item["tags"]:
                    score += 3 * entity.confidence

            # Priority boost
            score += (4 - item["priority"])

            if score > 0:
                results.append({
                    **item,
                    "relevance_score": score
                })

        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

class StrandsWorkflowEngine:
    """Simulated Strands Agents SDK workflow engine"""

    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client
        self.intent_classifier = IntentClassifier()
        self.knowledge_base = EnhancedKnowledgeBase()
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

    async def execute_workflow(self, query: str) -> EnhancedQueryResult:
        """Execute the enhanced agent workflow"""
        start_time = time.time()
        workflow_steps = []

        try:
            # Step 1: Intent Classification
            step_start = time.time()
            intent = self.intent_classifier.classify(query)
            workflow_steps.append(WorkflowStep(
                name="intent_classification",
                status="completed",
                duration=time.time() - step_start,
                output=asdict(intent)
            ))

            # Step 2: Entity Extraction (already done in classification)
            step_start = time.time()
            # Entities are extracted as part of intent classification
            workflow_steps.append(WorkflowStep(
                name="entity_extraction",
                status="completed",
                duration=time.time() - step_start,
                output={"entities": [asdict(e) for e in intent.entities]}
            ))

            # Step 3: Knowledge Retrieval
            step_start = time.time()
            kb_results = self.knowledge_base.search_by_intent(intent)
            workflow_steps.append(WorkflowStep(
                name="knowledge_retrieval",
                status="completed",
                duration=time.time() - step_start,
                output={"results_count": len(kb_results), "top_result": kb_results[0]["title"] if kb_results else None}
            ))

            # Step 4: Context Preparation
            step_start = time.time()
            context = self._prepare_enhanced_context(intent, kb_results)
            workflow_steps.append(WorkflowStep(
                name="context_preparation",
                status="completed",
                duration=time.time() - step_start,
                output={"context_length": len(context)}
            ))

            # Step 5: Response Generation
            step_start = time.time()
            response = await self._generate_enhanced_response(query, intent, context)
            workflow_steps.append(WorkflowStep(
                name="response_generation",
                status="completed",
                duration=time.time() - step_start,
                output={"response_length": len(response)}
            ))

            total_time = time.time() - start_time

            # Calculate enhanced confidence
            confidence = self._calculate_confidence(intent, kb_results, workflow_steps)

            sources = [item["title"] for item in kb_results]

            return EnhancedQueryResult(
                query=query,
                intent=intent,
                workflow_steps=workflow_steps,
                response=response,
                response_time=total_time,
                confidence=confidence,
                sources=sources,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")

            # Add error step
            workflow_steps.append(WorkflowStep(
                name="error_handling",
                status="failed",
                duration=time.time() - start_time,
                output=None,
                error=str(e)
            ))

            return EnhancedQueryResult(
                query=query,
                intent=Intent(IntentType.GENERAL_INQUIRY, 0.0, []),
                workflow_steps=workflow_steps,
                response=f"I apologize, but I encountered an error processing your request: {str(e)}",
                response_time=time.time() - start_time,
                confidence=0.0,
                sources=[],
                timestamp=datetime.now()
            )

    def _prepare_enhanced_context(self, intent: Intent, kb_results: List[Dict[str, Any]]) -> str:
        """Prepare enhanced context with intent and entity information"""
        if not kb_results:
            return f"No specific information found for intent: {intent.type.value}"

        context_parts = [
            f"User Intent: {intent.type.value} (confidence: {intent.confidence:.2f})"
        ]

        if intent.entities:
            entities_str = ", ".join([f"{e.type}: {e.value}" for e in intent.entities])
            context_parts.append(f"Extracted Entities: {entities_str}")

        context_parts.append("Relevant Knowledge Base Articles:")

        for i, item in enumerate(kb_results, 1):
            context_parts.append(f"\n{i}. {item['title']} (Score: {item['relevance_score']:.1f})")
            context_parts.append(f"   Content: {item['content']}")
            context_parts.append(f"   Category: {item['category']}")
            context_parts.append(f"   Last Updated: {item['last_updated']}")

        return "\n".join(context_parts)

    async def _generate_enhanced_response(self, query: str, intent: Intent, context: str) -> str:
        """Generate enhanced response using intent-aware prompting"""

        # Intent-specific prompt templates
        intent_prompts = {
            IntentType.PASSWORD_RESET: "You are helping a user reset their password. Be clear and step-by-step.",
            IntentType.ACCOUNT_ACTIVATION: "You are helping a user activate their account. Be encouraging and helpful.",
            IntentType.SUBSCRIPTION_INQUIRY: "You are helping a user understand subscription benefits. Be informative and persuasive.",
            IntentType.MOBILE_APP_SUPPORT: "You are helping a user with mobile app issues. Be practical and solution-focused.",
            IntentType.API_INTEGRATION: "You are helping a developer with API integration. Be technical and precise.",
            IntentType.GENERAL_INQUIRY: "You are a helpful customer support agent. Be friendly and comprehensive."
        }

        intent_instruction = intent_prompts.get(intent.type, intent_prompts[IntentType.GENERAL_INQUIRY])

        prompt = f"""
{intent_instruction}

Context Information:
{context}

User Question: {query}

Please provide a helpful, accurate, and contextually appropriate response. If the context contains relevant information, use it to give a comprehensive answer. If not, acknowledge the limitation and provide general guidance.


Assistant: I'll help you with your request based on the available information and context.
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

    def _calculate_confidence(self, intent: Intent, kb_results: List[Dict[str, Any]], workflow_steps: List[WorkflowStep]) -> float:
        """Calculate overall confidence score based on workflow results"""
        base_confidence = intent.confidence

        # Boost confidence based on knowledge base matches
        if kb_results:
            kb_boost = min(0.3, len(kb_results) * 0.1)
            base_confidence += kb_boost

        # Reduce confidence if any workflow steps failed
        failed_steps = [step for step in workflow_steps if step.status == "failed"]
        if failed_steps:
            base_confidence *= 0.5

        # Boost confidence for successful entity extraction
        entities_found = any(step.name == "entity_extraction" and step.output.get("entities")
                           for step in workflow_steps)
        if entities_found:
            base_confidence += 0.1

        return min(0.95, base_confidence)

class StrandsEnhancedAgent:
    """Enhanced agent using Strands SDK workflow engine"""

    def __init__(self):
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.workflow_engine = StrandsWorkflowEngine(self.bedrock_client)

    async def query(self, user_query: str) -> EnhancedQueryResult:
        """Process a user query using the enhanced workflow"""
        return await self.workflow_engine.execute_workflow(user_query)

async def demonstrate_strands_enhanced():
    """Demonstrate the Strands-enhanced implementation"""
    print("=" * 60)
    print("STAGE 2: Strands Agents SDK Enhanced Demo")
    print("=" * 60)
    print()

    agent = StrandsEnhancedAgent()

    # Test queries that show improvements and remaining limitations
    test_queries = [
        "How do I reset my password?",
        "My premium subscription isn't working with the new mobile app",
        "Integration issues with third-party APIs causing data sync problems",
        "What are the benefits of upgrading to premium?",
        "I can't activate my account, the email isn't coming through"
    ]

    results = []

    for query in test_queries:
        print(f"🔍 Query: {query}")
        print("-" * 40)

        result = await agent.query(query)
        results.append(result)

        print(f"🎯 Intent: {result.intent.type.value} (confidence: {result.intent.confidence:.2f})")
        print(f"🏷️  Entities: {', '.join([f'{e.type}:{e.value}' for e in result.intent.entities]) if result.intent.entities else 'None'}")
        print(f"⚙️  Workflow Steps: {len(result.workflow_steps)} steps")

        # Show workflow execution
        for step in result.workflow_steps:
            status_icon = "✅" if step.status == "completed" else "❌"
            print(f"   {status_icon} {step.name}: {step.duration:.3f}s")

        print(f"⏱️  Total Response Time: {result.response_time:.2f}s")
        print(f"🎯 Confidence: {result.confidence:.2f}")
        print(f"📚 Sources: {', '.join(result.sources) if result.sources else 'None'}")
        print(f"💬 Response: {result.response}")
        print()
        print("=" * 60)
        print()

    # Summary statistics
    avg_response_time = sum(r.response_time for r in results) / len(results)
    avg_confidence = sum(r.confidence for r in results) / len(results)
    avg_workflow_steps = sum(len(r.workflow_steps) for r in results) / len(results)

    print("📊 STAGE 2 SUMMARY STATISTICS")
    print("-" * 30)
    print(f"Average Response Time: {avg_response_time:.2f}s")
    print(f"Average Confidence: {avg_confidence:.2f}")
    print(f"Average Workflow Steps: {avg_workflow_steps:.1f}")
    print(f"Total Queries Processed: {len(results)}")
    print()
    print("✅ IMPROVEMENTS OBSERVED:")
    print("• Structured workflow execution")
    print("• Intent classification and entity extraction")
    print("• Better context preparation")
    print("• Enhanced confidence scoring")
    print("• Detailed execution tracking")
    print()
    print("🚨 REMAINING LIMITATIONS:")
    print("• Still using simple keyword matching")
    print("• No semantic search capabilities")
    print("• Limited relationship understanding")
    print("• SQLite-based storage constraints")
    print("• No vector embeddings or similarity search")
    print()

    return results

if __name__ == "__main__":
    # Run the demonstration
    results = asyncio.run(demonstrate_strands_enhanced())

    # Save results for comparison
    output_file = "data/performance_metrics/stage2_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump([
            {
                "query": r.query,
                "intent_type": r.intent.type.value,
                "intent_confidence": r.intent.confidence,
                "entities": [asdict(e) for e in r.intent.entities],
                "workflow_steps": [asdict(step) for step in r.workflow_steps],
                "response_time": r.response_time,
                "confidence": r.confidence,
                "sources": r.sources,
                "timestamp": r.timestamp.isoformat()
            }
            for r in results
        ], f, indent=2)

    print(f"📁 Results saved to: {output_file}")