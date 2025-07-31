import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { AlertCircle, CheckCircle, Clock, RefreshCw } from 'lucide-react'
import type { AnalysisResult } from '../../services/mcpService'

interface StageCardProps {
  title: string
  description: string
  result: AnalysisResult | null
  onExecute: () => void
  onReset: () => void
  children?: React.ReactNode
  executeLabel?: string
  executeDisabled?: boolean
  isProcessing?: boolean
}

export function StageCard({
  title,
  description,
  result,
  onExecute,
  onReset,
  children,
  executeLabel = '执行',
  executeDisabled = false,
  isProcessing = false
}: StageCardProps) {
  
  const getStageIcon = () => {
    if (isProcessing) {
      return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
    }
    if (!result) return <Clock className="h-5 w-5 text-muted-foreground" />
    if (result.status === 'success') return <CheckCircle className="h-5 w-5 text-green-500" />
    if (result.status === 'error') return <AlertCircle className="h-5 w-5 text-red-500" />
    return <Clock className="h-5 w-5 text-muted-foreground" />
  }

  const getStageStatus = () => {
    if (isProcessing) return '执行中'
    if (!result) return '待执行'
    if (result.status === 'success') return '已完成'
    if (result.status === 'error') return '执行失败'
    return '未知状态'
  }

  const getStageColor = () => {
    if (isProcessing) return 'border-l-blue-500'
    if (!result) return 'border-l-gray-300'
    if (result.status === 'success') return 'border-l-green-500'
    if (result.status === 'error') return 'border-l-red-500'
    return 'border-l-gray-300'
  }

  return (
    <Card className={`border-l-4 ${getStageColor()} transition-colors`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getStageIcon()}
            <span>{title}</span>
            <span className="text-sm text-muted-foreground">({getStageStatus()})</span>
          </div>
          {result && (
            <Button variant="outline" size="sm" onClick={onReset} disabled={isProcessing}>
              <RefreshCw className="h-4 w-4 mr-1" />
              重置
            </Button>
          )}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      
      <CardContent>
        {!result ? (
          <div className="space-y-4">
            {children}
            <Button 
              onClick={onExecute} 
              disabled={executeDisabled || isProcessing}
              loading={isProcessing}
            >
              {executeLabel}
            </Button>
          </div>
        ) : result.status === 'success' ? (
          <div className="space-y-4">
            {result.data?.summary && (
              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">分析结果</h4>
                <div className="text-sm whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {result.data.summary}
                </div>
              </div>
            )}

            {result.data?.insights && result.data.insights.length > 0 && (
              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h4 className="font-medium mb-2">关键洞察</h4>
                <ul className="text-sm space-y-1">
                  {result.data.insights.map((insight, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.data?.code && (
              <details className="group">
                <summary className="cursor-pointer p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                  <span className="font-medium">查看生成的代码</span>
                </summary>
                <div className="mt-2 p-4 bg-gray-900 rounded-lg">
                  <pre className="text-sm text-green-400 overflow-x-auto">
                    <code>{result.data.code}</code>
                  </pre>
                </div>
              </details>
            )}

            {result.data?.execution_results?.stdout && (
              <details className="group">
                <summary className="cursor-pointer p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                  <span className="font-medium">查看执行输出</span>
                </summary>
                <div className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <pre className="text-sm overflow-x-auto">
                    {result.data.execution_results.stdout}
                  </pre>
                </div>
              </details>
            )}
          </div>
        ) : (
          <div className="p-4 bg-red-50 dark:bg-red-950/20 rounded-lg">
            <div className="text-red-700 dark:text-red-300 font-medium mb-2">
              执行失败
            </div>
            <div className="text-sm text-red-600 dark:text-red-400">
              {result.error || result.message}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}