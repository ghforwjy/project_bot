import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { useQuery } from '@tanstack/react-query';
import { Spin, Empty, Tooltip, Select, Input, Button } from 'antd';
import { AppstoreOutlined, FolderOutlined, SearchOutlined, CloseCircleOutlined, UnorderedListOutlined, BarsOutlined } from '@ant-design/icons';
import { AllGanttData, GanttChartProps, GanttData, ProjectCategoryGantt, ProjectGantt, ExpandedStates } from './types';
import './GanttChart.css';

const { Option } = Select;

// 搜索输入组件 - 独立的组件避免焦点问题
const SearchInput: React.FC<{
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
}> = ({ value, onChange, onSearch }) => {
  return (
    <>
      <Input
        placeholder="输入任务名称或描述..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onPressEnter={onSearch}
        className="gantt-control-input"
      />
      <Button
        icon={<SearchOutlined />}
        onClick={onSearch}
        className="gantt-control-button"
      >
        搜索
      </Button>
    </>
  );
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
  const [expandedStates, setExpandedStates] = useState<ExpandedStates>({
    categories: {},
    projects: {}
  });
  const [viewMode, setViewMode] = useState<'single' | 'all'>('all');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchInputValue, setSearchInputValue] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [categories, setCategories] = useState<ProjectCategoryGantt[]>([]);
  const [containerWidth, setContainerWidth] = useState<number>(0);

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
      if (result.data) {
        if (result.data.project_categories) {
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
      }
      
      return { project_categories: [] };
    },
    enabled: true
  });

  const filteredCategories = useMemo(() => {
    let result = ganttData?.project_categories || [];
    
    // 使用本地选择的项目ID，如果没有则使用父组件传入的projectId
    const effectiveProjectId = selectedProjectId !== null ? selectedProjectId : projectId;
    
    if (viewMode === 'single' && effectiveProjectId) {
      result = result.filter((category: ProjectCategoryGantt) => 
        category.projects.some((project: ProjectGantt) => project.id === effectiveProjectId)
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
  }, [viewMode, projectId, selectedCategory, searchQuery, ganttData, selectedProjectId]);

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

  }, [filteredCategories, expandedStates, height, containerWidth]);

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
        // 如果总时间范围大于理想时间范围，以今天为中心显示
        const centerTime = today;
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
    svg.append('g')
      .attr('class', 'gantt-time-axis')
      .attr('transform', `translate(0, ${height - 40})`)
      .call(xAxis)
      .selectAll('text')
      .attr('class', 'gantt-time-label')
      .attr('dx', '-8px')
      .attr('dy', '8px')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .style('font-size', '11px')
      .style('fill', '#666666')
      .style('font-weight', '500');

    // 渲染时间轴网格线
    svg.append('g')
      .attr('class', 'gantt-grid')
      .attr('transform', `translate(0, ${height - 40})`)
      .call(
        d3.axisBottom(xScale)
          .ticks(tickCount)
          .tickSize(-(height - 80))
          .tickFormat('')
      )
      .selectAll('line')
      .attr('stroke', '#e8e8e8')
      .attr('stroke-dasharray', '2,2');
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

    // 项目名称
    titleGroup.append('text')
      .attr('x', 60)
      .attr('y', 0)
      .attr('class', 'gantt-project-title-text')
      .attr('font-size', '13px')
      .attr('font-weight', '600')
      .attr('fill', '#333333')
      .style('cursor', 'pointer')
      .text(`${project.name} ${!isExpanded ? '(已折叠)' : ''}`)
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

    // 项目进度
    titleGroup.append('text')
      .attr('x', svgWidth - 20)
      .attr('y', 0)
      .attr('text-anchor', 'end')
      .attr('font-size', '12px')
      .attr('fill', '#666666')
      .text(`进度: ${Math.round(project.progress)}%`);

    // 渲染任务
    if (isExpanded) {
      let taskY = yPosition + 32; // 项目标题高度32px
      
      project.tasks.forEach((task, taskIndex) => {
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

    // 渲染任务标题
    const taskTitle = svg.append('text')
      .attr('class', 'gantt-task-title')
      .attr('x', 60)
      .attr('y', y + 12)
      .attr('font-size', '12px')
      .attr('fill', '#333333')
      .style('cursor', 'pointer')
      .text(`🔍 ${task.name}`)
      .on('mouseover', function() {
        showTooltip(svg, task.description || '暂无描述', 60, y + 12, '任务描述', svgWidth);
      })
      .on('mouseout', function() {
        // 移除所有工具提示
        svg.selectAll('.gantt-tooltip').remove();
      });

    // 渲染任务条
    const taskBar = svg.append('rect')
      .attr('class', 'gantt-task-bar')
      .attr('x', taskX)
      .attr('y', y - 16)
      .attr('width', taskWidth)
      .attr('height', 20)
      .attr('rx', 4)
      .attr('fill', getTaskColor(task.custom_class, task.progress, categoryColor))
      .attr('stroke', adjustColorBrightness(getTaskColor(task.custom_class, task.progress, categoryColor), -30))
      .attr('stroke-width', 1)
      .style('cursor', 'pointer')
      .style('transition', 'all 0.2s ease')
      .on('mouseover', function() {
        d3.select(this)
          .attr('height', 22)
          .attr('y', y - 17);
        
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
        d3.select(this)
          .attr('height', 20)
          .attr('y', y - 16);
        
        svg.selectAll('.gantt-tooltip').remove();
      })
      .on('click', () => onTaskClick?.(task));

    // 渲染任务进度
    if (task.progress > 0) {
      const progressWidth = Math.max(0, Math.min(taskWidth, (taskWidth * task.progress) / 100));
      
      svg.append('rect')
        .attr('class', 'gantt-task-progress')
        .attr('x', taskX)
        .attr('y', y - 16)
        .attr('width', progressWidth)
        .attr('height', 32)
        .attr('rx', 4)
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

  // 控制栏组件
  const ControlBar = () => {
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
              <span className="gantt-control-label">视图模式</span>
            </div>
            <Select
              value={viewMode}
              onChange={(value) => {
                setViewMode(value);
                if (value === 'all') {
                  setSelectedProjectId(null);
                }
              }}
              className="gantt-control-select"
            >
              <Option value="all">
                <UnorderedListOutlined className="gantt-option-icon" />
                <span>所有项目</span>
              </Option>
              <Option value="single">
                <BarsOutlined className="gantt-option-icon" />
                <span>单个项目</span>
              </Option>
            </Select>
          </div>

          {viewMode === 'single' && (
            <div className="gantt-control-group">
              <div className="gantt-control-item">
                <FolderOutlined className="gantt-control-icon" />
                <span className="gantt-control-label">选择项目</span>
              </div>
              <Select
                value={selectedProjectId}
                onChange={(value) => setSelectedProjectId(value)}
                className="gantt-control-select"
                placeholder="请选择项目"
                showSearch
                optionFilterProp="children"
                allowClear
              >
                {allProjects.map(project => (
                  <Option key={project.id} value={project.id}>
                    {project.name}
                  </Option>
                ))}
              </Select>
            </div>
          )}

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
              <Option value={null}>
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
              value={searchInputValue}
              onChange={setSearchInputValue}
              onSearch={() => setSearchQuery(searchInputValue)}
            />
          </div>
        </div>

        <div className="gantt-control-bar-status">
          <span className="gantt-status-text">
            找到 <strong>{totalTaskCount}</strong> 个任务
          </span>
        </div>
      </div>
    );
  };

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
        <ControlBar />
        <div className="gantt-loading">
          <Spin tip="加载甘特图数据..." />
        </div>
        <Legend />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`gantt-container ${className}`} style={{ width }}>
        <ControlBar />
        <div className="gantt-empty">
          <Empty description="加载失败，请重试" />
        </div>
        <Legend />
      </div>
    );
  }

  return (
    <div className={`gantt-container ${className}`} style={{ width }}>
      <ControlBar />
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