import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { useAppStore } from '../../stores/appStore'
import { MCPService } from '../../services/mcpService'
import { Wifi, WifiOff, TestTube, AlertCircle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export function MCPSettings() {
  const { mcpEnabled, mcpConnected, setMCPEnabled, setMCPConnected } = useAppStore()
  const [mcpUrl, setMcpUrl] = useState('http://localhost:8080')
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'success' | 'error'>('unknown')

  const mcpService = new MCPService(mcpUrl)

  useEffect(() => {
    if (mcpEnabled) {
      testConnection()
    }
  }, [mcpEnabled])

  const testConnection = async () => {
    setIsTestingConnection(true)
    setConnectionStatus('unknown')

    try {
      const connected = await mcpService.checkConnection()
      setMCPConnected(connected)
      setConnectionStatus(connected ? 'success' : 'error')
      
      if (connected) {
        toast.success('MCP服务器连接成功')
      } else {
        toast.error('MCP服务器连接失败')
      }
    } catch (error) {
      setMCPConnected(false)
      setConnectionStatus('error')
      toast.error(`连接测试失败: ${error instanceof Error ? error.message : '未知错误'}`)
    } finally {
      setIsTestingConnection(false)
    }
  }

  const toggleMCP = () => {
    setMCPEnabled(!mcpEnabled)
    if (!mcpEnabled) {
      toast.success('已启用MCP模式，将使用Python后端进行数据分析')
    } else {
      setMCPConnected(false)
      toast.success('已禁用MCP模式，将使用本地JavaScript分析')
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          {mcpEnabled && mcpConnected ? (
            <Wifi className="h-5 w-5 text-green-500" />
          ) : (
            <WifiOff className="h-5 w-5 text-muted-foreground" />
          )}
          <span>MCP后端连接</span>
        </CardTitle>
        <CardDescription>
          配置Model Context Protocol后端连接，获得完整的Python数据分析能力
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* MCP开关 */}
        <div className="flex items-center justify-between p-4 border border-border rounded-lg">
          <div>
            <div className="font-medium">启用MCP模式</div>
            <div className="text-sm text-muted-foreground">
              {mcpEnabled 
                ? '使用Python后端，支持完整的数据分析和AI代码生成' 
                : '使用JavaScript本地分析，功能有限但无需后端'}
            </div>
          </div>
          <Button
            variant={mcpEnabled ? "default" : "outline"}
            onClick={toggleMCP}
          >
            {mcpEnabled ? '已启用' : '已禁用'}
          </Button>
        </div>

        {/* MCP连接配置 */}
        {mcpEnabled && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                MCP服务器地址
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  className="flex-1 p-3 border border-input rounded-md bg-background"
                  placeholder="http://localhost:8080"
                  value={mcpUrl}
                  onChange={(e) => setMcpUrl(e.target.value)}
                />
                <Button
                  variant="outline"
                  onClick={testConnection}
                  disabled={isTestingConnection}
                >
                  {isTestingConnection ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                  ) : (
                    <TestTube className="h-4 w-4 mr-2" />
                  )}
                  测试连接
                </Button>
              </div>
            </div>

            {/* 连接状态 */}
            {connectionStatus !== 'unknown' && (
              <div className={`flex items-center space-x-2 p-3 rounded-lg ${
                connectionStatus === 'success' 
                  ? 'bg-green-50 dark:bg-green-950/20 text-green-700 dark:text-green-300'
                  : 'bg-red-50 dark:bg-red-950/20 text-red-700 dark:text-red-300'
              }`}>
                {connectionStatus === 'success' ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <AlertCircle className="h-4 w-4" />
                )}
                <span className="text-sm">
                  {connectionStatus === 'success' 
                    ? '✅ MCP服务器连接正常，可使用完整功能'
                    : '❌ MCP服务器连接失败，将使用本地分析模式'}
                </span>
              </div>
            )}

            {/* MCP功能说明 */}
            <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <h4 className="font-medium text-blue-700 dark:text-blue-300 mb-2">MCP模式功能</h4>
              <ul className="text-sm text-blue-600 dark:text-blue-400 space-y-1">
                <li>• AI驱动的Python代码生成</li>
                <li>• 高质量的Plotly交互式图表</li>
                <li>• 深度统计分析和数据洞察</li>
                <li>• 自定义代码执行环境</li>
                <li>• 专业的数据分析报告</li>
              </ul>
            </div>

            {/* 启动MCP服务器的说明 */}
            {!mcpConnected && (
              <div className="p-4 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg">
                <h4 className="font-medium text-yellow-700 dark:text-yellow-300 mb-2">启动MCP服务器</h4>
                <div className="text-sm text-yellow-600 dark:text-yellow-400 space-y-2">
                  <p>请确保Python MCP服务器正在运行：</p>
                  <div className="font-mono bg-yellow-100 dark:bg-yellow-900/30 p-2 rounded">
                    python excel_mcp_server.py --transport http
                  </div>
                  <p>或者使用启动脚本：</p>
                  <div className="font-mono bg-yellow-100 dark:bg-yellow-900/30 p-2 rounded">
                    python start_server.py
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 本地模式说明 */}
        {!mcpEnabled && (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h4 className="font-medium mb-2">本地JavaScript模式</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• 基础数据统计和摘要</li>
              <li>• 简单的图表生成</li>
              <li>• 数据质量检查</li>
              <li>• 无需后端依赖</li>
            </ul>
            <div className="mt-2 text-xs text-muted-foreground">
              注意：本地模式功能有限，建议使用MCP模式获得完整体验
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}