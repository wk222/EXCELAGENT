import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useAppStore } from '../stores/appStore'
import { ExcelProcessor } from '../utils/excelProcessor'
import { ChartGenerator } from '../utils/chartGenerator'
import { FileSpreadsheet, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import Plot from 'react-plotly.js'
import type { ChartConfig } from '../types'

export function ChartsPage() {
  const { excelData } = useAppStore()
  const [customCharts, setCustomCharts] = useState<ChartConfig[]>([])
  const [chartConfig, setChartConfig] = useState({
    type: 'bar' as ChartConfig['type'],
    xAxis: '',
    yAxis: '',
    color: '',
    title: '',
  })

  if (!excelData) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="text-center py-12">
            <FileSpreadsheet className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">请先上传Excel文件</h3>
            <p className="text-muted-foreground mb-4">
              需要先上传Excel文件才能创建自定义图表
            </p>
            <Button onClick={() => window.location.href = '/'}>
              返回首页上传文件
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const currentSheet = ExcelProcessor.getCurrentSheetData(excelData)
  if (!currentSheet) {
    return <div>无法获取当前工作表数据</div>
  }

  const handleCreateChart = () => {
    if (!chartConfig.xAxis) {
      toast.error('请选择X轴数据列')
      return
    }

    if (!['pie', 'histogram'].includes(chartConfig.type) && !chartConfig.yAxis) {
      toast.error('请选择Y轴数据列')
      return
    }

    try {
      const newChart = ChartGenerator.generateChartConfig(
        currentSheet,
        chartConfig.type,
        chartConfig.xAxis,
        chartConfig.yAxis || undefined,
        chartConfig.color || undefined,
        chartConfig.title || undefined
      )

      setCustomCharts(prev => [...prev, newChart])
      toast.success('图表创建成功！')
      
      // 重置表单
      setChartConfig({
        type: 'bar',
        xAxis: '',
        yAxis: '',
        color: '',
        title: '',
      })
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '图表创建失败')
    }
  }

  const handleGenerateAutoCharts = () => {
    try {
      const autoCharts = ChartGenerator.generateAutoCharts(currentSheet)
      setCustomCharts(prev => [...prev, ...autoCharts])
      toast.success(`自动生成了${autoCharts.length}个图表！`)
    } catch (error) {
      toast.error('自动生成图表失败')
    }
  }

  const handleDeleteChart = (index: number) => {
    setCustomCharts(prev => prev.filter((_, i) => i !== index))
    toast.success('图表已删除')
  }

  const numericColumns = currentSheet.columns.filter(col => currentSheet.dtypes[col] === 'number')
  const categoricalColumns = currentSheet.columns.filter(col => currentSheet.dtypes[col] === 'string')
  const allColumns = currentSheet.columns

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold">自定义图表</h1>
        <p className="text-muted-foreground mt-2">
          为您的数据创建各种类型的可视化图表
        </p>
      </div>

      {/* 文件信息 */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm">
              <span>📄 {excelData.filename}</span>
              <span>📋 {excelData.currentSheet}</span>
              <span>📊 {currentSheet.shape.join(' × ')}</span>
            </div>
            <Button variant="outline" size="sm" onClick={handleGenerateAutoCharts}>
              <Plus className="h-4 w-4 mr-2" />
              自动生成图表
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 图表配置面板 */}
        <div className="lg:col-span-1">
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>图表配置</CardTitle>
              <CardDescription>
                选择图表类型和数据列来创建自定义图表
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 图表类型 */}
              <div>
                <label className="block text-sm font-medium mb-2">图表类型</label>
                <select
                  className="w-full p-2 border border-input rounded-md bg-background"
                  value={chartConfig.type}
                  onChange={(e) => setChartConfig(prev => ({ 
                    ...prev, 
                    type: e.target.value as ChartConfig['type'] 
                  }))}
                >
                  <option value="bar">条形图</option>
                  <option value="line">折线图</option>
                  <option value="scatter">散点图</option>
                  <option value="pie">饼图</option>
                  <option value="box">箱线图</option>
                  <option value="heatmap">热力图</option>
                </select>
              </div>

              {/* X轴 */}
              <div>
                <label className="block text-sm font-medium mb-2">X轴数据列</label>
                <select
                  className="w-full p-2 border border-input rounded-md bg-background"
                  value={chartConfig.xAxis}
                  onChange={(e) => setChartConfig(prev => ({ ...prev, xAxis: e.target.value }))}
                >
                  <option value="">请选择列...</option>
                  {allColumns.map(col => (
                    <option key={col} value={col}>
                      {col} ({currentSheet.dtypes[col]})
                    </option>
                  ))}
                </select>
              </div>

              {/* Y轴 */}
              {!['pie'].includes(chartConfig.type) && (
                <div>
                  <label className="block text-sm font-medium mb-2">Y轴数据列</label>
                  <select
                    className="w-full p-2 border border-input rounded-md bg-background"
                    value={chartConfig.yAxis}
                    onChange={(e) => setChartConfig(prev => ({ ...prev, yAxis: e.target.value }))}
                  >
                    <option value="">请选择列...</option>
                    {(chartConfig.type === 'scatter' ? numericColumns : allColumns).map(col => (
                      <option key={col} value={col}>
                        {col} ({currentSheet.dtypes[col]})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* 颜色分组 */}
              <div>
                <label className="block text-sm font-medium mb-2">颜色分组 (可选)</label>
                <select
                  className="w-full p-2 border border-input rounded-md bg-background"
                  value={chartConfig.color}
                  onChange={(e) => setChartConfig(prev => ({ ...prev, color: e.target.value }))}
                >
                  <option value="">无分组</option>
                  {categoricalColumns.map(col => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>

              {/* 图表标题 */}
              <div>
                <label className="block text-sm font-medium mb-2">图表标题</label>
                <input
                  type="text"
                  className="w-full p-2 border border-input rounded-md bg-background"
                  placeholder="自动生成标题"
                  value={chartConfig.title}
                  onChange={(e) => setChartConfig(prev => ({ ...prev, title: e.target.value }))}
                />
              </div>

              {/* 创建按钮 */}
              <Button 
                onClick={handleCreateChart} 
                className="w-full"
                disabled={!chartConfig.xAxis}
              >
                <Plus className="h-4 w-4 mr-2" />
                创建图表
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 图表展示区域 */}
        <div className="lg:col-span-2">
          {customCharts.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <div className="space-y-4">
                  <div className="text-6xl">📊</div>
                  <h3 className="text-lg font-medium">暂无自定义图表</h3>
                  <p className="text-muted-foreground">
                    使用左侧的配置面板创建您的第一个图表
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {customCharts.map((chart, index) => {
                const plotlyData = ChartGenerator.convertToPlotlyFormat(chart)
                return (
                  <Card key={index}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{chart.title}</CardTitle>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteChart(index)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="w-full h-96">
                        <Plot
                          data={plotlyData.data}
                          layout={{
                            ...plotlyData.layout,
                            autosize: true,
                            margin: { l: 50, r: 50, t: 50, b: 50 },
                          }}
                          config={plotlyData.config}
                          style={{ width: '100%', height: '100%' }}
                          useResizeHandler={true}
                        />
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}