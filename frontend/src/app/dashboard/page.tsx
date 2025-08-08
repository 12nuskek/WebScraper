"use client"

import * as React from "react"
import Link from "next/link"
import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import {
  getCount,
  listJobs,
  listRequests,
  listProxies,
  listUpcomingSchedules,
  listDueSchedules,
  getProxyStats,
  getResponseStats,
  type Job,
  type ProxyItem,
  type Schedule,
} from "@/lib/api"
import { Activity, AlertTriangle, Boxes, Clock, Gauge, ListChecks, Network, PlayCircle, XCircle } from "lucide-react"

export default function Page() {
  const [loading, setLoading] = React.useState(true)

  const [counts, setCounts] = React.useState({
    projects: 0,
    spiders: 0,
    jobs: 0,
    runningJobs: 0,
    failedJobs: 0,
    pendingRequests: 0,
  })

  const [proxyHealthPct, setProxyHealthPct] = React.useState<number>(0)
  const [unhealthyProxies, setUnhealthyProxies] = React.useState<ProxyItem[]>([])

  const [dueSchedulesCount, setDueSchedulesCount] = React.useState<number>(0)
  const [upcomingSchedules, setUpcomingSchedules] = React.useState<Schedule[]>([])

  const [recentJobs, setRecentJobs] = React.useState<Job[]>([])

  const [responseStats, setResponseStats] = React.useState<{
    total_responses: number
    successful_responses: number
    error_responses: number
    avg_latency_ms: number
    status_code_distribution: Record<string, number>
    cache_hit_rate: number
  } | null>(null)

  React.useEffect(() => {
    ;(async () => {
      try {
        const [projects, spiders, jobs] = await Promise.all([
          getCount("/projects"),
          getCount("/spiders"),
          getCount("/jobs"),
        ])

        const [runningJobsRes, failedJobsRes, pendingReqRes, proxyStatsRes, unhealthyProxiesRes, dueRes, upcomingRes, responseStatsRes, recentJobsRes] = await Promise.all([
          listJobs({ status: "running", page: 1 }),
          listJobs({ status: "failed", page: 1 }),
          listRequests({ status: "pending", page: 1 }),
          getProxyStats(),
          listProxies({ health: "unhealthy", page: 1 }),
          listDueSchedules(),
          listUpcomingSchedules({ hours: 24 }),
          getResponseStats(),
          listJobs({ page: 1 }),
        ])

        setCounts({
          projects,
          spiders,
          jobs,
          runningJobs: runningJobsRes.ok ? runningJobsRes.data!.count : 0,
          failedJobs: failedJobsRes.ok ? failedJobsRes.data!.count : 0,
          pendingRequests: pendingReqRes.ok ? pendingReqRes.data!.count : 0,
        })

        setProxyHealthPct(proxyStatsRes.ok ? Math.round(proxyStatsRes.data!.health_percentage) : 0)
        setUnhealthyProxies(unhealthyProxiesRes.ok ? unhealthyProxiesRes.data!.results.slice(0, 5) : [])

        setDueSchedulesCount(dueRes.ok ? dueRes.data!.length : 0)
        setUpcomingSchedules(upcomingRes.ok ? upcomingRes.data!.slice(0, 5) : [])

        setResponseStats(responseStatsRes.ok ? responseStatsRes.data! : null)

        if (recentJobsRes.ok) {
          const rows = [...recentJobsRes.data!.results]
          rows.sort((a, b) => {
            const ta = new Date(a.started_at ?? a.created_at ?? "").getTime()
            const tb = new Date(b.started_at ?? b.created_at ?? "").getTime()
            return tb - ta
          })
          setRecentJobs(rows.slice(0, 5))
        } else {
          setRecentJobs([])
        }
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const errorRatePct = React.useMemo(() => {
    if (!responseStats) return 0
    const total = responseStats.total_responses || 0
    if (!total) return 0
    return Math.round((responseStats.error_responses / total) * 100)
  }, [responseStats])

  const cacheHitRatePct = React.useMemo(() => {
    if (!responseStats) return 0
    return Math.round(responseStats.cache_hit_rate * 100)
  }, [responseStats])

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 data-[orientation=vertical]:h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Overview</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="ml-auto flex items-center gap-2 px-4">
            <Button asChild size="sm" variant="outline">
              <Link href="/dashboard/spiders">Manage Spiders</Link>
            </Button>
            <Button asChild size="sm" variant="outline">
              <Link href="/dashboard/requests">Manage Requests</Link>
            </Button>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* Top metrics */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <MetricCard title="Projects" icon={<Boxes className="h-4 w-4" />} value={counts.projects} loading={loading} />
            <MetricCard title="Spiders" icon={<Activity className="h-4 w-4" />} value={counts.spiders} loading={loading} />
            <MetricCard title="Jobs" icon={<ListChecks className="h-4 w-4" />} value={counts.jobs} loading={loading} />
            <MetricCard title="Pending Requests" icon={<Clock className="h-4 w-4" />} value={counts.pendingRequests} loading={loading} />
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2"><Gauge className="h-4 w-4" /> Proxy Health</CardTitle>
                <Badge variant={proxyHealthPct >= 80 ? "default" : proxyHealthPct >= 50 ? "secondary" : "destructive"}>{proxyHealthPct}%</Badge>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-3 w-full" />
                ) : (
                  <div className="space-y-2">
                    <Progress value={proxyHealthPct} />
                    <p className="text-sm text-muted-foreground">Healthy proxies across the fleet</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2"><PlayCircle className="h-4 w-4" /> Jobs Status</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Running</div>
                  {loading ? <Skeleton className="h-7 w-12" /> : <div className="text-2xl font-semibold">{counts.runningJobs}</div>}
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Failed</div>
                  {loading ? <Skeleton className="h-7 w-12" /> : <div className="text-2xl font-semibold">{counts.failedJobs}</div>}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2"><AlertTriangle className="h-4 w-4" /> Schedules</CardTitle>
                <Badge variant={dueSchedulesCount > 0 ? "destructive" : "secondary"}>{dueSchedulesCount} due</Badge>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-7 w-24" />
                ) : upcomingSchedules.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No upcoming runs in next 24h</p>
                ) : (
                  <div className="space-y-3">
                    {upcomingSchedules.map((s) => (
                      <div key={s.id} className="flex items-center justify-between text-sm">
                        <span className="truncate" title={s.cron_expr}>{s.cron_expr}</span>
                        <span className="text-muted-foreground">{formatDateTime(s.next_run_at)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Lower grid: Recent Jobs, Unhealthy Proxies, Response Stats */}
          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Recent Jobs</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-8 w-full" />
                  </div>
                ) : recentJobs.length === 0 ? (
                  <div className="py-6 text-center text-muted-foreground">No jobs yet.</div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Spider</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Duration</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recentJobs.map((j) => (
                        <TableRow key={j.id}>
                          <TableCell>#{j.id}</TableCell>
                          <TableCell>{j.spider}</TableCell>
                          <TableCell>
                            <Badge variant={j.status === "failed" ? "destructive" : j.status === "running" ? "secondary" : "default"} className="capitalize">
                              {j.status}
                            </Badge>
                          </TableCell>
                          <TableCell>{j.started_at ? formatDateTime(j.started_at) : "—"}</TableCell>
                          <TableCell>{formatDuration(j.duration)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="flex items-center gap-2"><Network className="h-4 w-4" /> Unhealthy Proxies</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-8 w-full" />
                  </div>
                ) : unhealthyProxies.length === 0 ? (
                  <div className="py-6 text-center text-muted-foreground">All good!</div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Proxy</TableHead>
                        <TableHead className="text-right">Fails</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {unhealthyProxies.map((p) => (
                        <TableRow key={p.id}>
                          <TableCell>#{p.id}</TableCell>
                          <TableCell className="truncate max-w-[26ch]" title={p.masked_uri}>{p.masked_uri}</TableCell>
                          <TableCell className="text-right">{p.fail_count}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Responses Overview</CardTitle>
            </CardHeader>
            <CardContent>
              {loading || !responseStats ? (
                <div className="space-y-2">
                  <Skeleton className="h-6 w-40" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-6 w-64" />
                </div>
              ) : (
                <div className="grid gap-6 md:grid-cols-3">
                  <div>
                    <div className="text-sm text-muted-foreground">Total</div>
                    <div className="text-2xl font-semibold">{responseStats.total_responses}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Error Rate</div>
                    <div className="text-2xl font-semibold flex items-center gap-2">
                      {errorRatePct}% {errorRatePct > 0 ? <XCircle className="h-4 w-4 text-destructive" /> : null}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Avg Latency</div>
                    <div className="text-2xl font-semibold">{Math.round(responseStats.avg_latency_ms)} ms</div>
                  </div>
                  <div className="md:col-span-3">
                    <div className="mb-2 flex items-center justify-between text-sm text-muted-foreground">
                      <span>Cache Hit Rate</span>
                      <span>{cacheHitRatePct}%</span>
                    </div>
                    <Progress value={cacheHitRatePct} />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

function MetricCard({ title, value, loading, icon }: { title: string; value: number; loading: boolean; icon?: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-7 w-16" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
      </CardContent>
    </Card>
  )
}

function formatDateTime(value?: string | null) {
  if (!value) return "—"
  try {
    return new Date(value).toLocaleString()
  } catch {
    return String(value)
  }
}

function formatDuration(value?: number | null) {
  if (!value && value !== 0) return "—"
  const seconds = Math.max(0, Math.round(value))
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins === 0) return `${secs}s`
  return `${mins}m ${secs}s`
}
