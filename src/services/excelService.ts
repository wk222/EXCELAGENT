import * as XLSX from 'xlsx'

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
  summary?: DataSummary
}

export interface DataSummary {
  rowCount: number
  columnCount: number
  numericColumns: string[]
  categoricalColumns: string[]
  dateColumns: string[]
  missingValues: Record<string, number>
  statistics: Record<string, any>
}

export class ExcelService {
  static async processFile(file: File): Promise<ExcelData> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target?.result as ArrayBuffer)
          const workbook = XLSX.read(data, { type: 'array' })
          
          const sheets: SheetData[] = workbook.SheetNames.map((sheetName) => {
            const worksheet = workbook.Sheets[sheetName]
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
            
            // 处理数据格式
            const headers = (jsonData[0] as string[]) || []
            const rows = jsonData.slice(1) as any[][]
            
            // 清理和标准化列名
            const cleanHeaders = headers.map((header, index) => {
              if (!header || header.toString().trim() === '') {
                return `Column_${index + 1}`
              }
              return header.toString().trim()
            })
            
            // 转换为对象数组
            const processedData = rows.map((row) => {
              const obj: Record<string, any> = {}
              cleanHeaders.forEach((header, index) => {
                obj[header] = row[index] !== undefined ? row[index] : ''
              })
              return obj
            }).filter(row => Object.values(row).some(value => value !== '' && value !== null && value !== undefined))

            // 检测数据类型
            const dtypes = this.detectDataTypes(processedData, cleanHeaders)
            
            // 生成数据摘要
            const summary = this.generateDataSummary(processedData, cleanHeaders, dtypes)

            return {
              name: sheetName,
              data: processedData,
              columns: cleanHeaders,
              shape: [processedData.length, cleanHeaders.length] as [number, number],
              dtypes,
              summary
            }
          })

          const result: ExcelData = {
            filename: file.name,
            sheets,
            currentSheet: sheets[0]?.name || '',
          }

          resolve(result)
        } catch (error) {
          reject(new Error(`Excel文件解析失败: ${error instanceof Error ? error.message : '未知错误'}`))
        }
      }
      
      reader.onerror = () => {
        reject(new Error('文件读取失败'))
      }
      
      reader.readAsArrayBuffer(file)
    })
  }

  private static detectDataTypes(data: Record<string, any>[], columns: string[]): Record<string, string> {
    const dtypes: Record<string, string> = {}
    
    columns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => val !== '' && val !== null && val !== undefined)
      
      if (values.length === 0) {
        dtypes[column] = 'string'
        return
      }

      // 检测数字
      const numericCount = values.filter(val => !isNaN(Number(val)) && isFinite(Number(val))).length
      const numericRatio = numericCount / values.length

      if (numericRatio > 0.8) {
        dtypes[column] = 'number'
        return
      }

      // 检测日期
      const dateCount = values.filter(val => {
        if (typeof val === 'string') {
          return !isNaN(Date.parse(val))
        }
        return false
      }).length
      const dateRatio = dateCount / values.length

      if (dateRatio > 0.7) {
        dtypes[column] = 'date'
        return
      }

      // 默认为字符串
      dtypes[column] = 'string'
    })

    return dtypes
  }

  private static generateDataSummary(data: Record<string, any>[], columns: string[], dtypes: Record<string, string>): DataSummary {
    const numericColumns = columns.filter(col => dtypes[col] === 'number')
    const categoricalColumns = columns.filter(col => dtypes[col] === 'string')
    const dateColumns = columns.filter(col => dtypes[col] === 'date')
    
    // 计算缺失值
    const missingValues: Record<string, number> = {}
    columns.forEach(col => {
      const missing = data.filter(row => 
        row[col] === '' || row[col] === null || row[col] === undefined
      ).length
      missingValues[col] = missing
    })

    // 计算数值列统计
    const statistics: Record<string, any> = {}
    numericColumns.forEach(col => {
      const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
      if (values.length > 0) {
        const sorted = values.sort((a, b) => a - b)
        const mean = values.reduce((sum, val) => sum + val, 0) / values.length
        const median = sorted[Math.floor(sorted.length / 2)]
        const min = Math.min(...values)
        const max = Math.max(...values)
        const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length)
        
        statistics[col] = { mean, median, min, max, std }
      }
    })

    return {
      rowCount: data.length,
      columnCount: columns.length,
      numericColumns,
      categoricalColumns,
      dateColumns,
      missingValues,
      statistics
    }
  }

  static getCurrentSheetData(excelData: ExcelData): SheetData | null {
    return excelData.sheets.find(sheet => sheet.name === excelData.currentSheet) || null
  }

  static exportToCSV(sheetData: SheetData): void {
    const csvContent = this.convertToCSV(sheetData.data, sheetData.columns)
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, `${sheetData.name}.csv`)
  }

  private static convertToCSV(data: Record<string, any>[], columns: string[]): string {
    const headers = columns.join(',')
    const rows = data.map(row => 
      columns.map(col => {
        const value = row[col]
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`
        }
        return value
      }).join(',')
    )
    return [headers, ...rows].join('\n')
  }
}