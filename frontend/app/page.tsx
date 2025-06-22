"use client"

import { useState } from "react"
import { UploadPanel } from "@/components/upload-panel"
import { ConfigPanel } from "@/components/config-panel"
import { ResultsPanel } from "@/components/results-panel"
import AnimatedBackground from "@/components/animated-background"
import type {
  ProcessingStage,
  DocumentData,
  ProcessingConfig,
  ProcessingResults,
} from "@/types"

const getFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      const base64Content = reader.result?.toString().split(",")[1]
      if (base64Content) {
        resolve(base64Content)
      } else {
        reject(new Error("Could not read file content as base64."))
      }
    }
    reader.onerror = (error) => reject(error)
  })
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
    if (!document) {
      console.error("No document to process")
      setStage("upload")
      return
    }

    setConfig(newConfig)
    setStage("processing")
    setIsProcessing(true)
    setResults(null)

    try {
      const base64Content = await getFileAsBase64(document.file)

      const response = await fetch("http://localhost:8001/process-document", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filename: document.filename,
          content: base64Content,
          config: newConfig,
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Analysis failed: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      setResults(data)
      setStage("results")
    } catch (error) {
      console.error("Processing failed:", error)
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred."
      setResults({ summary: `Error: ${errorMessage}` }) // Show error in UI
      setStage("results")
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

  const getStageIndex = (stageName: ProcessingStage) => {
    const stages = ["upload", "config", "processing", "results"]
    return stages.indexOf(stageName)
  }

  const currentStageIndex = getStageIndex(stage)

  return (
    <div className="min-h-screen relative overflow-hidden">
      <AnimatedBackground />

      {/* Header */}
      <div className="bg-white/60 backdrop-blur-xl border-b border-white/20 sticky top-0 z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-200">
                <span className="text-white font-bold text-lg">M</span>
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-semibold text-gray-900">Document Analyzer</h1>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs sm:text-sm text-gray-500 bg-gradient-to-r from-blue-100 to-purple-100 px-3 py-1 rounded-full border border-white/50">
                    Powered by LLaMA 4
                  </span>
                </div>
              </div>
            </div>
            {stage !== "upload" && (
              <button
                onClick={handleReset}
                className="text-sm text-gray-600 hover:text-gray-900 transition-all duration-200 hover:bg-white/50 px-3 py-2 rounded-lg backdrop-blur-sm"
              >
                Start Over
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12">
        <div className="space-y-8 lg:space-y-12">
          {/* Enhanced Progress Indicator */}
          <div className="flex items-center justify-center">
            <div className="flex items-center space-x-2 sm:space-x-4 bg-white/40 backdrop-blur-xl rounded-2xl p-4 sm:p-6 border border-white/30 shadow-xl">
              {["upload", "config", "results"].map((stepName, index) => {
                const isActive = currentStageIndex === index || (stepName === "results" && stage === "processing")
                const isCompleted = index < currentStageIndex || (stage === "results" && stepName !== "results")
                const stepLabels = ["Upload", "Configure", "Results"]

                return (
                  <div key={stepName} className="flex items-center">
                    <div className="flex flex-col items-center space-y-2">
                      <div
                        className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-500 transform ${
                          isActive
                            ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white scale-110 shadow-lg"
                            : isCompleted
                              ? "bg-gradient-to-r from-green-400 to-emerald-500 text-white scale-105 shadow-md"
                              : "bg-gray-200/80 text-gray-600 hover:bg-gray-300/80"
                        }`}
                      >
                        {isCompleted ? "✓" : index + 1}
                      </div>
                      <span
                        className={`text-xs sm:text-sm font-medium transition-colors duration-300 ${
                          isActive ? "text-blue-600" : isCompleted ? "text-green-600" : "text-gray-500"
                        }`}
                      >
                        {stepLabels[index]}
                      </span>
                    </div>
                    {index < 2 && (
                      <div
                        className={`w-8 sm:w-16 h-0.5 mx-2 sm:mx-4 transition-all duration-500 ${
                          index < currentStageIndex - 1 || (stage === "results" && index === 0)
                            ? "bg-gradient-to-r from-green-400 to-emerald-500"
                            : "bg-gray-300/60"
                        }`}
                      />
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Stage Content with Enhanced Transitions */}
          <div className="transition-all duration-700 ease-out">
            {stage === "upload" && (
              <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                <UploadPanel
                  onFileUpload={handleFileUpload}
                  onStartProcessing={handleStartProcessing}
                  document={document}
                />
              </div>
            )}

            {stage === "config" && document && (
              <div className="animate-in fade-in slide-in-from-right-8 duration-700">
                <ConfigPanel config={config} onConfigSubmit={handleConfigSubmit} documentData={document} />
              </div>
            )}

            {(stage === "processing" || stage === "results") && (
              <div className="animate-in fade-in slide-in-from-left-8 duration-700">
                <ResultsPanel results={results} config={config} isProcessing={isProcessing} documentData={document} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
