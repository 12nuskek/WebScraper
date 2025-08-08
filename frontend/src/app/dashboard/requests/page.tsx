"use client"

import * as React from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { apiFetch } from "@/lib/api"
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/data-table"
import { DataTableColumnHeader } from "@/components/data-table-column-header"
import { Pencil, Trash2, Play, Check, AlertTriangle, RotateCcw } from "lucide-react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type RequestItem = {
  id: number
  job: number
  url: string
  method: string
  priority: number
  retries: number
  max_retries: number
  status: string
  scheduled_at: string
}

type Paginated<T> = { count: number; results: T[] }

export default function RequestsPage() {
  const [data, setData] = React.useState<Paginated<RequestItem>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false)
  const [createJobId, setCreateJobId] = React.useState("")
  const [createUrl, setCreateUrl] = React.useState("")
  const [createMethod, setCreateMethod] = React.useState("GET")
  const [creating, setCreating] = React.useState(false)
  const [editDialogOpen, setEditDialogOpen] = React.useState(false)
  const [editRequest, setEditRequest] = React.useState<RequestItem | null>(null)
  const [editPriority, setEditPriority] = React.useState<string>("")
  const [deleteTarget, setDeleteTarget] = React.useState<RequestItem | null>(null)

  async function refresh() {
    const res = await apiFetch<Paginated<RequestItem>>("/requests/")
    if (res.ok && res.data) setData(res.data)
  }

  React.useEffect(() => {
    ;(async () => {
      await refresh()
      setLoading(false)
    })()
  }, [])

  async function handleCreateSubmit(e: React.FormEvent) {
    e.preventDefault()
    const job = Number(createJobId)
    if (!job || Number.isNaN(job) || !createUrl.trim()) return
    setCreating(true)
    const res = await apiFetch<RequestItem>("/requests/", {
      method: "POST",
      body: JSON.stringify({ job, url: createUrl.trim(), method: createMethod }),
    })
    setCreating(false)
    if (res.ok) {
      setCreateDialogOpen(false)
      setCreateJobId("")
      setCreateUrl("")
      setCreateMethod("GET")
      await refresh()
    }
  }

  function openEdit(r: RequestItem) {
    setEditRequest(r)
    setEditPriority(String(r.priority))
    setEditDialogOpen(true)
  }

  async function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!editRequest) return
    const priority = Number(editPriority)
    const res = await apiFetch<RequestItem>(`/requests/${editRequest.id}/`, { method: "PATCH", body: JSON.stringify({ priority }) })
    if (res.ok) {
      setEditDialogOpen(false)
      setEditRequest(null)
      await refresh()
    }
  }

  async function handleDelete(id: number) {
    const res = await apiFetch(`/requests/${id}/`, { method: "DELETE" })
    if (res.ok) await refresh()
  }

  async function handleInProgress(id: number) {
    const res = await apiFetch(`/requests/${id}/mark_in_progress/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  async function handleDone(id: number) {
    const res = await apiFetch(`/requests/${id}/mark_done/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  async function handleError(id: number) {
    const increment = window.confirm("Increment retry count? OK=yes / Cancel=no")
    const res = await apiFetch(`/requests/${id}/mark_error/`, { method: "POST", body: JSON.stringify({ increment_retry: increment }) })
    if (res.ok) await refresh()
  }

  async function handleRetry(id: number) {
    const res = await apiFetch(`/requests/${id}/retry/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  const columns: ColumnDef<RequestItem>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    { accessorKey: "job", header: ({ column }) => <DataTableColumnHeader column={column} title="Job" /> },
    { accessorKey: "method", header: ({ column }) => <DataTableColumnHeader column={column} title="Method" /> },
    {
      accessorKey: "url",
      header: ({ column }) => <DataTableColumnHeader column={column} title="URL" />,
      cell: ({ row }) => (
        <span className="max-w-[40ch] truncate inline-block" title={row.original.url}>{row.original.url}</span>
      ),
    },
    { accessorKey: "priority", header: ({ column }) => <DataTableColumnHeader column={column} title="Priority" /> },
    {
      id: "retries",
      header: "Retries",
      cell: ({ row }) => `${row.original.retries}/${row.original.max_retries}`,
    },
    { accessorKey: "status", header: ({ column }) => <DataTableColumnHeader column={column} title="Status" /> , cell: ({ row }) => <span className="capitalize">{row.original.status}</span>},
    { accessorKey: "scheduled_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Scheduled" />, cell: ({ row }) => new Date(row.original.scheduled_at).toLocaleString() },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          <Button size="icon" variant="outline" onClick={() => openEdit(row.original)} title="Edit" aria-label="Edit">
            <Pencil />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleInProgress(row.original.id)} title="In Progress" aria-label="In Progress">
            <Play />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleDone(row.original.id)} title="Done" aria-label="Done">
            <Check />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleError(row.original.id)} title="Error" aria-label="Error">
            <AlertTriangle />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleRetry(row.original.id)} title="Retry" aria-label="Retry">
            <RotateCcw />
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
                  <BreadcrumbPage>Requests</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Requests ({data.count})</CardTitle>
                <CardDescription>Queue and manage crawl requests.</CardDescription>
              </div>
              <Button size="sm" onClick={() => setCreateDialogOpen(true)}>New Request</Button>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-9 w-56" />
                  <div className="overflow-hidden rounded-md border">
                    <div className="grid grid-cols-7 gap-2 border-b p-3">
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-7 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-36" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-16" />
                        <Skeleton className="h-8 w-8 justify-self-end rounded" />
                      </div>
                    ))}
                  </div>
                </div>
              ) : data.results.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">📬</div>
                  <div className="text-lg font-medium">No requests</div>
                  <div className="text-sm text-muted-foreground">Create a request to enqueue a URL for crawling.</div>
                  <div className="mt-4">
                    <Button onClick={() => setCreateDialogOpen(true)}>New Request</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="url" filterPlaceholder="Filter URLs..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>New Request</DialogTitle>
              </DialogHeader>
              <form id="create-request-form" onSubmit={handleCreateSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="req-job">Job ID</Label>
                  <Input id="req-job" inputMode="numeric" value={createJobId} onChange={(e) => setCreateJobId(e.target.value.replace(/[^0-9]/g, ""))} required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="req-url">URL</Label>
                  <Input id="req-url" type="url" value={createUrl} onChange={(e) => setCreateUrl(e.target.value)} placeholder="https://example.com" required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="req-method">Method</Label>
                  <Select value={createMethod} onValueChange={setCreateMethod}>
                    <SelectTrigger id="req-method">
                      <SelectValue placeholder="Select method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="POST">POST</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="create-request-form" disabled={creating}>{creating ? "Creating…" : "Create"}</Button>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Request</DialogTitle>
              </DialogHeader>
              <form id="edit-request-form" onSubmit={handleEditSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="req-priority">Priority</Label>
                  <Input id="req-priority" inputMode="numeric" value={editPriority} onChange={(e) => setEditPriority(e.target.value.replace(/[^0-9]/g, ""))} />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="edit-request-form">Save</Button>
                  <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete request?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel onClick={() => setDeleteTarget(null)}>Cancel</AlertDialogCancel>
                <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={async () => {
                  if (deleteTarget) {
                    const id = deleteTarget.id
                    setDeleteTarget(null)
                    await handleDelete(id)
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


