import React from 'react'
import Plot from 'react-plotly.js'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { Download, Image } from 'lucide-react'

interface ChartViewerProps {
  charts: string[]
  title?: string
  className?: string
}

export function ChartViewer({ charts, title = "图表展示", className }: ChartViewerProps) {
  if (!charts || charts.length === 0) {
    return null
  }

  const downloadChart = (chartData: any, index: number) => {
    // 创建下载HTML
    const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Chart ${index + 1}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div id="chart" style="width:100%;height:600px;"></div>
    <script>
        Plotly.newPlot('chart', ${JSON.stringify(chartData.data)}, ${JSON.stringify(chartData.layout)});
    </script>
</body>
</html>`
    
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chart_${index + 1}.html`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>{title}</span>
          <span className="text-sm text-muted-foreground">({charts.length} 个图表)</span>
        </CardTitle>
        <CardDescription>
          AI自动生成的数据可视化图表
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {charts.map((chartJson, index) => {
            try {
              // 尝试解析图表数据
              let chartData
              
              // 如果是plotly格式的JSON字符串
              if (typeof chartJson === 'string') {
                try {
                  chartData = JSON.parse(chartJson)
                } catch {
                  // 如果解析失败，可能是plotly的to_json格式
                  const cleanJson = chartJson.replace(/NaN/g, 'null').replace(/Infinity/g, 'null')
                  chartData = JSON.parse(cleanJson)
                }
              } else {
                chartData = chartJson
              }

              // 确保数据格式正确
              if (!chartData.data) {
                throw new Error('无效的图表数据格式')
              }

              return (
                <div key={index} className="border border-border rounded-lg p-4 bg-card">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium">
                      图表 {index + 1}
                      {chartData.layout?.title && `: ${chartData.layout.title}`}
                    </h4>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadChart(chartData, index)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        下载
                      </Button>
                    </div>
                  </div>
                  
                  <div className="w-full h-96">
                    <Plot
                      data={chartData.data}
                      layout={{
                        ...chartData.layout,
                        autosize: true,
                        margin: { l: 50, r: 50, t: 50, b: 50 },
                        font: { family: 'Arial, sans-serif' },
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                      }}
                      config={{
                        displayModeBar: true,
                        displaylogo: false,
                        modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
                        responsive: true,
                      }}
                      style={{ width: '100%', height: '100%' }}
                      useResizeHandler={true}
                    />
                  </div>
                </div>
              )
            } catch (error) {
              console.error(`图表 ${index + 1} 渲染失败:`, error)
              return (
                <div key={index} className="border border-border rounded-lg p-4 bg-card">
                  <div className="text-center text-muted-foreground py-8">
                    <Image className="h-8 w-8 mx-auto mb-2" />
                    <div>图表 {index + 1} 加载失败</div>
                    <div className="text-xs mt-1">
                      {error instanceof Error ? error.message : '渲染错误'}
                    </div>
                  </div>
                </div>
              )
            }
          })}
        </div>
      </CardContent>
    </Card>
  )
}