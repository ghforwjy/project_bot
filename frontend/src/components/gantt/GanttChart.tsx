import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'
import { useQuery } from '@tanstack/react-query'

interface GanttTask {
  id: string
  name: string
  start: string
  end: string
  progress: number
  assignee?: string
  dependencies: string[]
  custom_class?: string
}

interface GanttData {
  project_name: string
  start_date: string
  end_date: string
  tasks: GanttTask[]
}

interface GanttChartProps {
  projectId?: number | null
}

const GanttChart: React.FC<GanttChartProps> = ({ projectId }) => {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)

  // 获取甘特图数据
  const { data: ganttData, isLoading } = useQuery<GanttData>({
    queryKey: ['gantt', projectId],
    queryFn: async () => {
      if (!projectId) {
        // 返回空数据或所有项目的甘特图数据
        return {
          project_name: '所有项目',
          start_date: '',
          end_date: '',
          tasks: []
        }
      }
      const response = await fetch(`/api/v1/projects/${projectId}/gantt`)
      const result = await response.json()
      return result.data
    },
    enabled: true
  })

  useEffect(() => {
    if (!chartRef.current) return

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    // 渲染甘特图
    if (ganttData?.tasks && ganttData.tasks.length > 0) {
      renderGantt(ganttData.tasks)
    } else {
      chartInstance.current.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center'
        }
      }, true)
    }

    // 响应式
    const handleResize = () => {
      chartInstance.current?.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [ganttData])

  const renderGantt = (tasks: GanttTask[]) => {
    if (!chartInstance.current) return

    // 准备数据
    const categories = tasks.map(t => t.name)
    const data = tasks.map((task, index) => {
      const start = new Date(task.start).getTime()
      const end = new Date(task.end).getTime()
      return {
        name: task.name,
        value: [index, start, end, end - start],
        itemStyle: {
          color: getTaskColor(task.progress, task.custom_class)
        },
        progress: task.progress,
        assignee: task.assignee
      }
    })

    const option: echarts.EChartsOption = {
      tooltip: {
        formatter: (params: any) => {
          const task = tasks[params.value[0]]
          return `
            <div style="padding: 8px;">
              <div style="font-weight: bold; margin-bottom: 4px;">${task.name}</div>
              <div>进度: ${task.progress}%</div>
              <div>负责人: ${task.assignee || '未分配'}</div>
              <div>时间: ${task.start} ~ ${task.end}</div>
            </div>
          `
        }
      },
      grid: {
        left: '150px',
        right: '50px',
        top: '50px',
        bottom: '50px'
      },
      xAxis: {
        type: 'time',
        axisLabel: {
          formatter: '{yyyy}-{MM}-{dd}'
        }
      },
      yAxis: {
        type: 'category',
        data: categories,
        axisLabel: {
          width: 140,
          overflow: 'truncate'
        }
      },
      series: [{
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const height = api.size([0, 1])[1] * 0.6

          return {
            type: 'rect',
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: end[0] - start[0],
              height: height
            },
            style: api.style()
          }
        },
        encode: {
          x: [1, 2],
          y: 0
        },
        data: data
      }]
    }

    chartInstance.current.setOption(option, true)
  }

  const getTaskColor = (progress: number, customClass?: string) => {
    if (customClass === 'bar-completed' || progress === 100) {
      return '#22c55e'
    }
    if (customClass === 'bar-delayed') {
      return '#ef4444'
    }
    if (customClass === 'bar-pending' || progress === 0) {
      return '#94a3b8'
    }
    return '#3b82f6'
  }

  if (isLoading) {
    return <div className="h-full flex items-center justify-center">加载中...</div>
  }

  return (
    <div 
      ref={chartRef} 
      className="w-full h-full min-h-[400px]"
    />
  )
}

export default GanttChart
