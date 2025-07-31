import * as XLSX from 'xlsx'
import type { ExcelData, SheetData } from '../types'

export class ExcelProcessor {
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
            const headers = jsonData[0] as string[] || []
            const rows = jsonData.slice(1) as any[][]
            
            // 转换为对象数组
            const processedData = rows.map((row) => {
              const obj: Record<string, any> = {}
              headers.forEach((header, index) => {
                obj[header || `Column_${index + 1}`] = row[index] || ''
              })
              return obj
            }).filter(row => Object.values(row).some(value => value !== ''))

            // 检测数据类型
            const dtypes: Record<string, string> = {}
            headers.forEach((header) => {
              if (!header) return
              
              const column = processedData.map(row => row[header]).filter(val => val !== '')
              if (column.length === 0) {
                dtypes[header] = 'string'
                return
              }

              // 检测是否为数字
              const numericCount = column.filter(val => !isNaN(Number(val))).length
              const numericRatio = numericCount / column.length

              if (numericRatio > 0.8) {
                dtypes[header] = 'number'
              } else {
                // 检测是否为日期
                const dateCount = column.filter(val => !isNaN(Date.parse(val))).length
                const dateRatio = dateCount / column.length
                
                if (dateRatio > 0.7) {
                  dtypes[header] = 'date'
                } else {
                  dtypes[header] = 'string'
                }
              }
            })

            return {
              name: sheetName,
              data: processedData,
              columns: headers.filter(h => h),
              shape: [processedData.length, headers.length] as [number, number],
              dtypes,
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

  static getCurrentSheetData(excelData: ExcelData): SheetData | null {
    return excelData.sheets.find(sheet => sheet.name === excelData.currentSheet) || null
  }

  static getDataSummary(sheetData: SheetData): string {
    const { data, columns, shape, dtypes } = sheetData
    
    let summary = `=== 数据摘要 ===\n`
    summary += `形状: ${shape[0]} 行 × ${shape[1]} 列\n`
    summary += `列名: ${columns.join(', ')}\n\n`

    // 数据类型统计
    const typeCount: Record<string, number> = {}
    Object.values(dtypes).forEach(type => {
      typeCount[type] = (typeCount[type] || 0) + 1
    })
    summary += `数据类型分布: ${JSON.stringify(typeCount)}\n\n`

    // 数值列统计
    const numericCols = columns.filter(col => dtypes[col] === 'number')
    if (numericCols.length > 0) {
      summary += `数值列 (${numericCols.length}个): ${numericCols.join(', ')}\n`
      
      numericCols.forEach(col => {
        const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
        if (values.length > 0) {
          const mean = values.reduce((sum, val) => sum + val, 0) / values.length
          const min = Math.min(...values)
          const max = Math.max(...values)
          summary += `  ${col}: 平均值 ${mean.toFixed(2)}, 范围 ${min} ~ ${max}\n`
        }
      })
      summary += '\n'
    }

    // 文本列统计
    const textCols = columns.filter(col => dtypes[col] === 'string')
    if (textCols.length > 0) {
      summary += `文本列 (${textCols.length}个): ${textCols.join(', ')}\n`
      
      textCols.slice(0, 3).forEach(col => {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        summary += `  ${col}: ${uniqueCount} 个唯一值\n`
      })
      summary += '\n'
    }

    // 数据预览
    summary += `前3行数据:\n`
    data.slice(0, 3).forEach((row, index) => {
      summary += `第${index + 1}行: ${JSON.stringify(row)}\n`
    })

    return summary
  }

  static validateData(sheetData: SheetData): { status: 'success' | 'warning' | 'error'; message: string }[] {
    const results = []
    const { data, shape } = sheetData

    // 检查行数
    if (shape[0] === 0) {
      results.push({ status: 'error' as const, message: '文件不包含任何数据行' })
    } else if (shape[0] < 5) {
      results.push({ status: 'warning' as const, message: `文件只包含 ${shape[0]} 行数据，可能不足以进行有意义的分析` })
    } else {
      results.push({ status: 'success' as const, message: `文件包含 ${shape[0]} 行数据，足够进行分析` })
    }

    // 检查列数
    if (shape[1] === 0) {
      results.push({ status: 'error' as const, message: '文件不包含任何数据列' })
    } else if (shape[1] < 2) {
      results.push({ status: 'warning' as const, message: '文件只包含1列数据，可能无法进行关联分析' })
    } else {
      results.push({ status: 'success' as const, message: `文件包含 ${shape[1]} 列数据` })
    }

    // 检查缺失值
    let missingCount = 0
    let totalCells = 0
    data.forEach(row => {
      Object.values(row).forEach(value => {
        totalCells++
        if (value === '' || value === null || value === undefined) {
          missingCount++
        }
      })
    })

    if (missingCount > 0) {
      const missingPct = (missingCount / totalCells) * 100
      if (missingPct > 50) {
        results.push({ status: 'error' as const, message: `文件包含大量缺失值 (${missingPct.toFixed(1)}%)，可能影响分析质量` })
      } else if (missingPct > 20) {
        results.push({ status: 'warning' as const, message: `文件包含较多缺失值 (${missingPct.toFixed(1)}%)，可能需要数据清理` })
      } else {
        results.push({ status: 'warning' as const, message: `文件包含少量缺失值 (${missingPct.toFixed(1)}%)，分析时将自动处理` })
      }
    } else {
      results.push({ status: 'success' as const, message: '文件不包含缺失值，数据完整' })
    }

    return results
  }
}