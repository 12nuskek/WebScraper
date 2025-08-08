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
import { Eye, Trash2 } from "lucide-react"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type ResponseItem = {
  id: number
  request: number
  final_url: string | null
  status_code: number | null
  fetched_at: string
  latency_ms: number | null
  from_cache: boolean
  body_size: number
}

type Paginated<T> = { count: number; results: T[] }

export default function ResponsesPage() {
  const [data, setData] = React.useState<Paginated<ResponseItem>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [deleteTarget, setDeleteTarget] = React.useState<ResponseItem | null>(null)
  const [bodyDialogOpen, setBodyDialogOpen] = React.useState(false)
  const [bodyContent, setBodyContent] = React.useState<string>("")

  async function refresh() {
    const res = await apiFetch<Paginated<ResponseItem>>("/responses/")
    if (res.ok && res.data) setData(res.data)
  }

  React.useEffect(() => {
    ;(async () => {
      await refresh()
      setLoading(false)
    })()
  }, [])

  async function handleDelete(id: number) {
    const res = await apiFetch(`/responses/${id}/`, { method: "DELETE" })
    if (res.ok) await refresh()
  }

  async function handleViewBody(id: number) {
    const res = await apiFetch<{ body?: string; content_type?: string }>(`/responses/${id}/body/`)
    if (res.ok && res.data?.body != null) {
      setBodyContent(res.data.body)
      setBodyDialogOpen(true)
    }
  }

  const columns: ColumnDef<ResponseItem>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    { accessorKey: "request", header: ({ column }) => <DataTableColumnHeader column={column} title="Request" /> },
    { accessorKey: "status_code", header: ({ column }) => <DataTableColumnHeader column={column} title="Status" /> },
    { accessorKey: "latency_ms", header: ({ column }) => <DataTableColumnHeader column={column} title="Latency (ms)" /> },
    { accessorKey: "from_cache", header: ({ column }) => <DataTableColumnHeader column={column} title="From Cache" />, cell: ({ row }) => (row.original.from_cache ? "Yes" : "No") },
    { accessorKey: "body_size", header: ({ column }) => <DataTableColumnHeader column={column} title="Size (bytes)" /> },
    { accessorKey: "fetched_at", header: ({ column }) => <DataTableColumnHeader column={column} title="Fetched" />, cell: ({ row }) => new Date(row.original.fetched_at).toLocaleString() },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button size="icon" variant="outline" onClick={() => handleViewBody(row.original.id)} title="View Body" aria-label="View Body">
            <Eye />
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
                  <BreadcrumbPage>Responses</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Responses ({data.count})</CardTitle>
                <CardDescription>Inspect and manage fetched responses.</CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={async () => {
                    const stats = await apiFetch(`/responses/stats/`)
                    if (stats.ok) window.alert("Fetched response stats")
                  }}
                >
                  Get Stats
                </Button>
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
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-7 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-36" />
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
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">📦</div>
                  <div className="text-lg font-medium">No responses</div>
                  <div className="text-sm text-muted-foreground">Responses will appear as requests are executed.</div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="status_code" filterPlaceholder="Filter status..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={bodyDialogOpen} onOpenChange={setBodyDialogOpen}>
            <DialogContent className="max-w-3xl">
              <DialogHeader>
                <DialogTitle>Response Body</DialogTitle>
              </DialogHeader>
              <div className="max-h-[60vh] overflow-auto whitespace-pre-wrap text-sm">
                {bodyContent || "(empty body)"}
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setBodyDialogOpen(false)}>Close</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete response?</AlertDialogTitle>
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


