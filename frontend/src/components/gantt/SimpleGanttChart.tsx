import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { useQuery } from '@tanstack/react-query';

// 简化的甘特图组件
const SimpleGanttChart: React.FC = () => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [ganttData, setGanttData] = useState<any>(null);

  // 获取甘特图数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/v1/gantt/all');
        const result = await response.json();
        console.log('Gantt data:', result);
        
        if (result.data?.project_categories) {
          setGanttData(result.data);
        }
      } catch (error) {
        console.error('Error fetching gantt data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  // 渲染甘特图
  useEffect(() => {
    if (!chartRef.current || !ganttData?.project_categories) return;

    const container = chartRef.current;
    const width = container.clientWidth || 1000;
    const height = 400;

    // 清除现有内容
    d3.select(container).selectAll('*').remove();

    // 创建SVG
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .style('background', '#f9f9f9')
      .style('border', '1px solid #e8e8e8')
      .style('border-radius', '4px');

    // 绘制标题
    svg.append('text')
      .attr('x', 20)
      .attr('y', 30)
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .attr('fill', '#333')
      .text('甘特图');

    // 绘制测试矩形
    svg.append('rect')
      .attr('x', 100)
      .attr('y', 80)
      .attr('width', 200)
      .attr('height', 40)
      .attr('fill', '#4a90e2')
      .attr('opacity', 0.7)
      .attr('rx', 4);

    // 绘制测试文本
    svg.append('text')
      .attr('x', 200)
      .attr('y', 105)
      .attr('text-anchor', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '14px')
      .text('测试任务');

    // 绘制时间轴
    svg.append('line')
      .attr('x1', 100)
      .attr('y1', 140)
      .attr('x2', width - 50)
      .attr('y2', 140)
      .attr('stroke', '#333')
      .attr('stroke-width', 2);

    // 显示数据统计
    svg.append('text')
      .attr('x', 20)
      .attr('y', 170)
      .attr('font-size', '12px')
      .attr('fill', '#666')
      .text(`项目大类数量: ${ganttData.project_categories.length}`);

    if (ganttData.project_categories.length > 0) {
      const totalProjects = ganttData.project_categories.reduce((sum: number, category: any) => {
        return sum + category.projects.length;
      }, 0);

      svg.append('text')
        .attr('x', 20)
        .attr('y', 190)
        .attr('font-size', '12px')
        .attr('fill', '#666')
        .text(`项目数量: ${totalProjects}`);
    }

    console.log('Simple gantt chart rendered successfully');

  }, [ganttData]);

  if (isLoading) {
    return <div style={{ padding: '20px' }}>加载中...</div>;
  }

  return (
    <div style={{ width: '100%', padding: '20px' }}>
      <h2>简化甘特图</h2>
      <div 
        ref={chartRef} 
        style={{ 
          width: '100%', 
          height: '400px',
          border: '1px dashed #e8e8e8',
          borderRadius: '4px',
          position: 'relative'
        }}
      >
        {!ganttData && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%', 
            color: '#999'
          }}>
            无甘特图数据
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleGanttChart;