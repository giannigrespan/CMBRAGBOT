[file name]: gemini.ts
[file content begin]
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { KnowledgeDocument, ChatMessage } from '../types';

// Funzione per ottenere la API key in modo sicuro
const getApiKey = (): string => {
  // In ambiente browser, usa import.meta.env
  if (typeof window !== 'undefined') {
    return (import.meta.env?.VITE_GEMINI_API_KEY || 
            import.meta.env?.GEMINI_API_KEY || 
            localStorage.getItem('GEMINI_API_KEY') || 
            '');
  }
  
  // In ambiente Node.js (per build)
  if (typeof process !== 'undefined') {
    return process.env?.VITE_GEMINI_API_KEY || 
           process.env?.GEMINI_API_KEY || 
           '';
  }
  
  return '';
};

export const generateResponse = async (
  history: ChatMessage[],
  currentQuery: string,
  documents: KnowledgeDocument[]
): Promise<string> => {
  try {
    const apiKey = getApiKey();
    
    if (!apiKey) {
      throw new Error("API Key non configurata. Inserisci la tua chiave Gemini nelle impostazioni.");
    }

    const ai = new GoogleGenAI({ apiKey });
    
    const modelId = 'gemini-2.0-flash';

    const systemInstruction = `
      Sei un assistente aziendale esperto e utile. 
      Il tuo compito è rispondere alle domande dei colleghi basandoti ESCLUSIVAMENTE sui documenti forniti nel contesto.
      
      Regole:
      1. Usa un tono professionale ma cordiale.
      2. Se la risposta non si trova nei documenti forniti, dillo chiaramente.
      3. Cita il nome del documento se rilevante.
      4. Rispondi in lingua italiana.
      5. Se non ci sono documenti caricati, spiega che è necessario caricare manuali prima di poter rispondere.
    `;

    // Costruisci il contesto dai documenti
    let documentContext = "";
    if (documents.length === 0) {
      documentContext = "ATTENZIONE: Non sono stati caricati documenti. Non puoi fornire risposte basate sui manuali.";
    } else {
      documentContext = `DOCUMENTI DISPONIBILI:\n${documents.map(doc => `- ${doc.name} (${doc.type})`).join('\n')}\n\n`;
    }

    // Prepara la conversazione
    const conversationHistory = history
      .slice(-10) // Ultimi 10 messaggi per limitare il contesto
      .map(msg => `${msg.role === 'user' ? 'Utente' : 'Assistente'}: ${msg.text}`)
      .join('\n');

    const fullPrompt = `${documentContext}

STORIA DELLA CONVERSAZIONE:
${conversationHistory}

DOMANDA ATTUALE: ${currentQuery}

RISPOSTA:`;

    const response: GenerateContentResponse = await ai.models.generateContent({
      model: modelId,
      contents: [{ 
        role: "user", 
        parts: [{ text: fullPrompt }] 
      }],
      config: {
        systemInstruction: { parts: [{ text: systemInstruction }] },
        temperature: 0.3,
        maxOutputTokens: 1000,
      }
    });

    return response.text || "Non sono riuscito a generare una risposta basata sui documenti.";

  } catch (error: any) {
    console.error("Errore Gemini:", error);
    
    if (error.message?.includes('API Key') || error.message?.includes('API_KEY')) {
      throw new Error("Errore di configurazione: Chiave API Gemini non valida o mancante. Contatta l'amministratore.");
    }
    
    if (error.message?.includes('quota') || error.message?.includes('rate limit')) {
      throw new Error("Limite di utilizzo raggiunto per l'API Gemini. Riprova più tardi.");
    }
    
    throw new Error("Errore durante la comunicazione con il servizio AI. Riprova.");
  }
};
[file content end]

[file name]: AdminPanel.tsx
[file content begin]
import React, { useRef } from 'react';
import { KnowledgeDocument } from '../types';
import { Trash2, FileText, FolderUp, AlertCircle, Loader2 } from 'lucide-react';

interface AdminPanelProps {
  documents: KnowledgeDocument[];
  onAddDocuments: (files: File[]) => void;
  onRemoveDocument: (id: string) => void;
  isUploading?: boolean;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ documents, onAddDocuments, onRemoveDocument, isUploading = false }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const filesList = e.target.files;
    
    if (filesList && filesList.length > 0) {
      const allFiles: File[] = Array.from(filesList);
      
      // Filtra solo i file supportati
      const validFiles = allFiles.filter(file => {
        const extension = file.name.toLowerCase().split('.').pop();
        return (
          file.type === 'application/pdf' || 
          file.type === 'text/plain' ||
          extension === 'md' ||
          extension === 'txt' ||
          extension === 'pdf'
        );
      });

      if (validFiles.length > 0) {
        onAddDocuments(validFiles);
      } else {
        alert("Nessun file valido trovato. Supportiamo solo PDF, TXT e MD.");
      }

      // Reset input
      e.target.value = '';
    }
  };

  const handleFolderSelect = () => {
    if (fileInputRef.current) {
      // Rimuovi gli attributi non standard che causano problemi
      fileInputRef.current.removeAttribute('webkitdirectory');
      fileInputRef.current.removeAttribute('directory');
      fileInputRef.current.setAttribute('multiple', '');
      fileInputRef.current.click();
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="flex flex-col h-full p-6 bg-slate-50 overflow-y-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Gestione Base di Conoscenza</h2>
        <p className="text-slate-600">
          Carica i manuali (PDF, TXT, MD) che vuoi utilizzare come base di conoscenza per l'assistente.
        </p>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-8">
        <div 
          className={`border-2 border-dashed border-slate-300 rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-colors ${
            isUploading ? 'bg-slate-50 opacity-75 cursor-not-allowed' : 'hover:border-blue-500 hover:bg-blue-50'
          }`}
          onClick={isUploading ? undefined : handleFolderSelect}
        >
          {isUploading ? (
            <>
              <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
              <h3 className="text-lg font-semibold text-slate-700">Caricamento in corso...</h3>
              <p className="text-sm text-slate-500 mt-1">Sto elaborando i file</p>
            </>
          ) : (
            <>
              <div className="bg-blue-100 p-3 rounded-full mb-4">
                <FolderUp className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-700">Clicca per selezionare file</h3>
              <p className="text-sm text-slate-500 mt-1">Supporta PDF, TXT, MD (multiselezione)</p>
            </>
          )}
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange}
            multiple
            accept=".pdf,.txt,.md,application/pdf,text/plain"
            className="hidden" 
          />
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
          Documenti Caricati
          <span className="bg-slate-200 text-slate-600 text-xs px-2 py-1 rounded-full">{documents.length}</span>
        </h3>

        {documents.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
            <AlertCircle className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">Nessun documento presente. Seleziona dei file per iniziare.</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center gap-4 overflow-hidden">
                  <div className="bg-red-50 p-2 rounded-lg">
                    <FileText className="w-6 h-6 text-red-500" />
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-medium text-slate-900 truncate" title={doc.name}>{doc.name}</h4>
                    <p className="text-xs text-slate-500">{formatSize(doc.size)} • {doc.uploadedAt.toLocaleDateString()} {doc.uploadedAt.toLocaleTimeString()}</p>
                  </div>
                </div>
                <button 
                  onClick={() => onRemoveDocument(doc.id)}
                  className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                  title="Rimuovi documento"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
[file content end]

[file name]: index.html
[file content begin]
<!DOCTYPE html>
<html lang="it">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Corporate Knowledge Bot</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
      body {
        font-family: 'Inter', sans-serif;
      }
    </style>
  <script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@19.2.0",
    "react-dom/": "https://esm.sh/react-dom@19.2.0/",
    "react-dom/client": "https://esm.sh/react-dom@19.2.0/client",
    "lucide-react": "https://esm.sh/lucide-react@0.554.0",
    "@google/genai": "https://esm.sh/@google/genai@1.30.0"
  }
}
</script>
</head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.tsx"></script>
  </body>
</html>
[file content end]

[file name]: vite.config.ts
[file content begin]
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Carica le variabili d'ambiente
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    server: {
      port: 3000,
      host: '0.0.0.0',
    },
    plugins: [react()],
    define: {
      // Espone le variabili d'ambiente al client in modo sicuro
      'import.meta.env.VITE_GEMINI_API_KEY': JSON.stringify(env.VITE_GEMINI_API_KEY || env.GEMINI_API_KEY || ''),
    },
    resolve: {
      alias: {
        '@': '/src',
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    }
  };
});
[file content end]