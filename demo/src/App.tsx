
import { useState, useEffect } from 'react'
import './App.css'
import { ChatInterface } from './components/ChatInterface'
import { SystemMonitor } from './components/SystemMonitor'
import { AgentVisualization } from './components/AgentVisualization'
import { PerformanceMetrics } from './components/PerformanceMetrics'
import { SettingsPanel } from './components/SettingsPanel'
import { HelpSystem } from './components/HelpSystem'
import { ThemeProvider } from './components/ThemeProvider'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { Button } from './components/ui/button'
import { Settings, HelpCircle, Activity, BarChart3, MessageSquare, Cpu } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [isHelpOpen, setIsHelpOpen] = useState(false)
  const [systemStatus, setSystemStatus] = useState({
    isOnline: true,
    gpuUsage: 65,
    memoryUsage: 78,
    activeAgents: 5,
    responseTime: 1.2
  })

  // 模拟系统状态更新
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        gpuUsage: Math.max(30, Math.min(95, prev.gpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(40, Math.min(90, prev.memoryUsage + (Math.random() - 0.5) * 8)),
        responseTime: Math.max(0.5, Math.min(3.0, prev.responseTime + (Math.random() - 0.5) * 0.4))
      }))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
        {/* Header */}
        <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Cpu className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-slate-900 dark:text-white">DevOps-MAS</h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400">智能工程问答系统</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-300">
                  <div className={`w-2 h-2 rounded-full ${
                    systemStatus.isOnline ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span>{systemStatus.isOnline ? '在线' : '离线'}</span>
                  <span className="text-slate-400">|</span>
                  <span>响应时间: {systemStatus.responseTime.toFixed(1)}s</span>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsHelpOpen(true)}
                  className="text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
                >
                  <HelpCircle className="w-4 h-4" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsSettingsOpen(true)}
                  className="text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white"
                >
                  <Settings className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-5 bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
              <TabsTrigger value="chat" className="flex items-center space-x-2">
                <MessageSquare className="w-4 h-4" />
                <span>聊天界面</span>
              </TabsTrigger>
              <TabsTrigger value="monitor" className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span>系统监控</span>
              </TabsTrigger>
              <TabsTrigger value="agents" className="flex items-center space-x-2">
                <Cpu className="w-4 h-4" />
                <span>智能体协调</span>
              </TabsTrigger>
              <TabsTrigger value="metrics" className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4" />
                <span>性能指标</span>
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center space-x-2">
                <Settings className="w-4 h-4" />
                <span>设置</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-6">
              <TabsContent value="chat" className="space-y-6">
                <ChatInterface systemStatus={systemStatus} />
              </TabsContent>
              
              <TabsContent value="monitor" className="space-y-6">
                <SystemMonitor systemStatus={systemStatus} />
              </TabsContent>
              
              <TabsContent value="agents" className="space-y-6">
                <AgentVisualization />
              </TabsContent>
              
              <TabsContent value="metrics" className="space-y-6">
                <PerformanceMetrics />
              </TabsContent>
              
              <TabsContent value="settings" className="space-y-6">
                <SettingsPanel />
              </TabsContent>
            </div>
          </Tabs>
        </main>

        {/* Modals */}
        <HelpSystem isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
        <SettingsPanel isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      </div>
    </ThemeProvider>
  )
}

export default App
