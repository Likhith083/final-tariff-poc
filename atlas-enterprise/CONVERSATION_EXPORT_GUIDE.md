# 📁 Conversation Export Feature Guide

## Overview

The **Conversation Export** feature allows users to export their AI chat conversations in multiple formats with customizable options. This is perfect for documentation, sharing insights, compliance records, and creating reports from AI interactions.

## 🌟 Key Features

### Multiple Export Formats
- **JSON**: Structured data format with full metadata
- **PDF**: Professional document format for printing and sharing
- **HTML**: Web format with rich styling and interactive elements
- **Markdown**: Documentation-friendly format with markup
- **Excel**: Spreadsheet format for data analysis and processing
- **Text**: Plain text format for simple viewing
- **CSV**: Comma-separated values for data import/analysis

### Export Templates
- **Standard**: Default template with balanced detail
- **Professional**: Formal template for business use
- **Detailed**: Comprehensive template with all metadata
- **Summary**: Condensed template with key information only

### Customization Options
- **Include/Exclude Metadata**: Conversation statistics and details
- **Timestamps**: Show when each message was sent
- **System Messages**: Include internal system communications
- **Knowledge Updates**: Show when knowledge base was updated
- **Data Anonymization**: Remove personal information for sharing
- **Custom Headers/Footers**: Add your own branding or notes

## 🚀 How to Use

### 1. Single Conversation Export

#### Via API
```bash
# Get export options for a conversation
curl -X GET "http://localhost:8000/api/v1/conversations/{conversation_id}/export-options"

# Export conversation as PDF with professional template
curl -X POST "http://localhost:8000/api/v1/conversations/{conversation_id}/export?format=pdf&template=professional&include_metadata=true&custom_title=My%20Conversation%20Export"

# Download the exported file
curl -X GET "http://localhost:8000/api/v1/conversations/download/{export_id}" -o "conversation.pdf"
```

#### Via React Component
```typescript
import { ConversationExport } from './components/ChatExport';
import { useChatExport } from './hooks/useChatExport';

function ChatInterface() {
  const [showExport, setShowExport] = useState(false);
  const { exportConversation } = useChatExport();
  
  const handleExport = async (exportId: string, format: string) => {
    console.log(`Exported as ${format} with ID: ${exportId}`);
  };
  
  return (
    <>
      <button onClick={() => setShowExport(true)}>
        Export Conversation
      </button>
      
      <ConversationExport
        conversationId="conv_123"
        isOpen={showExport}
        onClose={() => setShowExport(false)}
        onExport={handleExport}
      />
    </>
  );
}
```

### 2. Bulk Export

Export multiple conversations as a ZIP archive:

```bash
# Start bulk export
curl -X POST "http://localhost:8000/api/v1/conversations/bulk-export" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_ids": ["conv_1", "conv_2", "conv_3"],
    "format": "pdf",
    "template": "professional",
    "include_metadata": true
  }'

# Check bulk export status
curl -X GET "http://localhost:8000/api/v1/conversations/bulk-export-status/{bulk_export_id}"

# Download bulk export when complete
curl -X GET "http://localhost:8000/api/v1/conversations/download/{bulk_export_id}" -o "conversations.zip"
```

## 📋 Export Format Examples

### JSON Export
```json
{
  "export_id": "exp_abc123",
  "export_date": "2024-01-15T10:30:00Z",
  "conversation": {
    "id": "conv_123",
    "messages": [
      {
        "role": "user",
        "content": "What are the tariff rates for electronics?",
        "timestamp": "2024-01-15T10:00:00Z",
        "is_knowledge_update": false
      },
      {
        "role": "assistant", 
        "content": "Electronics tariff rates vary by product category...",
        "timestamp": "2024-01-15T10:00:05Z",
        "is_knowledge_update": false
      }
    ],
    "message_count": 8
  }
}
```

### PDF Export Features
- Professional formatting with ATLAS branding
- Color-coded message bubbles (user vs assistant)
- Metadata table with conversation statistics
- Custom headers and footers
- Page numbering and table of contents (for long conversations)
- Print-friendly layout

### HTML Export Features
- Interactive web format
- Responsive design for all devices
- Syntax highlighting for code blocks
- Expandable/collapsible sections
- Search functionality
- Social sharing buttons

### Excel Export Features
- Separate sheets for metadata and messages
- Colored rows for different message types
- Filterable columns
- Message length statistics
- Timestamp formatting
- Formula-ready data structure

## 🎨 Customization Examples

### Professional Business Export
```javascript
const businessExportOptions = {
  format: 'pdf',
  template: 'professional',
  include_metadata: true,
  include_timestamps: true,
  include_system_messages: false,
  include_knowledge_updates: true,
  anonymize_user_data: false,
  custom_title: 'Trade Compliance Consultation - Q1 2024',
  custom_header: 'ATLAS Enterprise - Confidential Business Consultation',
  custom_footer: 'This document contains proprietary trade compliance insights. Do not distribute.'
};
```

### Research Documentation Export
```javascript
const researchExportOptions = {
  format: 'markdown',
  template: 'detailed',
  include_metadata: true,
  include_timestamps: true,
  include_system_messages: true,
  include_knowledge_updates: true,
  anonymize_user_data: true,
  custom_title: 'AI Trade Compliance Research Session',
  custom_header: '# Research Notes - Trade Compliance Analysis',
  custom_footer: 'Generated by ATLAS Enterprise AI Assistant'
};
```

### Data Analysis Export
```javascript
const dataAnalysisOptions = {
  format: 'csv',
  template: 'standard',
  include_metadata: false,
  include_timestamps: true,
  include_system_messages: false,
  include_knowledge_updates: false,
  anonymize_user_data: true
};
```

## 🔒 Security & Privacy

### Data Protection
- **Anonymization**: Automatically removes emails, phone numbers, and other PII
- **Access Control**: Only conversation participants can export
- **Audit Logging**: All export activities are logged for compliance
- **Temporary Storage**: Export files are automatically cleaned up after 24 hours

### Compliance Features
- **GDPR Compliance**: Full data portability and right to erasure
- **SOC 2 Ready**: Comprehensive audit trails and security controls
- **Data Encryption**: All exports are encrypted during generation and storage
- **Retention Policies**: Configurable data retention for different export types

## 📊 Analytics & Monitoring

### Export Metrics
- Number of exports per user/organization
- Popular export formats and templates
- Export file sizes and processing times
- Failed export attempts and error analysis

### Performance Optimization
- **Caching**: Frequently exported conversations are cached
- **Background Processing**: Large exports don't block the UI
- **Compression**: ZIP archives for bulk exports save bandwidth
- **CDN Integration**: Fast global download speeds

## 🛠️ Advanced Usage

### Automated Exports
Schedule regular exports using the API:

```python
import asyncio
import aiohttp

async def schedule_weekly_export():
    """Export all conversations from the past week"""
    async with aiohttp.ClientSession() as session:
        # Get recent conversations
        conversations = await get_recent_conversations(session, days=7)
        
        # Start bulk export
        export_result = await session.post(
            '/api/v1/conversations/bulk-export',
            json={
                'conversation_ids': [c['id'] for c in conversations],
                'format': 'pdf',
                'template': 'summary',
                'include_metadata': True
            }
        )
        
        # Monitor progress and download when complete
        bulk_id = export_result['bulk_export_id']
        await monitor_and_download(session, bulk_id)

# Run weekly
asyncio.create_task(schedule_weekly_export())
```

### Integration with External Systems
```python
# Export to SharePoint
async def export_to_sharepoint(conversation_id: str):
    export_result = await export_conversation(
        conversation_id, 
        format='pdf',
        template='professional'
    )
    
    # Upload to SharePoint
    await sharepoint_client.upload(
        export_result['file_path'],
        folder='AI Conversations',
        metadata={
            'conversation_id': conversation_id,
            'export_date': export_result['export_date']
        }
    )

# Export to Slack
async def share_to_slack(conversation_id: str, channel: str):
    export_result = await export_conversation(
        conversation_id,
        format='html',
        template='summary'
    )
    
    await slack_client.share_file(
        channel=channel,
        file_path=export_result['file_path'],
        title='AI Conversation Summary'
    )
```

## 🎯 Use Cases

### 1. Business Documentation
- **Client Consultations**: Export professional PDFs for client records
- **Training Materials**: Create training documents from AI interactions
- **Compliance Records**: Maintain audit trails for regulatory compliance

### 2. Research & Analysis
- **Academic Research**: Export conversations for analysis and citation
- **Market Intelligence**: Analyze patterns in trade compliance questions
- **Knowledge Management**: Build organizational knowledge bases

### 3. Team Collaboration
- **Knowledge Sharing**: Share insights across teams via exports
- **Meeting Preparation**: Export relevant conversations before meetings
- **Documentation**: Create project documentation from AI consultations

### 4. Customer Support
- **Case Resolution**: Export conversation history for support tickets
- **Training**: Use successful conversations for agent training
- **Quality Assurance**: Review and analyze support interactions

## 🔧 Configuration

### Environment Variables
```bash
# Export service configuration
EXPORT_CLEANUP_HOURS=24
EXPORT_MAX_FILE_SIZE=100MB
EXPORT_MAX_BULK_CONVERSATIONS=50
EXPORT_STORAGE_PATH=/data/exports
EXPORT_TEMP_PATH=/data/temp

# PDF generation settings
PDF_FONT_SIZE=12
PDF_PAGE_SIZE=letter
PDF_ENABLE_TOC=true

# Security settings
EXPORT_REQUIRE_AUTHENTICATION=true
EXPORT_ENABLE_ANONYMIZATION=true
EXPORT_LOG_ALL_ACTIVITIES=true
```

### Customization
```python
# Custom export templates
EXPORT_TEMPLATES = {
    'corporate': {
        'name': 'Corporate Standard',
        'description': 'Company-branded template with logo',
        'logo_path': '/assets/company-logo.png',
        'color_scheme': '#1a365d'
    },
    'technical': {
        'name': 'Technical Documentation',
        'description': 'Template optimized for technical content',
        'code_highlighting': True,
        'include_diagrams': True
    }
}
```

## 📞 Support

### Troubleshooting
- **Large Files**: Use bulk export for multiple conversations
- **Slow Generation**: PDF exports may take longer for long conversations
- **Download Issues**: Check network connectivity and file permissions

### API Rate Limits
- Standard users: 10 exports per hour
- Premium users: 50 exports per hour
- Enterprise: Unlimited exports

### Contact
- **Documentation**: [ATLAS Enterprise Docs](https://docs.atlas-enterprise.com)
- **Support**: support@atlas-enterprise.com
- **API Issues**: api-support@atlas-enterprise.com

---

**🎉 Start Exporting Your Conversations Today!**

The conversation export feature makes it easy to preserve, share, and analyze your AI interactions. Whether you need professional documentation, research data, or simple conversation backups, ATLAS Enterprise has you covered with flexible, secure, and powerful export capabilities. 