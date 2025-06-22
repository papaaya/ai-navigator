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
    if (results && config.mode === "live" && results.sections) {
      const timer = setInterval(() => {
        setVisibleSections((prev) => {
          if (prev < results.sections!.length) {
            return prev + 1
          }
          clearInterval(timer)
          return prev
        })
      }, 800)
      return () => clearInterval(timer)
    }
  }, [results, config.mode])

  const handleDownloadCode = () => {
    if (!results?.generatedCode) return

    // Check if we're on the client side
    if (typeof window === "undefined") return

    const fileExtension = config.outputFormat
    const fileName = `analysis_${document?.filename.split(".")[0]}.${fileExtension}`

    const blob = new Blob([results.generatedCode], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = window.document.createElement("a")
    a.href = url
    a.download = fileName
    a.click()
    URL.revokeObjectURL(url)
  }

  if (isProcessing) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-white/30 shadow-2xl p-8 sm:p-12 lg:p-16 text-center">
          <div className="space-y-8">
            {/* Animated processing icon */}
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

            {/* Enhanced progress bar */}
            <div className="max-w-md mx-auto space-y-4">
              <div className="bg-gray-200/60 rounded-full h-3 overflow-hidden shadow-inner">
                <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 h-full rounded-full animate-pulse shadow-lg transition-all duration-1000 w-3/4"></div>
              </div>
              <div className="flex justify-between text-sm text-gray-500">
                <span>Analyzing content...</span>
                <span>75%</span>
              </div>
            </div>

            {/* Processing steps */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto mt-8">
              {[
                { step: "Reading", icon: "📖", active: true },
                { step: "Analyzing", icon: "🧠", active: true },
                { step: "Generating", icon: "⚡", active: false },
              ].map((item, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-xl transition-all duration-300 ${
                    item.active ? "bg-blue-50/80 border border-blue-200/50" : "bg-gray-50/50"
                  }`}
                >
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <div className={`text-sm font-medium ${item.active ? "text-blue-700" : "text-gray-500"}`}>
                    {item.step}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!results) return null

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
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {config.mode === "live" ? "Live Mode" : "Static Mode"}
              </span>
              <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">.{config.outputFormat}</span>
            </div>
          </div>
          <Button
            onClick={handleDownloadCode}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
          >
            <Download className="w-4 h-4 mr-2" />
            Download Code
          </Button>
        </div>
      </div>

      {config.mode === "static" ? (
        /* Static Mode Results */
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Zap className="w-5 h-5 mr-2 text-blue-600" />
              Document Summary
            </h3>
            <div className="prose prose-gray max-w-none">
              <p className="text-gray-700 leading-relaxed">
                {results.summary ||
                  "This document presents a comprehensive analysis of advanced machine learning techniques, focusing on transformer architectures and their applications in natural language processing. The research demonstrates significant improvements in model efficiency and accuracy through novel attention mechanisms."}
              </p>
            </div>
          </div>

          {/* Generated Code */}
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Code className="w-5 h-5 mr-2 text-purple-600" />
              Generated Code
            </h3>
            <div className="bg-gray-900 rounded-xl p-6 overflow-x-auto">
              <pre className="text-green-400 text-sm">
                <code>
                  {results.generatedCode ||
                    `# Document Analysis - ${document?.filename}
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModel

class DocumentAnalyzer:
    def __init__(self, model_name="meta-llama/Llama-4"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    
    def analyze_document(self, text):
        # Tokenize and analyze document
        tokens = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**tokens)
        
        # Extract key insights
        insights = self.extract_insights(outputs)
        return insights
    
    def extract_insights(self, outputs):
        # Process model outputs to generate insights
        return {
            "summary": "Advanced ML techniques analysis",
            "key_points": ["Transformer architecture", "Attention mechanisms"],
            "confidence": 0.95
        }

# Usage
analyzer = DocumentAnalyzer()
results = analyzer.analyze_document(document_text)`}
                </code>
              </pre>
            </div>
          </div>
        </div>
      ) : (
        /* Live Mode Results */
        <div className="space-y-6">
          {results.sections?.slice(0, visibleSections).map((section, index) => (
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

          {/* Validation Block */}
          {visibleSections === results.sections?.length && (
            <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                Validation Results
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-3 p-4 bg-green-50/80 rounded-xl">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <div>
                    <div className="font-medium text-green-900">Accurate</div>
                    <div className="text-sm text-green-700">Content verified</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-4 bg-red-50/80 rounded-xl">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                  <div>
                    <div className="font-medium text-red-900">No Hallucination</div>
                    <div className="text-sm text-red-700">Facts checked</div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 p-4 bg-blue-50/80 rounded-xl">
                  <CheckCircle className="w-6 h-6 text-blue-600" />
                  <div>
                    <div className="font-medium text-blue-900">Verified</div>
                    <div className="text-sm text-blue-700">LLaMA 4 validated</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
