export interface ExcelData {
  filename: string
  sheets: SheetData[]
  currentSheet: string
}

export interface SheetData {
  name: string
  data: Record<string, any>[]
  columns: string[]
  shape: [number, number]
  dtypes: Record<string, string>
}

export interface LLMSettings {
  model: string
  temperature: number
  maxTokens: number
  apiKey: string
  baseUrl: string
}

export interface AnalysisResult {
  status: 'success' | 'error' | 'processing'
  message: string
  data?: {
    summary?: string
    charts?: string[]
    code?: string
    insights?: string[]
  }
  error?: string
}

export interface ChartConfig {
  type: 'bar' | 'line' | 'scatter' | 'pie' | 'box' | 'heatmap'
  xAxis: string
  yAxis?: string
  color?: string
  title: string
  data: Record<string, any>[]
}

export interface Theme {
  mode: 'light' | 'dark'
  primary: string
  accent: string
}