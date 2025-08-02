# 🚀 AgentCore + Strands + Tacnode Demo Instructions

## 📋 **Quick Start Guide**

### **Prerequisites**
- AWS Account with credentials configured
- Python 3.9+ installed
- Git installed
- Terminal/Command line access

### **1. Clone the Repository**
```bash
git clone https://github.com/zytbeyond/agentcore-tacnode-demo.git
cd agentcore-tacnode-demo
```

### **2. Install Dependencies**
```bash
pip install boto3 python-dotenv
```

### **3. Configure AWS Credentials**
Make sure your AWS credentials are configured for **us-east-1** region:
```bash
aws configure
# OR set environment variables:
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

---

## 🎯 **Demo Execution**

### **Stage 1: AgentCore + DynamoDB (Current)**
```bash
cd ai-agent-integration-demo
python3 src/stage1_basic_agentcore.py
```

**What This Demonstrates:**
- Real AgentCore + DynamoDB integration
- Enterprise incident scenarios with financial impact
- 11+ second response times showing database limitations
- $1B+ annual projected losses due to slow performance

**Expected Output:**
```
🚨 ENTERPRISE INCIDENT: Trading system latency spiked to 50ms - we're losing millions per minute
⏱️  Response Time: 15.06s (🔴 CRITICAL DELAY)
💰 Business Impact: $753,147/minute potential loss
```

### **Stage 2: + Strands SDK (Coming Next)**
```bash
# Will be available after Tacnode integration
python3 src/stage2_strands_enhanced.py
```

### **Stage 3: + Tacnode Complete (Final)**
```bash
# Will show dramatic improvement with Tacnode
python3 src/stage3_tacnode_complete.py
```

---

## 📊 **What Each Stage Shows**

### **Stage 1 Results (AgentCore + DynamoDB)**
- ⏱️ **Average Response Time**: 11.54s (TARGET: <1.0s)
- 💰 **Business Cost**: $1,031,618,591 annual projected loss
- 🚨 **Critical Delays**: 7/7 incidents over 3 seconds
- 📊 **Average Incident Cost**: $403,765 per delay

### **Stage 2 Results (+ Strands SDK)**
- ⏱️ **Expected**: ~7-8s response time
- 💰 **Expected**: ~$600M annual loss
- ✅ **Improvements**: Better workflows, structured processing
- ❌ **Still Limited**: Database bottlenecks remain

### **Stage 3 Results (+ Tacnode)**
- ⏱️ **Target**: <1s response time (75% faster)
- 💰 **Target**: <$200M annual loss (80% reduction)
- ✅ **Breakthrough**: Semantic search, graph relationships, real-time analytics

---

## 🎯 **Demo Presentation Flow**

### **Opening Hook (2 minutes)**
*"I'm about to show you how a single database decision can cost your enterprise $10 million per year - and how the right choice can create $20 million in competitive advantage."*

### **Stage 1 Demo (8 minutes)**
1. **Run the demo**: `python3 src/stage1_basic_agentcore.py`
2. **Highlight key metrics**:
   - 11+ second delays for critical incidents
   - $400K+ cost per incident delay
   - Real AgentCore + DynamoDB infrastructure
3. **Key message**: *"AgentCore + DynamoDB gives us persistence and scale, but we're still missing AI-optimized database capabilities."*

### **Business Impact Moment (3 minutes)**
- **Point out**: $1B+ annual projected losses
- **Emphasize**: 7/7 incidents showing critical delays
- **Ask audience**: *"How many of you have experienced similar delays in production?"*

### **Solution Setup (2 minutes)**
*"This is exactly why you need the complete stack. AgentCore gives you LLM orchestration, Strands gives you workflows, but Tacnode completes the picture with enterprise-grade AI database performance."*

---

## 🗄️ **DynamoDB Integration Details**

### **Table Information**
- **Table Name**: `AgentCoreContextStore`
- **Region**: us-east-1
- **Schema**: session_id (PK), timestamp (SK)
- **GSI**: ContextTypeIndex for efficient querying

### **What Gets Stored**
- Enterprise knowledge base items
- Conversation history and context
- Performance metrics and metadata
- Real-time interaction data

### **Verify DynamoDB Setup**
```bash
# Check if table exists and has data
python3 analyze_agentcore_dynamodb.py
```

---

## 🎯 **Key Demo Talking Points**

### **Technical Audience**
- "Notice the 11+ second response times even with AWS-native infrastructure"
- "DynamoDB provides scale but lacks semantic search and graph relationships"
- "This demonstrates why AI workloads need specialized database architecture"

### **Business Audience**
- "$400K average cost per incident delay"
- "$1B+ annual losses due to slow AI agent responses"
- "75% faster performance = millions in competitive advantage"

### **Executive Audience**
- "Single database decision: $10M problem vs $20M opportunity"
- "Real enterprise scenarios: trading losses, security breaches, compliance violations"
- "Complete stack ROI: 600% return in first year"

---

## 🔧 **Troubleshooting**

### **Common Issues**

**1. AWS Credentials Error**
```bash
# Solution: Configure AWS credentials
aws configure
# Or check IAM permissions for DynamoDB access
```

**2. DynamoDB Table Not Found**
```bash
# Solution: Run setup script
python3 setup_agentcore_dynamodb.py
```

**3. Import Errors**
```bash
# Solution: Install dependencies
pip install boto3 python-dotenv
```

**4. Region Issues**
```bash
# Solution: Ensure us-east-1 region
export AWS_DEFAULT_REGION=us-east-1
```

### **Verify Setup**
```bash
# Check AgentCore status
python3 check_agentcore_status.py

# Test DynamoDB client
python3 agentcore_dynamodb_client.py

# Analyze current setup
python3 analyze_agentcore_dynamodb.py
```

---

## 📚 **Additional Resources**

### **Documentation**
- `README_AGENTCORE_INTEGRATION.md` - Complete setup guide
- `US_EAST_1_SETUP_COMPLETE.md` - Region-specific setup
- `BUSINESS_IMPACT_SHOWCASE.md` - ROI calculations
- `ENTERPRISE_DEMO_TRANSFORMATION_SUMMARY.md` - Demo enhancement details

### **Demo Materials**
- `ai-agent-integration-demo/demo-script/DEMO_SCRIPT.md` - Presentation script
- `ai-agent-integration-demo/BUSINESS_IMPACT_SHOWCASE.md` - Business case

### **Architecture**
- AgentCore + DynamoDB integration working
- Strands SDK integration ready
- Tacnode completion planned

---

## 🎉 **Success Metrics**

**Demo is successful when audience:**
- ✅ Understands the $10M problem (slow AI agents)
- ✅ Sees real infrastructure in action (AgentCore + DynamoDB)
- ✅ Recognizes database limitations even with AWS-native stack
- ✅ Wants to see the complete solution (+ Tacnode)
- ✅ Asks about implementation timeline and ROI

**Ready to demonstrate the power of AgentCore + Strands + Tacnode!** 🚀
