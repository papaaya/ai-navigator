"use client"

import { useState } from "react"
import { Settings, Download, Zap, Code, FileJson } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { DocumentData, ProcessingConfig, OutputFormat, ProcessingMode } from "@/app/page"

interface ConfigPanelProps {
  config: ProcessingConfig
  onConfigSubmit: (config: ProcessingConfig) => void
  document: DocumentData
}

export function ConfigPanel({ config, onConfigSubmit, document }: ConfigPanelProps) {
  const [localConfig, setLocalConfig] = useState<ProcessingConfig>(config)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    setIsSubmitting(true)
    // Add a small delay for better UX
    await new Promise((resolve) => setTimeout(resolve, 500))
    onConfigSubmit(localConfig)
  }

  const formatOptions = [
    {
      value: "py" as OutputFormat,
      label: "Python",
      extension: ".py",
      icon: Code,
      color: "from-green-400 to-blue-500",
      description: "Generate Python analysis code",
    },
    {
      value: "js" as OutputFormat,
      label: "JavaScript",
      extension: ".js",
      icon: Zap,
      color: "from-yellow-400 to-orange-500",
      description: "Generate JavaScript analysis code",
    },
    {
      value: "json" as OutputFormat,
      label: "JSON",
      extension: ".json",
      icon: FileJson,
      color: "from-purple-400 to-pink-500",
      description: "Generate structured JSON output",
    },
  ]

  const modeOptions = [
    {
      value: "static" as ProcessingMode,
      label: "Static Analysis",
      description: "Single comprehensive summary with generated code",
      icon: "📄",
      features: ["Complete overview", "Generated code", "Quick results"],
    },
    {
      value: "live" as ProcessingMode,
      label: "Live Analysis",
      description: "Section-by-section breakdown with AI reasoning",
      icon: "🔄",
      features: ["Detailed breakdown", "AI reasoning", "Validation checks"],
    },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-white/30 shadow-2xl p-6 sm:p-8 lg:p-12 transition-all duration-300">
        <div className="text-center mb-8 lg:mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl mb-6 shadow-lg">
            <Settings className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-gray-900 mb-3">Configure Analysis</h2>
          <p className="text-gray-600 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
            Customize how you want to analyze <span className="font-medium text-gray-800">"{document.filename}"</span>
          </p>
        </div>

        <div className="space-y-8 lg:space-y-12">
          {/* Output Format Selection */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-6">Choose Output Format</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 lg:gap-6">
              {formatOptions.map((format) => {
                const Icon = format.icon
                const isSelected = localConfig.outputFormat === format.value

                return (
                  <button
                    key={format.value}
                    onClick={() => setLocalConfig({ ...localConfig, outputFormat: format.value })}
                    className={`group relative p-6 lg:p-8 rounded-2xl border-2 transition-all duration-300 text-left transform hover:scale-105 ${
                      isSelected
                        ? "border-transparent bg-gradient-to-br from-blue-50 to-purple-50 shadow-xl scale-105"
                        : "border-gray-200/60 hover:border-gray-300/80 bg-white/40 hover:bg-white/60 shadow-lg hover:shadow-xl"
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl" />
                    )}

                    <div className="relative">
                      <div
                        className={`inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4 bg-gradient-to-r ${format.color} shadow-lg`}
                      >
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-gray-900 text-lg">{format.label}</h3>
                          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                            {format.extension}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 leading-relaxed">{format.description}</p>
                      </div>

                      {isSelected && (
                        <div className="absolute top-4 right-4 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs">✓</span>
                        </div>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Processing Mode Selection */}
          <div>
            <label className="block text-lg font-semibold text-gray-900 mb-6">Select Analysis Mode</label>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {modeOptions.map((mode) => {
                const isSelected = localConfig.mode === mode.value

                return (
                  <button
                    key={mode.value}
                    onClick={() => setLocalConfig({ ...localConfig, mode: mode.value })}
                    className={`group relative p-6 lg:p-8 rounded-2xl border-2 transition-all duration-300 text-left transform hover:scale-[1.02] ${
                      isSelected
                        ? "border-transparent bg-gradient-to-br from-blue-50 to-purple-50 shadow-xl scale-[1.02]"
                        : "border-gray-200/60 hover:border-gray-300/80 bg-white/40 hover:bg-white/60 shadow-lg hover:shadow-xl"
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl" />
                    )}

                    <div className="relative">
                      <div className="flex items-start justify-between mb-4">
                        <div className="text-4xl">{mode.icon}</div>
                        {isSelected && (
                          <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                            <span className="text-white text-xs">✓</span>
                          </div>
                        )}
                      </div>

                      <div className="space-y-3">
                        <h3 className="font-semibold text-gray-900 text-xl">{mode.label}</h3>
                        <p className="text-gray-600 leading-relaxed">{mode.description}</p>

                        <div className="space-y-2 pt-2">
                          {mode.features.map((feature, index) => (
                            <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                              <div className="w-1.5 h-1.5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full" />
                              <span>{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Submit Button */}
          <div className="text-center pt-6">
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              size="lg"
              className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white px-12 py-4 text-lg font-medium shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isSubmitting ? (
                <span className="flex items-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Starting Analysis...</span>
                </span>
              ) : (
                <span className="flex items-center space-x-2">
                  <Download className="w-5 h-5" />
                  <span>Start Analysis</span>
                </span>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
