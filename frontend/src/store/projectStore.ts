import { create } from 'zustand'

interface Project {
  id: number
  name: string
  description: string
  progress: number
  status: string
  start_date: string
  end_date: string
}

interface Task {
  id: number
  project_id: number
  name: string
  assignee: string
  progress: number
  status: string
}

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  tasks: Task[]
  selectedProjectId: number | null
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  setTasks: (tasks: Task[]) => void
  setSelectedProjectId: (id: number | null) => void
  updateProjectProgress: (projectId: number, progress: number) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  tasks: [],
  selectedProjectId: null,
  
  setProjects: (projects) => set({ projects }),
  
  setCurrentProject: (project) => set({ currentProject: project }),
  
  setTasks: (tasks) => set({ tasks }),
  
  setSelectedProjectId: (id) => set({ selectedProjectId: id }),
  
  updateProjectProgress: (projectId, progress) => set((state) => ({
    projects: state.projects.map(p =>
      p.id === projectId ? { ...p, progress } : p
    )
  }))
}))
