# 🚀 ATLAS Enterprise - Quick Start for PowerShell

## ⚡ Fast Setup (3 steps)

### 1. Start Ollama (if not already running)
```powershell
# In a new PowerShell terminal
ollama serve
```

### 2. Start Backend
```powershell
# In the atlas-enterprise directory
.\start-backend.ps1
```

### 3. Start Frontend (in another terminal)
```powershell
# In a new PowerShell terminal, in atlas-enterprise directory
.\start-frontend.ps1
```

## 🎯 Access Points

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs

## 🧪 Test the Fixes

### Recent Searches (Fixed ✅)
1. Go to HTS Search page
2. Search for "computer" or "electronics"
3. Search for something else like "textile"
4. Check the "Recent Searches" section in the sidebar
5. Click on a recent search to use it again

### AI Chatbot (Fixed ✅)
1. Go to AI Chatbot page
2. Try asking: "What are HTS codes?"
3. Try asking: "What are Section 301 tariffs?"
4. Test different models from the dropdown

## 🔧 Troubleshooting

### If Ollama shows "bind" error:
```powershell
# Ollama is already running - that's good!
# Just continue with the backend and frontend
```

### If AI Chatbot still doesn't work:
```powershell
# Check if Ollama is responding
curl http://localhost:11434/api/tags

# Try pulling a model
ollama pull llama3.1
```

### If Frontend doesn't start:
```powershell
# Make sure you're in the frontend directory
cd atlas-enterprise\frontend
npm install
npm run dev
```

## 🎬 Demo Flow

1. **HTS Search**: Search "computer" → Select code → Calculate tariff
2. **Recent Searches**: Use a previous search from sidebar  
3. **AI Chat**: Ask "What are Section 301 tariffs?"
4. **Unified Dashboard**: Switch between Procurement/Compliance/Analyst views

---

**Your ATLAS Enterprise demo is ready! 🌟** 