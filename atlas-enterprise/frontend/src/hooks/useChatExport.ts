import { useState, useCallback } from 'react';
import { useToast } from './use-toast';

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

interface ExportResult {
  success: boolean;
  export_id?: string;
  file_name?: string;
  file_size?: number;
  download_url?: string;
  format?: string;
  error?: string;
}

interface BulkExportResult {
  success: boolean;
  bulk_export_id?: string;
  total_conversations?: number;
  status?: string;
  status_url?: string;
  error?: string;
}

interface BulkExportStatus {
  status: string;
  progress: number;
  total: number;
  completed: number;
  failed: number;
  download_url?: string;
  zip_size?: number;
  error?: string;
}

export const useChatExport = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [isBulkExporting, setIsBulkExporting] = useState(false);
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [bulkExportStatus, setBulkExportStatus] = useState<BulkExportStatus | null>(null);
  const { toast } = useToast();

  // Get export options for a conversation
  const getExportOptions = useCallback(async (conversationId: string) => {
    try {
      const response = await fetch(`/api/v1/conversations/${conversationId}/export-options`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get export options');
      }
      
      return data;
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load export options",
        variant: "destructive"
      });
      throw error;
    }
  }, [toast]);

  // Export a single conversation
  const exportConversation = useCallback(async (
    conversationId: string, 
    options: ExportOptions
  ): Promise<ExportResult> => {
    setIsExporting(true);
    setExportResult(null);

    try {
      const queryParams = new URLSearchParams({
        format: options.format,
        template: options.template,
        include_metadata: options.include_metadata.toString(),
        include_timestamps: options.include_timestamps.toString(),
        include_system_messages: options.include_system_messages.toString(),
        include_knowledge_updates: options.include_knowledge_updates.toString(),
        anonymize_user_data: options.anonymize_user_data.toString()
      });

      // Add optional fields
      if (options.custom_title) {
        queryParams.append('custom_title', options.custom_title);
      }
      if (options.custom_header) {
        queryParams.append('custom_header', options.custom_header);
      }
      if (options.custom_footer) {
        queryParams.append('custom_footer', options.custom_footer);
      }

      const response = await fetch(
        `/api/v1/conversations/${conversationId}/export?${queryParams}`,
        { method: 'POST' }
      );
      
      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.detail || result.error || 'Export failed');
      }

      setExportResult(result);
      
      toast({
        title: "Export Successful",
        description: `Conversation exported as ${result.format.toUpperCase()}`,
      });

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      toast({
        title: "Export Failed",
        description: errorMessage,
        variant: "destructive"
      });
      throw error;
    } finally {
      setIsExporting(false);
    }
  }, [toast]);

  // Export multiple conversations (bulk export)
  const exportConversationsBulk = useCallback(async (
    conversationIds: string[],
    options: Partial<ExportOptions> = {}
  ): Promise<BulkExportResult> => {
    setIsBulkExporting(true);
    setBulkExportStatus(null);

    try {
      const requestData = {
        conversation_ids: conversationIds,
        format: options.format || 'json',
        template: options.template || 'standard',
        include_metadata: options.include_metadata ?? true
      };

      const response = await fetch('/api/v1/conversations/bulk-export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.detail || result.error || 'Bulk export failed');
      }

      toast({
        title: "Bulk Export Started",
        description: `Exporting ${result.total_conversations} conversations`,
      });

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Bulk export failed';
      toast({
        title: "Bulk Export Failed",
        description: errorMessage,
        variant: "destructive"
      });
      throw error;
    } finally {
      setIsBulkExporting(false);
    }
  }, [toast]);

  // Check bulk export status
  const checkBulkExportStatus = useCallback(async (bulkExportId: string): Promise<BulkExportStatus> => {
    try {
      const response = await fetch(`/api/v1/conversations/bulk-export-status/${bulkExportId}`);
      const status = await response.json();

      if (!response.ok) {
        throw new Error(status.detail || 'Failed to get bulk export status');
      }

      setBulkExportStatus(status);
      return status;
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to check bulk export status",
        variant: "destructive"
      });
      throw error;
    }
  }, [toast]);

  // Download exported file
  const downloadExportedFile = useCallback(async (downloadUrl: string, fileName?: string) => {
    try {
      const response = await fetch(downloadUrl);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName || 'conversation-export';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Download Complete",
        description: "File downloaded successfully",
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to download the exported file",
        variant: "destructive"
      });
      throw error;
    }
  }, [toast]);

  // Monitor bulk export progress
  const monitorBulkExport = useCallback(async (
    bulkExportId: string,
    onProgress?: (status: BulkExportStatus) => void,
    onComplete?: (status: BulkExportStatus) => void,
    onError?: (error: string) => void
  ) => {
    const checkProgress = async () => {
      try {
        const status = await checkBulkExportStatus(bulkExportId);
        
        if (onProgress) {
          onProgress(status);
        }

        if (status.status === 'completed') {
          if (onComplete) {
            onComplete(status);
          }
          toast({
            title: "Bulk Export Complete",
            description: `${status.completed} conversations exported successfully`,
          });
          return;
        } else if (status.status === 'failed') {
          if (onError) {
            onError(status.error || 'Bulk export failed');
          }
          toast({
            title: "Bulk Export Failed",
            description: status.error || 'Unknown error occurred',
            variant: "destructive"
          });
          return;
        } else if (status.status === 'processing') {
          // Continue monitoring
          setTimeout(checkProgress, 2000); // Check every 2 seconds
        }
      } catch (error) {
        if (onError) {
          onError(error instanceof Error ? error.message : 'Status check failed');
        }
      }
    };

    checkProgress();
  }, [checkBulkExportStatus, toast]);

  // Utility function to format file size
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // Clear export state
  const clearExportState = useCallback(() => {
    setExportResult(null);
    setBulkExportStatus(null);
  }, []);

  return {
    // State
    isExporting,
    isBulkExporting,
    exportResult,
    bulkExportStatus,

    // Functions
    getExportOptions,
    exportConversation,
    exportConversationsBulk,
    checkBulkExportStatus,
    downloadExportedFile,
    monitorBulkExport,
    formatFileSize,
    clearExportState,

    // Computed values
    hasExportResult: !!exportResult,
    hasBulkExportStatus: !!bulkExportStatus,
    isBulkExportComplete: bulkExportStatus?.status === 'completed',
    isBulkExportFailed: bulkExportStatus?.status === 'failed',
    bulkExportProgress: bulkExportStatus?.progress || 0
  };
};

// Export format configurations
export const EXPORT_FORMATS = [
  {
    value: 'json',
    name: 'JSON',
    description: 'Structured data format with full metadata',
    extension: 'json',
    mimeType: 'application/json'
  },
  {
    value: 'pdf',
    name: 'PDF',
    description: 'Professional document format for printing',
    extension: 'pdf',
    mimeType: 'application/pdf'
  },
  {
    value: 'html',
    name: 'HTML',
    description: 'Web format with rich styling and formatting',
    extension: 'html',
    mimeType: 'text/html'
  },
  {
    value: 'markdown',
    name: 'Markdown',
    description: 'Text format with markup for documentation',
    extension: 'md',
    mimeType: 'text/markdown'
  },
  {
    value: 'excel',
    name: 'Excel',
    description: 'Spreadsheet format for data analysis',
    extension: 'xlsx',
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  },
  {
    value: 'txt',
    name: 'Text',
    description: 'Plain text format for simple viewing',
    extension: 'txt',
    mimeType: 'text/plain'
  },
  {
    value: 'csv',
    name: 'CSV',
    description: 'Comma-separated values for data import',
    extension: 'csv',
    mimeType: 'text/csv'
  }
];

export const EXPORT_TEMPLATES = [
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

export default useChatExport; 