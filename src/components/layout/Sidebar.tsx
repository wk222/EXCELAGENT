import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  BarChart3, 
  PieChart, 
  Settings, 
  ChevronLeft,
  ChevronRight,
  FileSpreadsheet,
  Lightbulb
} from 'lucide-react'
import { useAppStore } from '../../stores/appStore'
import { cn } from '../../utils/cn'
import { Button } from '../ui/Button'

const navigation = [
  { name: '首页', href: '/', icon: Home },
  { name: '数据分析', href: '/analysis', icon: BarChart3 },
  { name: '自定义图表', href: '/charts', icon: PieChart },
  { name: '设置', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()
  const { sidebarCollapsed, setSidebarCollapsed, excelData, theme } = useAppStore()

  return (
    <div className={cn(
      'flex flex-col bg-card border-r border-border transition-all duration-300',
      sidebarCollapsed ? 'w-16' : 'w-64'
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!sidebarCollapsed && (
          <div className="flex items-center space-x-2">
            <FileSpreadsheet className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">Excel智能体</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="p-1"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent',
                sidebarCollapsed ? 'justify-center' : 'justify-start'
              )}
              title={sidebarCollapsed ? item.name : undefined}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!sidebarCollapsed && <span className="ml-3">{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* File Info */}
      {!sidebarCollapsed && excelData && (
        <div className="p-4 border-t border-border">
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-foreground">当前文件</h4>
            <div className="text-xs text-muted-foreground space-y-1">
              <div className="truncate" title={excelData.filename}>
                📄 {excelData.filename}
              </div>
              <div>
                📋 {excelData.currentSheet}
              </div>
              <div>
                📊 {excelData.sheets.find(s => s.name === excelData.currentSheet)?.shape.join(' × ') || '0 × 0'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      {!sidebarCollapsed && (
        <div className="p-4 border-t border-border">
          <div className="flex items-start space-x-2 text-xs text-muted-foreground">
            <Lightbulb className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div>
              <div className="font-medium mb-1">💡 使用提示</div>
              <div className="space-y-1">
                <div>• 上传Excel文件开始分析</div>
                <div>• 支持多工作表切换</div>
                <div>• 可调整AI参数获得更好结果</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Version */}
      <div className="p-2 border-t border-border text-center">
        {sidebarCollapsed ? (
          <div className="text-xs text-muted-foreground">v2.0</div>
        ) : (
          <div className="text-xs text-muted-foreground">
            <div>Excel智能体 v2.0</div>
            <div>JavaScript版本</div>
          </div>
        )}
      </div>
    </div>
  )
}