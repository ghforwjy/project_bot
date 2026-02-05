// 甘特图数据结构类型定义

// 任务数据结构
export interface GanttTask {
  id: number;
  name: string;
  description: string;
  assignee: string;
  progress: number;
  status: 'pending' | 'active' | 'completed' | 'delayed' | 'cancelled';
  deliverable: string;
  planned_start_date: string;
  planned_end_date: string;
  actual_start_date: string;
  actual_end_date: string;
  priority: number;
  dependencies: string[];
  custom_class?: string;
  phase_id?: string;
  project_id?: number; // 项目ID，用于任务点击时定位项目
}

// 项目阶段数据结构
export interface ProjectPhase {
  id: string;
  name: string;
  start: string;
  end: string;
  description: string;
}

// 项目数据结构
export interface ProjectGantt {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  progress: number;
  tasks: GanttTask[];
  phases: ProjectPhase[];
  category_id?: number;
  category_name?: string;
  color?: string; // 项目颜色，基于大类主题色
}

// 项目大类数据结构
export interface ProjectCategoryGantt {
  id: number;
  name: string;
  projects: ProjectGantt[];
  color: string; // 大类主题色
  expanded?: boolean; // 展开状态
}

// 完整的甘特图数据结构
export interface AllGanttData {
  project_categories: ProjectCategoryGantt[];
}

// 单个项目的甘特图数据
export interface GanttData {
  project_name: string;
  project_description?: string;
  start_date: string;
  end_date: string;
  tasks: GanttTask[];
}

// 甘特图组件属性
export interface GanttChartProps {
  projectId?: number | null;
  className?: string;
  height?: number;
  width?: number;
  onTaskClick?: (task: GanttTask) => void;
  onProjectClick?: (project: ProjectGantt) => void;
  onCategoryClick?: (category: ProjectCategoryGantt) => void;
}

// 甘特图控制栏属性
export interface GanttControlBarProps {
  viewMode: 'single' | 'all';
  onViewModeChange: (mode: 'single' | 'all') => void;
  selectedCategory: number | null;
  onCategoryChange: (categoryId: number | null) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  categories: ProjectCategoryGantt[];
}

// 甘特图图例属性
export interface GanttLegendProps {
  className?: string;
}

// 甘特图折叠/展开状态
export interface ExpandedStates {
  categories: Record<number, boolean>;
  projects: Record<string, boolean>;
}

// 甘特图配置选项
export interface GanttOptions {
  showTodayLine: boolean;
  showLegend: boolean;
  enableZoom: boolean;
  enableDrag: boolean;
  enableTooltip: boolean;
  enableSearch: boolean;
  enableFilter: boolean;
  animationDuration: number;
}

// 甘特图颜色配置
export interface GanttColorConfig {
  categoryColors: string[];
  taskStatusColors: Record<string, string>;
  progressColors: {
    low: string;
    medium: string;
    high: string;
  };
}

// 甘特图时间范围
export interface GanttTimeRange {
  min: number;
  max: number;
  today: number;
}

// 甘特图渲染数据
export interface GanttRenderData {
  categories: ProjectCategoryGantt[];
  timeRange: GanttTimeRange;
  expandedStates: ExpandedStates;
  searchQuery: string;
  selectedCategory: number | null;
}
