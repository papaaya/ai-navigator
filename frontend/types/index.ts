export interface DocumentData {
  file: File
  filename: string
  content?: string
}

export interface ProcessingConfig {
  mode: "static" | "live"
  outputFormat: string
}

export interface ProcessingResults {
  summary?: string
  generatedCode?: string
  sections?: Array<{
    title: string
    content: string
    reasoning: string
  }>
} 