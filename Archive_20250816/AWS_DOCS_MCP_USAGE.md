# AWS Documentation MCP Server Usage Guide

## Available Tools

1. **read_documentation(url)** - Fetch and convert AWS documentation pages to markdown
2. **search_documentation(search_phrase, limit)** - Search AWS documentation 
3. **recommend(url)** - Get content recommendations for AWS documentation pages

## Example Usage

### Search for S3 documentation
```
search_documentation("S3 bucket naming rules", 5)
```

### Read specific documentation page
```
read_documentation("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
```

### Get recommendations for a page
```
recommend("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
```

## Integration

The MCP server is now available for integration with AI assistants and can provide:
- Real-time access to AWS documentation
- Search capabilities across AWS docs
- Content recommendations
- Markdown-formatted documentation for easy processing
