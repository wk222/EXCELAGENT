import _ from 'lodash'
import type { SheetData } from './excelService'
import type { AnalysisResult } from './mcpService'

// 本地分析服务 - 当MCP不可用时的备选方案
export class LocalAnalysisService {
  
  static analyzeData(sheetData: SheetData, question: string): AnalysisResult {
    try {
      const analysis = this.performBasicAnalysis(sheetData, question)
      const insights = this.generateInsights(sheetData)
      const charts = this.generateBasicCharts(sheetData)

      return {
        status: 'success',
        message: '本地分析完成',
        data: {
          summary: analysis,
          insights,
          charts: charts.map(chart => JSON.stringify(chart))
        }
      }
    } catch (error) {
      return {
        status: 'error',
        message: '本地分析失败',
        error: error instanceof Error ? error.message : '未知错误'
      }
    }
  }

  static getDataSummary(sheetData: SheetData): AnalysisResult {
    try {
      const summary = this.generateDetailedSummary(sheetData)
      
      return {
        status: 'success',
        message: '数据摘要生成完成',
        data: {
          summary
        }
      }
    } catch (error) {
      return {
        status: 'error',
        message: '数据摘要生成失败',
        error: error instanceof Error ? error.message : '未知错误'
      }
    }
  }

  private static performBasicAnalysis(sheetData: SheetData, question: string): string {
    const { data, columns, dtypes, summary } = sheetData
    
    let analysis = `## 📊 数据分析报告\n\n`
    analysis += `**分析问题**: ${question}\n\n`
    
    // 基本信息
    analysis += `### 📋 数据概况\n`
    analysis += `- 数据行数: ${data.length}\n`
    analysis += `- 数据列数: ${columns.length}\n`
    analysis += `- 数值列: ${summary?.numericColumns.length || 0} 个\n`
    analysis += `- 分类列: ${summary?.categoricalColumns.length || 0} 个\n`
    analysis += `- 日期列: ${summary?.dateColumns.length || 0} 个\n\n`

    // 数值分析
    if (summary?.numericColumns.length) {
      analysis += `### 📈 数值分析\n`
      summary.numericColumns.forEach(col => {
        const stats = summary.statistics[col]
        if (stats) {
          analysis += `**${col}**:\n`
          analysis += `- 平均值: ${stats.mean.toFixed(2)}\n`
          analysis += `- 中位数: ${stats.median.toFixed(2)}\n`
          analysis += `- 范围: ${stats.min.toFixed(2)} ~ ${stats.max.toFixed(2)}\n`
          analysis += `- 标准差: ${stats.std.toFixed(2)}\n\n`
        }
      })
    }

    // 分类分析
    if (summary?.categoricalColumns.length) {
      analysis += `### 📊 分类分析\n`
      summary.categoricalColumns.slice(0, 3).forEach(col => {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        const topValue = _.head(_.toPairs(_.countBy(values)).sort((a, b) => b[1] - a[1]))
        
        analysis += `**${col}**:\n`
        analysis += `- 唯一值数量: ${uniqueCount}\n`
        if (topValue) {
          analysis += `- 最常见值: "${topValue[0]}" (${topValue[1]} 次, ${((topValue[1] / values.length) * 100).toFixed(1)}%)\n`
        }
        analysis += '\n'
      })
    }

    // 数据质量
    analysis += `### ⚠️ 数据质量\n`
    const totalMissing = Object.values(summary?.missingValues || {}).reduce((sum, count) => sum + count, 0)
    const totalCells = data.length * columns.length
    const missingRate = (totalMissing / totalCells) * 100
    
    analysis += `- 总缺失值: ${totalMissing} 个 (${missingRate.toFixed(1)}%)\n`
    
    if (missingRate > 10) {
      analysis += `- ⚠️ 缺失值较多，建议进行数据清理\n`
    } else {
      analysis += `- ✅ 数据质量良好\n`
    }

    return analysis
  }

  private static generateDetailedSummary(sheetData: SheetData): string {
    const { data, columns, dtypes, summary } = sheetData
    
    let detailedSummary = `=== Excel数据详细摘要 ===\n\n`
    
    // 基本信息
    detailedSummary += `数据形状: ${data.length} 行 × ${columns.length} 列\n`
    detailedSummary += `列名: ${columns.join(', ')}\n\n`
    
    // 数据类型分布
    const typeCount = _.countBy(Object.values(dtypes))
    detailedSummary += `数据类型分布: ${JSON.stringify(typeCount)}\n\n`
    
    // 详细列信息
    detailedSummary += `=== 列详细信息 ===\n`
    columns.forEach((col, index) => {
      const dtype = dtypes[col]
      const missingCount = summary?.missingValues[col] || 0
      const missingPct = ((missingCount / data.length) * 100).toFixed(1)
      
      detailedSummary += `${index + 1}. 列名: '${col}' | 数据类型: ${dtype} | 缺失值: ${missingCount}个(${missingPct}%)\n`
      
      if (dtype === 'number' && summary?.statistics[col]) {
        const stats = summary.statistics[col]
        detailedSummary += `   数值范围: ${stats.min.toFixed(2)} ~ ${stats.max.toFixed(2)}\n`
        detailedSummary += `   均值: ${stats.mean.toFixed(2)}, 中位数: ${stats.median.toFixed(2)}\n`
      } else if (dtype === 'string') {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        detailedSummary += `   唯一值数量: ${uniqueCount}\n`
        
        if (uniqueCount <= 10) {
          const topValues = _.toPairs(_.countBy(values)).sort((a, b) => b[1] - a[1]).slice(0, 5)
          detailedSummary += `   前5个值: ${topValues.map(([val, count]) => `${val}(${count})`).join(', ')}\n`
        }
      }
      detailedSummary += '\n'
    })
    
    // 数据预览
    detailedSummary += `=== 数据前3行示例 ===\n`
    data.slice(0, 3).forEach((row, index) => {
      detailedSummary += `第${index + 1}行: ${JSON.stringify(row)}\n`
    })
    
    return detailedSummary
  }

  private static generateInsights(sheetData: SheetData): string[] {
    const insights: string[] = []
    const { data, columns, dtypes, summary } = sheetData
    
    // 数据规模洞察
    if (data.length > 10000) {
      insights.push('数据量较大，适合进行统计分析和机器学习')
    } else if (data.length < 100) {
      insights.push('数据量较小，分析结果可能不够稳定')
    }

    // 数值列洞察
    if (summary?.numericColumns.length) {
      summary.numericColumns.forEach(col => {
        const stats = summary.statistics[col]
        if (stats) {
          const cv = stats.std / stats.mean // 变异系数
          if (cv > 1) {
            insights.push(`${col} 数据变异性很大 (变异系数: ${cv.toFixed(2)})，存在明显的分布差异`)
          }
          
          // 检查异常值
          const range = stats.max - stats.min
          const iqr = range * 0.5 // 简化的IQR估算
          if (stats.max > stats.mean + 3 * stats.std || stats.min < stats.mean - 3 * stats.std) {
            insights.push(`${col} 可能存在极端异常值，建议进一步检查`)
          }
        }
      })
    }

    // 分类列洞察
    if (summary?.categoricalColumns.length) {
      summary.categoricalColumns.forEach(col => {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        const uniqueRatio = uniqueCount / values.length
        
        if (uniqueRatio < 0.1) {
          insights.push(`${col} 是高度集中的分类变量 (${uniqueCount} 个类别)，适合作为分组变量`)
        } else if (uniqueRatio > 0.9) {
          insights.push(`${col} 几乎每个值都不同，可能是标识符或唯一编码`)
        }
      })
    }

    // 数据质量洞察
    const totalMissing = Object.values(summary?.missingValues || {}).reduce((sum, count) => sum + count, 0)
    const missingRate = (totalMissing / (data.length * columns.length)) * 100
    
    if (missingRate > 20) {
      insights.push(`数据缺失率较高 (${missingRate.toFixed(1)}%)，建议进行数据清理`)
    } else if (missingRate === 0) {
      insights.push('数据完整无缺失，质量优秀')
    }

    return insights.length > 0 ? insights : ['数据结构正常，可以进行深入分析']
  }

  private static generateBasicCharts(sheetData: SheetData): any[] {
    const { data, columns, dtypes, summary } = sheetData
    const charts: any[] = []

    // 1. 数值列分布直方图
    if (summary?.numericColumns.length) {
      summary.numericColumns.slice(0, 2).forEach(col => {
        const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
        const histogramData = this.createHistogram(values, col)
        charts.push(histogramData)
      })
    }

    // 2. 分类列饼图
    if (summary?.categoricalColumns.length) {
      summary.categoricalColumns.slice(0, 2).forEach(col => {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        
        if (uniqueCount <= 10 && uniqueCount > 1) {
          const counts = _.countBy(values)
          const pieData = {
            data: [{
              type: 'pie',
              labels: Object.keys(counts),
              values: Object.values(counts),
              title: `${col} 分布`
            }],
            layout: {
              title: `${col} 分布`,
              font: { family: 'Arial, sans-serif' }
            }
          }
          charts.push(pieData)
        }
      })
    }

    // 3. 相关性分析（如果有多个数值列）
    if (summary?.numericColumns.length && summary.numericColumns.length >= 2) {
      const scatterData = this.createScatterPlot(data, summary.numericColumns[0], summary.numericColumns[1])
      charts.push(scatterData)
    }

    return charts
  }

  private static createHistogram(values: number[], columnName: string): any {
    const min = Math.min(...values)
    const max = Math.max(...values)
    const binCount = Math.min(20, Math.max(5, Math.floor(Math.sqrt(values.length))))
    const binWidth = (max - min) / binCount
    
    const bins = Array(binCount).fill(0)
    const binLabels = []
    
    for (let i = 0; i < binCount; i++) {
      const binStart = min + i * binWidth
      const binEnd = min + (i + 1) * binWidth
      binLabels.push(`${binStart.toFixed(1)}-${binEnd.toFixed(1)}`)
    }
    
    values.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binWidth), binCount - 1)
      bins[binIndex]++
    })

    return {
      data: [{
        type: 'bar',
        x: binLabels,
        y: bins,
        marker: { color: '#3b82f6' }
      }],
      layout: {
        title: `${columnName} 分布`,
        xaxis: { title: columnName },
        yaxis: { title: '频次' },
        font: { family: 'Arial, sans-serif' }
      }
    }
  }

  private static createScatterPlot(data: Record<string, any>[], xCol: string, yCol: string): any {
    const xValues = data.map(row => Number(row[xCol])).filter(val => !isNaN(val))
    const yValues = data.map(row => Number(row[yCol])).filter(val => !isNaN(val))
    
    return {
      data: [{
        type: 'scatter',
        mode: 'markers',
        x: xValues,
        y: yValues,
        marker: { color: '#3b82f6', size: 6 }
      }],
      layout: {
        title: `${xCol} vs ${yCol}`,
        xaxis: { title: xCol },
        yaxis: { title: yCol },
        font: { family: 'Arial, sans-serif' }
      }
    }
  }
}