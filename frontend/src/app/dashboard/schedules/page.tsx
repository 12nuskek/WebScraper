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
import { Power, CheckSquare, Trash2 } from "lucide-react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type Schedule = {
  id: number
  spider: number
  cron_expr: string
  timezone: string
  enabled: boolean
  next_run_at: string | null
}

type Paginated<T> = { count: number; results: T[] }

export default function SchedulesPage() {
  const [data, setData] = React.useState<Paginated<Schedule>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [createDialogOpen, setCreateDialogOpen] = React.useState(false)
  const [createSpiderId, setCreateSpiderId] = React.useState("")
  const [createCron, setCreateCron] = React.useState("")
  const [createTz, setCreateTz] = React.useState("UTC")
  const [creating, setCreating] = React.useState(false)
  const [deleteTarget, setDeleteTarget] = React.useState<Schedule | null>(null)

  async function refresh() {
    const res = await apiFetch<Paginated<Schedule>>("/schedules/")
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
    if (!spider || Number.isNaN(spider) || !createCron.trim()) return
    setCreating(true)
    const res = await apiFetch<Schedule>("/schedules/", { method: "POST", body: JSON.stringify({ spider, cron_expr: createCron.trim(), timezone: createTz }) })
    setCreating(false)
    if (res.ok) {
      setCreateDialogOpen(false)
      setCreateSpiderId("")
      setCreateCron("")
      setCreateTz("UTC")
      await refresh()
    }
  }

  async function handleToggleEnabled(s: Schedule) {
    const res = await apiFetch<Schedule>(`/schedules/${s.id}/${s.enabled ? "disable" : "enable"}/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  async function handleDelete(id: number) {
    const res = await apiFetch(`/schedules/${id}/`, { method: "DELETE" })
    if (res.ok) await refresh()
  }

  async function handleMarkExecuted(id: number) {
    const res = await apiFetch(`/schedules/${id}/mark_executed/`, { method: "POST" })
    if (res.ok) await refresh()
  }

  const columns: ColumnDef<Schedule>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    { accessorKey: "spider", header: ({ column }) => <DataTableColumnHeader column={column} title="Spider" /> },
    { accessorKey: "cron_expr", header: ({ column }) => <DataTableColumnHeader column={column} title="Cron" />, cell: ({ row }) => <span className="font-mono">{row.original.cron_expr}</span> },
    { accessorKey: "timezone", header: ({ column }) => <DataTableColumnHeader column={column} title="Timezone" /> },
    { accessorKey: "enabled", header: ({ column }) => <DataTableColumnHeader column={column} title="Enabled" />, cell: ({ row }) => (row.original.enabled ? "Yes" : "No") },
    { accessorKey: "next_run_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Next Run" />, cell: ({ row }) => row.original.next_run_at ? new Date(row.original.next_run_at).toLocaleString() : "-" },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          <Button size="icon" variant="outline" onClick={() => handleToggleEnabled(row.original)} title={row.original.enabled ? "Disable" : "Enable"} aria-label={row.original.enabled ? "Disable" : "Enable"}>
            <Power />
          </Button>
          <Button size="icon" variant="outline" onClick={() => handleMarkExecuted(row.original.id)} title="Mark Executed" aria-label="Mark Executed">
            <CheckSquare />
          </Button>
          <Button size="icon" variant="destructive" onClick={() => handleDelete(row.original.id)} title="Delete" aria-label="Delete">
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
                  <BreadcrumbPage>Schedules</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Schedules ({data.count})</CardTitle>
                <CardDescription>Automate when spiders run.</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={() => setCreateDialogOpen(true)}>New Schedule</Button>
                <Button size="sm" variant="outline" onClick={async () => {
                  const due = await apiFetch(`/schedules/due/`)
                  if (due.ok) window.alert("Fetched due schedules")
                }}>Due</Button>
                <Button size="sm" variant="outline" onClick={async () => {
                  const upcoming = await apiFetch(`/schedules/upcoming/`)
                  if (upcoming.ok) window.alert("Fetched upcoming schedules")
                }}>Upcoming</Button>
              </div>
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
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-7 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-8 w-8 justify-self-end rounded" />
                      </div>
                    ))}
                  </div>
                </div>
              ) : data.results.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">⏰</div>
                  <div className="text-lg font-medium">No schedules</div>
                  <div className="text-sm text-muted-foreground">Create a schedule to run spiders automatically.</div>
                  <div className="mt-4">
                    <Button onClick={() => setCreateDialogOpen(true)}>New Schedule</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="cron_expr" filterPlaceholder="Filter cron..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>New Schedule</DialogTitle>
              </DialogHeader>
              <form id="create-schedule-form" onSubmit={handleCreateSubmit} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="sch-spider">Spider ID</Label>
                  <Input id="sch-spider" inputMode="numeric" value={createSpiderId} onChange={(e) => setCreateSpiderId(e.target.value.replace(/[^0-9]/g, ""))} required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="sch-cron">Cron expression</Label>
                  <Input id="sch-cron" value={createCron} onChange={(e) => setCreateCron(e.target.value)} placeholder="0 * * * *" required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="sch-tz">Timezone</Label>
                  <Input id="sch-tz" value={createTz} onChange={(e) => setCreateTz(e.target.value)} placeholder="UTC" required />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="create-schedule-form" disabled={creating}>{creating ? "Creating…" : "Create"}</Button>
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete schedule?</AlertDialogTitle>
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


