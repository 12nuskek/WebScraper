// User and Authentication Types
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  created_at: string
  updated_at: string
}

export interface UserProfile {
  id: string
  user: User
  bio?: string
  avatar?: string
  preferences: Record<string, any>
}

// Project Types
export interface Project {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  user: string
  is_active: boolean
  settings: Record<string, any>
  spider_count: number
  job_count: number
  last_run?: string
}

// Spider Types
export interface Spider {
  id: string
  name: string
  description: string
  project: string
  start_urls: string[]
  allowed_domains: string[]
  custom_settings: Record<string, any>
  created_at: string
  updated_at: string
  is_active: boolean
  success_rate: number
  total_requests: number
}

// Job Types
export interface Job {
  id: string
  name: string
  spider: string
  project: string
  status: 'queued' | 'running' | 'done' | 'failed' | 'cancelled'
  priority: number
  created_at: string
  started_at?: string
  finished_at?: string
  result_file?: string
  error_message?: string
  progress: number
  items_scraped: number
}

// Request Types
export interface Request {
  id: string
  job: string
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers: Record<string, string>
  data?: string
  status: 'pending' | 'in_progress' | 'done' | 'error'
  priority: number
  retry_count: number
  max_retries: number
  created_at: string
  updated_at: string
}

// Response Types
export interface Response {
  id: string
  request: string
  status_code: number
  headers: Record<string, string>
  body: string
  size: number
  response_time: number
  created_at: string
  is_success: boolean
}

// Schedule Types
export interface Schedule {
  id: string
  name: string
  spider: string
  cron_expression: string
  is_enabled: boolean
  next_run: string
  last_run?: string
  created_at: string
  updated_at: string
  run_count: number
}

// Session Types
export interface Session {
  id: string
  name: string
  cookies: Record<string, any>
  headers: Record<string, string>
  user_agent?: string
  proxy?: string
  created_at: string
  is_active: boolean
}

// Proxy Types
export interface Proxy {
  id: string
  name: string
  host: string
  port: number
  username?: string
  password?: string
  proxy_type: 'http' | 'https' | 'socks4' | 'socks5'
  is_active: boolean
  success_rate: number
  last_used?: string
}

// Statistics Types
export interface Stats {
  total_projects: number
  total_spiders: number
  total_jobs: number
  active_jobs: number
  successful_requests: number
  failed_requests: number
  success_rate: number
  data_points_collected: number
}