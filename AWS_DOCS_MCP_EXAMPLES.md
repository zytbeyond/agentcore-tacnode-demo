# AWS Documentation MCP Server - Usage Examples

## Available Tools

### 1. search_documentation
Search AWS documentation for specific topics.

**Example:**
```python
search_documentation("S3 bucket naming rules", 5)
search_documentation("Lambda function configuration", 3)
search_documentation("EC2 instance types", 10)
```

### 2. read_documentation  
Read and convert AWS documentation pages to markdown.

**Example:**
```python
read_documentation("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
read_documentation("https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html")
```

### 3. recommend
Get content recommendations for AWS documentation pages.

**Example:**
```python
recommend("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
```

## Integration with AI Agents

The AWS Documentation MCP server enables AI agents to:

1. **Real-time Documentation Access**: Query the latest AWS documentation
2. **Contextual Search**: Find relevant AWS docs based on user questions
3. **Content Recommendations**: Discover related AWS documentation
4. **Markdown Conversion**: Get documentation in AI-friendly format

## Example AI Agent Queries

- "What are the S3 bucket naming rules?"
- "How do I configure Lambda function memory?"
- "What are the different EC2 instance types?"
- "Show me documentation about VPC security groups"
- "Find information about RDS backup strategies"

## Benefits

- ✅ Always up-to-date AWS documentation
- ✅ Intelligent search capabilities  
- ✅ Content recommendations
- ✅ Markdown formatting for AI processing
- ✅ Real-time access to AWS knowledge base
