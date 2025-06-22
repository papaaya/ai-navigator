export type ProcessingStage = "upload" | "config" | "processing" | "results"
export type OutputFormat = "py" | "js" | "json"
export type ProcessingMode = "live" | "static"

export interface DocumentData {
  file: File
  filename: string
}

export interface ProcessingConfig {
  outputFormat: OutputFormat
  mode: ProcessingMode
}

export interface VerificationItem {
  claim: string
  question: string
  answer: string
}

export interface ProcessingResults {
  summary?: string
  sections?: Record<string, string>
  generatedCode?: string
  tablesAnalysis?: string
  verifications?: VerificationItem[]
} 