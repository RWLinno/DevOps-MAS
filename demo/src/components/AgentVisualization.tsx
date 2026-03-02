import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { 
  Brain, 
  Eye, 
  Search, 
  FileText, 
  BarChart3, 
  Activity, 
  ArrowRight, 
  Zap,

  Play,
  Pause,
  RotateCcw,
  Target,
  Layers,
  GitBranch
} from 'lucide-react'

interface Agent {
  id: string
  name: string
  displayName: string
  icon: React.ComponentType<{ className?: string }>
  confidence: number
  status: 'active' | 'idle' | 'processing' | 'selected'
  position: { x: number; y: number }
  description: string
  specialties: string[]
  memoryUsage: number
  responseTime: number
}

interface RoutingStep {
  step: number
  title: string
  description: string
  selectedAgent?: string
  confidence?: number
  reasoning?: string
}

export function AgentVisualization() {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'route_agent',
      name: 'route_agent',
      displayName: '路由智能体',
      icon: Brain,
      confidence: 0.95,
      status: 'active',
      position: { x: 50, y: 20 },
      description: '分析查询并选择最适合的智能体',
      specialties: ['查询分析', '智能体选择', '置信度评估'],
      memoryUsage: 512,
      responseTime: 0.1
    },
    {
      id: 'visual_analysis_agent',
      name: 'visual_analysis_agent',
      displayName: '视觉分析智能体',
      icon: Eye,
      confidence: 0.88,
      status: 'idle',
      position: { x: 20, y: 60 },
      description: '处理图像分析和视觉内容理解',
      specialties: ['图像识别', '图表分析', '截图理解'],
      memoryUsage: 2048,
      responseTime: 1.2
    },
    {
      id: 'search_agent',
      name: 'search_agent',
      displayName: '搜索智能体',
      icon: Search,
      confidence: 0.92,
      status: 'processing',
      position: { x: 80, y: 60 },
      description: '执行网络搜索和信息检索',
      specialties: ['网络搜索', 'GitHub检索', '实时信息'],
      memoryUsage: 768,
      responseTime: 2.3
    },
    {
      id: 'knowledge_agent',
      name: 'knowledge_agent',
      displayName: '知识库智能体',
      icon: FileText,
      confidence: 0.89,
      status: 'selected',
      position: { x: 20, y: 80 },
      description: '查询知识库和技术文档',
      specialties: ['文档检索', '知识问答', 'RAG增强'],
      memoryUsage: 1024,
      responseTime: 0.8
    },
    {
      id: 'metrics_analysis_agent',
      name: 'metrics_analysis_agent',
      displayName: '指标分析智能体',
      icon: BarChart3,
      confidence: 0.85,
      status: 'idle',
      position: { x: 50, y: 80 },
      description: '分析系统指标和性能数据',
      specialties: ['性能分析', '指标监控', '趋势预测'],
      memoryUsage: 896,
      responseTime: 1.5
    },
    {
      id: 'comprehensive_agent',
      name: 'comprehensive_agent',
      displayName: '综合分析智能体',
      icon: Activity,
      confidence: 0.93,
      status: 'idle',
      position: { x: 80, y: 80 },
      description: '处理复杂问题和综合分析',
      specialties: ['复杂推理', '多步分析', '综合决策'],
      memoryUsage: 3072,
      responseTime: 2.8
    }
  ])

  const [routingSteps] = useState<RoutingStep[]>([
    {
      step: 1,
      title: '查询接收',
      description: '路由智能体接收用户查询并进行初步分析',
      reasoning: '检测查询类型、符号和关键词'
    },
    {
      step: 2,
      title: '符号检测',
      description: '检测到 "@" 符号，激活文档检索功能',
      reasoning: '符号检测系统识别出文档引用需求'
    },
    {
      step: 3,
      title: '智能体评估',
      description: '评估各智能体的适配度和置信度',
      reasoning: '基于查询内容和智能体能力进行匹配'
    },
    {
      step: 4,
      title: '权重调整',
      description: '根据符号检测结果调整智能体权重',
      selectedAgent: 'knowledge_agent',
      confidence: 0.89,
      reasoning: '文档检索需求提升知识库智能体权重'
    },
    {
      step: 5,
      title: '最终选择',
      description: '选择置信度最高的智能体执行任务',
      selectedAgent: 'knowledge_agent',
      confidence: 0.89,
      reasoning: '知识库智能体最适合处理文档相关查询'
    }
  ])

  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string | null>('knowledge_agent')

  // 自动播放路由过程
  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setCurrentStep(prev => {
          if (prev >= routingSteps.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, 2000)

      return () => clearInterval(interval)
    }
  }, [isPlaying, routingSteps.length])

  // 更新智能体状态
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => ({
        ...agent,
        confidence: Math.max(0.7, Math.min(1.0, agent.confidence + (Math.random() - 0.5) * 0.05)),
        memoryUsage: Math.max(256, Math.min(4096, agent.memoryUsage + (Math.random() - 0.5) * 100)),
        responseTime: Math.max(0.1, Math.min(5.0, agent.responseTime + (Math.random() - 0.5) * 0.2))
      })))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'border-green-500 bg-green-50 dark:bg-green-900/20'
      case 'processing': return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
      case 'selected': return 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
      case 'idle': return 'border-slate-300 bg-slate-50 dark:bg-slate-800/50'
      default: return 'border-slate-300 bg-slate-50 dark:bg-slate-800/50'
    }
  }

  const getStatusDot = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'processing': return 'bg-blue-500 animate-pulse'
      case 'selected': return 'bg-purple-500'
      case 'idle': return 'bg-slate-400'
      default: return 'bg-slate-400'
    }
  }

  const resetVisualization = () => {
    setCurrentStep(0)
    setIsPlaying(false)
    setSelectedAgent('knowledge_agent')
  }

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="space-y-6">
      {/* 控制面板 */}
      <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center space-x-2">
              <GitBranch className="w-5 h-5 text-blue-500" />
              <span>智能体协调可视化</span>
            </span>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={resetVisualization}
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                重置
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={togglePlayback}
              >
                {isPlaying ? (
                  <>
                    <Pause className="w-4 h-4 mr-1" />
                    暂停
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-1" />
                    播放
                  </>
                )}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 text-sm text-slate-600 dark:text-slate-400">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span>当前步骤: {currentStep + 1}/{routingSteps.length}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4" />
              <span>活跃智能体: {agents.filter(a => a.status === 'active' || a.status === 'processing').length}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 智能体网络图 */}
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-purple-500" />
              <span>智能体协作网络</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative h-96 bg-slate-50 dark:bg-slate-900/50 rounded-lg overflow-hidden">
              {/* 连接线 */}
              <svg className="absolute inset-0 w-full h-full">
                {/* 路由智能体到其他智能体的连接 */}
                {agents.slice(1).map((agent, _index) => {
                  const routeAgent = agents[0]
                  const opacity = agent.status === 'selected' ? 1 : 0.3
                  const strokeWidth = agent.status === 'selected' ? 2 : 1
                  const color = agent.status === 'selected' ? '#8b5cf6' : '#94a3b8'
                  
                  return (
                    <line
                      key={agent.id}
                      x1={`${routeAgent.position.x}%`}
                      y1={`${routeAgent.position.y}%`}
                      x2={`${agent.position.x}%`}
                      y2={`${agent.position.y}%`}
                      stroke={color}
                      strokeWidth={strokeWidth}
                      opacity={opacity}
                      strokeDasharray={agent.status === 'processing' ? '5,5' : 'none'}
                    />
                  )
                })}
              </svg>

              {/* 智能体节点 */}
              {agents.map((agent) => {
                const Icon = agent.icon
                return (
                  <div
                    key={agent.id}
                    className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 ${
                      selectedAgent === agent.id ? 'scale-110' : 'hover:scale-105'
                    }`}
                    style={{
                      left: `${agent.position.x}%`,
                      top: `${agent.position.y}%`
                    }}
                    onClick={() => setSelectedAgent(agent.id)}
                  >
                    <div className={`w-16 h-16 rounded-full border-2 ${getStatusColor(agent.status)} flex items-center justify-center shadow-lg`}>
                      <Icon className="w-6 h-6 text-slate-700 dark:text-slate-300" />
                    </div>
                    <div className={`absolute -top-1 -right-1 w-4 h-4 rounded-full ${getStatusDot(agent.status)}`} />
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 text-xs font-medium text-center whitespace-nowrap">
                      {agent.displayName}
                    </div>
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-6 text-xs text-slate-500 text-center">
                      {(agent.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* 路由决策过程 */}
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              <span>路由决策过程</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {routingSteps.map((step, index) => (
                <div
                  key={step.step}
                  className={`relative p-4 rounded-lg border transition-all duration-300 ${
                    index <= currentStep
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      index <= currentStep
                        ? 'bg-blue-500 text-white'
                        : 'bg-slate-300 text-slate-600'
                    }`}>
                      {step.step}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm mb-1">{step.title}</h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                        {step.description}
                      </p>
                      
                      {step.selectedAgent && index <= currentStep && (
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="outline" className="text-xs">
                            选中: {agents.find(a => a.id === step.selectedAgent)?.displayName}
                          </Badge>
                          {step.confidence && (
                            <Badge variant="outline" className="text-xs">
                              置信度: {(step.confidence * 100).toFixed(1)}%
                            </Badge>
                          )}
                        </div>
                      )}
                      
                      {step.reasoning && index <= currentStep && (
                        <p className="text-xs text-slate-500 italic">
                          推理: {step.reasoning}
                        </p>
                      )}
                    </div>
                    
                    {index < routingSteps.length - 1 && index <= currentStep && (
                      <ArrowRight className="w-4 h-4 text-blue-500 mt-1" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 智能体详细信息 */}
      {selectedAgent && (
        <Card className="bg-white/60 dark:bg-slate-800/60 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-green-500" />
              <span>智能体详细信息</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const agent = agents.find(a => a.id === selectedAgent)
              if (!agent) return null
              
              const Icon = agent.icon
              return (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-12 h-12 rounded-lg ${getStatusColor(agent.status)} flex items-center justify-center`}>
                        <Icon className="w-6 h-6 text-slate-700 dark:text-slate-300" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{agent.displayName}</h3>
                        <p className="text-sm text-slate-500">{agent.name}</p>
                      </div>
                    </div>
                    
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {agent.description}
                    </p>
                    
                    <div>
                      <h4 className="font-medium text-sm mb-2">专业领域</h4>
                      <div className="flex flex-wrap gap-1">
                        {agent.specialties.map((specialty, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {specialty}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>置信度</span>
                        <span>{(agent.confidence * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={agent.confidence * 100} className="h-2" />
                    </div>
                    
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>内存使用</span>
                        <span>{agent.memoryUsage}MB</span>
                      </div>
                      <Progress value={(agent.memoryUsage / 4096) * 100} className="h-2" />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-500">响应时间</span>
                        <p className="font-medium">{agent.responseTime.toFixed(2)}s</p>
                      </div>
                      <div>
                        <span className="text-slate-500">状态</span>
                        <p className="font-medium capitalize">{agent.status}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })()}
          </CardContent>
        </Card>
      )}
    </div>
  )
}