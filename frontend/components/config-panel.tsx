"use client"

import { useState } from "react"
import { Settings, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { DocumentData, ProcessingConfig, OutputFormat, ProcessingMode } from "@/app/page"

interface ConfigPanelProps {
  config: ProcessingConfig
  onConfigSubmit: (config: ProcessingConfig) => void
  document: DocumentData
}

export function ConfigPanel({ config, onConfigSubmit, document }: ConfigPanelProps) {
  const [localConfig, setLocalConfig] = useState<ProcessingConfig>(config)

  const handleSubmit = () => {
    onConfigSubmit(localConfig)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white/70 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-xl p-8">
        <div className="text-center mb-8">
          <Settings className="w-12 h-12 text-blue-600 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Output Configuration</h2>
          <p className="text-gray-600">Configure how you want to analyze "{document.filename}"</p>
        </div>

        <div className="space-y-6">
          {/* Output Format */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-3">Code Output Format</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: "py" as OutputFormat, label: "Python (.py)", icon: "🐍" },
                { value: "js" as OutputFormat, label: "JavaScript (.js)", icon: "⚡" },
                { value: "json" as OutputFormat, label: "JSON (.json)", icon: "📋" },
              ].map((format) => (
                <button
                  key={format.value}
                  onClick={() => setLocalConfig({ ...localConfig, outputFormat: format.value })}
                  className={`p-4 rounded-xl border-2 transition-all text-left ${
                    localConfig.outputFormat === format.value
                      ? "border-blue-500 bg-blue-50/50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="text-2xl mb-2">{format.icon}</div>
                  <div className="font-medium text-gray-900 text-sm">{format.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Processing Mode */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-3">Processing Mode</label>
            <div className="grid grid-cols-2 gap-4">
              {[
                {
                  value: "static" as ProcessingMode,
                  label: "Static Mode",
                  description: "Single comprehensive summary",
                  icon: "📄",
                },
                {
                  value: "live" as ProcessingMode,
                  label: "Live Mode",
                  description: "Section-by-section breakdown",
                  icon: "🔄",
                },
              ].map((mode) => (
                <button
                  key={mode.value}
                  onClick={() => setLocalConfig({ ...localConfig, mode: mode.value })}
                  className={`p-6 rounded-xl border-2 transition-all text-left ${
                    localConfig.mode === mode.value
                      ? "border-blue-500 bg-blue-50/50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <div className="text-3xl mb-3">{mode.icon}</div>
                  <div className="font-medium text-gray-900 mb-1">{mode.label}</div>
                  <div className="text-sm text-gray-600">{mode.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="text-center pt-4">
            <Button
              onClick={handleSubmit}
              size="lg"
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 text-lg font-medium"
            >
              <Download className="w-5 h-5 mr-2" />
              Generate Analysis
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
