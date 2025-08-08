"use client"

import * as React from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { apiFetch } from "@/lib/api"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/data-table"
import { DataTableColumnHeader } from "@/components/data-table-column-header"
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type Project = {
  id: number
  name: string
  notes: string
  created_at: string
}

type Paginated<T> = { count: number; results: T[] }

export default function ProjectsPage() {
  const [data, setData] = React.useState<Paginated<Project>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [formDialogOpen, setFormDialogOpen] = React.useState(false)
  const [editing, setEditing] = React.useState<Project | null>(null)
  const [formName, setFormName] = React.useState("")
  const [formNotes, setFormNotes] = React.useState("")
  const [saving, setSaving] = React.useState(false)
  const [deleteTarget, setDeleteTarget] = React.useState<Project | null>(null)
  const { toast } = useToast()
  const router = useRouter()

  async function refresh() {
    const res = await apiFetch<Paginated<Project>>("/projects/")
    if (res.ok && res.data) setData(res.data)
  }

  React.useEffect(() => {
    ;(async () => {
      await refresh()
      setLoading(false)
    })()
  }, [])

  function openCreate() {
    setEditing(null)
    setFormName("")
    setFormNotes("")
    setFormDialogOpen(true)
  }

  function openEdit(p: Project) {
    setEditing(p)
    setFormName(p.name)
    setFormNotes(p.notes ?? "")
    setFormDialogOpen(true)
  }

  async function submitProject(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    const payload = { name: formName.trim(), notes: formNotes }
    const res = await apiFetch<Project>(editing ? `/projects/${editing.id}/` : "/projects/", {
      method: editing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    })
    setSaving(false)
    if (res.ok) {
      setFormDialogOpen(false)
      toast({ title: editing ? "Project updated" : "Project created" })
      await refresh()
    } else {
      toast({ title: "Save failed", description: "Please try again.", variant: "destructive" })
    }
  }

  async function handleDelete(project: Project) {
    const res = await apiFetch(`/projects/${project.id}/`, { method: "DELETE" })
    if (res.ok) {
      toast({ title: "Project deleted" })
      await refresh()
    } else {
      toast({ title: "Delete failed", description: "Please try again.", variant: "destructive" })
    }
  }

  function formatDateTime(value?: string | null) {
    if (!value) return "—"
    try {
      return new Date(value).toLocaleString()
    } catch {
      return String(value)
    }
  }

  function formatRelativeTime(value?: string | null) {
    if (!value) return ""
    const date = new Date(value)
    const diffMs = Date.now() - date.getTime()
    const seconds = Math.round(diffMs / 1000)
    const minutes = Math.round(seconds / 60)
    const hours = Math.round(minutes / 60)
    const days = Math.round(hours / 24)
    if (Math.abs(seconds) < 60) return `${seconds}s ago`
    if (Math.abs(minutes) < 60) return `${minutes}m ago`
    if (Math.abs(hours) < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  const columns: ColumnDef<Project>[] = [
    { accessorKey: "id", header: ({ column }) => <DataTableColumnHeader column={column} title="ID" /> },
    {
      accessorKey: "name",
      header: ({ column }) => <DataTableColumnHeader column={column} title="Name" />,
      cell: ({ row }) => (
        <Link href={`/dashboard/spiders?project=${row.original.id}`} className="underline-offset-4 hover:underline font-medium">
          {row.original.name}
        </Link>
      ),
    },
    {
      accessorKey: "notes",
      header: ({ column }) => <DataTableColumnHeader column={column} title="Notes" />,
      cell: ({ row }) => (
        <span className="max-w-[40ch] truncate inline-block" title={row.original.notes}>{row.original.notes}</span>
      ),
    },
    {
      accessorKey: "created_at",
      header: ({ column }) => <DataTableColumnHeader column={column} title="Created" />,
      cell: ({ row }) => (
        <div className="flex flex-col">
          <span title={formatDateTime(row.original.created_at)}>{new Date(row.original.created_at).toLocaleDateString()}</span>
          <span className="text-xs text-muted-foreground">{formatRelativeTime(row.original.created_at)}</span>
        </div>
      ),
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button size="icon" variant="ghost" aria-label="Actions">
              <MoreHorizontal />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/dashboard/spiders?project=${row.original.id}`}>View spiders</Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => openEdit(row.original)}>
              <Pencil className="mr-2 h-4 w-4" /> Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={() => setDeleteTarget(row.original)}>
              <Trash2 className="mr-2 h-4 w-4" /> Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
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
                  <BreadcrumbPage>Projects</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Projects ({data.count})</CardTitle>
                <CardDescription>Create and organize your scraping projects.</CardDescription>
              </div>
              <div className="ml-auto flex items-center gap-2">
                <Button size="sm" variant="outline" disabled>
                  Import
                </Button>
                <Button size="sm" onClick={openCreate} disabled={formDialogOpen}>New Project</Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-9 w-56" />
                  <div className="overflow-hidden rounded-md border">
                    <div className="grid grid-cols-4 gap-2 border-b p-3">
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-36" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-4 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-48" />
                        <Skeleton className="h-4 w-64" />
                        <Skeleton className="h-8 w-8 justify-self-end rounded" />
                      </div>
                    ))}
                  </div>
                </div>
              ) : data.results.length === 0 ? (
                <div className="py-12 text-center">
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">🏗️</div>
                  <div className="text-lg font-medium">No projects yet</div>
                  <div className="text-sm text-muted-foreground">Create your first project to start organizing spiders and jobs.</div>
                  <div className="mt-4">
                    <Button onClick={openCreate}>Create Project</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="name" filterPlaceholder="Filter names..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={formDialogOpen} onOpenChange={setFormDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editing ? "Edit Project" : "New Project"}</DialogTitle>
              </DialogHeader>
              <form id="project-form" onSubmit={submitProject} className="flex flex-col gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="project-name">Name</Label>
                  <Input id="project-name" value={formName} onChange={(e) => setFormName(e.target.value)} required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="project-notes">Notes</Label>
                  <Textarea id="project-notes" value={formNotes} onChange={(e) => setFormNotes(e.target.value)} rows={6} />
                </div>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="project-form" disabled={saving}>{saving ? "Saving…" : "Save"}</Button>
                  <Button type="button" variant="outline" onClick={() => setFormDialogOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete project?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. {deleteTarget ? `"${deleteTarget.name}"` : "This project"} and its related data may become inaccessible.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel onClick={() => setDeleteTarget(null)}>Cancel</AlertDialogCancel>
                <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90" onClick={async () => {
                  if (deleteTarget) {
                    const target = deleteTarget
                    setDeleteTarget(null)
                    await handleDelete(target)
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


