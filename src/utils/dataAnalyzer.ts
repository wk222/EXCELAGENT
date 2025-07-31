import _ from 'lodash'
import type { SheetData } from '../types'

export class DataAnalyzer {
  static analyzeData(sheetData: SheetData) {
    const { data, columns, dtypes } = sheetData
    
    const analysis = {
      summary: this.generateSummary(sheetData),
      insights: this.generateInsights(sheetData),
      correlations: this.calculateCorrelations(sheetData),
      distributions: this.analyzeDistributions(sheetData),
      outliers: this.detectOutliers(sheetData),
    }

    return analysis
  }

  private static generateSummary(sheetData: SheetData): string {
    const { data, columns, shape, dtypes } = sheetData
    
    const numericCols = columns.filter(col => dtypes[col] === 'number')
    const textCols = columns.filter(col => dtypes[col] === 'string')
    const dateCols = columns.filter(col => dtypes[col] === 'date')

    let summary = `数据包含 ${shape[0]} 行 ${shape[1]} 列\n\n`
    
    if (numericCols.length > 0) {
      summary += `数值列分析 (${numericCols.length} 列):\n`
      numericCols.forEach(col => {
        const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
        if (values.length > 0) {
          const stats = this.calculateStatistics(values)
          summary += `• ${col}: 平均值 ${stats.mean.toFixed(2)}, 中位数 ${stats.median.toFixed(2)}, 标准差 ${stats.std.toFixed(2)}\n`
        }
      })
      summary += '\n'
    }

    if (textCols.length > 0) {
      summary += `分类列分析 (${textCols.length} 列):\n`
      textCols.slice(0, 3).forEach(col => {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        const topValue = _.head(_.toPairs(_.countBy(values)).sort((a, b) => b[1] - a[1]))
        if (topValue) {
          summary += `• ${col}: ${uniqueCount} 个唯一值, 最常见值 "${topValue[0]}" (${topValue[1]} 次)\n`
        }
      })
    }

    return summary
  }

  private static generateInsights(sheetData: SheetData): string[] {
    const insights = []
    const { data, columns, dtypes } = sheetData
    
    const numericCols = columns.filter(col => dtypes[col] === 'number')
    const textCols = columns.filter(col => dtypes[col] === 'string')

    // 数值分析洞察
    if (numericCols.length > 0) {
      numericCols.forEach(col => {
        const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
        if (values.length > 0) {
          const stats = this.calculateStatistics(values)
          
          // 检查偏度
          if (Math.abs(stats.skewness) > 1) {
            insights.push(`${col} 数据分布${stats.skewness > 0 ? '右偏' : '左偏'}，存在${stats.skewness > 0 ? '大' : '小'}值异常`)
          }
          
          // 检查变异系数
          const cv = stats.std / stats.mean
          if (cv > 1) {
            insights.push(`${col} 数据变异性较大 (变异系数: ${cv.toFixed(2)})，建议进一步分组分析`)
          }
        }
      })
    }

    // 分类数据洞察
    if (textCols.length > 0) {
      textCols.forEach(col => {
        const values = data.map(row => row[col]).filter(val => val)
        const uniqueCount = new Set(values).size
        const uniqueRatio = uniqueCount / values.length
        
        if (uniqueRatio < 0.1) {
          insights.push(`${col} 是高度集中的分类变量 (${uniqueCount} 个类别)，适合作为分组变量`)
        } else if (uniqueRatio > 0.9) {
          insights.push(`${col} 几乎每个值都不同，可能是标识符列`)
        }
      })
    }

    // 数据质量洞察
    const missingRatios = columns.map(col => {
      const missingCount = data.filter(row => !row[col] || row[col] === '').length
      return { col, ratio: missingCount / data.length }
    }).filter(item => item.ratio > 0.1)

    if (missingRatios.length > 0) {
      insights.push(`以下列存在较多缺失值: ${missingRatios.map(item => `${item.col} (${(item.ratio * 100).toFixed(1)}%)`).join(', ')}`)
    }

    return insights.length > 0 ? insights : ['数据质量良好，可以进行深入分析']
  }

  private static calculateStatistics(values: number[]) {
    const sorted = values.sort((a, b) => a - b)
    const n = values.length
    const mean = _.mean(values)
    const median = n % 2 === 0 ? (sorted[n/2 - 1] + sorted[n/2]) / 2 : sorted[Math.floor(n/2)]
    const std = Math.sqrt(_.mean(values.map(v => Math.pow(v - mean, 2))))
    
    // 计算偏度 (简化版本)
    const skewness = _.mean(values.map(v => Math.pow((v - mean) / std, 3)))
    
    return {
      mean,
      median,
      std,
      min: Math.min(...values),
      max: Math.max(...values),
      skewness,
    }
  }

  private static calculateCorrelations(sheetData: SheetData) {
    const { data, columns, dtypes } = sheetData
    const numericCols = columns.filter(col => dtypes[col] === 'number')
    
    if (numericCols.length < 2) return {}

    const correlations: Record<string, Record<string, number>> = {}
    
    numericCols.forEach(col1 => {
      correlations[col1] = {}
      numericCols.forEach(col2 => {
        if (col1 !== col2) {
          const values1 = data.map(row => Number(row[col1])).filter(val => !isNaN(val))
          const values2 = data.map(row => Number(row[col2])).filter(val => !isNaN(val))
          
          if (values1.length > 0 && values2.length > 0) {
            correlations[col1][col2] = this.pearsonCorrelation(values1, values2)
          }
        }
      })
    })

    return correlations
  }

  private static pearsonCorrelation(x: number[], y: number[]): number {
    const n = Math.min(x.length, y.length)
    const sumX = _.sum(x.slice(0, n))
    const sumY = _.sum(y.slice(0, n))
    const sumXY = _.sum(x.slice(0, n).map((xi, i) => xi * y[i]))
    const sumX2 = _.sum(x.slice(0, n).map(xi => xi * xi))
    const sumY2 = _.sum(y.slice(0, n).map(yi => yi * yi))
    
    const numerator = n * sumXY - sumX * sumY
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))
    
    return denominator === 0 ? 0 : numerator / denominator
  }

  private static analyzeDistributions(sheetData: SheetData) {
    const { data, columns, dtypes } = sheetData
    const distributions: Record<string, any> = {}
    
    columns.forEach(col => {
      if (dtypes[col] === 'number') {
        const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
        if (values.length > 0) {
          const stats = this.calculateStatistics(values)
          const histogram = this.createHistogram(values, 10)
          distributions[col] = {
            type: 'numeric',
            statistics: stats,
            histogram,
          }
        }
      } else if (dtypes[col] === 'string') {
        const values = data.map(row => row[col]).filter(val => val)
        const counts = _.countBy(values)
        const sorted = _.toPairs(counts).sort((a, b) => b[1] - a[1])
        distributions[col] = {
          type: 'categorical',
          uniqueCount: Object.keys(counts).length,
          topValues: sorted.slice(0, 10),
        }
      }
    })

    return distributions
  }

  private static createHistogram(values: number[], bins: number) {
    const min = Math.min(...values)
    const max = Math.max(...values)
    const binWidth = (max - min) / bins
    
    const histogram = Array(bins).fill(0)
    values.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1)
      histogram[binIndex]++
    })

    return histogram.map((count, index) => ({
      range: [min + index * binWidth, min + (index + 1) * binWidth],
      count,
    }))
  }

  private static detectOutliers(sheetData: SheetData) {
    const { data, columns, dtypes } = sheetData
    const outliers: Record<string, number[]> = {}
    
    columns.forEach(col => {
      if (dtypes[col] === 'number') {
        const values = data.map(row => Number(row[col])).filter(val => !isNaN(val))
        if (values.length > 0) {
          const sorted = values.sort((a, b) => a - b)
          const q1 = sorted[Math.floor(sorted.length * 0.25)]
          const q3 = sorted[Math.floor(sorted.length * 0.75)]
          const iqr = q3 - q1
          const lowerBound = q1 - 1.5 * iqr
          const upperBound = q3 + 1.5 * iqr
          
          const outlierValues = values.filter(val => val < lowerBound || val > upperBound)
          if (outlierValues.length > 0) {
            outliers[col] = outlierValues
          }
        }
      }
    })

    return outliers
  }
}