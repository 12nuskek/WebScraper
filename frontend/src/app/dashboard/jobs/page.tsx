"use client"

import * as React from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useSearchParams, useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/data-table"
import { DataTableColumnHeader } from "@/components/data-table-column-header"
import { Pencil, Trash2 } from "lucide-react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type Job = {
  id: number
  spider: number
  status: string
  started_at: string | null
  finished_at: string | null
  duration: number | null
  created_at: string
}

type Paginated<T> = { count: number; results: T[] }

export default function JobsPage() {
  const [data, setData] = React.useState<Paginated<Job>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [statusFilter, setStatusFilter] = React.useState<string>("")
  const [spiderFilter, setSpiderFilter] = React.useState<string>("")
  const [creating, setCreating] = React.useState(false)
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false)
  const [createSpiderId, setCreateSpiderId] = React.useState<string>("")
  const [editDialogOpen, setEditDialogOpen] = React.useState(false)
  const [editJob, setEditJob] = React.useState<Job | null>(null)
  const [editStatus, setEditStatus] = React.useState<string>("")
  const [deleteTarget, setDeleteTarget] = React.useState<Job | null>(null)
  const searchParams = useSearchParams()
  const router = useRouter()
  const { toast } = useToast()

  async function refresh(params?: { status?: string; spider?: string }) {
    const s = params?.status ?? statusFilter
    const sp = params?.spider ?? spiderFilter
    const usp = new URLSearchParams()
    if (s) usp.set("status", s)
    if (sp) usp.set("spider", sp)
    const qs = usp.toString()
    const res = await apiFetch<Paginated<Job>>(`/jobs/${qs ? `?${qs}` : ""}`)
    if (res.ok && res.data) setData(res.data)
  }

  React.useEffect(() => {
    ;(async () => {
      const initStatus = searchParams.get("status") || ""
      const initSpider = searchParams.get("spider") || ""
      setStatusFilter(initStatus)
      setSpiderFilter(initSpider)
      await refresh({ status: initStatus, spider: initSpider })
      setLoading(false)
    })()
  }, [])

  async function handleCreateSubmit(e: React.FormEvent) {
    e.preventDefault()
    const spider = Number(createSpiderId)
    if (!spider || Number.isNaN(spider)) return
    setCreating(true)
    const res = await apiFetch<Job>("/jobs/", { method: "POST", body: JSON.stringify({ spider }) })
    setCreating(false)
    if (res.ok) {
      toast({ title: "Job created", description: `Job #${res.data!.id} for spider #${spider}` })
      setCreateDialogOpen(false)
      setCreateSpiderId("")
      await refresh()
    } else {
      toast({ title: "Failed to create job", variant: "destructive" as any })
    }
  }

  function openEdit(j: Job) {
    setEditJob(j)
    setEditStatus(j.status)
    setEditDialogOpen(true)
  }

  async function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!editJob) return
    const res = await apiFetch<Job>(`/jobs/${editJob.id}/`, { method: "PATCH", body: JSON.stringify({ status: editStatus }) })
    if (res.ok) {
      toast({ title: "Job updated" })
      setEditDialogOpen(false)
      setEditJob(null)
      await refresh()
    }
  }

  async function handleDelete(id: number) {
    const res = await apiFetch(`/jobs/${id}/`, { method: "DELETE" })
    if (res.ok) {
      toast({ title: "Job deleted" })
      await refresh()
    }
  }

  const columns: ColumnDef<Job>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    { accessorKey: "spider", header: ({ column }) => <DataTableColumnHeader column={column} title="Spider" /> },
    { accessorKey: "status", header: ({ column }) => <DataTableColumnHeader column={column} title="Status" />, cell: ({ row }) => <Badge className="capitalize" variant={row.original.status === "failed" ? "destructive" : row.original.status === "running" ? "secondary" : "default"}>{row.original.status}</Badge> },
    { accessorKey: "started_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Started" />, cell: ({ row }) => row.original.started_at ? new Date(row.original.started_at).toLocaleString() : "-" },
    { accessorKey: "finished_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Finished" />, cell: ({ row }) => row.original.finished_at ? new Date(row.original.finished_at).toLocaleString() : "-" },
    { accessorKey: "duration", header: ({ column }) => <DataTableColumnHeader column={column} title="Duration (s)" />, cell: ({ row }) => row.original.duration ?? "-" },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button size="icon" variant="outline" onClick={() => openEdit(row.original)} title="Edit" aria-label="Edit">
            <Pencil />
          </Button>
          <Button size="icon" variant="destructive" onClick={() => setDeleteTarget(row.original)} title="Delete" aria-label="Delete">
            <Trash2 />
          </Button>
        </div>
      ),
      enableSorting: false,
      enableHiding: false,
    },
  ]

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
                  <BreadcrumbPage>Jobs</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Jobs ({data.count})</CardTitle>
                <CardDescription>Track and manage spider executions.</CardDescription>
              </div>
              <Button size="sm" onClick={() => setCreateDialogOpen(true)} disabled={creating}>{creating ? "Creating…" : "New Job"}</Button>
            </CardHeader>
            <CardContent>
              <div className="mb-4 grid gap-4 md:grid-cols-3">
                <div className="grid gap-2">
                  <Label htmlFor="filter-status">Status</Label>
                  <Select
                    value={statusFilter || "__all__"}
                    onValueChange={async (v) => {
                      const newStatus = v === "__all__" ? "" : v
                      setStatusFilter(newStatus)
                      const usp = new URLSearchParams()
                      if (newStatus) usp.set("status", newStatus)
                      if (spiderFilter) usp.set("spider", spiderFilter)
                      router.push(`/dashboard/jobs${usp.toString() ? `?${usp.toString()}` : ""}`)
                      await refresh({ status: newStatus })
                    }}
                  >
                    <SelectTrigger id="filter-status">
                      <SelectValue placeholder="All statuses" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="__all__">All</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="running">Running</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="failed">Failed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="filter-spider">Spider ID</Label>
                  <Input
                    id="filter-spider"
                    inputMode="numeric"
                    value={spiderFilter}
                    onChange={(e) => setSpiderFilter(e.target.value.replace(/[^0-9]/g, ""))}
                    onBlur={async () => {
                      const usp = new URLSearchParams()
                      if (statusFilter) usp.set("status", statusFilter)
                      if (spiderFilter) usp.set("spider", spiderFilter)
                      router.push(`/dashboard/jobs${usp.toString() ? `?${usp.toString()}` : ""}`)
                      await refresh()
                    }}
                    placeholder="e.g. 12"
                  />
                </div>
              </div>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-9 w-56" />
                  <div className="overflow-hidden rounded-md border">
                    <div className="grid grid-cols-6 gap-2 border-b p-3">
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-6 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-8 w-8 justify-self-end rounded" />
                      </div>
                    ))}
                  </div>
                </div>
              ) : data.results.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">🧰</div>
                  <div className="text-lg font-medium">No jobs found</div>
                  <div className="text-sm text-muted-foreground">Create a job to start running spiders.</div>
                  <div className="mt-4">
                    <Button onClick={() => setCreateDialogOpen(true)}>New Job</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="status" filterPlaceholder="Filter status..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>New Job</DialogTitle>
              </DialogHeader>
              <form id="create-job-form" onSubmit={handleCreateSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="job-spider">Spider ID</Label>
                  <Input id="job-spider" inputMode="numeric" value={createSpiderId} onChange={(e) => setCreateSpiderId(e.target.value.replace(/[^0-9]/g, ""))} placeholder="e.g. 12" required />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="create-job-form" disabled={creating}>{creating ? "Creating…" : "Create"}</Button>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Job</DialogTitle>
              </DialogHeader>
              <form id="edit-job-form" onSubmit={handleEditSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="job-status">Status</Label>
                  <Select value={editStatus} onValueChange={setEditStatus}>
                    <SelectTrigger id="job-status">
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="running">Running</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="failed">Failed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="edit-job-form">Save</Button>
                  <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete job?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. Job and related data may be affected.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel onClick={() => setDeleteTarget(null)}>Cancel</AlertDialogCancel>
                <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={async () => {
                  if (deleteTarget) {
                    const target = deleteTarget
                    setDeleteTarget(null)
                    await handleDelete(target.id)
                  }
                }}>Delete</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}


