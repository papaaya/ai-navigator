"use client"

import { useState, useEffect } from "react"
import { Download, CheckCircle, AlertCircle, Loader2, FileText, Code, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { DocumentData, ProcessingConfig, ProcessingResults } from "@/app/page"

interface ResultsPanelProps {
  results: ProcessingResults | null
  config: ProcessingConfig
  isProcessing: boolean
  document: DocumentData | null
}

export function ResultsPanel({ results, config, isProcessing, document }: ResultsPanelProps) {
  const [visibleSections, setVisibleSections] = useState<number>(0)

  useEffect(() => {
    if (results && config.mode === "live" && results.sections && results.sections.length > 0) {
      const timer = setInterval(() => {
        setVisibleSections((prev) => {
          if (prev < results.sections!.length) {
            return prev + 1
          }
          clearInterval(timer)
          return prev
        })
      }, 500) // Speed up the animation
      return () => clearInterval(timer)
    }
  }, [results, config.mode])

  const handleDownloadCode = () => {
    if (!results?.generatedCode) return;
    if (typeof window === "undefined") return;

    const fileExtension = config.outputFormat
    const fileName = `analysis_${document?.filename.split(".")[0] || "document"}.${fileExtension}`

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
                <Loader2 className="w-12 h-12 text-white animate-spin" />
              </div>
              <div className="absolute inset-0 w-24 h-24 mx-auto bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-ping opacity-20"></div>
            </div>
            <div className="space-y-4">
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-gray-900">Processing Document</h2>
              <p className="text-gray-600 text-lg max-w-2xl mx-auto leading-relaxed">
                LLaMA 4 is analyzing your document with advanced AI techniques...
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Handle the case where there are no results or an error occurred
  if (!results || (!results.summary && !results.sections && !results.generatedCode)) {
    return (
        <div className="max-w-5xl mx-auto text-center">
            <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-red-200/50 shadow-xl p-8">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-red-800">Analysis Failed</h2>
                <p className="text-red-600 mt-2">
                    The AI model did not return a valid response. Please check the backend logs or try again.
                </p>
            </div>
        </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FileText className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Analysis Results</h2>
            </div>
            <div className="flex items-center space-x-2 text-sm">
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full capitalize">
                {config.mode} Mode
              </span>
              <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">.{config.outputFormat}</span>
            </div>
          </div>
          {results.generatedCode && (
            <Button
              onClick={handleDownloadCode}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Code
            </Button>
          )}
        </div>
      </div>
      
      {/* Display Summary if available (Static mode) */}
      {results.summary && (
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-blue-600" />
            Document Summary
          </h3>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-700 leading-relaxed">{results.summary}</p>
          </div>
        </div>
      )}

      {/* Display Sections if available (Live mode) */}
      {results.sections && results.sections.length > 0 && (
        <div className="space-y-6">
          {results.sections.slice(0, visibleSections).map((section, index) => (
            <div
              key={index}
              className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8 animate-in fade-in slide-in-from-bottom-4 duration-700"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Section {index + 1}: {section.title}
              </h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Content</h4>
                  <p className="text-gray-700 leading-relaxed bg-gray-50/80 p-4 rounded-xl">{section.content}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">AI Reasoning</h4>
                  <p className="text-blue-700 leading-relaxed bg-blue-50/80 p-4 rounded-xl">{section.reasoning}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Display Generated Code if available (Both modes) */}
      {results.generatedCode && (
         <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Code className="w-5 h-5 mr-2 text-purple-600" />
              Generated Code
            </h3>
            <div className="bg-gray-900 rounded-xl p-6 overflow-x-auto">
              <pre className="text-green-400 text-sm">
                <code>{results.generatedCode}</code>
              </pre>
            </div>
          </div>
      )}
    </div>
  )
}
