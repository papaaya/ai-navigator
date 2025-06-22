"use client"

import { Download, AlertCircle, Loader2, FileText, Code, BookOpen, BrainCircuit } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { DocumentData, ProcessingConfig, ProcessingResults } from "@/types"

interface ResultsPanelProps {
  results: ProcessingResults | null
  config: ProcessingConfig
  isProcessing: boolean
  documentData: DocumentData | null
}

const ResultCard = ({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) => (
  <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-6 sm:p-8">
    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
      {icon}
      {title}
    </h3>
    <div className="prose prose-gray max-w-none text-gray-700 leading-relaxed">
      {children}
    </div>
  </div>
)

export function ResultsPanel({ results, config, isProcessing, documentData }: ResultsPanelProps) {
  const handleDownloadCode = () => {
    if (!results?.generatedCode || typeof window === "undefined") return;

    const fileExtension = config.outputFormat
    const fileName = `analysis_${documentData?.filename.split(".")[0] || "document"}.${fileExtension}`

    const blob = new Blob([results.generatedCode], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement("a")
    a.href = url
    a.download = fileName
    window.document.body.appendChild(a)
    a.click()
    window.document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isProcessing) {
    return (
        <div className="max-w-5xl mx-auto">
            <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-white/30 shadow-2xl p-8 sm:p-12 lg:p-16 text-center">
                <div className="space-y-8">
                    <div className="relative">
                        <div className="w-24 h-24 mx-auto bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-xl">
                            <Loader2 className="w-12 h-12 text-white animate-spin"/>
                        </div>
                        <div className="absolute inset-0 w-24 h-24 mx-auto bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-ping opacity-20"></div>
                    </div>
                    <div className="space-y-4">
                        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-gray-900">Analyzing Document</h2>
                        <p className="text-gray-600 text-lg max-w-2xl mx-auto leading-relaxed">
                            LlamaLens is dissecting the paper to extract key insights and generate code...
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
  }

  // Handle error state or empty results
  if (!results || (!results.summary && !results.sections && !results.generatedCode)) {
    const errorMessage = results?.summary?.startsWith("Error:")
        ? results.summary
        : "The AI model did not return a valid response. Please check the backend logs or try again."

    return (
        <div className="max-w-5xl mx-auto text-center">
            <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-red-200/50 shadow-xl p-8">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4"/>
                <h2 className="text-2xl font-semibold text-red-800">Analysis Failed</h2>
                <p className="text-red-600 mt-2 px-4">{errorMessage}</p>
            </div>
        </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <FileText className="w-8 h-8 text-blue-600"/>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Analysis for "{documentData?.filename}"</h2>
              <div className="flex items-center space-x-2 text-sm mt-1">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full capitalize">
                  {config.mode} Mode
                </span>
                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">.{config.outputFormat}</span>
              </div>
            </div>
          </div>
          {results.generatedCode && (
            <Button
              onClick={handleDownloadCode}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white w-full sm:w-auto"
            >
              <Download className="w-4 h-4 mr-2"/>
              Download Code
            </Button>
          )}
        </div>
      </div>

      {/* Main Results Grid */}
      <div className="space-y-6">
        {results.summary && (
          <ResultCard icon={<BookOpen className="w-5 h-5 mr-3 text-blue-600"/>} title="Executive Summary">
            <p>{results.summary}</p>
          </ResultCard>
        )}

        {results.sections && Object.entries(results.sections).map(([key, value]) => (
            <ResultCard key={key} icon={<BrainCircuit className="w-5 h-5 mr-3 text-purple-600"/>} title={`Extracted: ${key.charAt(0).toUpperCase() + key.slice(1)}`}>
              <p className="whitespace-pre-wrap">{value}</p>
            </ResultCard>
        ))}

        {results.generatedCode && (
          <ResultCard icon={<Code className="w-5 h-5 mr-3 text-green-600"/>} title="Generated Code">
             <div className="bg-gray-900 rounded-xl p-4 -m-4 sm:p-6 sm:-m-6 overflow-x-auto">
              <pre className="text-green-300 text-sm font-mono">
                <code>{results.generatedCode}</code>
              </pre>
            </div>
          </ResultCard>
        )}
      </div>
    </div>
  )
}
