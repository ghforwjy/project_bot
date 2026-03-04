import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import * as d3 from 'd3';
import html2canvas from 'html2canvas';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Spin, Empty, Tooltip, Select, Input, Button, message, Dropdown, Menu, Switch } from 'antd';
import { AppstoreOutlined, FolderOutlined, SearchOutlined, CloseCircleOutlined, UnorderedListOutlined, BarsOutlined, DownloadOutlined } from '@ant-design/icons';
import { AllGanttData, GanttChartProps, GanttData, ProjectCategoryGantt, ProjectGantt, ExpandedStates } from './types';
import './GanttChart.css';

const { Option } = Select;

// 搜索输入组件 - 使用内部状态避免焦点问题
const SearchInput: React.FC<{
  onSearch: (value: string) => void;
}> = React.memo(({ onSearch }) => {
  const [localValue, setLocalValue] = useState('');
  
  const handleSearch = useCallback(() => {
    onSearch(localValue);
  }, [localValue, onSearch]);
  
  return (
    <>
      <Input
        placeholder="输入任务名称或描述..."
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        onPressEnter={handleSearch}
        className="gantt-control-input"
      />
      <Button
        icon={<SearchOutlined />}
        onClick={handleSearch}
        className="gantt-control-button"
      >
        搜索
      </Button>
    </>
  );
});

// 搜索状态管理 hook
const useSearchState = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
  // 使用 useCallback 缓存回调函数，避免每次渲染都创建新函数
  const handleSearch = useCallback((value: string) => {
    setSearchQuery(value);
  }, []);
  
  return {
    searchQuery,
    setSearchQuery,
    handleSearch
  };
};

//甘特图组件
const GanttChart: React.FC<GanttChartProps> = ({
  projectId = null,
  className = '',
  height = 600,
  width = '100%',
  onTaskClick,
  onProjectClick,
  onCategoryClick
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const [expandedStates, setExpandedStates] = useState<ExpandedStates>({
    categories: {},
    projects: {}
  });
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const {
    searchQuery,
    setSearchQuery,
    handleSearch
  } = useSearchState();
  const [selectedProject, setSelectedProject] = useState<number | null>(null); // null表示所有项目
  const [categories, setCategories] = useState<ProjectCategoryGantt[]>([]);
  const [containerWidth, setContainerWidth] = useState<number>(0);
  const [showAssignee, setShowAssignee] = useState<boolean>(false); // 是否显示项目负责人
  
  // 任务条和进度条尺寸配置
  const TASK_BAR_HEIGHT = 32;           // 任务条总高度（与任务行32px一致）
  const TASK_BAR_BORDER_WIDTH = 1;      // 边框宽度
  const TASK_BAR_INNER_HEIGHT = TASK_BAR_HEIGHT - TASK_BAR_BORDER_WIDTH * 2;  // 内部高度（30）
  const TASK_BAR_Y_OFFSET = TASK_BAR_HEIGHT / 2;  // Y轴偏移量（16）

  // 拖拽状态管理
  const [dragState, setDragState] = useState<{
    isDragging: boolean;
    draggedTask: any | null;
    draggedTaskId: number | null;
    originalY: number;
    currentY: number;
    taskHeight: number;
  }>({
    isDragging: false,
    draggedTask: null,
    draggedTaskId: null,
    originalY: 0,
    currentY: 0,
    taskHeight: 32 // 任务条高度
  });

  // 获取甘特图数据
  const { data: ganttData, isLoading, error } = useQuery<AllGanttData>({
    queryKey: ['gantt', projectId || 'all'],
    queryFn: async () => {
      const url = projectId 
        ? `/api/v1/projects/${projectId}/gantt` 
        : '/api/v1/gantt/all';
      
      const response = await fetch(url);
      const result = await response.json();
      
      // 处理数据，为每个大类和项目添加颜色
      if (result.data && result.data.project_categories) {
        return {
          project_categories: result.data.project_categories.map((category: any, index: number) => {
            const categoryColor = getCategoryColor(index);
            return {
              ...category,
              color: categoryColor,
              projects: category.projects.map((project: any) => ({
                ...project,
                color: categoryColor
              }))
            };
          })
        };
      }
      
      return { project_categories: [] };
    },
    enabled: true,
    staleTime: 0, // 数据立即过期，确保缓存失效能触发重新获取
    refetchOnWindowFocus: false, // 窗口获得焦点时不自动刷新
    refetchOnMount: true // 组件挂载时自动刷新
  });

  const filteredCategories = useMemo(() => {
    let result = ganttData?.project_categories || [];
    
    // 使用本地选择的项目ID
    const effectiveProjectId = selectedProject;
    
    if (effectiveProjectId !== null) {
      // 只显示选中的项目
      result = result.map((category: ProjectCategoryGantt) => ({
        ...category,
        projects: category.projects.filter((project: ProjectGantt) => project.id === effectiveProjectId)
      })).filter((category: ProjectCategoryGantt) => 
        category.projects.length > 0
      );
    }
    
    if (selectedCategory !== null) {
      result = result.filter((category: ProjectCategoryGantt) => category.id === selectedCategory);
    }
    
    if (searchQuery && searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.map((category: ProjectCategoryGantt) => ({
        ...category,
        projects: category.projects.map((project: ProjectGantt) => ({
          ...project,
          tasks: project.tasks.filter((task: any) => 
            task.name.toLowerCase().includes(query) ||
            (task.description && task.description.toLowerCase().includes(query))
          )
        }))
      })).filter((category: ProjectCategoryGantt) => 
        category.projects.some((project: ProjectGantt) => project.tasks.length > 0)
      );
    }
    
    return result;
  }, [selectedProject, selectedCategory, searchQuery, ganttData]);

  const totalTaskCount = useMemo(() => {
    return filteredCategories.reduce((sum, category) => 
      sum + category.projects.reduce((pSum, project) => 
        pSum + project.tasks.length, 0
      ), 0);
  }, [filteredCategories]);

  // 更新分类列表
  useEffect(() => {
    if (ganttData?.project_categories) {
      setCategories(ganttData.project_categories);
    }
  }, [ganttData]);

  // 监听窗口大小变化和数据加载
  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current) {
        const width = chartRef.current.clientWidth;
        if (width > 0) {
          setContainerWidth(width);
        }
      }
    };

    // 初始化容器宽度
    const initWidth = () => {
      if (chartRef.current) {
        const width = chartRef.current.clientWidth;
        if (width > 0) {
          setContainerWidth(width);
        } else {
          // 如果当前宽度为0，等待一下再尝试
          setTimeout(initWidth, 100);
        }
      }
    };

    initWidth();

    // 添加事件监听器
    window.addEventListener('resize', handleResize);

    // 清理事件监听器
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // 当数据加载完成后重新计算宽度
  useEffect(() => {
    if (ganttData?.project_categories && ganttData.project_categories.length > 0) {
      setTimeout(() => {
        if (chartRef.current) {
          setContainerWidth(chartRef.current.clientWidth);
        }
      }, 100);
    }
  }, [ganttData]);

  // 渲染甘特图
  useEffect(() => {
    if (!chartRef.current || !filteredCategories || containerWidth === 0) return;
    const container = chartRef.current;
    const chartWidth = containerWidth;

    d3.select(container).selectAll('*').remove();
    d3.select(container)
      .style('overflow-y', 'auto')
      .style('overflow-x', 'hidden');

    const timeRange = calculateTimeRange(filteredCategories, chartWidth);
    const svgWidth = chartWidth;

    // 计算实际内容高度，加上顶部和底部边距
    const actualContentHeight = calculateTotalHeight(filteredCategories, expandedStates);
    const svgHeight = actualContentHeight + 80; // 40px顶部 + 40px底部边距

    const svg = d3.select(container)
      .append('svg')
      .attr('width', svgWidth)
      .attr('height', svgHeight)
      .attr('class', 'gantt-svg');

    const xScale = d3.scaleTime()
      .domain([new Date(timeRange.min), new Date(timeRange.max)])
      .range([240, svgWidth - 40]);

    // 直接使用y坐标，不进行压缩
    const yScale = (y: number) => y + 40;

    renderTimeAxis(svg, xScale, svgWidth, svgHeight);
    renderTodayLine(svg, xScale, svgHeight, timeRange, svgWidth);
    renderYearTransitions(svg, xScale, svgHeight, timeRange, svgWidth);

    let currentY = 0;
    filteredCategories.forEach((category, categoryIndex) => {
      const isCategoryExpanded = expandedStates.categories[categoryIndex] !== false;
      const categoryHeight = calculateCategoryHeight(category, isCategoryExpanded);
      
      renderCategory(
        svg, 
        category, 
        categoryIndex, 
        xScale, 
        yScale, 
        currentY,
        svgWidth,
        isCategoryExpanded
      );
      
      currentY += categoryHeight;
    });

  }, [filteredCategories, expandedStates, height, containerWidth, showAssignee]);

  // 计算时间范围
  const calculateTimeRange = (categories: ProjectCategoryGantt[], containerWidth: number) => {
    let minTime = Infinity;
    let maxTime = -Infinity;
    const today = new Date().getTime();

    categories.forEach(category => {
      category.projects.forEach(project => {
        project.tasks.forEach(task => {
          const start = new Date(task.start).getTime();
          const end = new Date(task.end).getTime();
          
          if (start < minTime) minTime = start;
          if (end > maxTime) maxTime = end;
        });
      });
    });

    // 如果没有任务，使用当前时间前后30天
    if (minTime === Infinity || maxTime === -Infinity) {
      minTime = today - 30 * 24 * 60 * 60 * 1000;
      maxTime = today + 30 * 24 * 60 * 60 * 1000;
    } else {
      // 计算有效宽度（减去左侧标签区域的宽度）
      const effectiveWidth = containerWidth - 280;
      
      // 计算总时间范围（毫秒）
      const totalTimeRange = maxTime - minTime;
      
      // 根据有效宽度计算理想的时间范围
      // 假设每个任务条至少需要20px宽度
      const idealTimeRange = (effectiveWidth / 20) * (7 * 24 * 60 * 60 * 1000); // 每个任务条7天
      
      // 添加缓冲时间
      const bufferDays = effectiveWidth > 800 ? 7 : 3;
      const bufferTime = bufferDays * 24 * 60 * 60 * 1000;
      
      // 调整时间范围
      if (totalTimeRange > idealTimeRange) {
        // 如果总时间范围大于理想时间范围，以任务时间范围的中心显示
        const centerTime = (minTime + maxTime) / 2;
        const halfRange = Math.max(idealTimeRange / 2, totalTimeRange / 2);
        minTime = centerTime - halfRange;
        maxTime = centerTime + halfRange;
      } else {
        // 如果总时间范围小于理想时间范围，添加缓冲
        minTime -= bufferTime;
        maxTime += bufferTime;
      }
    }

    return { min: minTime, max: maxTime, today };
  };

  // 计算总高度
  const calculateTotalHeight = (categories: ProjectCategoryGantt[], expandedStates: ExpandedStates) => {
    return categories.reduce((total, category, index) => {
      const isExpanded = expandedStates.categories[index] !== false;
      // 在每个大类之间添加20px的padding
      const categoryPadding = index > 0 ? 20 : 0;
      return total + categoryPadding + calculateCategoryHeight(category, isExpanded);
    }, 0);
  };

  // 计算大类高度
  const calculateCategoryHeight = (category: ProjectCategoryGantt, isExpanded: boolean) => {
    if (!isExpanded) return 50; // 折叠状态下只显示标题

    return 50 + category.projects.reduce((total, project) => {
      const projectKey = `${category.id}-${project.id}`;
      const isProjectExpanded = expandedStates.projects[projectKey] !== false;
      return total + calculateProjectHeight(project, isProjectExpanded);
    }, 0);
  };

  // 计算项目高度
  const calculateProjectHeight = (project: ProjectGantt, isExpanded: boolean) => {
    if (!isExpanded) return 32; // 折叠状态下只显示标题
    return 32 + project.tasks.length * 32; // 每个任务32px高度
  };

  // 渲染时间轴
  const renderTimeAxis = (svg: any, xScale: any, width: number, height: number) => {
    // 根据宽度计算合适的刻度密度
    const tickCount = Math.max(2, Math.min(15, Math.floor((width - 240) / 80)));
    
    // 时间轴刻度
    const xAxis = d3.axisBottom(xScale)
      .ticks(tickCount)
      .tickFormat(d3.timeFormat('%m/%d'));

    // 渲染时间轴
    const timeAxisGroup = svg.append('g')
      .attr('class', 'gantt-time-axis')
      .attr('transform', `translate(0, ${height - 40})`)
      .call(xAxis);
    
    // 设置时间标签样式
    timeAxisGroup.selectAll('text')
      .attr('class', 'gantt-time-label')
      .attr('dx', '-8px')
      .attr('dy', '8px')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .style('font-size', '11px')
      .style('fill', '#666666')
      .style('font-weight', '500');
    
    // 隐藏轴路径，去掉左右两端的竖向黑线
    timeAxisGroup.selectAll('path')
      .style('display', 'none');

    // 渲染时间轴网格线
    const gridGroup = svg.append('g')
      .attr('class', 'gantt-grid')
      .attr('transform', `translate(0, ${height - 40})`)
      .call(
        d3.axisBottom(xScale)
          .ticks(tickCount)
          .tickSize(-(height - 80))
          .tickFormat('')
      );
    
    // 设置网格线样式
    gridGroup.selectAll('line')
      .attr('stroke', '#e8e8e8')
      .attr('stroke-dasharray', '2,2');
    
    // 隐藏网格线的路径，去掉左右两端的竖向黑线
    gridGroup.selectAll('path')
      .style('display', 'none');
  };

  // 渲染今天标记线
  const renderTodayLine = (svg: any, xScale: any, height: number, timeRange: any, chartWidth: number) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const todayX = xScale(today);
    
    // 只有当今天在时间范围内时才显示
    if (todayX >= 240 && todayX <= chartWidth - 40) {
      // 垂直线
      svg.append('line')
        .attr('class', 'gantt-today-line')
        .attr('x1', todayX)
        .attr('y1', 40)
        .attr('x2', todayX)
        .attr('y2', height - 40)
        .attr('stroke', '#ff4d4f')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5');

      // 文本标签
      svg.append('text')
        .attr('class', 'gantt-today-text')
        .attr('x', todayX + 5)
        .attr('y', 55)
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .attr('fill', '#ff4d4f')
        .text('今天');
    }
  };

  // 渲染跨年日期标记
  const renderYearTransitions = (svg: any, xScale: any, height: number, timeRange: any, chartWidth: number) => {
    const minDate = new Date(timeRange.min);
    const maxDate = new Date(timeRange.max);
    
    // 计算时间范围内的所有1月1日
    const yearStartDates: Date[] = [];
    const startYear = minDate.getFullYear();
    const endYear = maxDate.getFullYear();
    
    for (let year = startYear; year <= endYear; year++) {
      const yearStart = new Date(year, 0, 1); // 1月1日
      yearStart.setHours(0, 0, 0, 0);
      yearStartDates.push(yearStart);
    }
    
    // 对每个跨年日期，检查是否在时间范围内并渲染
    yearStartDates.forEach((date) => {
      const yearX = xScale(date);
      
      // 只有当日期在时间范围内时才显示
      if (yearX >= 240 && yearX <= chartWidth - 40) {
        // 垂直线
        svg.append('line')
          .attr('class', 'gantt-year-transition-line')
          .attr('x1', yearX)
          .attr('y1', 40)
          .attr('x2', yearX)
          .attr('y2', height - 40)
          .attr('stroke', '#94a3b8')
          .attr('stroke-width', 1)
          .attr('stroke-dasharray', '3,3');

        // 上一年标签（左侧）
        const previousYear = date.getFullYear() - 1;
        svg.append('text')
          .attr('class', 'gantt-year-label')
          .attr('x', yearX - 5)
          .attr('y', 55)
          .attr('font-size', '11px')
          .attr('font-weight', 'bold')
          .attr('fill', '#64748b')
          .attr('text-anchor', 'end')
          .text(`(${previousYear})`);

        // 下一年标签（右侧）
        const nextYear = date.getFullYear();
        svg.append('text')
          .attr('class', 'gantt-year-label')
          .attr('x', yearX + 5)
          .attr('y', 55)
          .attr('font-size', '11px')
          .attr('font-weight', 'bold')
          .attr('fill', '#64748b')
          .text(`(${nextYear})`);
      }
    });
  };

  // 渲染项目大类
  const renderCategory = (
    svg: any, 
    category: ProjectCategoryGantt, 
    categoryIndex: number, 
    xScale: any, 
    yScale: any, 
    yPosition: number,
    svgWidth: number,
    isExpanded: boolean
  ) => {
    const categoryHeight = calculateCategoryHeight(category, isExpanded);
    const y = yScale(yPosition);

    // 渲染大类背景
    svg.append('rect')
      .attr('class', 'gantt-category-background')
      .attr('x', 0)
      .attr('y', y)
      .attr('width', svgWidth)
      .attr('height', yScale(yPosition + categoryHeight) - y)
      .attr('fill', `${category.color}05`) // 5%透明度
      .attr('stroke', `${category.color}33`) // 20%透明度
      .attr('stroke-width', 1);

    // 渲染大类标题
    const titleGroup = svg.append('g')
      .attr('class', 'gantt-category-title')
      .attr('transform', `translate(0, ${y + 24})`)
      .style('cursor', 'pointer')
      .on('click', () => handleToggleCategory(categoryIndex));

    // 展开/折叠图标
    titleGroup.append('text')
      .attr('x', 20)
      .attr('y', 0)
      .attr('font-size', '14px')
      .text(isExpanded ? '📂' : '📁');

    // 大类名称
    titleGroup.append('text')
      .attr('x', 40)
      .attr('y', 0)
      .attr('class', 'gantt-category-title-text')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .attr('fill', category.color)
      .text(`${category.name} ${!isExpanded ? '(已折叠)' : ''}`);

    // 项目数量
    titleGroup.append('text')
      .attr('x', svgWidth - 20)
      .attr('y', 0)
      .attr('text-anchor', 'end')
      .attr('font-size', '12px')
      .attr('fill', '#666666')
      .text(`${category.projects.length} 个项目`);

    // 渲染项目
    if (isExpanded) {
      let projectY = yPosition + 50; // 大类标题高度50px
      
      category.projects.forEach((project, projectIndex) => {
        const projectKey = `${category.id}-${project.id}`;
        const isProjectExpanded = expandedStates.projects[projectKey] !== false;
        const projectHeight = calculateProjectHeight(project, isProjectExpanded);
        
        renderProject(
          svg, 
          project, 
          projectKey, 
          category.color,
          xScale, 
          yScale, 
          projectY,
          svgWidth,
          isProjectExpanded
        );
        
        projectY += projectHeight;
      });
    }
  };

  // 渲染项目
  const renderProject = (
    svg: any, 
    project: ProjectGantt, 
    projectKey: string, 
    categoryColor: string,
    xScale: any, 
    yScale: any, 
    yPosition: number,
    svgWidth: number,
    isExpanded: boolean
  ) => {
    const projectHeight = calculateProjectHeight(project, isExpanded);
    const y = yScale(yPosition);

    // 渲染项目容器
    svg.append('rect')
      .attr('class', 'gantt-project-container')
      .attr('x', 20)
      .attr('y', y)
      .attr('width', svgWidth - 20)
      .attr('height', yScale(yPosition + projectHeight) - y)
      .attr('fill', 'white')
      .attr('stroke', `${categoryColor}1a`) // 10%透明度
      .attr('stroke-width', 1)
      .attr('rx', 4);

    // 渲染项目标题
    const titleGroup = svg.append('g')
      .attr('class', 'gantt-project-title')
      .attr('transform', `translate(0, ${y + 24})`);

    // 展开/折叠图标
    titleGroup.append('text')
      .attr('x', 40)
      .attr('y', 0)
      .attr('font-size', '14px')
      .style('cursor', 'pointer')
      .text(isExpanded ? '📋' : '📂')
      .on('click', () => handleToggleProject(projectKey));

    // 项目名称（根据showAssignee决定是否显示负责人）
    const projectDisplayName = showAssignee && project.assignee 
      ? `${project.name} (${project.assignee})` 
      : `${project.name} ${!isExpanded ? '(已折叠)' : ''}`;
    
    titleGroup.append('text')
      .attr('x', 60)
      .attr('y', 0)
      .attr('class', 'gantt-project-title-text')
      .attr('font-size', '13px')
      .attr('font-weight', '600')
      .attr('fill', '#333333')
      .style('cursor', 'pointer')
      .text(projectDisplayName)
      .on('click', () => onProjectClick?.(project))
      .on('mouseover', function() {
        d3.select(this)
          .attr('fill', '#1890ff')
          .attr('text-decoration', 'underline');
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('fill', '#333333')
          .attr('text-decoration', 'none');
      });

    // 任务状态解析函数
    const getStatusFromCustomClass = (customClass: string): string => {
      const statusMap: Record<string, string> = {
        'bar-active': 'active',
        'bar-pending': 'pending',
        'bar-completed': 'completed',
        'bar-delayed': 'delayed',
        'bar-cancelled': 'cancelled'
      };
      const status = statusMap[customClass] || 'unknown';
      // 添加调试信息
      console.log('Status parsing:', { customClass, status });
      return status;
    };

    // 项目进度
    const progressText = titleGroup.append('text')
      .attr('x', svgWidth - 20)
      .attr('y', 0)
      .attr('text-anchor', 'end')
      .attr('font-size', '12px')
      .attr('fill', '#666666')
      .style('cursor', 'pointer')
      .text(`进度: ${Math.round(project.progress)}%`)
      .on('mouseover', function() {
        try {
          // 计算进度相关数据
          const totalTasks = project.tasks.length;
          
          // 修正：使用 custom_class 解析任务状态，添加字段验证
          const completedTasks = project.tasks.filter(task => 
            getStatusFromCustomClass(task.custom_class || '') === 'completed'
          ).length;
          const activeTasks = project.tasks.filter(task => 
            getStatusFromCustomClass(task.custom_class || '') === 'active'
          ).length;
          const pendingTasks = project.tasks.filter(task => 
            getStatusFromCustomClass(task.custom_class || '') === 'pending'
          ).length;
          
          // 计算计划总天数和实际已进行天数
          let totalPlannedDays = 0;
          let totalActualDays = 0;
          const today = new Date();
          
          console.log('开始计算进度数据:', {
            projectName: project.name,
            projectProgress: project.progress,
            totalTasks: project.tasks.length
          });
          
          project.tasks.forEach((task, index) => {
            // 修正：使用 start 和 end 字段计算计划天数
            if (task.start && task.end) {
              try {
                const plannedStart = new Date(task.start);
                const plannedEnd = new Date(task.end);
                
                // 验证日期有效性
                if (!isNaN(plannedStart.getTime()) && !isNaN(plannedEnd.getTime())) {
                  const plannedDays = (plannedEnd.getTime() - plannedStart.getTime()) / (1000 * 60 * 60 * 24);
                  if (plannedDays > 0) {
                    totalPlannedDays += plannedDays;
                    console.log(`任务 ${index + 1} 计划天数:`, {
                      taskName: task.name,
                      start: task.start,
                      end: task.end,
                      plannedDays: plannedDays.toFixed(1)
                    });
                  }
                }
              } catch (error) {
                console.warn('计划天数计算错误:', { task: task.name, error });
              }
            }
            
            // 修正：基于任务状态和时间计算实际已进行天数
            if (task.start) {
              try {
                const actualStart = new Date(task.start);
                
                // 验证日期有效性
                if (!isNaN(actualStart.getTime())) {
                  const taskStatus = getStatusFromCustomClass(task.custom_class || '');
                  
                  if (taskStatus === 'completed') {
                    // 已完成任务：使用整个任务周期
                    if (task.end) {
                      const actualEnd = new Date(task.end);
                      if (!isNaN(actualEnd.getTime())) {
                        const actualDays = (actualEnd.getTime() - actualStart.getTime()) / (1000 * 60 * 60 * 24);
                        if (actualDays > 0) {
                          totalActualDays += actualDays;
                          console.log(`任务 ${index + 1} 实际天数 (已完成):`, {
                            taskName: task.name,
                            status: taskStatus,
                            actualDays: actualDays.toFixed(1)
                          });
                        }
                      }
                    }
                  } else if (taskStatus === 'active' || taskStatus === 'delayed') {
                    // 进行中或延迟任务：使用从开始到当前的时间
                    const actualDays = (today.getTime() - actualStart.getTime()) / (1000 * 60 * 60 * 24);
                    if (actualDays > 0) {
                      totalActualDays += actualDays;
                      console.log(`任务 ${index + 1} 实际天数 (进行中):`, {
                        taskName: task.name,
                        status: taskStatus,
                        actualDays: actualDays.toFixed(1)
                      });
                    }
                  }
                }
              } catch (error) {
                console.warn('实际天数计算错误:', { task: task.name, error });
              }
            }
          });
          
          console.log('计算结果:', {
            totalPlannedDays: totalPlannedDays.toFixed(1),
            totalActualDays: totalActualDays.toFixed(1),
            completedTasks,
            activeTasks,
            pendingTasks
          });
          
          // 计算时间进度
          let timeProgress = 0;
          if (project.start_date && project.end_date) {
            try {
              const projectStart = new Date(project.start_date);
              const projectEnd = new Date(project.end_date);
              
              // 验证日期有效性
              if (!isNaN(projectStart.getTime()) && !isNaN(projectEnd.getTime())) {
                const totalProjectDays = (projectEnd.getTime() - projectStart.getTime()) / (1000 * 60 * 60 * 24);
                console.log('时间进度计算:', {
                  projectStart: projectStart.toISOString(),
                  projectEnd: projectEnd.toISOString(),
                  today: today.toISOString(),
                  totalProjectDays: totalProjectDays.toFixed(1),
                  projectName: project.name
                });
                
                if (totalProjectDays > 0.1) { // 避免非常小的时间范围导致计算异常
                  const elapsedDays = (today.getTime() - projectStart.getTime()) / (1000 * 60 * 60 * 24);
                  console.log('时间进度计算详情:', {
                    elapsedDays: elapsedDays.toFixed(1),
                    totalProjectDays: totalProjectDays.toFixed(1),
                    ratio: (elapsedDays / totalProjectDays).toFixed(2)
                  });
                  
                  if (elapsedDays >= 0) {
                    timeProgress = Math.min(100, Math.max(0, (elapsedDays / totalProjectDays) * 100));
                    console.log('最终时间进度:', timeProgress.toFixed(1) + '%');
                  }
                } else {
                  console.warn('项目时间范围过小:', { totalProjectDays });
                }
              } else {
                console.warn('无效的项目日期:', {
                  start: project.start_date,
                  end: project.end_date,
                  startValid: !isNaN(projectStart.getTime()),
                  endValid: !isNaN(projectEnd.getTime())
                });
              }
            } catch (error) {
              console.warn('时间进度计算错误:', error);
            }
          } else {
            console.warn('项目缺少日期信息:', {
              hasStartDate: !!project.start_date,
              hasEndDate: !!project.end_date,
              projectName: project.name
            });
          }
          
          // 构建tooltip内容
          const tooltipContent = [
            `当前进度: ${Math.round(project.progress)}%`,
            `计算公式: (实际已进行天数 / 计划总天数) × 100%`,
            ``,
            `分子 - 实际已进行天数: ${totalActualDays.toFixed(1)}天`,
            `  已完成任务: ${completedTasks}个`,
            `  进行中任务: ${activeTasks}个`,
            `  未开始任务: ${pendingTasks}个`,
            ``,
            `分母 - 计划总天数: ${totalPlannedDays.toFixed(1)}天`,
            `  总任务数: ${totalTasks}个`,
            `  平均任务计划天数: ${totalTasks > 0 ? (totalPlannedDays / totalTasks).toFixed(1) : 0}天`,
            ``,
            `时间进度: ${timeProgress.toFixed(1)}%`,
            `实际进度: ${Math.round(project.progress)}%`,
            ``,
            `进度状态: ${project.progress >= timeProgress ? '正常' : '滞后'}`
          ];
          
          // 显示tooltip - 使用正确的y坐标（基于项目标题的实际位置）
          showTooltip(svg, tooltipContent, svgWidth - 20, y + 24, '进度详情', svgWidth);
        } catch (error) {
          console.error('Tooltip计算错误:', error);
          // 显示错误信息tooltip
          showTooltip(svg, ['数据计算错误，请刷新页面重试'], svgWidth - 20, y + 24, '错误', svgWidth);
        }
      })
      .on('mouseout', function() {
        svg.selectAll('.gantt-tooltip').remove();
      });

    // 渲染任务
    if (isExpanded) {
      let taskY = yPosition + 32; // 项目标题高度32px
      
      // 按任务的 order 字段排序
      const sortedTasks = [...project.tasks].sort((a, b) => {
        const orderA = a.order || 0;
        const orderB = b.order || 0;
        return orderA - orderB;
      });
      
      sortedTasks.forEach((task, taskIndex) => {
        renderTask(
          svg, 
          task, 
          categoryColor,
          xScale, 
          yScale, 
          taskY,
          svgWidth
        );
        
        taskY += 32; // 每个任务32px高度
      });
    }
  };

  // 文本换行辅助函数
  const wrapText = (text: string, maxWidth: number) => {
    const lines: string[] = [];
    let currentLine = '';
    let currentWidth = 0;
    
    for (const char of text) {
      const charWidth = /[\u4e00-\u9fa5]/.test(char) ? 10 : 6;
      
      if (currentWidth + charWidth > maxWidth && currentLine !== '') {
        lines.push(currentLine);
        currentLine = char;
        currentWidth = charWidth;
      } else {
        currentLine += char;
        currentWidth += charWidth;
      }
    }
    
    if (currentLine) {
      lines.push(currentLine);
    }
    
    return lines;
  };

  // 统一显示工具提示的函数
  const showTooltip = (
    svg: any, 
    content: string | string[], 
    x: number, 
    y: number,
    title?: string,
    svgWidth?: number
  ) => {
    if (!content) return;
  
    const contentArray = Array.isArray(content) ? content : [content];
    const maxWidth = 160;
    const lineHeight = 16;
    const padding = 12;
    
    const wrappedLines: string[] = [];
    contentArray.forEach(line => {
      const lines = wrapText(line, maxWidth);
      wrappedLines.push(...lines);
    });
    
    const totalLines = title ? wrappedLines.length + 1 : wrappedLines.length;
    const tooltipHeight = padding * 2 + totalLines * lineHeight;
    const tooltipWidth = maxWidth + padding * 2;
    
    const tooltip = svg.append('g')
      .attr('class', 'gantt-tooltip')
      .style('pointer-events', 'none');
    
    let tooltipX = x;
    let tooltipY = y - tooltipHeight - 10;
    
    if (svgWidth) {
      const leftEdge = tooltipX - tooltipWidth / 2;
      const rightEdge = tooltipX + tooltipWidth / 2;
      
      if (leftEdge < 10) {
        tooltipX = 10 + tooltipWidth / 2;
      } else if (rightEdge > svgWidth - 10) {
        tooltipX = svgWidth - 10 - tooltipWidth / 2;
      }
      
      if (tooltipY < 10) {
        tooltipY = y + 20;
      }
    }
    
    tooltip.attr('transform', `translate(${tooltipX}, ${tooltipY})`);
  
    tooltip.append('rect')
      .attr('x', -tooltipWidth / 2)
      .attr('y', -tooltipHeight / 2)
      .attr('width', tooltipWidth)
      .attr('height', tooltipHeight)
      .attr('rx', 8)
      .attr('fill', 'white')
      .attr('stroke', '#e8e8e8')
      .attr('stroke-width', 1)
      .attr('filter', 'drop-shadow(0 4px 12px rgba(0,0,0,0.15))');
  
    if (title) {
      tooltip.append('text')
        .attr('x', 0)
        .attr('y', -tooltipHeight / 2 + padding + lineHeight * 0.7)
        .attr('font-size', '12px')
        .attr('font-weight', '600')
        .attr('fill', '#1f2937')
        .attr('text-anchor', 'middle')
        .text(title);
    }
  
    wrappedLines.forEach((line, index) => {
      const yOffset = title 
        ? -tooltipHeight / 2 + padding + lineHeight * 1.7 + index * lineHeight
        : -tooltipHeight / 2 + padding + lineHeight * 0.7 + index * lineHeight;
      
      tooltip.append('text')
        .attr('x', 0)
        .attr('y', yOffset)
        .attr('font-size', '10px')
        .attr('fill', '#4b5563')
        .attr('text-anchor', 'middle')
        .text(line);
    });
  };

  // 渲染任务
  const renderTask = (
    svg: any, 
    task: any, 
    categoryColor: string,
    xScale: any, 
    yScale: any, 
    yPosition: number,
    svgWidth: number
  ) => {
    const y = yScale(yPosition);
    const start = new Date(task.start).getTime();
    const end = new Date(task.end).getTime();

    // 计算任务条位置和宽度
    const taskX = xScale(new Date(task.start));
    const taskWidth = Math.max(1, xScale(new Date(task.end)) - taskX);

    // 渲染任务标题（根据showAssignee决定是否显示负责人）
    const taskDisplayName = showAssignee && task.assignee
      ? `${task.name} (${task.assignee})`
      : task.name;
    
    const taskTitle = svg.append('text')
      .attr('class', 'gantt-task-title')
      .attr('x', 60)
      .attr('y', y + 12)
      .attr('font-size', '12px')
      .attr('fill', '#333333')
      .style('cursor', 'pointer')
      .text(`🔍 ${taskDisplayName}`)
      .on('mouseover', function() {
        if (dragState.isDragging) return;
        showTooltip(svg, task.description || '暂无描述', 60, y + 12, '任务描述', svgWidth);
      })
      .on('mouseout', function() {
        if (dragState.isDragging) return;
        svg.selectAll('.gantt-tooltip').remove();
      });

    // 判断任务是否有时间信息
    const hasTime = task.has_time !== false;
    
    // 只有有时间的任务才渲染任务条和进度条
    if (hasTime) {
      renderTaskBar(svg, task, categoryColor, xScale, y, taskX, taskWidth, svgWidth);
    }
  };

  // 渲染任务条（独立函数，只处理有时间的任务）
  const renderTaskBar = (
    svg: any,
    task: any,
    categoryColor: string,
    xScale: any,
    y: number,
    taskX: number,
    taskWidth: number,
    svgWidth: number
  ) => {
    // 渲染任务条背景（带边框）
    // 任务条位置调整：与进度条对齐，去除多余的边框空间
    const taskBar = svg.append('rect')
      .attr('class', 'gantt-task-bar')
      .attr('data-task-id', task.id)
      .attr('data-task-order', task.order)
      .attr('x', taskX + TASK_BAR_BORDER_WIDTH)
      .attr('y', y - TASK_BAR_Y_OFFSET)
      .attr('width', taskWidth - TASK_BAR_BORDER_WIDTH * 2)
      .attr('height', TASK_BAR_INNER_HEIGHT)
      .attr('rx', 3)
      .attr('fill', getTaskColor(task.custom_class, task.progress, categoryColor))
      .attr('stroke', adjustColorBrightness(getTaskColor(task.custom_class, task.progress, categoryColor), -30))
      .attr('stroke-width', TASK_BAR_BORDER_WIDTH)
      .style('cursor', 'grab')
      .style('transition', 'all 0.2s ease');

    // 添加拖拽行为
    const dragBehavior = d3.drag()
      .on('start', function(event: any) {
        event.sourceEvent.stopPropagation();
        const taskId = parseInt(task.id.toString().replace('task_', ''));
        
        setDragState({
          isDragging: true,
          draggedTask: task,
          draggedTaskId: taskId,
          originalY: y - TASK_BAR_Y_OFFSET,
          currentY: y - TASK_BAR_Y_OFFSET,
          taskHeight: 32
        });
        
        d3.select(this)
          .style('opacity', '0.7')
          .style('cursor', 'grabbing')
          .classed('dragging', true);
      })
      .on('drag', function(event: any) {
        event.sourceEvent.stopPropagation();
        // 使用event.y获取当前拖拽位置，减去偏移量使鼠标在任务条中心
        const newY = event.y - TASK_BAR_Y_OFFSET - TASK_BAR_BORDER_WIDTH;
        
        setDragState(prev => ({
          ...prev,
          currentY: newY
        }));
        
        d3.select(this)
          .attr('y', newY);
        
        // 移除之前的指示线和高亮
        svg.selectAll('.gantt-drag-indicator').remove();
        svg.selectAll('.gantt-task-bar').classed('drop-target', false);
        
        // 计算并显示指示线
        const taskElements = document.querySelectorAll('.gantt-task-bar');
        let nearestElement: Element | null = null;
        let minDistance = Infinity;
        let insertAfter = true;
        
        taskElements.forEach((el) => {
          if (el === this) return;
          const rect = el.getBoundingClientRect();
          const centerY = rect.top + rect.height / 2;
          const distance = Math.abs(centerY - event.sourceEvent.clientY);
          
          if (distance < minDistance) {
            minDistance = distance;
            nearestElement = el;
            // 判断鼠标在目标元素的上方还是下方
            insertAfter = event.sourceEvent.clientY > centerY;
          }
        });
        
        // 显示指示线和目标高亮
        if (nearestElement && minDistance < 50) {
          const targetRect = nearestElement.getBoundingClientRect();
          const svgRect = svg.node().getBoundingClientRect();
          const indicatorY = insertAfter 
            ? targetRect.bottom - svgRect.top 
            : targetRect.top - svgRect.top;
          
          // 添加指示线
          svg.append('line')
            .attr('class', 'gantt-drag-indicator')
            .attr('x1', 60)
            .attr('y1', indicatorY)
            .attr('x2', svgWidth)
            .attr('y2', indicatorY);
          
          // 高亮目标元素
          d3.select(nearestElement as any).classed('drop-target', true);
        }
      })
      .on('end', function(event: any) {
        event.sourceEvent.stopPropagation();
        
        // 移除指示线和高亮
        svg.selectAll('.gantt-drag-indicator').remove();
        svg.selectAll('.gantt-task-bar').classed('drop-target', false);
        
        d3.select(this)
          .style('opacity', '1')
          .style('cursor', 'grab')
          .classed('dragging', false);
        
        // 计算目标位置
        const taskElements = document.querySelectorAll('.gantt-task-bar');
        let nearestElement: Element | null = null;
        let minDistance = Infinity;
        let insertAfter = true;
        
        taskElements.forEach((el) => {
          if (el === this) return;
          const rect = el.getBoundingClientRect();
          const centerY = rect.top + rect.height / 2;
          const distance = Math.abs(centerY - event.sourceEvent.clientY);
          
          if (distance < minDistance) {
            minDistance = distance;
            nearestElement = el;
            // 判断鼠标在目标元素的上方还是下方
            insertAfter = event.sourceEvent.clientY > centerY;
          }
        });
        
        // 如果找到目标位置且距离足够近
        const taskProjectId = task.project_id || projectId;
        if (nearestElement && minDistance < 100 && taskProjectId) {
          const targetOrderAttr = nearestElement.getAttribute('data-task-order');
          const targetOrder = targetOrderAttr ? parseInt(targetOrderAttr) : task.order;
          
          // 计算新的order值
          let newOrder = targetOrder;
          if (insertAfter) {
            newOrder = targetOrder + 1;
          }
          
          // 获取任务ID
          const taskId = parseInt(task.id.toString().replace('task_', ''));
          
          console.log('准备更新任务顺序:', {
            taskId,
            taskProjectId,
            oldOrder: task.order,
            newOrder,
            targetOrder,
            insertAfter
          });
          
          // 如果位置发生变化，更新任务顺序
          if (newOrder !== task.order) {
            // 调用API更新任务顺序
            fetch(`/api/v1/projects/${taskProjectId}/tasks/${taskId}`, {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ order: newOrder })
            })
            .then(response => {
              console.log('API响应状态:', response.status);
              if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
              }
              return response.json();
            })
            .then(data => {
              console.log('API响应数据:', data);
              message.success('任务顺序已更新');
              // 使用React Query刷新甘特图数据，而不是整页刷新
              queryClient.invalidateQueries({ queryKey: ['gantt', projectId || 'all'] });
            })
            .catch(error => {
              console.error('更新任务顺序失败:', error);
              // 恢复原始位置
              d3.select(this).attr('y', y - TASK_BAR_Y_OFFSET - TASK_BAR_BORDER_WIDTH);
            });
          } else {
            // 恢复原始位置
            d3.select(this).attr('y', y - TASK_BAR_Y_OFFSET - TASK_BAR_BORDER_WIDTH);
          }
        } else {
          console.log('未满足更新条件:', {
            hasNearestElement: !!nearestElement,
            minDistance,
            taskProjectId,
            projectId
          });
          // 恢复原始位置
          d3.select(this).attr('y', y - TASK_BAR_Y_OFFSET - TASK_BAR_BORDER_WIDTH);
        }
        
        setDragState({
          isDragging: false,
          draggedTask: null,
          draggedTaskId: null,
          originalY: 0,
          currentY: 0,
          taskHeight: 32
        });
      });
    
    taskBar.call(dragBehavior as any);

    // 添加鼠标事件（仅在非拖拽状态下）
    taskBar.on('mouseover', function() {
      if (dragState.isDragging) return;
      
      d3.select(this)
        .attr('height', 34)
        .attr('y', y - TASK_BAR_Y_OFFSET - 1);
      
      const fullStartDate = new Date(task.start).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
      const fullEndDate = new Date(task.end).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
      const startTypeText = task.startTimeType === 'actual' ? '实际' : '计划';
      const endTypeText = task.endTimeType === 'actual' ? '实际' : '计划';
      const statusText = getStatusText(task.custom_class);
      
      const tooltipContent = [
        `开始时间 (${startTypeText}): ${fullStartDate}`,
        `结束时间 (${endTypeText}): ${fullEndDate}`,
        `状态: ${statusText}`,
        `进度: ${task.progress}%`
      ];
      
      showTooltip(svg, tooltipContent, taskX + taskWidth / 2, y - 30, task.name, svgWidth);
    })
    .on('mouseout', function() {
      if (dragState.isDragging) return;
      
      d3.select(this)
        .attr('height', TASK_BAR_INNER_HEIGHT)
        .attr('y', y - TASK_BAR_Y_OFFSET);
      
      svg.selectAll('.gantt-tooltip').remove();
    })
    .on('click', function(event) {
      if (dragState.isDragging) return;
      event.stopPropagation();
      onTaskClick?.(task);
    });

    // 渲染任务进度 - 基于时间进度（到今天为止）
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const taskStart = new Date(task.start);
    const taskEnd = new Date(task.end);
    
    // 计算时间进度：今天相对于任务开始和结束的位置
    let timeProgressWidth = 0;
    if (today >= taskEnd) {
      // 今天已过任务结束时间，显示完整进度条
      timeProgressWidth = taskWidth;
    } else if (today > taskStart) {
      // 今天在任务时间范围内，按比例计算
      const totalDuration = taskEnd.getTime() - taskStart.getTime();
      const elapsedDuration = today.getTime() - taskStart.getTime();
      const timeProgressRatio = elapsedDuration / totalDuration;
      timeProgressWidth = Math.max(0, Math.min(taskWidth, taskWidth * timeProgressRatio));
    }
    // 如果今天 < 任务开始时间，timeProgressWidth 保持为 0
    
    if (timeProgressWidth > 0) {
      // 进度条：填充在任务条边框内部
      // 由于任务条有 1px 边框，进度条需要向内偏移 1px
      const progressX = taskX + TASK_BAR_BORDER_WIDTH;
      const progressY = y - TASK_BAR_Y_OFFSET;
      const progressHeight = TASK_BAR_INNER_HEIGHT;
      // 宽度不能超过任务条内部区域
      const maxProgressWidth = Math.max(0, taskWidth - TASK_BAR_BORDER_WIDTH * 2);
      const progressWidth = Math.max(0, Math.min(timeProgressWidth - TASK_BAR_BORDER_WIDTH, maxProgressWidth));
      
      svg.append('rect')
        .attr('class', 'gantt-task-progress')
        .attr('x', progressX)
        .attr('y', progressY)
        .attr('width', progressWidth)
        .attr('height', progressHeight)
        .attr('rx', 3)
        .attr('fill', getProgressColor(task.custom_class, task.progress, categoryColor))
        .style('pointer-events', 'none');
    }

    // 渲染任务时间标签
    const shortStartDate = new Date(task.start).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    const shortEndDate = new Date(task.end).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
    const compactStartDate = new Date(task.start).toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
    const compactEndDate = new Date(task.end).toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
    
    // 根据任务条宽度判断显示模式
    if (taskWidth > 90) {
      // 宽任务条：显示开始时间（左侧）和结束时间（右侧）
      // 开始时间
      svg.append('text')
        .attr('class', 'gantt-task-time-label')
        .attr('x', taskX + 8)
        .attr('y', y)
        .attr('font-size', '10px')
        .attr('font-weight', '500')
        .attr('fill', 'white')
        .attr('text-anchor', 'start')
        .attr('text-shadow', '0 1px 2px rgba(0,0,0,0.3)')
        .style('pointer-events', 'none')
        .text(shortStartDate);
      
      // 结束时间
      svg.append('text')
        .attr('class', 'gantt-task-time-label')
        .attr('x', taskX + taskWidth - 8)
        .attr('y', y)
        .attr('font-size', '10px')
        .attr('font-weight', '500')
        .attr('fill', 'white')
        .attr('text-anchor', 'end')
        .attr('text-shadow', '0 1px 2px rgba(0,0,0,0.3)')
        .style('pointer-events', 'none')
        .text(shortEndDate);
    } else if (taskWidth > 40) {
      // 中等宽度任务条：内部显示开始时间，右侧外部显示结束时间
      // 开始时间
      svg.append('text')
        .attr('class', 'gantt-task-time-label')
        .attr('x', taskX + 8)
        .attr('y', y)
        .attr('font-size', '10px')
        .attr('font-weight', '500')
        .attr('fill', 'white')
        .attr('text-anchor', 'start')
        .attr('text-shadow', '0 1px 2px rgba(0,0,0,0.3)')
        .style('pointer-events', 'none')
        .text(shortStartDate);
      
      // 结束时间（右侧外部）
      svg.append('text')
        .attr('class', 'gantt-task-time-label-external')
        .attr('x', taskX + taskWidth + 8)
        .attr('y', y)
        .attr('font-size', '9px')
        .attr('fill', '#666666')
        .attr('text-anchor', 'start')
        .style('pointer-events', 'none')
        .text(shortEndDate);
    } else if (taskWidth > 15) {
      // 短任务条：两侧外部显示开始和结束时间
      // 开始时间（左侧外部）
      svg.append('text')
        .attr('class', 'gantt-task-time-label-external')
        .attr('x', taskX - 8)
        .attr('y', y)
        .attr('font-size', '9px')
        .attr('fill', '#666666')
        .attr('text-anchor', 'end')
        .style('pointer-events', 'none')
        .text(shortStartDate);
      
      // 结束时间（右侧外部）
      svg.append('text')
        .attr('class', 'gantt-task-time-label-external')
        .attr('x', taskX + taskWidth + 8)
        .attr('y', y)
        .attr('font-size', '9px')
        .attr('fill', '#666666')
        .attr('text-anchor', 'start')
        .style('pointer-events', 'none')
        .text(shortEndDate);
    } else {
      // 极短任务条：两侧外部显示紧凑格式的时间
      // 开始时间（左侧外部）
      svg.append('text')
        .attr('class', 'gantt-task-time-label-external')
        .attr('x', taskX - 6)
        .attr('y', y)
        .attr('font-size', '8px')
        .attr('fill', '#666666')
        .attr('text-anchor', 'end')
        .style('pointer-events', 'none')
        .text(compactStartDate);
      
      // 结束时间（右侧外部）
      svg.append('text')
        .attr('class', 'gantt-task-time-label-external')
        .attr('x', taskX + taskWidth + 6)
        .attr('y', y)
        .attr('font-size', '8px')
        .attr('fill', '#666666')
        .attr('text-anchor', 'start')
        .style('pointer-events', 'none')
        .text(compactEndDate);
    }
  };

  // 处理大类折叠/展开
  const handleToggleCategory = (categoryIndex: number) => {
    setExpandedStates(prev => ({
      ...prev,
      categories: {
        ...prev.categories,
        [categoryIndex]: !prev.categories[categoryIndex]
      }
    }));
  };

  // 处理项目折叠/展开
  const handleToggleProject = (projectKey: string) => {
    setExpandedStates(prev => ({
      ...prev,
      projects: {
        ...prev.projects,
        [projectKey]: !prev.projects[projectKey]
      }
    }));
  };

  // 获取大类颜色
  const getCategoryColor = (index: number) => {
    const colors = [
      '#1890ff', // 蓝色
      '#52c41a', // 绿色
      '#faad14', // 黄色
      '#f5222d', // 红色
      '#722ed1', // 紫色
      '#13c2c2', // 青色
      '#fa8c16', // 橙色
      '#eb2f96'  // 粉色
    ];
    return colors[index % colors.length];
  };

  // 获取任务颜色
  const getTaskColor = (customClass: string, progress: number, categoryColor: string) => {
    return '#64748b'; // 深灰色，任务条固定为深灰色背景
  };

  // 获取进度条颜色
  const getProgressColor = (customClass: string, progress: number, categoryColor: string) => {
    switch (customClass) {
      case 'bar-active':
        return '#3b82f6'; // 蓝色 - 进行中
      case 'bar-pending':
        return '#94a3b8'; // 浅灰色 - 待处理
      case 'bar-completed':
        return '#22c55e'; // 绿色 - 已完成
      case 'bar-delayed':
        return '#ef4444'; // 红色 - 已延迟
      case 'bar-cancelled':
        return '#64748b'; // 深灰色 - 已取消
      default:
        return '#94a3b8'; // 浅灰色 - 默认
    }
  };

  // 调整颜色亮度
  const adjustColorBrightness = (color: string, percent: number) => {
    // 移除#号
    color = color.replace(/^#/, '');
    
    // 解析RGB值
    let r = parseInt(color.substring(0, 2), 16);
    let g = parseInt(color.substring(2, 4), 16);
    let b = parseInt(color.substring(4, 6), 16);
    
    // 调整亮度
    r = Math.max(0, Math.min(255, Math.round(r * (100 + percent) / 100)));
    g = Math.max(0, Math.min(255, Math.round(g * (100 + percent) / 100)));
    b = Math.max(0, Math.min(255, Math.round(b * (100 + percent) / 100)));
    
    // 转换回十六进制
    const toHex = (num: number) => {
      const hex = num.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };
    
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  };

  // 获取状态文本
  const getStatusText = (customClass: string) => {
    const statusMap: Record<string, string> = {
      'bar-pending': '待处理',
      'bar-active': '进行中',
      'bar-completed': '已完成',
      'bar-delayed': '已延迟',
      'bar-cancelled': '已取消'
    };
    return statusMap[customClass] || '未知';
  };

  // 导出甘特图为图片
  const handleExport = async (format: 'png' | 'jpg' = 'png', quality: number = 0.9) => {
    // 首先检查chartRef是否存在
    if (!chartRef.current) {
      message.error('图表容器不存在');
      return;
    }

    // 尝试获取SVG元素
    const svgElement = chartRef.current.querySelector('svg');
    if (!svgElement) {
      message.error('未找到甘特图元素');
      return;
    }

    // 检查是否有数据
    if (!ganttData?.project_categories || ganttData.project_categories.length === 0) {
      message.error('甘特图无数据可导出');
      return;
    }

    try {
      const loadingMessage = message.loading('正在导出...', 0);

      // 优化：在导出前暂时禁用按钮，避免重复点击
      const exportButton = document.querySelector('.gantt-export-button');
      if (exportButton) {
        (exportButton as HTMLButtonElement).disabled = true;
      }

      // 方法1：尝试使用SVG直接转换为图片（备选方案）
      try {
        // 将SVG转换为data URL
        const svgString = new XMLSerializer().serializeToString(svgElement);
        const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        const svgUrl = URL.createObjectURL(svgBlob);

        // 创建图片元素
        const img = new Image();
        img.onload = async () => {
          try {
            // 创建canvas
            const canvas = document.createElement('canvas');
            canvas.width = img.width * 2; // 提高分辨率
            canvas.height = img.height * 2;
            
            // 绘制图片到canvas
            const ctx = canvas.getContext('2d');
            if (ctx) {
              // 设置背景色
              ctx.fillStyle = '#ffffff';
              ctx.fillRect(0, 0, canvas.width, canvas.height);
              
              // 绘制图片
              ctx.scale(2, 2); // 提高分辨率
              ctx.drawImage(img, 0, 0);

              // 将canvas转换为图片并下载
              const dataUrl = canvas.toDataURL(`image/${format}`, quality);
              const link = document.createElement('a');
              link.href = dataUrl;
              link.download = `甘特图_${new Date().toISOString().slice(0, 10)}.${format}`;
              link.click();

              // 清理
              URL.revokeObjectURL(svgUrl);
              setTimeout(() => {
                loadingMessage(); // 关闭加载提示
                message.success('导出成功');
                if (exportButton) {
                  (exportButton as HTMLButtonElement).disabled = false;
                }
              }, 500);
            } else {
              throw new Error('无法获取canvas上下文');
            }
          } catch (error) {
            console.error('图片绘制失败:', error);
            throw error;
          }
        };

        img.onerror = () => {
          console.error('图片加载失败');
          throw new Error('图片加载失败');
        };

        img.src = svgUrl;
      } catch (error) {
        console.error('SVG转换失败，尝试使用html2canvas:', error);
        
        // 方法2：回退到html2canvas
        // 优化配置，使用不同的方法来处理元素
        const canvas = await html2canvas(chartRef.current, {
          backgroundColor: '#ffffff',
          scale: 2, // 提高分辨率
          useCORS: true,
          logging: false,
          removeContainer: true,
          allowTaint: true,
          foreignObjectRendering: true,
          // 只捕获可见区域
          x: 0,
          y: 0,
          width: chartRef.current.clientWidth,
          height: chartRef.current.clientHeight
        });

        // 将canvas转换为图片并下载
        const dataUrl = canvas.toDataURL(`image/${format}`, quality);
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `甘特图_${new Date().toISOString().slice(0, 10)}.${format}`;
        link.click();

        // 清理
        setTimeout(() => {
          loadingMessage(); // 关闭加载提示
          message.success('导出成功');
          if (exportButton) {
            (exportButton as HTMLButtonElement).disabled = false;
          }
        }, 500);
      }
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败，请重试');
      // 确保按钮重新启用
      const exportButton = document.querySelector('.gantt-export-button');
      if (exportButton) {
        (exportButton as HTMLButtonElement).disabled = false;
      }
    }
  };

  // 控制栏组件
interface ControlBarProps {
  ganttData: AllGanttData | undefined;
  selectedProject: number | null;
  setSelectedProject: (value: number | null) => void;
  selectedCategory: number | null;
  setSelectedCategory: (value: number | null) => void;
  handleSearch: (value: string) => void;
  totalTaskCount: number;
  onExport: (format?: 'png' | 'jpg') => void;
  showAssignee: boolean;
  setShowAssignee: (value: boolean) => void;
}

const ControlBar: React.FC<ControlBarProps> = ({  ganttData,  selectedProject,  setSelectedProject,  selectedCategory,  setSelectedCategory,  handleSearch,  totalTaskCount, onExport, showAssignee, setShowAssignee}) => {
  // 获取所有项目列表用于选择
  const allProjects = useMemo(() => {
    if (!ganttData?.project_categories) return [];
    const projects: { id: number; name: string }[] = [];
    ganttData.project_categories.forEach(category => {
      category.projects.forEach(project => {
        projects.push({ id: project.id, name: project.name });
      });
    });
    return projects;
  }, [ganttData]);

  return (
    <div className="gantt-control-bar">
      <div className="gantt-control-bar-main">
        <div className="gantt-control-group">
          <div className="gantt-control-item">
            <AppstoreOutlined className="gantt-control-icon" />
            <span className="gantt-control-label">项目</span>
          </div>
          <Select
            value={selectedProject}
            onChange={(value) => setSelectedProject(value)}
            className="gantt-control-select"
            showSearch
            optionFilterProp="children"
            allowClear
          >
            <Option value="">
              <UnorderedListOutlined className="gantt-option-icon" />
              <span>所有项目</span>
            </Option>
            {allProjects.map(project => (
              <Option key={project.id} value={project.id}>
                {project.name}
              </Option>
            ))}
          </Select>
        </div>

        <div className="gantt-control-group">
          <div className="gantt-control-item">
            <FolderOutlined className="gantt-control-icon" />
            <span className="gantt-control-label">项目大类</span>
          </div>
          <Select
            value={selectedCategory}
            onChange={(value) => setSelectedCategory(value)}
            className="gantt-control-select"
            allowClear
            placeholder="全部"
          >
            <Option value="">
              <span>全部</span>
            </Option>
            {ganttData?.project_categories.map(category => (
              <Option key={category.id} value={category.id}>
                <span>{category.name}</span>
                <span className="gantt-option-count">
                  ({category.projects.length})
                </span>
              </Option>
            ))}
          </Select>
        </div>

        <div className="gantt-control-group">
          <div className="gantt-control-item">
            <SearchOutlined className="gantt-control-icon" />
            <span className="gantt-control-label">搜索任务</span>
          </div>
          <SearchInput
            onSearch={handleSearch}
          />
        </div>

        <div className="gantt-control-group">
          <div className="gantt-control-item">
            <span className="gantt-control-label">显示负责人</span>
          </div>
          <Switch
            checked={showAssignee}
            onChange={(checked) => setShowAssignee(checked)}
            size="small"
          />
        </div>
      </div>

      <div className="gantt-control-bar-status">
        <span className="gantt-status-text">
          找到 <strong>{totalTaskCount}</strong> 个任务
        </span>
      </div>

      <div className="gantt-control-bar-export">
        <Dropdown
          menu={{
            items: [
              {
                key: 'png',
                label: '导出为PNG',
                onClick: () => {
                  if (typeof onExport === 'function') {
                    onExport('png');
                  }
                }
              },
              {
                key: 'jpg',
                label: '导出为JPG',
                onClick: () => {
                  if (typeof onExport === 'function') {
                    onExport('jpg');
                  }
                }
              }
            ]
          }}
        >
          <Button
            icon={<DownloadOutlined />}
            className="gantt-export-button"
          >
            导出
          </Button>
        </Dropdown>
      </div>
    </div>
  );
};

// 使用 React.memo 优化 ControlBar 组件
const MemoizedControlBar = React.memo(ControlBar);

  // 图例组件
  const Legend = () => (
    <div className="gantt-legend">
      <div className="gantt-legend-item">
        <div className="gantt-legend-color gantt-legend-category"></div>
        <span className="gantt-legend-label">项目大类</span>
      </div>
      <div className="gantt-legend-item">
        <div className="gantt-legend-color gantt-legend-project"></div>
        <span className="gantt-legend-label">项目</span>
      </div>
      <div className="gantt-legend-item">
        <div className="gantt-legend-color gantt-legend-task"></div>
        <span className="gantt-legend-label">任务</span>
      </div>
      <div className="gantt-legend-item">
        <div className="gantt-legend-color gantt-legend-today"></div>
        <span className="gantt-legend-label">今天</span>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className={`gantt-container ${className}`} style={{ width }}>
        <MemoizedControlBar
          ganttData={ganttData}
          selectedProject={selectedProject}
          setSelectedProject={setSelectedProject}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          handleSearch={handleSearch}
          totalTaskCount={totalTaskCount}
          onExport={(format) => handleExport(format || 'png')}
          showAssignee={showAssignee}
          setShowAssignee={setShowAssignee}
        />
        <div className="gantt-loading">
          <Spin>
            <div style={{ padding: '20px' }}>加载甘特图数据...</div>
          </Spin>
        </div>
        <Legend />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`gantt-container ${className}`} style={{ width }}>
        <MemoizedControlBar
          ganttData={ganttData}
          selectedProject={selectedProject}
          setSelectedProject={setSelectedProject}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          handleSearch={handleSearch}
          totalTaskCount={totalTaskCount}
          onExport={(format) => handleExport(format || 'png')}
          showAssignee={showAssignee}
          setShowAssignee={setShowAssignee}
        />
        <div className="gantt-empty">
          <Empty description="加载失败，请重试" />
        </div>
        <Legend />
      </div>
    );
  }

  return (
    <div className={`gantt-container ${className}`} style={{ width }}>
      <MemoizedControlBar
        ganttData={ganttData}
        selectedProject={selectedProject}
        setSelectedProject={setSelectedProject}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        handleSearch={handleSearch}
        totalTaskCount={totalTaskCount}
        onExport={(format) => handleExport(format || 'png')}
        showAssignee={showAssignee}
        setShowAssignee={setShowAssignee}
      />
      <div className="gantt-chart-wrapper" style={{ overflowX: 'auto', marginBottom: '20px' }}>
        <div 
          ref={chartRef} 
          className="gantt-chart" 
          style={{ minWidth: '800px' }}
        />
      </div>
      <Legend />
    </div>
  );
};

export default GanttChart;