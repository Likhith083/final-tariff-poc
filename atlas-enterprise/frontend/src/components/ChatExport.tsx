import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle 
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import { 
  Download, 
  FileText, 
  FileImage, 
  FileSpreadsheet, 
  Globe, 
  Settings,
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';

interface ExportOptions {
  format: string;
  template: string;
  include_metadata: boolean;
  include_timestamps: boolean;
  include_system_messages: boolean;
  include_knowledge_updates: boolean;
  anonymize_user_data: boolean;
  custom_title?: string;
  custom_header?: string;
  custom_footer?: string;
}

interface ExportFormat {
  value: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

interface ExportTemplate {
  value: string;
  name: string;
  description: string;
}

interface ConversationExportProps {
  conversationId: string;
  isOpen: boolean;
  onClose: () => void;
  onExport?: (exportId: string, format: string) => void;
}

const exportFormats: ExportFormat[] = [
  {
    value: 'json',
    name: 'JSON',
    description: 'Structured data format with full metadata',
    icon: <FileText className="h-4 w-4" />,
    color: 'bg-blue-100 text-blue-800'
  },
  {
    value: 'pdf',
    name: 'PDF',
    description: 'Professional document format for printing',
    icon: <FileImage className="h-4 w-4" />,
    color: 'bg-red-100 text-red-800'
  },
  {
    value: 'html',
    name: 'HTML',
    description: 'Web format with rich styling and formatting',
    icon: <Globe className="h-4 w-4" />,
    color: 'bg-green-100 text-green-800'
  },
  {
    value: 'markdown',
    name: 'Markdown',
    description: 'Text format with markup for documentation',
    icon: <FileText className="h-4 w-4" />,
    color: 'bg-purple-100 text-purple-800'
  },
  {
    value: 'excel',
    name: 'Excel',
    description: 'Spreadsheet format for data analysis',
    icon: <FileSpreadsheet className="h-4 w-4" />,
    color: 'bg-emerald-100 text-emerald-800'
  },
  {
    value: 'txt',
    name: 'Text',
    description: 'Plain text format for simple viewing',
    icon: <FileText className="h-4 w-4" />,
    color: 'bg-gray-100 text-gray-800'
  },
  {
    value: 'csv',
    name: 'CSV',
    description: 'Comma-separated values for data import',
    icon: <FileSpreadsheet className="h-4 w-4" />,
    color: 'bg-yellow-100 text-yellow-800'
  }
];

const exportTemplates: ExportTemplate[] = [
  {
    value: 'standard',
    name: 'Standard',
    description: 'Default template with balanced detail'
  },
  {
    value: 'professional',
    name: 'Professional',
    description: 'Formal template for business use'
  },
  {
    value: 'detailed',
    name: 'Detailed',
    description: 'Comprehensive template with all metadata'
  },
  {
    value: 'summary',
    name: 'Summary',
    description: 'Condensed template with key information only'
  }
];

export const ConversationExport: React.FC<ConversationExportProps> = ({
  conversationId,
  isOpen,
  onClose,
  onExport
}) => {
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'json',
    template: 'standard',
    include_metadata: true,
    include_timestamps: true,
    include_system_messages: false,
    include_knowledge_updates: true,
    anonymize_user_data: false
  });

  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [conversationSummary, setConversationSummary] = useState<any>(null);

  // Load conversation export options
  useEffect(() => {
    if (isOpen && conversationId) {
      loadExportOptions();
    }
  }, [isOpen, conversationId]);

  const loadExportOptions = async () => {
    try {
      const response = await fetch(`/api/v1/conversations/${conversationId}/export-options`);
      const data = await response.json();
      
      if (response.ok) {
        setConversationSummary(data.conversation_summary);
        setError(null);
      } else {
        setError(data.detail || 'Failed to load export options');
      }
    } catch (err) {
      setError('Failed to load export options');
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    setError(null);
    setExportResult(null);

    try {
      const queryParams = new URLSearchParams({
        format: exportOptions.format,
        template: exportOptions.template,
        include_metadata: exportOptions.include_metadata.toString(),
        include_timestamps: exportOptions.include_timestamps.toString(),
        include_system_messages: exportOptions.include_system_messages.toString(),
        include_knowledge_updates: exportOptions.include_knowledge_updates.toString(),
        anonymize_user_data: exportOptions.anonymize_user_data.toString()
      });

      // Add optional fields if provided
      if (exportOptions.custom_title) {
        queryParams.append('custom_title', exportOptions.custom_title);
      }
      if (exportOptions.custom_header) {
        queryParams.append('custom_header', exportOptions.custom_header);
      }
      if (exportOptions.custom_footer) {
        queryParams.append('custom_footer', exportOptions.custom_footer);
      }

      const response = await fetch(
        `/api/v1/conversations/${conversationId}/export?${queryParams}`,
        { method: 'POST' }
      );
      
      const result = await response.json();

      if (response.ok && result.success) {
        setExportResult(result);
        if (onExport) {
          onExport(result.export_id, result.format);
        }
      } else {
        setError(result.detail || result.error || 'Export failed');
      }
    } catch (err) {
      setError('Export request failed');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownload = async () => {
    if (exportResult?.download_url) {
      try {
        const response = await fetch(exportResult.download_url);
        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = exportResult.file_name || `conversation-export.${exportOptions.format}`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else {
          setError('Download failed');
        }
      } catch (err) {
        setError('Download failed');
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const selectedFormat = exportFormats.find(f => f.value === exportOptions.format);
  const selectedTemplate = exportTemplates.find(t => t.value === exportOptions.template);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Conversation
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Conversation Summary */}
          {conversationSummary && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Conversation Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Messages:</span> {conversationSummary.message_count || 0}
                  </div>
                  <div>
                    <span className="font-medium">Created:</span> {
                      conversationSummary.start_time ? 
                      new Date(conversationSummary.start_time).toLocaleDateString() : 
                      'Unknown'
                    }
                  </div>
                  <div>
                    <span className="font-medium">Last Activity:</span> {
                      conversationSummary.last_activity ? 
                      new Date(conversationSummary.last_activity).toLocaleDateString() : 
                      'Unknown'
                    }
                  </div>
                  <div>
                    <span className="font-medium">Knowledge Updates:</span> {conversationSummary.knowledge_updates || 0}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Export Format Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Export Format</CardTitle>
              <CardDescription>
                Choose how you want to export your conversation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {exportFormats.map((format) => (
                  <Card 
                    key={format.value}
                    className={`cursor-pointer transition-all ${
                      exportOptions.format === format.value 
                        ? 'ring-2 ring-blue-500 bg-blue-50' 
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setExportOptions(prev => ({ ...prev, format: format.value }))}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        {format.icon}
                        <Badge className={format.color}>{format.name}</Badge>
                      </div>
                      <p className="text-xs text-gray-600">{format.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Template Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Template</CardTitle>
              <CardDescription>
                Select the level of detail for your export
              </CardDescription>
            </CardHeader>
            <CardContent>
              <select
                value={exportOptions.template}
                onChange={(e) => setExportOptions(prev => ({ ...prev, template: e.target.value }))}
              >
                {exportTemplates.map((template) => (
                  <option key={template.value} value={template.value}>
                    <div>
                      <div className="font-medium">{template.name}</div>
                      <div className="text-sm text-gray-500">{template.description}</div>
                    </div>
                  </option>
                ))}
              </select>
            </CardContent>
          </Card>

          {/* Export Options */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Export Options
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="include_metadata"
                      checked={exportOptions.include_metadata}
                      onChange={(e) => 
                        setExportOptions(prev => ({ ...prev, include_metadata: !!e.target.checked }))
                      }
                    />
                    <label htmlFor="include_metadata" className="text-sm">
                      Include metadata
                    </label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="include_timestamps"
                      checked={exportOptions.include_timestamps}
                      onChange={(e) => 
                        setExportOptions(prev => ({ ...prev, include_timestamps: !!e.target.checked }))
                      }
                    />
                    <label htmlFor="include_timestamps" className="text-sm">
                      Include timestamps
                    </label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="include_knowledge_updates"
                      checked={exportOptions.include_knowledge_updates}
                      onChange={(e) => 
                        setExportOptions(prev => ({ ...prev, include_knowledge_updates: !!e.target.checked }))
                      }
                    />
                    <label htmlFor="include_knowledge_updates" className="text-sm">
                      Include knowledge updates
                    </label>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="include_system_messages"
                      checked={exportOptions.include_system_messages}
                      onChange={(e) => 
                        setExportOptions(prev => ({ ...prev, include_system_messages: !!e.target.checked }))
                      }
                    />
                    <label htmlFor="include_system_messages" className="text-sm">
                      Include system messages
                    </label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="anonymize_user_data"
                      checked={exportOptions.anonymize_user_data}
                      onChange={(e) => 
                        setExportOptions(prev => ({ ...prev, anonymize_user_data: !!e.target.checked }))
                      }
                    />
                    <label htmlFor="anonymize_user_data" className="text-sm">
                      Anonymize user data
                    </label>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Custom Headers/Footers */}
              <div className="space-y-3">
                <div>
                  <label htmlFor="custom_title" className="text-sm font-medium">
                    Custom Title (optional)
                  </label>
                  <input
                    id="custom_title"
                    placeholder="Enter custom title for export"
                    value={exportOptions.custom_title || ''}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      custom_title: e.target.value || undefined 
                    }))}
                  />
                </div>

                <div>
                  <label htmlFor="custom_header" className="text-sm font-medium">
                    Custom Header (optional)
                  </label>
                  <input
                    id="custom_header"
                    placeholder="Enter custom header text"
                    value={exportOptions.custom_header || ''}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      custom_header: e.target.value || undefined 
                    }))}
                  />
                </div>

                <div>
                  <label htmlFor="custom_footer" className="text-sm font-medium">
                    Custom Footer (optional)
                  </label>
                  <input
                    id="custom_footer"
                    placeholder="Enter custom footer text"
                    value={exportOptions.custom_footer || ''}
                    onChange={(e) => setExportOptions(prev => ({ 
                      ...prev, 
                      custom_footer: e.target.value || undefined 
                    }))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Export Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Export Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  {selectedFormat?.icon}
                  <span className="font-medium">{selectedFormat?.name} Export</span>
                  <Badge variant="secondary">{selectedTemplate?.name} Template</Badge>
                </div>
                <p className="text-sm text-gray-600">{selectedFormat?.description}</p>
                
                <div className="mt-3 text-xs text-gray-500">
                  Options: {[
                    exportOptions.include_metadata && 'Metadata',
                    exportOptions.include_timestamps && 'Timestamps',
                    exportOptions.include_knowledge_updates && 'Knowledge Updates',
                    exportOptions.include_system_messages && 'System Messages',
                    exportOptions.anonymize_user_data && 'Anonymized'
                  ].filter(Boolean).join(', ') || 'Default settings'}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Error Display */}
          {error && (
            <div className="alert">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Export Result */}
          {exportResult && (
            <div className="alert">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                <div className="space-y-2">
                  <div>Export completed successfully!</div>
                  <div className="text-sm">
                    <strong>File:</strong> {exportResult.file_name}<br />
                    <strong>Size:</strong> {formatFileSize(exportResult.file_size)}<br />
                    <strong>Format:</strong> {exportResult.format.toUpperCase()}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleExport}
              disabled={isExporting}
              className="flex-1"
            >
              {isExporting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Export Conversation
                </>
              )}
            </Button>

            {exportResult && (
              <Button
                onClick={handleDownload}
                variant="outline"
              >
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            )}

            <Button onClick={onClose} variant="outline">
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ConversationExport; 