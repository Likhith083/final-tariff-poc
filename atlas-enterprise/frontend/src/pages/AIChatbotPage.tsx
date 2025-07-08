import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  MessageSquare, 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Sparkles,
  FileText,
  Calculator,
  Search,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Info,
  Settings,
  ShoppingCart,
  Upload,
  X,
  File,
  FileType,
  Plus
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useAIChat } from '@/hooks/useAI'
import ConversationExport from '@/components/ChatExport'
import { useChatExport } from '@/hooks/useChatExport'
import { mockProducts, Product } from '@/data/mockProducts'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: {
    hts_code?: string
    duty_rate?: number
    analysis_type?: string
    confidence?: number
    model?: string
    usage?: any
    product_info?: any
    error?: string
  }
}

interface QuickPrompt {
  id: string
  title: string
  prompt: string
  icon: React.ReactNode
  category: 'analysis' | 'calculation' | 'search' | 'general'
}

type ModelType = 'groq' | 'openai' | 'llava' | 'devstral:24b' | 'llama3.2:3b' | 'qwen3:8b' | 'deepseek-r1:8b' | 'moondream' | 'llama3.1' | 'gemma3:4b' | 'phi4' | string

export const AIChatbotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your ATLAS AI assistant. I can help you with:\n\n• HTS code classification and analysis\n• Tariff calculations and duty estimates\n• Trade compliance questions\n• Sourcing optimization\n• Regulatory guidance\n\nWhat would you like to know about today?',
      timestamp: new Date(),
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [selectedModel, setSelectedModel] = useState<ModelType>('groq')
  const [enableProductSearch, setEnableProductSearch] = useState(false)
  const [productQuery, setProductQuery] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [showExport, setShowExport] = useState(false)
  const [knowledgeText, setKnowledgeText] = useState('')
  const [isSubmittingKnowledge, setIsSubmittingKnowledge] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [realProducts, setRealProducts] = useState<Product[]>([])
  const [showAddProduct, setShowAddProduct] = useState(false)
  const [newProduct, setNewProduct] = useState<Partial<Product>>({ name: '', description: '', htsCode: '', alternatives: [] })
  const [addProductError, setAddProductError] = useState<string | null>(null)

  // AI chat mutation
  const aiChatMutation = useAIChat()
  const { exportConversation } = useChatExport()

  const quickPrompts: QuickPrompt[] = [
    {
      id: '1',
      title: 'Classify Product',
      prompt: 'I need to classify a laptop computer for import. Can you help me find the correct HTS code?',
      icon: <Search className="h-4 w-4" />,
      category: 'search'
    },
    {
      id: '2',
      title: 'Calculate Duties',
      prompt: 'What are the import duties for smartphones from China?',
      icon: <Calculator className="h-4 w-4" />,
      category: 'calculation'
    },
    {
      id: '3',
      title: 'Trade Compliance',
      prompt: 'What are the requirements for importing textiles from Vietnam?',
      icon: <FileText className="h-4 w-4" />,
      category: 'analysis'
    },
    {
      id: '4',
      title: 'Sourcing Analysis',
      prompt: 'Compare sourcing options for electronics between China, Vietnam, and Mexico',
      icon: <TrendingUp className="h-4 w-4" />,
      category: 'analysis'
    },
    {
      id: '5',
      title: 'Regulatory Update',
      prompt: 'What are the latest changes to Section 301 tariffs?',
      icon: <Info className="h-4 w-4" />,
      category: 'general'
    },
    {
      id: '6',
      title: 'Documentation Help',
      prompt: 'What documents do I need for importing machinery?',
      icon: <FileText className="h-4 w-4" />,
      category: 'general'
    }
  ]

  // allProducts combines mock data (for demo/testing) and user-added products
  const allProducts = [...mockProducts, ...realProducts]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')

    try {
      // Call backend API using the hook
      const result = await aiChatMutation.mutateAsync({
        messages: [...messages.map(msg => ({
          role: msg.role,
          content: msg.content
        })), { role: 'user', content }],
        model: selectedModel,
        serp_search: enableProductSearch,
        product_query: enableProductSearch ? (productQuery || content) : undefined,
        temperature: 0.1,
        max_tokens: 1000
      })
      
      // Handle both success and error responses from the backend
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.content || 'I apologize, but I received an empty response.',
        timestamp: new Date(),
        metadata: {
          model: result.model,
          usage: result.usage,
          product_info: result.product_info,
          error: result.error
        }
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Show appropriate toast message
      if (result.error) {
        toast.error('AI response received with issues')
      } else {
        toast.success('AI response received')
      }
      
    } catch (error) {
      console.error('AI response error:', error)
      
      // Create error message for display
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I apologize, but I'm experiencing technical difficulties. The error was: ${error instanceof Error ? error.message : 'Unknown error'}\n\nPlease try:\n1. Checking if Ollama is running\n2. Using a different model\n3. Refreshing the page`,
        timestamp: new Date(),
        metadata: {
          model: selectedModel,
          error: error instanceof Error ? error.message : 'Unknown error'
        },
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('Failed to get AI response')
    }
  }

  const handleQuickPrompt = (prompt: QuickPrompt) => {
    handleSendMessage(prompt.prompt)
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    const validFiles = files.filter(file => {
      const isValidType = file.type === 'application/pdf' || 
                         file.type === 'application/msword' ||
                         file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                         file.type === 'text/plain'
      const isValidSize = file.size <= 10 * 1024 * 1024 // 10MB limit
      
      if (!isValidType) {
        toast.error(`${file.name}: Unsupported file type`)
        return false
      }
      if (!isValidSize) {
        toast.error(`${file.name}: File too large (max 10MB)`)
        return false
      }
      return true
    })
    
    setUploadedFiles(prev => [...prev, ...validFiles])
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    if (uploadedFiles.length === 0) return
    
    setIsUploading(true)
    try {
      const formData = new FormData()
      uploadedFiles.forEach((file, index) => {
        formData.append(`files`, file)
      })
      
      // Call backend API to upload files
      const response = await fetch('/api/v1/knowledge/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (response.ok) {
        const result = await response.json()
        toast.success(`Successfully uploaded ${uploadedFiles.length} files to knowledge base`)
        setUploadedFiles([])
        setShowFileUpload(false)
      } else {
        throw new Error('Upload failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload files. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getModelDisplayName = (model: ModelType) => {
    switch (model) {
      case 'groq': return 'Groq (Fast)'
      case 'openai': return 'OpenAI GPT-4'
      case 'llava': return 'LLaVA (Local)'
      case 'devstral:24b': return 'DevStral 24B (Local)'
      case 'llama3.2:3b': return 'Llama 3.2 3B (Local)'
      case 'qwen3:8b': return 'Qwen3 8B (Local)'
      case 'deepseek-r1:8b': return 'DeepSeek R1 8B (Local)'
      case 'moondream': return 'Moondream (Local)'
      case 'llama3.1': return 'Llama 3.1 (Local)'
      case 'gemma3:4b': return 'Gemma3 4B (Local)'
      case 'phi4': return 'Phi4 (Local)'
      default: return model
    }
  }

  // Handler to add a real product (with validation)
  const handleAddProduct = () => {
    if (!newProduct.name || !newProduct.htsCode) {
      setAddProductError('Product name and HTS code are required.');
      return;
    }
    setRealProducts(prev => [
      ...prev,
      { ...newProduct, id: `real-${Date.now()}`, alternatives: newProduct.alternatives || [] } as Product
    ]);
    setShowAddProduct(false);
    setNewProduct({ name: '', description: '', htsCode: '', alternatives: [] });
    setAddProductError(null);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Bot className="h-6 w-6 text-white" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900">AI Tariff Assistant</h1>
        <p className="text-gray-600 mt-2">Your intelligent guide for trade compliance and tariff analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Quick Prompts */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Quick Prompts
              </CardTitle>
              <CardDescription>
                Common questions to get started
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {quickPrompts.map((prompt) => (
                <Button
                  key={prompt.id}
                  className="w-full justify-start h-auto p-3 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 whitespace-normal break-words text-left"
                  style={{ wordBreak: 'break-word', whiteSpace: 'normal', minHeight: '56px' }}
                  onClick={() => handleQuickPrompt(prompt)}
                >
                  <div className="flex items-start gap-3 text-left w-full">
                    <div className="mt-0.5 text-blue-600">
                      {prompt.icon}
                    </div>
                    <div className="w-full">
                      <div className="font-medium text-sm">{prompt.title}</div>
                      <div className="text-xs text-gray-500 mt-1 line-clamp-2 break-words whitespace-normal w-full">
                        {prompt.prompt}
                      </div>
                    </div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* File Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Knowledge Base Upload
              </CardTitle>
              <CardDescription>
                Upload documents or paste text to enhance AI responses
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-3">
                <Button
                  onClick={() => setShowFileUpload(!showFileUpload)}
                  variant="outline"
                  className="w-full justify-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  {showFileUpload ? 'Hide Upload' : 'Upload Files'}
                </Button>
                
                {showFileUpload && (
                  <div className="space-y-3">
                    <div 
                      className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors cursor-pointer"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm text-gray-600">
                        Drop files here or click to browse
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Supports: PDF, DOC, DOCX, TXT files
                      </p>
                    </div>
                    
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    
                    {uploadedFiles.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700">
                          Selected Files ({uploadedFiles.length}):
                        </p>
                        {uploadedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <div className="flex items-center gap-2">
                              <FileType className="h-4 w-4 text-blue-500" />
                              <span className="text-sm">{file.name}</span>
                              <span className="text-xs text-gray-500">
                                ({(file.size / 1024).toFixed(1)} KB)
                              </span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeFile(index)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ))}
                        
                        <Button
                          onClick={uploadFiles}
                          disabled={isUploading}
                          className="w-full"
                        >
                          {isUploading ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Uploading...
                            </>
                          ) : (
                            <>
                              <Upload className="h-4 w-4 mr-2" />
                              Upload to Knowledge Base
                            </>
                          )}
                        </Button>
                      </div>
                    )}
                    {/* Direct Text Input for Knowledge Base */}
                    <div className="space-y-2">
                      <textarea
                        className="w-full min-h-[80px] p-2 border border-gray-300 rounded-md text-sm resize-vertical"
                        placeholder="Paste or type knowledge here (e.g. regulations, product info, compliance notes)"
                        value={knowledgeText}
                        onChange={e => setKnowledgeText(e.target.value)}
                        maxLength={5000}
                      />
                      <Button
                        onClick={async () => {
                          if (!knowledgeText.trim()) return;
                          setIsSubmittingKnowledge(true);
                          try {
                            const response = await fetch('/api/v1/knowledge/add-from-text', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ content: knowledgeText })
                            });
                            if (response.ok) {
                              toast.success('Knowledge added successfully!');
                              setKnowledgeText('');
                            } else {
                              toast.error('Failed to add knowledge.');
                            }
                          } catch (err) {
                            toast.error('Error adding knowledge.');
                          } finally {
                            setIsSubmittingKnowledge(false);
                          }
                        }}
                        disabled={isSubmittingKnowledge || !knowledgeText.trim()}
                        className="w-full"
                      >
                        {isSubmittingKnowledge ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                        Add to Knowledge Base
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Product Quick Prompts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Product Quick Prompts
              </CardTitle>
              <CardDescription>
                Explore products and alternatives
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <>
                {allProducts.map(product => (
                  <Button
                    key={product.id}
                    className="w-full justify-start h-auto p-2 border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 whitespace-normal break-words text-left"
                    style={{ wordBreak: 'break-word', whiteSpace: 'normal', minHeight: '40px' }}
                    onClick={() => handleQuickPrompt({
                      id: product.id,
                      title: product.name,
                      prompt: `Classify or analyze: ${product.name} (HTS: ${product.htsCode})\n${product.description}`,
                      icon: <Search className="h-4 w-4" />,
                      category: 'search'
                    })}
                  >
                    <div className="font-medium text-sm">{product.name}</div>
                    <div className="text-xs text-gray-500 mt-1 line-clamp-2 break-words whitespace-normal w-full">
                      {product.description}
                    </div>
                    {product.alternatives && product.alternatives.length > 0 && (
                      <div className="text-xs text-blue-500 mt-1">Alternatives: {product.alternatives.map(a => a.name).join(', ')}</div>
                    )}
                  </Button>
                ))}
                <Button variant="outline" className="w-full mt-2" onClick={() => setShowAddProduct(true)}>
                  + Add Real Product
                </Button>
                {showAddProduct && (
                  <Dialog open={showAddProduct} onOpenChange={setShowAddProduct}>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add a New Product</DialogTitle>
                      </DialogHeader>
                      <input
                        className="w-full border p-1 rounded mb-1"
                        placeholder="Product Name"
                        value={newProduct.name}
                        onChange={e => setNewProduct(p => ({ ...p, name: e.target.value }))}
                      />
                      <input
                        className="w-full border p-1 rounded mb-1"
                        placeholder="HTS Code"
                        value={newProduct.htsCode}
                        onChange={e => setNewProduct(p => ({ ...p, htsCode: e.target.value }))}
                      />
                      <textarea
                        className="w-full border p-1 rounded mb-1"
                        placeholder="Description"
                        value={newProduct.description}
                        onChange={e => setNewProduct(p => ({ ...p, description: e.target.value }))}
                      />
                      {/* Alternatives input (simple comma-separated for now) */}
                      <input
                        className="w-full border p-1 rounded mb-1"
                        placeholder="Alternatives (comma separated names)"
                        value={Array.isArray(newProduct.alternatives) ? newProduct.alternatives.map(a => a.name).join(', ') : ''}
                        onChange={e => {
                          const names = e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                          setNewProduct(p => ({
                            ...p,
                            alternatives: names.map((name, idx) => ({ id: `alt-${Date.now()}-${idx}`, name, htsCode: '', reason: '' }))
                          }))
                        }}
                      />
                      {addProductError && <div className="text-red-500 text-sm mb-2">{addProductError}</div>}
                      <Button className="w-full" onClick={handleAddProduct}>Save Product</Button>
                      <Button className="w-full mt-1" variant="ghost" onClick={() => { setShowAddProduct(false); setAddProductError(null); }}>Cancel</Button>
                    </DialogContent>
                  </Dialog>
                )}
              </>
            </CardContent>
          </Card>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Chat with AI Assistant
              </CardTitle>
              <CardDescription>
                Ask questions about tariffs, classification, compliance, and more
              </CardDescription>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col">
              {/* Settings Bar */}
              <div className="flex items-center gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Settings className="h-4 w-4 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Settings:</span>
                </div>
                
                {/* Model Selection */}
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600">Model:</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => {
                      const value = e.target.value;
                      const validModels = ['groq', 'openai', 'llava', 'devstral:24b', 'llama3.2:3b', 'qwen3:8b', 'deepseek-r1:8b', 'moondream', 'llama3.1', 'gemma3:4b', 'phi4'];
                      if (validModels.includes(value)) {
                        setSelectedModel(value as ModelType);
                      }
                    }}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="groq">Groq (Fast)</option>
                    <option value="openai">OpenAI GPT-4</option>
                    <option value="llava">LLaVA (Local)</option>
                    <option value="devstral:24b">DevStral 24B (Local)</option>
                    <option value="llama3.2:3b">Llama 3.2 3B (Local)</option>
                    <option value="qwen3:8b">Qwen3 8B (Local)</option>
                    <option value="deepseek-r1:8b">DeepSeek R1 8B (Local)</option>
                    <option value="moondream">Moondream (Local)</option>
                    <option value="llama3.1">Llama 3.1 (Local)</option>
                    <option value="gemma3:4b">Gemma3 4B (Local)</option>
                    <option value="phi4">Phi4 (Local)</option>
                  </select>
                </div>

                {/* Product Search Toggle */}
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="product-search"
                    checked={enableProductSearch}
                    onChange={(e) => setEnableProductSearch(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="product-search" className="text-sm text-gray-600 flex items-center gap-1">
                    <ShoppingCart className="h-3 w-3" />
                    Product Search
                  </label>
                </div>

                {enableProductSearch && (
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600">Product Query:</label>
                    <input
                      type="text"
                      value={productQuery}
                      onChange={(e) => setProductQuery(e.target.value)}
                      placeholder="Enter product search query..."
                      className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}

                {/* Export Conversation Button */}
                <Button
                  variant="outline"
                  className="ml-auto"
                  onClick={() => setShowExport(true)}
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Export Conversation
                </Button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start gap-2 mb-2">
                        {message.role === 'user' ? (
                          <User className="h-4 w-4 mt-0.5" />
                        ) : (
                          <Bot className="h-4 w-4 mt-0.5 text-blue-600" />
                        )}
                        <div className="text-xs opacity-70">
                          {formatTimestamp(message.timestamp)}
                        </div>
                      </div>
                      
                      <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                      </div>
                      
                      {message.metadata && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="flex flex-wrap gap-2">
                            {message.metadata.hts_code && (
                              <Badge className="text-xs bg-gray-200 text-gray-800">
                                HTS: {message.metadata.hts_code}
                              </Badge>
                            )}
                            {message.metadata.duty_rate !== undefined && (
                              <Badge className="text-xs bg-gray-200 text-gray-800">
                                Duty: {message.metadata.duty_rate}%
                              </Badge>
                            )}
                            {message.metadata.analysis_type && (
                              <Badge className="text-xs border border-gray-300 bg-white text-gray-700">
                                {message.metadata.analysis_type}
                              </Badge>
                            )}
                            {message.metadata.confidence && (
                              <Badge className="text-xs border border-gray-300 bg-white text-gray-700">
                                Confidence: {Math.round(message.metadata.confidence * 100)}%
                              </Badge>
                            )}
                            {message.metadata.model && (
                              <Badge className="text-xs bg-blue-100 text-blue-800">
                                {getModelDisplayName(message.metadata.model)}
                              </Badge>
                            )}
                            {message.metadata.product_info && (
                              <Badge className="text-xs bg-green-100 text-green-800">
                                <ShoppingCart className="h-3 w-3 mr-1" />
                                Product Info
                              </Badge>
                            )}
                          </div>
                          
                          {/* Product Info Display */}
                          {message.metadata.product_info && (
                            <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
                              <div className="text-xs font-medium text-green-800 mb-1">Product Information:</div>
                              <div className="text-xs text-green-700">
                                {typeof message.metadata.product_info === 'string' 
                                  ? message.metadata.product_info
                                  : JSON.stringify(message.metadata.product_info, null, 2)
                                }
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {/* Loading indicator */}
                {aiChatMutation.isPending && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg p-4 max-w-[80%]">
                      <div className="flex items-center gap-2">
                        <Bot className="h-4 w-4 text-blue-600" />
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm text-gray-600">Analyzing with {getModelDisplayName(selectedModel)}...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
              
              {/* Input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputMessage)}
                  placeholder="Ask about tariffs, classification, compliance..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <Button
                  onClick={() => handleSendMessage(inputMessage)}
                  disabled={!inputMessage.trim() || aiChatMutation.isPending}
                  className="px-4"
                >
                  {aiChatMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Export Dialog */}
      <ConversationExport
        conversationId={/* pass the current conversation ID or a placeholder */ 'current-conversation-id'}
        isOpen={showExport}
        onClose={() => setShowExport(false)}
      />
    </div>
  )
} 