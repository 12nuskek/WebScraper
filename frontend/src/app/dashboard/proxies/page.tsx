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
import { Power, Check, XOctagon, RotateCcw, Trash2 } from "lucide-react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type ProxyItem = {
  id: number
  masked_uri: string
  is_active: boolean
  last_ok_at: string | null
  fail_count: number
  is_healthy: boolean
  success_rate: number | null
  updated_at: string
}

type Paginated<T> = { count: number; results: T[] }

export default function ProxiesPage() {
  const [data, setData] = React.useState<Paginated<ProxyItem>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false)
  const [createUri, setCreateUri] = React.useState("")
  const [creating, setCreating] = React.useState(false)
  const [failureDialogOpen, setFailureDialogOpen] = React.useState(false)
  const [failureTargetId, setFailureTargetId] = React.useState<number | null>(null)
  const [failureReason, setFailureReason] = React.useState("")
  const [deleteTarget, setDeleteTarget] = React.useState<ProxyItem | null>(null)

  async function refresh() {
    const res = await apiFetch<Paginated<ProxyItem>>("/proxies/")
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
    if (!createUri.trim()) return
    setCreating(true)
    const res = await apiFetch<ProxyItem>("/proxies/", { method: "POST", body: JSON.stringify({ uri: createUri.trim() }) })
    setCreating(false)
    if (res.ok) {
      setCreateDialogOpen(false)
      setCreateUri("")
      await refresh()
    }
  }

  async function handleToggleActive(p: ProxyItem) {
    const res = await apiFetch<ProxyItem>(`/proxies/${p.id}/`, { method: "PATCH", body: JSON.stringify({ is_active: !p.is_active }) })
    if (res.ok) await refresh()
  }

  async function handleDelete(id: number) {
    const res = await apiFetch(`/proxies/${id}/`, { method: "DELETE" })
    if (res.ok) await refresh()
  }

  async function handleMarkSuccess(id: number) {
    const res = await apiFetch(`/proxies/${id}/mark_success/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  function openFailureDialog(id: number) {
    setFailureTargetId(id)
    setFailureReason("")
    setFailureDialogOpen(true)
  }

  async function handleMarkFailureSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (failureTargetId == null) return
    const res = await apiFetch(`/proxies/${failureTargetId}/mark_failure/`, { method: "POST", body: JSON.stringify({ error_message: failureReason || undefined }) })
    if (res.ok) {
      setFailureDialogOpen(false)
      setFailureTargetId(null)
      setFailureReason("")
      await refresh()
    }
  }

  async function handleResetStats(id: number) {
    const res = await apiFetch(`/proxies/${id}/reset_stats/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  const columns: ColumnDef<ProxyItem>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    { accessorKey: "masked_uri", header: ({ column }) => <DataTableColumnHeader column={column} title="URI" />, cell: ({ row }) => <span className="font-mono">{row.original.masked_uri}</span> },
    { accessorKey: "is_active", header: ({ column }) => <DataTableColumnHeader column={column} title="Active" />, cell: ({ row }) => (row.original.is_active ? "Yes" : "No") },
    { accessorKey: "is_healthy", header: ({ column }) => <DataTableColumnHeader column={column} title="Healthy" />, cell: ({ row }) => (row.original.is_healthy ? "Yes" : "No") },
    { accessorKey: "fail_count", header: ({ column }) => <DataTableColumnHeader column={column} title="Fail Count" /> },
    { accessorKey: "success_rate", header: ({ column }) => <DataTableColumnHeader column={column} title="Success %" />, cell: ({ row }) => (row.original.success_rate != null ? Math.round(row.original.success_rate) : "-") },
    { accessorKey: "last_ok_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Last OK" />, cell: ({ row }) => (row.original.last_ok_at ? new Date(row.original.last_ok_at).toLocaleString() : "-") },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          <Button size="icon" variant="outline" onClick={() => handleToggleActive(row.original)} title={row.original.is_active ? "Deactivate" : "Activate"} aria-label={row.original.is_active ? "Deactivate" : "Activate"}>
            <Power />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleMarkSuccess(row.original.id)} title="Mark Success" aria-label="Mark Success">
            <Check />
          </Button>
          <Button size="icon" variant="outline" onClick={() => openFailureDialog(row.original.id)} title="Mark Failure" aria-label="Mark Failure">
            <XOctagon />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleResetStats(row.original.id)} title="Reset Stats" aria-label="Reset Stats">
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
                  <BreadcrumbPage>Proxies</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Proxies ({data.count})</CardTitle>
                <CardDescription>Manage and monitor proxy health.</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => setCreateDialogOpen(true)}>Add Proxy</Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-9 w-56" />
                  <div className="overflow-hidden rounded-md border">
                    <div className="grid grid-cols-7 gap-2 border-b p-3">
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-7 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-36" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-16" />
                        <Skeleton className="h-8 w-8 justify-self-end rounded" />
                      </div>
                    ))}
                  </div>
                </div>
              ) : data.results.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">🛰️</div>
                  <div className="text-lg font-medium">No proxies</div>
                  <div className="text-sm text-muted-foreground">Add a proxy to start routing requests.</div>
                  <div className="mt-4">
                    <Button onClick={() => setCreateDialogOpen(true)}>Add Proxy</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="masked_uri" filterPlaceholder="Filter URIs..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Proxy</DialogTitle>
              </DialogHeader>
              <form id="create-proxy-form" onSubmit={handleCreateSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="proxy-uri">Proxy URI</Label>
                  <Input id="proxy-uri" value={createUri} onChange={(e) => setCreateUri(e.target.value)} placeholder="http://user:pass@host:port" required />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="create-proxy-form" disabled={creating}>{creating ? "Adding…" : "Add"}</Button>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Dialog open={failureDialogOpen} onOpenChange={setFailureDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Mark Failure</DialogTitle>
              </DialogHeader>
              <form id="failure-form" onSubmit={handleMarkFailureSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="failure-reason">Reason (optional)</Label>
                  <Input id="failure-reason" value={failureReason} onChange={(e) => setFailureReason(e.target.value)} />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="failure-form">Save</Button>
                  <Button type="button" variant="outline" onClick={() => setFailureDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete proxy?</AlertDialogTitle>
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


