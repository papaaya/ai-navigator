"use client"

import type React from "react"
import { useState, useRef } from "react"
import { Upload, X, CheckCircle2, File } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { DocumentData } from "@/app/page"

interface UploadPanelProps {
  onFileUpload: (file: File) => void
  onStartProcessing: () => void
  document: DocumentData | null
}

export function UploadPanel({ onFileUpload, onStartProcessing, document }: UploadPanelProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [isHovering, setIsHovering] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    const validFile = files.find(
      (file) =>
        file.type === "application/pdf" ||
        file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        file.type === "text/plain",
    )

    if (validFile) {
      onFileUpload(validFile)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileUpload(file)
    }
  }

  const handleRemoveFile = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const getFileIcon = (filename: string) => {
    const extension = filename.split(".").pop()?.toLowerCase()
    switch (extension) {
      case "pdf":
        return "📄"
      case "docx":
        return "📝"
      case "txt":
        return "📋"
      default:
        return "📄"
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-white/30 shadow-2xl p-6 sm:p-8 lg:p-12 transition-all duration-300 hover:shadow-3xl">
        <div className="text-center mb-8 lg:mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl mb-6 shadow-lg">
            <Upload className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-gray-900 mb-3">Document Upload</h2>
          <p className="text-gray-600 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
            Upload your research paper, report, or document for AI-powered analysis with LLaMA 4
          </p>
        </div>

        {!document ? (
          <div
            className={`border-2 border-dashed rounded-2xl lg:rounded-3xl p-8 sm:p-12 lg:p-16 text-center transition-all duration-300 transform ${
              isDragOver
                ? "border-blue-400 bg-gradient-to-br from-blue-50/80 to-purple-50/80 scale-[1.02] shadow-xl"
                : "border-gray-300/60 hover:border-gray-400/80 hover:bg-gray-50/30"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => setIsHovering(false)}
          >
            <div className={`transition-all duration-300 ${isHovering ? "transform scale-105" : ""}`}>
              <Upload
                className={`w-16 h-16 mx-auto mb-6 transition-all duration-300 ${
                  isDragOver ? "text-blue-500 animate-bounce" : "text-gray-400"
                }`}
              />
              <h3 className="text-xl sm:text-2xl font-medium text-gray-900 mb-3">
                {isDragOver ? "Drop your document here" : "Drop your document here"}
              </h3>
              <p className="text-gray-600 mb-6 text-sm sm:text-base">Supports PDF, DOCX, and TXT files up to 10MB</p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-8 py-3 text-base font-medium shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  size="lg"
                >
                  Choose File
                </Button>
                <span className="text-gray-500 text-sm">or drag and drop</span>
              </div>

              <div className="flex items-center justify-center space-x-6 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <span>📄</span>
                  <span>PDF</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span>📝</span>
                  <span>DOCX</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span>📋</span>
                  <span>TXT</span>
                </div>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        ) : (
          <div className="space-y-8">
            <div className="bg-gradient-to-r from-green-50/80 to-emerald-50/80 backdrop-blur-sm rounded-2xl p-6 sm:p-8 border border-green-200/50 shadow-lg transition-all duration-300 hover:shadow-xl">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="text-4xl">{getFileIcon(document.filename)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <h3 className="font-semibold text-gray-900 text-lg truncate">{document.filename}</h3>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-1 sm:space-y-0 text-sm text-gray-600">
                      <span className="flex items-center space-x-1">
                        <File className="w-4 h-4" />
                        <span>{formatFileSize(document.file.size)}</span>
                      </span>
                      <span className="hidden sm:block">•</span>
                      <span>Ready for processing</span>
                    </div>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRemoveFile}
                  className="text-gray-600 hover:text-gray-900 hover:bg-red-50 border-gray-300 transition-all duration-200 flex-shrink-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="text-center">
              <Button
                onClick={onStartProcessing}
                size="lg"
                className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white px-12 py-4 text-lg font-medium shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 rounded-2xl"
              >
                <span className="flex items-center space-x-2">
                  <span>Continue</span>
                  <span className="text-xl">→</span>
                </span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
