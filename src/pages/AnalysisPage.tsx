import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useAppStore } from '../stores/appStore'
import { ExcelProcessor } from '../utils/excelProcessor'
import { DataAnalyzer } from '../utils/dataAnalyzer'
import { LLMService } from '../utils/llmService'
import { ChartGenerator } from '../utils/chartGenerator'
import { AlertCircle, BarChart3, Brain, CheckCircle, Clock, FileSpreadsheet } from 'lucide-react'
import toast from 'react-hot-toast'
import Plot from 'react-plotly.js'

export function AnalysisPage() {
  const { 
    excelData, 
    llmSettings,
    stage1Result, 
    stage2Result, 
    stage3Result,
    setStageResult,
    setIsProcessing,
    isProcessing 
  } = useAppStore()

  const [questions, setQuestions] = useState({
    stage2: '',
    stage3: ''
  })

  if (!excelData) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="text-center py-12">
            <FileSpreadsheet className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">请先上传Excel文件</h3>
            <p className="text-muted-foreground mb-4">
              需要先上传并解析Excel文件才能进行数据分析
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

  // 阶段一：数据摘要
  const handleStage1 = async () => {
    setIsProcessing(true)
    const loadingToast = toast.loading('正在生成数据摘要...')

    try {
      setStageResult(1, { status: 'processing', message: '正在处理...' })
      
      // 模拟处理延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const summary = ExcelProcessor.getDataSummary(currentSheet)
      const analysis = DataAnalyzer.analyzeData(currentSheet)
      const validation = ExcelProcessor.validateData(currentSheet)
      
      setStageResult(1, {
        status: 'success',
        message: '数据摘要生成完成',
        data: {
          summary,
          insights: analysis.insights,
        }
      })
      
      toast.success('阶段一完成！', { id: loadingToast })
    } catch (error) {
      setStageResult(1, {
        status: 'error',
        message: '数据摘要生成失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
      toast.error('阶段一执行失败', { id: loadingToast })
    } finally {
      setIsProcessing(false)
    }
  }

  // 阶段二：AI分析
  const handleStage2 = async () => {
    if (!questions.stage2.trim()) {
      toast.error('请输入分析问题')
      return
    }

    setIsProcessing(true)
    const loadingToast = toast.loading('正在进行AI分析...')

    try {
      setStageResult(2, { status: 'processing', message: '正在处理...' })
      
      const llmService = new LLMService(llmSettings)
      const dataContent = stage1Result?.data?.summary || ExcelProcessor.getDataSummary(currentSheet)
      
      // 生成分析结果
      const analysis = await llmService.generateDataAnalysis(dataContent, questions.stage2)
      
      // 生成图表建议
      const chartSuggestion = await llmService.generateCodeSuggestion(dataContent, questions.stage2)
      
      // 自动生成一些图表
      const autoCharts = ChartGenerator.generateAutoCharts(currentSheet)
      const chartJsons = autoCharts.map(chart => JSON.stringify(ChartGenerator.convertToPlotlyFormat(chart)))
      
      setStageResult(2, {
        status: 'success',
        message: `AI分析完成，生成了${autoCharts.length}个图表`,
        data: {
          summary: analysis,
          charts: chartJsons,
          insights: [chartSuggestion],
        }
      })
      
      toast.success('阶段二完成！', { id: loadingToast })
    } catch (error) {
      setStageResult(2, {
        status: 'error',
        message: 'AI分析失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
      toast.error('阶段二执行失败', { id: loadingToast })
    } finally {
      setIsProcessing(false)
    }
  }

  // 阶段三：深度分析
  const handleStage3 = async () => {
    if (!questions.stage3.trim()) {
      toast.error('请输入深度分析问题')
      return
    }

    setIsProcessing(true)
    const loadingToast = toast.loading('正在进行深度分析...')

    try {
      setStageResult(3, { status: 'processing', message: '正在处理...' })
      
      const llmService = new LLMService(llmSettings)
      
      // 构建深度分析上下文
      const context = `
        阶段一数据摘要：${stage1Result?.data?.summary || ''}
        阶段二分析结果：${stage2Result?.data?.summary || ''}
        阶段二发现洞察：${stage2Result?.data?.insights?.join('\n') || ''}
      `
      
      const deepAnalysis = await llmService.generateDataAnalysis(context, 
        `基于前面的分析结果，请深入分析：${questions.stage3}`)
      
      setStageResult(3, {
        status: 'success',
        message: '深度分析完成',
        data: {
          summary: deepAnalysis,
        }
      })
      
      toast.success('阶段三完成！', { id: loadingToast })
    } catch (error) {
      setStageResult(3, {
        status: 'error',
        message: '深度分析失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
      toast.error('阶段三执行失败', { id: loadingToast })
    } finally {
      setIsProcessing(false)
    }
  }

  const resetStage = (stage: 1 | 2 | 3) => {
    setStageResult(stage, null)
    if (stage <= 2) setStageResult(3, null)
    if (stage === 1) setStageResult(2, null)
  }

  const getStageIcon = (result: typeof stage1Result) => {
    if (!result) return <Clock className="h-5 w-5 text-muted-foreground" />
    if (result.status === 'processing') return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
    if (result.status === 'success') return <CheckCircle className="h-5 w-5 text-green-500" />
    return <AlertCircle className="h-5 w-5 text-red-500" />
  }

  const getStageStatus = (result: typeof stage1Result) => {
    if (!result) return '待执行'
    if (result.status === 'processing') return '执行中'
    if (result.status === 'success') return '已完成'
    return '执行失败'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 文件信息 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileSpreadsheet className="h-5 w-5" />
            <span>当前分析文件</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-muted-foreground">文件名</div>
              <div className="font-medium truncate">{excelData.filename}</div>
            </div>
            <div>
              <div className="text-muted-foreground">工作表</div>
              <div className="font-medium">{excelData.currentSheet}</div>
            </div>
            <div>
              <div className="text-muted-foreground">数据规模</div>
              <div className="font-medium">{currentSheet.shape.join(' × ')}</div>
            </div>
            <div>
              <div className="text-muted-foreground">列数</div>
              <div className="font-medium">{currentSheet.columns.length} 列</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 阶段一：数据摘要 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStageIcon(stage1Result)}
              <span>阶段一：数据摘要</span>
              <span className="text-sm text-muted-foreground">({getStageStatus(stage1Result)})</span>
            </div>
            {stage1Result && (
              <Button variant="outline" size="sm" onClick={() => resetStage(1)}>
                重置
              </Button>
            )}
          </CardTitle>
          <CardDescription>
            自动分析数据结构、类型和基本统计信息
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!stage1Result ? (
            <Button onClick={handleStage1} disabled={isProcessing}>
              <BarChart3 className="h-4 w-4 mr-2" />
              开始数据摘要分析
            </Button>
          ) : stage1Result.status === 'success' ? (
            <div className="space-y-4">
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">数据摘要</h4>
                <pre className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {stage1Result.data?.summary}
                </pre>
              </div>
              {stage1Result.data?.insights && (
                <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                  <h4 className="font-medium mb-2">关键洞察</h4>
                  <ul className="text-sm space-y-1">
                    {stage1Result.data.insights.map((insight, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="text-blue-500 mt-1">•</span>
                        <span>{insight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-500">
              执行失败: {stage1Result.error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 阶段二：AI分析 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStageIcon(stage2Result)}
              <span>阶段二：AI数据分析</span>
              <span className="text-sm text-muted-foreground">({getStageStatus(stage2Result)})</span>
            </div>
            {stage2Result && (
              <Button variant="outline" size="sm" onClick={() => resetStage(2)}>
                重置
              </Button>
            )}
          </CardTitle>
          <CardDescription>
            基于AI的智能数据分析和可视化生成
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!stage1Result ? (
            <div className="text-muted-foreground">请先完成阶段一</div>
          ) : !stage2Result ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  分析问题
                </label>
                <textarea
                  className="w-full p-3 border border-input rounded-md bg-background"
                  rows={3}
                  placeholder="例如：分析销售数据的趋势，找出异常值和关键影响因素"
                  value={questions.stage2}
                  onChange={(e) => setQuestions(prev => ({ ...prev, stage2: e.target.value }))}
                />
              </div>
              <Button 
                onClick={handleStage2} 
                disabled={isProcessing || !questions.stage2.trim()}
              >
                <Brain className="h-4 w-4 mr-2" />
                开始AI分析
              </Button>
            </div>
          ) : stage2Result.status === 'success' ? (
            <div className="space-y-6">
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">AI分析结果</h4>
                <div className="text-sm whitespace-pre-wrap">
                  {stage2Result.data?.summary}
                </div>
              </div>
              
              {stage2Result.data?.charts && stage2Result.data.charts.length > 0 && (
                <div>
                  <h4 className="font-medium mb-4">自动生成的图表</h4>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {stage2Result.data.charts.map((chartJson, index) => {
                      try {
                        const chartData = JSON.parse(chartJson)
                        return (
                          <div key={index} className="border border-border rounded-lg p-4">
                            <Plot
                              data={chartData.data}
                              layout={{
                                ...chartData.layout,
                                autosize: true,
                                margin: { l: 50, r: 50, t: 50, b: 50 },
                              }}
                              config={chartData.config}
                              style={{ width: '100%', height: '400px' }}
                              useResizeHandler={true}
                            />
                          </div>
                        )
                      } catch (error) {
                        return (
                          <div key={index} className="border border-border rounded-lg p-4 text-center text-muted-foreground">
                            图表加载失败
                          </div>
                        )
                      }
                    })}
                  </div>
                </div>
              )}

              {stage2Result.data?.insights && (
                <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                  <h4 className="font-medium mb-2">分析建议</h4>
                  <div className="text-sm whitespace-pre-wrap">
                    {stage2Result.data.insights.join('\n\n')}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-500">
              执行失败: {stage2Result.error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 阶段三：深度分析 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStageIcon(stage3Result)}
              <span>阶段三：深度分析</span>
              <span className="text-sm text-muted-foreground">({getStageStatus(stage3Result)})</span>
            </div>
            {stage3Result && (
              <Button variant="outline" size="sm" onClick={() => resetStage(3)}>
                重置
              </Button>
            )}
          </CardTitle>
          <CardDescription>
            基于前面分析结果的深度洞察和业务建议
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!stage2Result ? (
            <div className="text-muted-foreground">请先完成阶段二</div>
          ) : !stage3Result ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  深度分析问题
                </label>
                <textarea
                  className="w-full p-3 border border-input rounded-md bg-background"
                  rows={3}
                  placeholder="例如：基于前面的分析结果，请深入探讨异常值的业务原因，并提供改进建议"
                  value={questions.stage3}
                  onChange={(e) => setQuestions(prev => ({ ...prev, stage3: e.target.value }))}
                />
              </div>
              <Button 
                onClick={handleStage3} 
                disabled={isProcessing || !questions.stage3.trim()}
              >
                <Brain className="h-4 w-4 mr-2" />
                开始深度分析
              </Button>
            </div>
          ) : stage3Result.status === 'success' ? (
            <div className="p-4 bg-muted rounded-lg">
              <h4 className="font-medium mb-2">深度分析报告</h4>
              <div className="text-sm whitespace-pre-wrap">
                {stage3Result.data?.summary}
              </div>
            </div>
          ) : (
            <div className="text-red-500">
              执行失败: {stage3Result.error}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}