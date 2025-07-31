import type { ExcelData, SheetData } from './excelService'

export interface MCPResponse {
  status: 'success' | 'error' | 'processing'
  message: string
  data?: any
  error?: string
}

export interface AnalysisResult extends MCPResponse {
  data?: {
    summary?: string
    charts?: string[]
    code?: string
    insights?: string[]
    execution_results?: {
      stdout: string
      stderr: string
      plotly_figures: string[]
      error?: string
    }
  }
}

export class MCPService {
  private baseUrl: string
  private connected: boolean = false

  constructor(baseUrl: string = 'http://localhost:8080') {
    this.baseUrl = baseUrl
  }

  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        timeout: 5000,
      } as RequestInit)
      
      this.connected = response.ok
      return this.connected
    } catch (error) {
      console.warn('MCP服务器连接失败:', error)
      this.connected = false
      return false
    }
  }

  async analyzeExcelData(fileData: any, question: string): Promise<AnalysisResult> {
    if (!this.connected) {
      throw new Error('MCP服务器未连接')
    }

    try {
      const response = await fetch(`${this.baseUrl}/tools/analyze_excel_data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_data: fileData,
          question: question
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      return result as AnalysisResult
    } catch (error) {
      throw new Error(`MCP分析请求失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  async getDataSummary(fileData: any): Promise<AnalysisResult> {
    if (!this.connected) {
      throw new Error('MCP服务器未连接')
    }

    try {
      const response = await fetch(`${this.baseUrl}/tools/get_data_summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_data: fileData
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      return result as AnalysisResult
    } catch (error) {
      throw new Error(`MCP摘要请求失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  async generateVisualizations(fileData: any, chartType: string = 'auto'): Promise<AnalysisResult> {
    if (!this.connected) {
      throw new Error('MCP服务器未连接')
    }

    try {
      const response = await fetch(`${this.baseUrl}/tools/generate_visualizations_only`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_data: fileData,
          chart_type: chartType
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      return result as AnalysisResult
    } catch (error) {
      throw new Error(`MCP可视化请求失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  async executeCustomCode(fileData: any, pythonCode: string): Promise<AnalysisResult> {
    if (!this.connected) {
      throw new Error('MCP服务器未连接')
    }

    try {
      const response = await fetch(`${this.baseUrl}/tools/execute_custom_code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_data: fileData,
          python_code: pythonCode
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      return result as AnalysisResult
    } catch (error) {
      throw new Error(`MCP代码执行请求失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  async generateDeepAnalysis(stage2Question: string, stage3Question: string, stage2Result: AnalysisResult, dataSummary: string = ''): Promise<AnalysisResult> {
    if (!this.connected) {
      throw new Error('MCP服务器未连接')
    }

    try {
      const response = await fetch(`${this.baseUrl}/tools/generate_deep_analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stage2_question: stage2Question,
          stage3_question: stage3Question,
          stage2_result: stage2Result,
          data_summary: dataSummary
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      return result as AnalysisResult
    } catch (error) {
      throw new Error(`MCP深度分析请求失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  isConnected(): boolean {
    return this.connected
  }
}