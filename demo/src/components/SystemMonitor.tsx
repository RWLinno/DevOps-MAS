import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Progress } from './ui/progress'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { 
  Cpu, 
  MemoryStick, 

  Activity, 
  Zap, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Server,


  Eye,
  Search,
  FileText,
  BarChart3,
  Brain
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

interface SystemStatus {
  isOnline: boolean
  gpuUsage: number
  memoryUsage: number
  activeAgents: number
  responseTime: number
}

interface SystemMonitorProps {
  systemStatus: SystemStatus
}

interface AgentStatus {
  name: string
  displayName: string
  status: 'active' | 'idle' | 'loading' | 'error'
  confidence: number
  lastUsed: Date
  memoryUsage: number
  icon: React.ComponentType<{ className?: string }>
  description: string
}

interface MetricData {
  time: string
  gpu: number
  memory: number
  responseTime: number
}

export function SystemMonitor({ systemStatus }: SystemMonitorProps) {
  const [agents, setAgents] = useState<AgentStatus[]>([
    {
      name: 'route_agent',
      displayName: '路由智能体',
      status: 'active',
      confidence: 0.95,
      lastUsed: new Date(),
      memoryUsage: 512,
      icon: Brain,
      description: '负责分析查询并选择最适合的智能体'
    },
    {
      name: 'visual_analysis_agent',
      displayName: '视觉分析智能体',
      status: 'idle',
      confidence: 0.88,
      lastUsed: new Date(Date.now() - 300000),
      memoryUsage: 2048,
      icon: Eye,
      description: '处理图像分析和视觉内容理解'
    },
    {
      name: 'search_agent',
      displayName: '搜索智能体',
      status: 'active',
      confidence: 0.92,
      lastUsed: new Date(Date.now() - 60000),
      memoryUsage: 768,
      icon: Search,
      description: '执行网络搜索和信息检索'
    },
    {
      name: 'knowledge_agent',
      displayName: '知识库智能体',
      status: 'active',
      confidence: 0.89,
      lastUsed: new Date(Date.now() - 120000),
      memoryUsage: 1024,
      icon: FileText,
      description: '查询知识库和技术文档'
    },
    {
      name: 'metrics_analysis_agent',
      displayName: '指标分析智能体',
      status: 'idle',
      confidence: 0.85,
      lastUsed: new Date(Date.now() - 600000),
      memoryUsage: 896,
      icon: BarChart3,
      description: '分析系统指标和性能数据'
    },
    {
      name: 'comprehensive_agent',
      displayName: '综合分析智能体',
      status: 'loading',
      confidence: 0.93,
      lastUsed: new Date(Date.now() - 30000),
      memoryUsage: 3072,
      icon: Activity,
      description: '处理复杂问题和综合分析'
    }
  ])

  const [metricsHistory, setMetricsHistory] = useState<MetricData[]>([])
  const [vramInfo] = useState({
    total: 24,
    used: 16.8,
    available: 7.2,
    tier: 'Mid-High (24GB)',
    modelLoaded: 'Qwen2.5-32B-Instruct'
  })

  // 生成历史数据
  useEffect(() => {
    const generateHistoryData = () => {
      const data: MetricData[] = []
      const now = new Date()
      
      for (let i = 29; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60000)
        data.push({
          time: time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
          gpu: Math.max(30, Math.min(95, systemStatus.gpuUsage + (Math.random() - 0.5) * 20)),
          memory: Math.max(40, Math.min(90, systemStatus.memoryUsage + (Math.random() - 0.5) * 15)),
          responseTime: Math.max(0.5, Math.min(3.0, systemStatus.responseTime + (Math.random() - 0.5) * 1.0))
        })
      }
      
      setMetricsHistory(data)
    }

    generateHistoryData()
    const interval = setInterval(generateHistoryData, 60000)
    return () => clearInterval(interval)
  }, [systemStatus])

  // 模拟智能体状态更新
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => ({
        ...agent,
        confidence: Math.max(0.7, Math.min(1.0, agent.confidence + (Math.random() - 0.5) * 0.1)),
        memoryUsage: Math.max(256, Math.min(4096, agent.memoryUsage + (Math.random() - 0.5) * 200))
      })))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'idle': return 'bg-yellow-500'
      case 'loading': return 'bg-blue-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '活跃'
      case 'idle': return '空闲'
      case 'loading': return '加载中'
      case 'error': return '错误'
      default: return '未知'
    }
  }

  const refreshSystemStatus = () => {
    // 模拟刷新操作
    console.log('刷新系统状态...')
  }

  return (
    <div className="space-y-6">
      {/* 系统概览 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">系统状态</p>
                <div className="flex items-center space-x-2 mt-1">
                  {systemStatus.isOnline ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-500" />
                  )}
                  <span className="text-lg font-semibold">
                    {systemStatus.isOnline ? '在线' : '离线'}
                  </span>
                </div>
              </div>
              <Server className="w-8 h-8 text-slate-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">GPU使用率</p>
                <p className="text-lg font-semibold mt-1">{systemStatus.gpuUsage.toFixed(1)}%</p>
                <Progress value={systemStatus.gpuUsage} className="mt-2 h-2" />
              </div>
              <Cpu className="w-8 h-8 text-slate-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">内存使用</p>
                <p className="text-lg font-semibold mt-1">{systemStatus.memoryUsage.toFixed(1)}%</p>
                <Progress value={systemStatus.memoryUsage} className="mt-2 h-2" />
              </div>
              <MemoryStick className="w-8 h-8 text-slate-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">活跃智能体</p>
                <p className="text-lg font-semibold mt-1">{systemStatus.activeAgents}</p>
                <p className="text-xs text-slate-500 mt-1">共6个智能体</p>
              </div>
              <Activity className="w-8 h-8 text-slate-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* VRAM感知系统状态 */}
      <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-blue-500" />
            <span>VRAM感知模型选择状态</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">硬件层级</p>
              <Badge variant="outline" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                {vramInfo.tier}
              </Badge>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">当前加载模型</p>
              <p className="text-sm font-mono bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
                {vramInfo.modelLoaded}
              </p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">VRAM使用情况</p>
              <div className="text-sm">
                <div className="flex justify-between">
                  <span>已使用: {vramInfo.used}GB</span>
                  <span>可用: {vramInfo.available}GB</span>
                </div>
                <Progress value={(vramInfo.used / vramInfo.total) * 100} className="mt-1 h-2" />
                <p className="text-xs text-slate-500 mt-1">总计: {vramInfo.total}GB</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 性能指标图表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>GPU & 内存使用趋势</span>
              <Button variant="ghost" size="sm" onClick={refreshSystemStatus}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metricsHistory}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="time" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="gpu" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="GPU使用率(%)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="memory" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    name="内存使用率(%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>响应时间趋势</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metricsHistory}>
                  <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                  <XAxis dataKey="time" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="responseTime" 
                    stroke="#f59e0b" 
                    fill="#f59e0b" 
                    fillOpacity={0.3}
                    name="响应时间(s)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 智能体状态 */}
      <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-purple-500" />
            <span>智能体状态监控</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => {
              const Icon = agent.icon
              return (
                <div
                  key={agent.name}
                  className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-white/40 dark:bg-slate-800/40"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                      <div>
                        <h4 className="font-medium text-sm">{agent.displayName}</h4>
                        <p className="text-xs text-slate-500">{agent.name}</p>
                      </div>
                    </div>
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                  </div>
                  
                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">
                    {agent.description}
                  </p>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span>状态:</span>
                      <Badge variant="outline" className="text-xs">
                        {getStatusText(agent.status)}
                      </Badge>
                    </div>
                    
                    <div className="flex justify-between text-xs">
                      <span>置信度:</span>
                      <span>{(agent.confidence * 100).toFixed(1)}%</span>
                    </div>
                    
                    <div className="flex justify-between text-xs">
                      <span>内存使用:</span>
                      <span>{agent.memoryUsage}MB</span>
                    </div>
                    
                    <div className="flex justify-between text-xs">
                      <span>最后使用:</span>
                      <span>{agent.lastUsed.toLocaleTimeString('zh-CN', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* 系统警告和通知 */}
      <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            <span>系统通知</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
              <div>
                <p className="text-sm font-medium">VRAM感知系统已激活</p>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  系统已检测到24GB VRAM环境，自动选择Qwen2.5-32B-Instruct模型
                </p>
                <p className="text-xs text-slate-500 mt-1">2分钟前</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
              <div>
                <p className="text-sm font-medium">智能体协调优化完成</p>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  路由智能体成功优化了智能体选择策略，置信度提升至95%
                </p>
                <p className="text-xs text-slate-500 mt-1">5分钟前</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
              <div className="w-2 h-2 bg-amber-500 rounded-full mt-2" />
              <div>
                <p className="text-sm font-medium">内存使用率较高</p>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  当前内存使用率为78%，建议关闭不必要的智能体以释放内存
                </p>
                <p className="text-xs text-slate-500 mt-1">10分钟前</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}