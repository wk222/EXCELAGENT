import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileSpreadsheet, BarChart3, Settings, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { useAppStore } from '../stores/appStore'
import { ExcelService } from '../services/excelService'
import { cn } from '../utils/cn'

export function HomePage() {
  const navigate = useNavigate()
  const { excelData, setExcelData, resetAll, mcpEnabled, mcpConnected } = useAppStore()
  const [isDragOver, setIsDragOver] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileUpload = useCallback(async (file: File) => {
    if (!file) return

    // 验证文件类型
    const allowedTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ]
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls)$/i)) {
      toast.error('请上传Excel文件 (.xlsx 或 .xls)')
      return
    }

    // 验证文件大小 (50MB限制)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('文件大小不能超过50MB')
      return
    }

    setIsProcessing(true)
    const loadingToast = toast.loading('正在解析Excel文件...')

    try {
      const data = await ExcelService.processFile(file)
      setExcelData(data)
      
      toast.success('文件上传成功！', { id: loadingToast })
      
      // 自动跳转到分析页面
      setTimeout(() => {
        navigate('/analysis')
      }, 1000)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '文件处理失败', { id: loadingToast })
    } finally {
      setIsProcessing(false)
    }
  }, [setExcelData, navigate])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileUpload(file)
    }
  }, [handleFileUpload])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }, [handleFileUpload])

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center space-y-4">
        {/* 模式状态指示 */}
        <div className="flex justify-center">
          <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm ${
            mcpEnabled && mcpConnected 
              ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
          }`}>
            <span>{mcpEnabled && mcpConnected ? '🐍 MCP增强模式' : '🔧 本地基础模式'}</span>
          </div>
        </div>
      </div>
      
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3">
          <FileSpreadsheet className="h-12 w-12 text-primary" />
          <h1 className="text-4xl font-bold text-foreground">Excel智能体</h1>
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          基于人工智能的Excel数据分析工具，{mcpEnabled && mcpConnected ? '支持Python后端增强分析' : '纯JavaScript本地分析'}
        </p>
      </div>

      {/* 功能特性 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <BarChart3 className="h-8 w-8 text-primary mx-auto mb-2" />
            <CardTitle className="text-lg">智能分析</CardTitle>
            <CardDescription>
              {mcpEnabled && mcpConnected ? 'Python AI驱动的深度数据分析' : 'JavaScript本地数据分析'}
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <Zap className="h-8 w-8 text-primary mx-auto mb-2" />
            <CardTitle className="text-lg">快速处理</CardTitle>
            <CardDescription>
              支持多工作表，秒级完成数据解析和预处理
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="text-center">
            <Settings className="h-8 w-8 text-primary mx-auto mb-2" />
            <CardTitle className="text-lg">灵活配置</CardTitle>
            <CardDescription>
              支持MCP和本地双模式，{mcpEnabled && mcpConnected ? '可调节AI参数' : '轻量级部署'}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* 文件上传区域 */}
      <Card className="border-2 border-dashed border-border hover:border-primary/50 transition-colors">
        <CardContent className="p-8">
          <div
            className={cn(
              'relative rounded-lg p-8 text-center transition-colors',
              isDragOver && 'bg-primary/5 border-primary',
              !isDragOver && 'hover:bg-muted/50'
            )}
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragOver(true)
            }}
            onDragLeave={() => setIsDragOver(false)}
          >
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isProcessing}
            />
            
            <div className="space-y-4">
              <Upload className="h-16 w-16 text-muted-foreground mx-auto" />
              <div>
                <h3 className="text-lg font-medium">
                  {isDragOver ? '释放文件开始上传' : '拖拽Excel文件到此处'}
                </h3>
                <p className="text-muted-foreground mt-1">
                  或者 <span className="text-primary font-medium cursor-pointer hover:underline">点击选择文件</span>
                </p>
              </div>
              <div className="text-sm text-muted-foreground">
                支持 .xlsx 和 .xls 格式，最大50MB
              </div>
            </div>
            
            {isProcessing && (
              <div className="absolute inset-0 bg-background/80 rounded-lg flex items-center justify-center">
                <div className="text-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <div className="text-sm text-muted-foreground">正在处理文件...</div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 当前文件信息 */}
      {excelData && (
        <Card className="animate-fade-in">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileSpreadsheet className="h-5 w-5" />
              <span>当前文件</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">文件名</div>
                <div className="font-medium truncate" title={excelData.filename}>
                  {excelData.filename}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">工作表</div>
                <div className="font-medium">
                  {excelData.currentSheet} ({excelData.sheets.length} 个工作表)
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">数据规模</div>
                <div className="font-medium">
                  {excelData.sheets.find(s => s.name === excelData.currentSheet)?.shape.join(' × ') || '0 × 0'}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 mt-4">
              <Button onClick={() => navigate('/analysis')}>
                开始分析
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  resetAll()
                  toast.success('文件已清除')
                }}
              >
                清除文件
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 使用说明 */}
      <Card>
        <CardHeader>
          <CardTitle>使用方法</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium">基本步骤</h4>
              <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
                <li>上传Excel文件（.xlsx 或 .xls格式）</li>
                <li>选择要分析的工作表</li>
                <li>进入数据分析页面</li>
                <li>输入分析问题，获得AI洞察</li>
                <li>查看自动生成的图表和建议</li>
              </ol>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium">高级功能</h4>
              <ul className="list-disc list-inside space-y-2 text-sm text-muted-foreground">
                <li>多工作表支持和快速切换</li>
                <li>自定义图表创建和配置</li>
                <li>{mcpEnabled && mcpConnected ? 'Python MCP后端增强分析' : 'JavaScript本地轻量分析'}</li>
                <li>{mcpEnabled && mcpConnected ? 'AI参数调节和优化' : '基础数据统计和图表'}</li>
                <li>{mcpEnabled && mcpConnected ? '专业级分析报告' : '简化分析结果'}</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}