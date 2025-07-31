import _ from 'lodash'
import type { SheetData, ChartConfig } from '../types'

export class ChartGenerator {
  static generateChartConfig(
    sheetData: SheetData,
    chartType: ChartConfig['type'],
    xAxis: string,
    yAxis?: string,
    colorBy?: string,
    title?: string
  ): ChartConfig {
    const { data, dtypes } = sheetData

    // 数据处理
    let processedData = [...data]

    // 根据图表类型进行特定的数据预处理
    if (chartType === 'pie') {
      // 饼图：统计分类数据
      const counts = _.countBy(data, xAxis)
      processedData = Object.entries(counts).map(([key, value]) => ({
        [xAxis]: key,
        count: value,
      }))
    } else if (chartType === 'bar' && dtypes[xAxis] === 'string') {
      // 条形图：如果X轴是分类变量，可能需要聚合
      if (yAxis && dtypes[yAxis] === 'number') {
        const grouped = _.groupBy(data, xAxis)
        processedData = Object.entries(grouped).map(([key, values]) => ({
          [xAxis]: key,
          [yAxis]: _.meanBy(values, yAxis),
        }))
      }
    }

    // 数据排序
    if (chartType === 'bar' && yAxis) {
      processedData = _.sortBy(processedData, yAxis).reverse()
    } else if (chartType === 'line' && dtypes[xAxis] === 'date') {
      processedData = _.sortBy(processedData, xAxis)
    }

    return {
      type: chartType,
      xAxis,
      yAxis,
      color: colorBy,
      title: title || this.generateTitle(chartType, xAxis, yAxis),
      data: processedData,
    }
  }

  static generateAutoCharts(sheetData: SheetData): ChartConfig[] {
    const { columns, dtypes, data } = sheetData
    const charts: ChartConfig[] = []

    const numericCols = columns.filter(col => dtypes[col] === 'number')
    const categoricalCols = columns.filter(col => dtypes[col] === 'string')
    const dateCols = columns.filter(col => dtypes[col] === 'date')

    // 1. 数值列分布图 (直方图)
    numericCols.slice(0, 2).forEach(col => {
      charts.push({
        type: 'bar',
        xAxis: col,
        title: `${col} 分布`,
        data: this.createHistogramData(data, col),
      })
    })

    // 2. 分类列饼图
    categoricalCols.slice(0, 2).forEach(col => {
      const uniqueCount = new Set(data.map(row => row[col])).size
      if (uniqueCount <= 10 && uniqueCount > 1) {
        charts.push(this.generateChartConfig(sheetData, 'pie', col, undefined, undefined, `${col} 分布`))
      }
    })

    // 3. 数值相关性散点图
    if (numericCols.length >= 2) {
      charts.push(this.generateChartConfig(
        sheetData, 
        'scatter', 
        numericCols[0], 
        numericCols[1],
        categoricalCols[0],
        `${numericCols[0]} vs ${numericCols[1]}`
      ))
    }

    // 4. 时间序列图
    if (dateCols.length > 0 && numericCols.length > 0) {
      charts.push(this.generateChartConfig(
        sheetData,
        'line',
        dateCols[0],
        numericCols[0],
        undefined,
        `${numericCols[0]} 时间趋势`
      ))
    }

    // 5. 分组条形图
    if (categoricalCols.length > 0 && numericCols.length > 0) {
      const catCol = categoricalCols[0]
      const numCol = numericCols[0]
      const uniqueCount = new Set(data.map(row => row[catCol])).size
      
      if (uniqueCount <= 20 && uniqueCount > 1) {
        charts.push(this.generateChartConfig(
          sheetData,
          'bar',
          catCol,
          numCol,
          undefined,
          `按${catCol}分组的${numCol}`
        ))
      }
    }

    return charts.slice(0, 5) // 最多返回5个图表
  }

  private static createHistogramData(data: any[], column: string, bins: number = 10) {
    const values = data.map(row => Number(row[column])).filter(val => !isNaN(val))
    if (values.length === 0) return []

    const min = Math.min(...values)
    const max = Math.max(...values)
    const binWidth = (max - min) / bins

    const histogram = Array(bins).fill(0)
    values.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1)
      histogram[binIndex]++
    })

    return histogram.map((count, index) => ({
      [column]: `${(min + index * binWidth).toFixed(1)}-${(min + (index + 1) * binWidth).toFixed(1)}`,
      count,
    }))
  }

  private static generateTitle(chartType: string, xAxis: string, yAxis?: string): string {
    const typeNames = {
      bar: '条形图',
      line: '折线图',
      scatter: '散点图',
      pie: '饼图',
      box: '箱线图',
      heatmap: '热力图',
    }

    const typeName = typeNames[chartType as keyof typeof typeNames] || chartType
    
    if (yAxis) {
      return `${typeName}: ${xAxis} vs ${yAxis}`
    } else {
      return `${typeName}: ${xAxis}`
    }
  }

  static convertToPlotlyFormat(chartConfig: ChartConfig): any {
    const { type, xAxis, yAxis, color, title, data } = chartConfig

    const baseConfig = {
      layout: {
        title: title,
        font: { family: 'Arial, sans-serif' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
      },
      config: {
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
      },
    }

    switch (type) {
      case 'bar':
        return {
          data: [{
            x: data.map(row => row[xAxis]),
            y: data.map(row => yAxis ? row[yAxis] : row.count),
            type: 'bar',
            marker: { color: color ? data.map(row => row[color]) : '#3b82f6' },
          }],
          ...baseConfig,
        }

      case 'line':
        return {
          data: [{
            x: data.map(row => row[xAxis]),
            y: data.map(row => row[yAxis!]),
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#3b82f6' },
          }],
          ...baseConfig,
        }

      case 'scatter':
        return {
          data: [{
            x: data.map(row => row[xAxis]),
            y: data.map(row => row[yAxis!]),
            type: 'scatter',
            mode: 'markers',
            marker: { 
              color: color ? data.map(row => row[color]) : '#3b82f6',
              size: 8,
            },
          }],
          ...baseConfig,
        }

      case 'pie':
        return {
          data: [{
            labels: data.map(row => row[xAxis]),
            values: data.map(row => row.count || row[yAxis!]),
            type: 'pie',
          }],
          ...baseConfig,
        }

      default:
        return baseConfig
    }
  }
}