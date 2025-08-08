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
import { Pencil, Clock, Trash2 } from "lucide-react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type SessionItem = {
  id: number
  spider: number
  spider_name?: string
  label: string | null
  valid_until: string | null
  is_expired?: boolean
  updated_at: string
}

type Paginated<T> = { count: number; results: T[] }

export default function SessionsPage() {
  const [data, setData] = React.useState<Paginated<SessionItem>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false)
  const [createSpiderId, setCreateSpiderId] = React.useState("")
  const [createLabel, setCreateLabel] = React.useState("")
  const [creating, setCreating] = React.useState(false)
  const [editDialogOpen, setEditDialogOpen] = React.useState(false)
  const [editSession, setEditSession] = React.useState<SessionItem | null>(null)
  const [editLabel, setEditLabel] = React.useState("")
  const [extendDialogOpen, setExtendDialogOpen] = React.useState(false)
  const [extendTargetId, setExtendTargetId] = React.useState<number | null>(null)
  const [extendHours, setExtendHours] = React.useState("24")
  const [deleteTarget, setDeleteTarget] = React.useState<SessionItem | null>(null)

  async function refresh() {
    const res = await apiFetch<Paginated<SessionItem>>("/sessions/")
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
    const spider = Number(createSpiderId)
    if (!spider || Number.isNaN(spider)) return
    setCreating(true)
    const res = await apiFetch<SessionItem>("/sessions/", { method: "POST", body: JSON.stringify({ spider, label: createLabel || undefined }) })
    setCreating(false)
    if (res.ok) {
      setCreateDialogOpen(false)
      setCreateSpiderId("")
      setCreateLabel("")
      await refresh()
    }
  }

  function openEdit(s: SessionItem) {
    setEditSession(s)
    setEditLabel(s.label ?? "")
    setEditDialogOpen(true)
  }

  async function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!editSession) return
    const res = await apiFetch<SessionItem>(`/sessions/${editSession.id}/`, { method: "PATCH", body: JSON.stringify({ label: editLabel || null }) })
    if (res.ok) {
      setEditDialogOpen(false)
      setEditSession(null)
      await refresh()
    }
  }

  async function handleDelete(id: number) {
    const res = await apiFetch(`/sessions/${id}/`, { method: "DELETE" })
    if (res.ok) await refresh()
  }

  function openExtend(id: number) {
    setExtendTargetId(id)
    setExtendHours("24")
    setExtendDialogOpen(true)
  }

  async function handleExtendSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (extendTargetId == null) return
    const hours = Number(extendHours)
    if (!hours || Number.isNaN(hours)) return
    const res = await apiFetch(`/sessions/${extendTargetId}/extend_validity/`, { method: "POST", body: JSON.stringify({ hours }) })
    if (res.ok) {
      setExtendDialogOpen(false)
      setExtendTargetId(null)
      await refresh()
    }
  }

  async function handleCleanupExpired() {
    const res = await apiFetch(`/sessions/cleanup_expired/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  const columns: ColumnDef<SessionItem>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    { accessorKey: "spider_name", header: ({ column }) => <DataTableColumnHeader column={column} title="Spider" />, cell: ({ row }) => row.original.spider_name ?? row.original.spider },
    { accessorKey: "label", header: ({ column }) => <DataTableColumnHeader column={column} title="Label" />, cell: ({ row }) => row.original.label ?? "default" },
    { accessorKey: "valid_until", header: ({ column }) => <DataTableColumnHeader column={column} title="Valid Until" />, cell: ({ row }) => row.original.valid_until ? new Date(row.original.valid_until).toLocaleString() : "-" },
    { accessorKey: "is_expired", header: ({ column }) => <DataTableColumnHeader column={column} title="Expired" />, cell: ({ row }) => (row.original.is_expired ? "Yes" : "No") },
    { accessorKey: "updated_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Updated" />, cell: ({ row }) => new Date(row.original.updated_at).toLocaleString() },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          <Button size="icon" variant="outline" onClick={() => openEdit(row.original)} title="Edit" aria-label="Edit">
            <Pencil />
          </Button>
          <Button size="icon" variant="outline" onClick={() => openExtend(row.original.id)} title="Extend" aria-label="Extend">
            <Clock />
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
                  <BreadcrumbPage>Sessions</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Sessions ({data.count})</CardTitle>
                <CardDescription>Control and extend spider sessions.</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => setCreateDialogOpen(true)}>New Session</Button>
                <Button size="sm" variant="outline" onClick={handleCleanupExpired}>Cleanup Expired</Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-9 w-56" />
                  <div className="overflow-hidden rounded-md border">
                    <div className="grid grid-cols-7 gap-2 border-b p-3">
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-7 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-8 w-8 justify-self-end rounded" />
                      </div>
                    ))}
                  </div>
                </div>
              ) : data.results.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">🔐</div>
                  <div className="text-lg font-medium">No sessions</div>
                  <div className="text-sm text-muted-foreground">Create a session to maintain state for spiders.</div>
                  <div className="mt-4">
                    <Button onClick={() => setCreateDialogOpen(true)}>New Session</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="label" filterPlaceholder="Filter labels..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>New Session</DialogTitle>
              </DialogHeader>
              <form id="create-session-form" onSubmit={handleCreateSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="ses-spider">Spider ID</Label>
                  <Input id="ses-spider" inputMode="numeric" value={createSpiderId} onChange={(e) => setCreateSpiderId(e.target.value.replace(/[^0-9]/g, ""))} required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="ses-label">Label (optional)</Label>
                  <Input id="ses-label" value={createLabel} onChange={(e) => setCreateLabel(e.target.value)} />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="create-session-form" disabled={creating}>{creating ? "Creating…" : "Create"}</Button>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Session</DialogTitle>
              </DialogHeader>
              <form id="edit-session-form" onSubmit={handleEditSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="ses-edit-label">Label</Label>
                  <Input id="ses-edit-label" value={editLabel} onChange={(e) => setEditLabel(e.target.value)} />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="edit-session-form">Save</Button>
                  <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={extendDialogOpen} onOpenChange={setExtendDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Extend Session</DialogTitle>
              </DialogHeader>
              <form id="extend-session-form" onSubmit={handleExtendSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="ses-extend-hours">Hours</Label>
                  <Input id="ses-extend-hours" inputMode="numeric" value={extendHours} onChange={(e) => setExtendHours(e.target.value.replace(/[^0-9]/g, ""))} />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="extend-session-form">Save</Button>
                  <Button type="button" variant="outline" onClick={() => setExtendDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete session?</AlertDialogTitle>
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


