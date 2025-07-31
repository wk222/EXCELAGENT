import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useAppStore } from '../stores/appStore'
import { ExcelService } from '../services/excelService'
import { MCPService } from '../services/mcpService'
import { LocalAnalysisService } from '../services/localAnalysisService'
import { StageCard } from '../components/analysis/StageCard'
import { ChartViewer } from '../components/charts/ChartViewer'
import { FileSpreadsheet, Brain, BarChart3, Target } from 'lucide-react'
import toast from 'react-hot-toast'

export function AnalysisPage() {
  const { 
    excelData, 
    mcpEnabled,
    mcpConnected,
    llmSettings,
    stage1Result, 
    stage2Result, 
    stage3Result,
    stage2Question,
    stage3Question,
    setStageResult,
    setStageQuestion,
    setIsProcessing,
    isProcessing 
  } = useAppStore()

  const mcpService = new MCPService('http://localhost:8080')

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

  const currentSheet = ExcelService.getCurrentSheetData(excelData)
  if (!currentSheet) {
    return <div>无法获取当前工作表数据</div>
  }

  // 准备MCP格式的文件数据
  const prepareFileDataForMCP = () => {
    return {
      filename: excelData.filename,
      dataframe: currentSheet.data,
      columns: currentSheet.columns,
      shape: currentSheet.shape,
      dtypes: Object.fromEntries(
        Object.entries(currentSheet.dtypes).map(([col, type]) => [
          col, 
          type === 'number' ? 'float64' : type === 'date' ? 'datetime64[ns]' : 'object'
        ])
      ),
      current_sheet: currentSheet.name,
      sheet_names: excelData.sheets.map(s => s.name)
    }
  }

  // 阶段一：数据摘要
  const handleStage1 = async () => {
    setIsProcessing(true)

    try {
      setStageResult(1, { status: 'processing', message: '正在处理...' })
      
      let result
      
      if (mcpEnabled && mcpConnected) {
        // 使用MCP后端
        const fileData = prepareFileDataForMCP()
        result = await mcpService.getDataSummary(fileData)
      } else {
        // 使用本地分析
        result = LocalAnalysisService.getDataSummary(currentSheet)
      }
      
      setStageResult(1, result)
      
      if (result.status === 'success') {
        toast.success('阶段一完成！')
      } else {
        toast.error('阶段一执行失败')
      }
    } catch (error) {
      setStageResult(1, {
        status: 'error',
        message: '数据摘要生成失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
      toast.error('阶段一执行失败')
    } finally {
      setIsProcessing(false)
    }
  }

  // 阶段二：AI分析
  const handleStage2 = async () => {
    if (!stage2Question.trim()) {
      toast.error('请输入分析问题')
      return
    }

    setIsProcessing(true)

    try {
      setStageResult(2, { status: 'processing', message: '正在处理...' })
      
      let result
      
      if (mcpEnabled && mcpConnected) {
        // 使用MCP后端进行AI分析
        const fileData = prepareFileDataForMCP()
        const enhancedQuestion = `【阶段二预分析】${stage2Question}\n\n请生成既包含可视化图表又包含统计分析的代码，重点关注有助于后续深度分析的数据洞察。`
        result = await mcpService.analyzeExcelData(fileData, enhancedQuestion)
      } else {
        // 使用本地分析
        result = LocalAnalysisService.analyzeData(currentSheet, stage2Question)
      }
      
      setStageResult(2, result)
      
      if (result.status === 'success') {
        toast.success('阶段二完成！')
      } else {
        toast.error('阶段二执行失败')
      }
    } catch (error) {
      setStageResult(2, {
        status: 'error',
        message: 'AI分析失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
      toast.error('阶段二执行失败')
    } finally {
      setIsProcessing(false)
    }
  }

  // 阶段三：深度分析
  const handleStage3 = async () => {
    if (!stage3Question.trim()) {
      toast.error('请输入深度分析问题')
      return
    }

    setIsProcessing(true)

    try {
      setStageResult(3, { status: 'processing', message: '正在处理...' })
      
      let result
      
      if (mcpEnabled && mcpConnected && stage2Result) {
        // 使用MCP后端进行深度分析
        const dataSummary = stage1Result?.data?.summary || ''
        result = await mcpService.generateDeepAnalysis(stage2Question, stage3Question, stage2Result, dataSummary)
      } else {
        // 本地模式的简化深度分析
        const contextualQuestion = `基于前面的分析结果，${stage3Question}`
        result = LocalAnalysisService.analyzeData(currentSheet, contextualQuestion)
        result.data!.summary = `## 深度分析报告\n\n${result.data!.summary}\n\n**注意**: 当前使用本地分析模式，功能有限。启用MCP模式可获得更深入的AI洞察。`
      }
      
      setStageResult(3, result)
      
      if (result.status === 'success') {
        toast.success('阶段三完成！')
      } else {
        toast.error('阶段三执行失败')
      }
    } catch (error) {
      setStageResult(3, {
        status: 'error',
        message: '深度分析失败',
        error: error instanceof Error ? error.message : '未知错误'
      })
      toast.error('阶段三执行失败')
    } finally {
      setIsProcessing(false)
    }
  }

  const resetStage = (stage: 1 | 2 | 3) => {
    setStageResult(stage, null)
    if (stage <= 2) setStageResult(3, null)
    if (stage === 1) setStageResult(2, null)
    if (stage === 2) setStageQuestion(3, '')
    if (stage === 1) {
      setStageQuestion(2, '')
      setStageQuestion(3, '')
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">数据分析</h1>
          <p className="text-muted-foreground mt-2">
            分阶段进行智能数据分析和洞察发现
          </p>
        </div>
        
        {/* 模式指示器 */}
        <div className="flex items-center space-x-2 text-sm">
          <div className={`px-3 py-1 rounded-full ${
            mcpEnabled && mcpConnected 
              ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
          }`}>
            {mcpEnabled && mcpConnected ? '🐍 MCP模式' : '🔧 本地模式'}
          </div>
        </div>
      </div>

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
      <StageCard
        title="阶段一：数据摘要"
        description="自动分析数据结构、类型和基本统计信息"
        result={stage1Result}
        onExecute={handleStage1}
        onReset={() => resetStage(1)}
        executeLabel="开始数据摘要分析"
        isProcessing={isProcessing && stage1Result?.status === 'processing'}
      />

      {/* 阶段二：AI分析 */}
      <StageCard
        title="阶段二：AI数据分析"
        description={`基于${mcpEnabled && mcpConnected ? 'AI' : '本地'}的智能数据分析和可视化生成`}
        result={stage2Result}
        onExecute={handleStage2}
        onReset={() => resetStage(2)}
        executeLabel="开始AI分析"
        executeDisabled={!stage1Result || !stage2Question.trim()}
        isProcessing={isProcessing && stage2Result?.status === 'processing'}
      >
        {!stage1Result ? (
          <div className="text-muted-foreground">请先完成阶段一</div>
        ) : (
          <div>
            <label className="block text-sm font-medium mb-2">
              分析问题
            </label>
            <textarea
              className="w-full p-3 border border-input rounded-md bg-background"
              rows={3}
              placeholder="例如：分析销售数据的趋势，找出异常值和关键影响因素"
              value={stage2Question}
              onChange={(e) => setStageQuestion(2, e.target.value)}
            />
          </div>
        )}
      </StageCard>

      {/* 阶段二图表展示 */}
      {stage2Result?.status === 'success' && stage2Result.data?.charts && (
        <ChartViewer 
          charts={stage2Result.data.charts}
          title="阶段二生成的图表"
        />
      )}

      {/* 阶段三：深度分析 */}
      <StageCard
        title="阶段三：深度洞察分析"
        description="基于前面分析结果的深度洞察和业务建议"
        result={stage3Result}
        onExecute={handleStage3}
        onReset={() => resetStage(3)}
        executeLabel="开始深度分析"
        executeDisabled={!stage2Result || !stage3Question.trim()}
        isProcessing={isProcessing && stage3Result?.status === 'processing'}
      >
        {!stage2Result ? (
          <div className="text-muted-foreground">请先完成阶段二</div>
        ) : (
          <div className="space-y-4">
            {/* 显示阶段二问题作为上下文 */}
            {stage2Question && (
              <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  <strong>阶段二分析问题：</strong>{stage2Question}
                </div>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium mb-2">
                深度分析问题
              </label>
              <textarea
                className="w-full p-3 border border-input rounded-md bg-background"
                rows={3}
                placeholder="例如：基于前面的分析结果，请深入探讨异常值的业务原因，并提供改进建议"
                value={stage3Question}
                onChange={(e) => setStageQuestion(3, e.target.value)}
              />
            </div>
          </div>
        )}
      </StageCard>
    </div>
  )
}