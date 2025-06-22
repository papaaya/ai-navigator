"use client"

import { useState } from "react"
import { UploadPanel } from "@/components/upload-panel"
import { ConfigPanel } from "@/components/config-panel"
import { ResultsPanel } from "@/components/results-panel"

export type ProcessingStage = "upload" | "config" | "processing" | "results"
export type OutputFormat = "py" | "js" | "json"
export type ProcessingMode = "live" | "static"

export interface DocumentData {
  file: File
  filename: string
  content?: string
}

export interface ProcessingConfig {
  outputFormat: OutputFormat
  mode: ProcessingMode
}

export interface ProcessingResults {
  summary?: string
  sections?: Array<{
    title: string
    content: string
    reasoning: string
  }>
  generatedCode?: string
  validation?: {
    accuracy: boolean
    hallucinated: boolean
    verified: boolean
  }
}

export default function DocumentAnalyzer() {
  const [stage, setStage] = useState<ProcessingStage>("upload")
  const [document, setDocument] = useState<DocumentData | null>(null)
  const [config, setConfig] = useState<ProcessingConfig>({
    outputFormat: "py",
    mode: "static",
  })
  const [results, setResults] = useState<ProcessingResults | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileUpload = (file: File) => {
    setDocument({
      file,
      filename: file.name,
    })
  }

  const handleStartProcessing = () => {
    if (document) {
      setStage("config")
    }
  }

  const handleConfigSubmit = async (newConfig: ProcessingConfig) => {
    setConfig(newConfig)
    setStage("processing")
    setIsProcessing(true)

    try {
      // Mock API call to process document
      const response = await fetch("/api/process-document", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filename: document?.filename,
          config: newConfig,
        }),
      })

      const data = await response.json()
      setResults(data)
      setStage("results")
    } catch (error) {
      console.error("Processing failed:", error)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReset = () => {
    setStage("upload")
    setDocument(null)
    setResults(null)
    setIsProcessing(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Document Analyzer</h1>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">LLaMA 4</span>
            </div>
            {stage !== "upload" && (
              <button onClick={handleReset} className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
                Start Over
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Progress Indicator */}
          <div className="flex items-center justify-center space-x-4">
            {["upload", "config", "results"].map((stepName, index) => (
              <div key={stepName} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                    stage === stepName || (stepName === "results" && stage === "processing")
                      ? "bg-blue-600 text-white"
                      : index < ["upload", "config", "processing", "results"].indexOf(stage)
                        ? "bg-green-500 text-white"
                        : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {index + 1}
                </div>
                {index < 2 && (
                  <div
                    className={`w-12 h-0.5 mx-2 transition-colors ${
                      index < ["upload", "config", "processing", "results"].indexOf(stage) - 1
                        ? "bg-green-500"
                        : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>

          {/* Stage Content */}
          {stage === "upload" && (
            <UploadPanel
              onFileUpload={handleFileUpload}
              onStartProcessing={handleStartProcessing}
              document={document}
            />
          )}

          {stage === "config" && document && (
            <ConfigPanel config={config} onConfigSubmit={handleConfigSubmit} document={document} />
          )}

          {(stage === "processing" || stage === "results") && (
            <ResultsPanel results={results} config={config} isProcessing={isProcessing} document={document} />
          )}
        </div>
      </div>
    </div>
  )
}
