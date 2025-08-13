"use client"

import * as React from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { apiFetch, createJob } from "@/lib/api"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Switch } from "@/components/ui/switch"
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/data-table"
import { DataTableColumnHeader } from "@/components/data-table-column-header"
import { Pencil, Trash2, PlusCircle } from "lucide-react"
import Link from "next/link"
import { useSearchParams, useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { Skeleton } from "@/components/ui/skeleton"

type Spider = {
  id: number
  project: number
  name: string
  start_urls_json: string[] | string | Record<string, unknown> | null
  settings_json: Record<string, unknown> | null
  parse_rules_json: Record<string, unknown> | null
  created_at: string
}

type Paginated<T> = { count: number; results: T[] }

type Project = {
  id: number
  name: string
}

type ParseRule = { id: string; key: string; value: string }

export default function SpidersPage() {
  const [data, setData] = React.useState<Paginated<Spider>>({ count: 0, results: [] })
  const [loading, setLoading] = React.useState(true)
  const [formCardOpen, setFormCardOpen] = React.useState(false)
  const [editing, setEditing] = React.useState<Spider | null>(null)
  const [formProject, setFormProject] = React.useState<string>("")
  const [formName, setFormName] = React.useState<string>("")
  const [formStartUrls, setFormStartUrls] = React.useState<string>("")

  // Browser Settings
  const [formHeadless, setFormHeadless] = React.useState<boolean>(true)
  const [formBlockImages, setFormBlockImages] = React.useState<boolean>(false)
  const [formBlockImagesAndCss, setFormBlockImagesAndCss] = React.useState<boolean>(false)
  const [formUserAgent, setFormUserAgent] = React.useState<string>("")
  const [formWindowSize, setFormWindowSize] = React.useState<string>("")
  const [formWaitForCompletePageLoad, setFormWaitForCompletePageLoad] = React.useState<boolean>(false)
  const [formMaxRetry, setFormMaxRetry] = React.useState<number>(3)

  // Parsing Rules
  const [formParseRules, setFormParseRules] = React.useState<ParseRule[]>([])

  const [saving, setSaving] = React.useState(false)
  const [projects, setProjects] = React.useState<Project[]>([])
  const [projectsLoading, setProjectsLoading] = React.useState<boolean>(false)
  const [projectFilter, setProjectFilter] = React.useState<string>("")
  const [urlsDialogOpen, setUrlsDialogOpen] = React.useState(false)
  const [urlsDialogList, setUrlsDialogList] = React.useState<string[]>([])
  const [deleteTarget, setDeleteTarget] = React.useState<Spider | null>(null)
  const searchParams = useSearchParams()
  const router = useRouter()
  const { toast } = useToast()

  async function refresh(selectedProject?: string) {
    const projectParam = selectedProject ?? projectFilter
    const qs = projectParam ? `?project=${encodeURIComponent(projectParam)}` : ""
    const res = await apiFetch<Paginated<Spider>>(`/spiders/${qs}`)
    if (res.ok && res.data) setData(res.data)
  }

  React.useEffect(() => {
    ;(async () => {
      const initialProject = searchParams.get("project") || ""
      if (initialProject) setProjectFilter(initialProject)
      await refresh(initialProject || undefined)
      setLoading(false)
    })()
  }, [])

  React.useEffect(() => {
    ;(async () => {
      setProjectsLoading(true)
      const res = await apiFetch<Paginated<Project>>("/projects/")
      if (res.ok && res.data) setProjects(res.data.results)
      setProjectsLoading(false)
    })()
  }, [])

  function resetForm() {
    setFormProject("")
    setFormName("")
    setFormStartUrls("")
    setFormHeadless(true)
    setFormBlockImages(false)
    setFormBlockImagesAndCss(false)
    setFormUserAgent("")
    setFormWindowSize("")
    setFormWaitForCompletePageLoad(false)
    setFormMaxRetry(3)
    setFormParseRules([])
  }

  function openCreate() {
    setEditing(null)
    resetForm()
    setFormCardOpen(true)
  }

  function openEdit(s: Spider) {
    setEditing(s)
    resetForm()
    setFormProject(String(s.project))
    setFormName(s.name)

    const urls = Array.isArray(s.start_urls_json)
      ? (s.start_urls_json as string[])
      : typeof s.start_urls_json === "string"
      ? [s.start_urls_json]
      : Array.isArray((s.start_urls_json as any)?.urls)
      ? ((s.start_urls_json as any).urls as string[])
      : []
    setFormStartUrls(urls.join("\n"))

    if (s.settings_json) {
      setFormHeadless(s.settings_json.headless === true)
      setFormBlockImages(s.settings_json.block_images === true)
      setFormBlockImagesAndCss(s.settings_json.block_images_and_css === true)
      setFormUserAgent(s.settings_json.user_agent as string || "")
      setFormWindowSize(s.settings_json.window_size as string || "")
      setFormWaitForCompletePageLoad(s.settings_json.wait_for_complete_page_load === true)
      setFormMaxRetry(s.settings_json.max_retry as number ?? 3)
    }

    if (s.parse_rules_json) {
      const rules = Object.entries(s.parse_rules_json).map(([key, value]) => ({
        id: crypto.randomUUID(),
        key,
        value: value as string,
      }))
      setFormParseRules(rules)
    }

    setFormCardOpen(true)
  }

  async function submitSpider(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    if (!formProject || isNaN(Number(formProject))) {
      setSaving(false)
      return
    }
    const project = Number(formProject)
    const start_urls_json = formStartUrls
      .split(/\n|\r|,/)
      .map((s) => s.trim())
      .filter(Boolean)

    const settings_json: Record<string, unknown> = {
      headless: formHeadless,
      block_images: formBlockImages,
      block_images_and_css: formBlockImagesAndCss,
      wait_for_complete_page_load: formWaitForCompletePageLoad,
      max_retry: formMaxRetry,
    }
    if (formUserAgent) settings_json.user_agent = formUserAgent
    if (formWindowSize) settings_json.window_size = formWindowSize

    const parse_rules_json: Record<string, string> = {}
    for (const rule of formParseRules) {
      if (rule.key && rule.value) {
        parse_rules_json[rule.key] = rule.value
      }
    }

    const payload = {
      project,
      name: formName.trim(),
      start_urls_json,
      settings_json,
      parse_rules_json,
    }
    const res = await apiFetch<Spider>(editing ? `/spiders/${editing.id}/` : "/spiders/", {
      method: editing ? "PUT" : "POST",
      body: JSON.stringify(payload),
    })
    setSaving(false)
    if (res.ok) {
      setFormCardOpen(false)
      toast({ title: editing ? "Spider updated" : "Spider created" })
      await refresh()
    }
  }

  async function handleDelete(id: number) {
    const res = await apiFetch(`/spiders/${id}/`, { method: "DELETE" })
    if (res.ok) {
      toast({ title: "Spider deleted" })
      await refresh()
    }
  }

  async function handleRunSpider(id: number) {
    const res = await createJob({ spider: id })
    if (res.ok) {
      toast({ title: "Job started", description: `Job #${res.data!.id} created` })
      router.push("/dashboard/jobs?status=running")
    } else {
      toast({ title: "Failed to start job", description: "Please try again.", variant: "destructive" as any })
    }
  }

  function openUrlsDialog(spider: Spider) {
    const urls = Array.isArray(spider.start_urls_json)
      ? (spider.start_urls_json as string[])
      : typeof spider.start_urls_json === "string"
      ? [spider.start_urls_json]
      : Array.isArray((spider.start_urls_json as any)?.urls)
      ? ((spider.start_urls_json as any).urls as string[])
      : []
    setUrlsDialogList(urls)
    setUrlsDialogOpen(true)
  }

  const columns: ColumnDef<Spider>[] = [
    {
      accessorKey: "id",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="ID" />
      ),
      cell: ({ row }) => row.original.id,
    },
    {
      accessorKey: "name",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Name" />
      ),
    },
    {
      accessorKey: "project",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Project" />
      ),
      cell: ({ row }) => (
        <Link href={`/dashboard/spiders?project=${row.original.project}`} className="underline underline-offset-2">
          #{row.original.project}
        </Link>
      ),
    },
    {
      id: "start_urls_count",
      header: "Start URLs",
      cell: ({ row }) => {
        const s = row.original
        const urls = Array.isArray(s.start_urls_json)
          ? (s.start_urls_json as string[])
          : typeof s.start_urls_json === "string"
          ? [s.start_urls_json]
          : Array.isArray((s.start_urls_json as any)?.urls)
          ? ((s.start_urls_json as any).urls as string[])
          : []
        return (
          <Button variant="ghost" size="sm" onClick={() => openUrlsDialog(s)}>
            {urls.length}
          </Button>
        )
      },
    },
    {
      accessorKey: "created_at",
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Created" />
      ),
      cell: ({ row }) => new Date(row.original.created_at).toLocaleString(),
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={() => handleRunSpider(row.original.id)} title="Run" aria-label="Run">
            Run
          </Button>
          <Button size="sm" variant="outline" asChild title="Jobs" aria-label="Jobs">
            <Link href={`/dashboard/jobs?spider=${row.original.id}`}>Jobs</Link>
          </Button>
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
                  <BreadcrumbPage>Spiders</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Filters</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-3">
              <div className="grid gap-2">
                <Label htmlFor="filter-project">Project</Label>
                <Select
                  value={projectFilter}
                  onValueChange={async (v) => {
                    const newVal = v === "__all__" ? "" : v
                    setProjectFilter(newVal)
                    const url = newVal ? `/dashboard/spiders?project=${newVal}` : "/dashboard/spiders"
                    router.push(url)
                    await refresh(newVal)
                  }}
                >
                  <SelectTrigger id="filter-project">
                    <SelectValue placeholder={projectsLoading ? "Loading projects…" : "All projects"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__all__">All</SelectItem>
                    {projects.map((p) => (
                      <SelectItem key={p.id} value={String(p.id)}>
                        {p.name} (#{p.id})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
          <Dialog open={formCardOpen} onOpenChange={setFormCardOpen}>
            <DialogContent className="max-w-3xl">
              <DialogHeader>
                <DialogTitle>{editing ? "Edit Spider" : "New Spider"}</DialogTitle>
              </DialogHeader>
              <form id="spider-form" onSubmit={submitSpider}>
                <Tabs defaultValue="general">
                  <TabsList className="mb-4">
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="settings">Browser Settings</TabsTrigger>
                    <TabsTrigger value="parsing">Parsing Rules</TabsTrigger>
                  </TabsList>
                  <TabsContent value="general" className="flex flex-col gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="spider-project">Project</Label>
                      <Select value={formProject} onValueChange={setFormProject}>
                        <SelectTrigger id="spider-project">
                          <SelectValue placeholder={projectsLoading ? "Loading projects…" : "Select a project"} />
                        </SelectTrigger>
                        <SelectContent>
                          {projects.map((p) => (
                            <SelectItem key={p.id} value={String(p.id)}>
                              {p.name} (#{p.id})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="spider-name">Name</Label>
                      <Input id="spider-name" value={formName} onChange={(e) => setFormName(e.target.value)} required />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="spider-urls">Start URLs (one per line)</Label>
                      <Textarea id="spider-urls" value={formStartUrls} onChange={(e) => setFormStartUrls(e.target.value)} rows={8} />
                    </div>
                  </TabsContent>
                  <TabsContent value="settings" className="grid gap-y-6 gap-x-4 md:grid-cols-2">
                    <div className="flex items-center space-x-2">
                      <Switch id="headless" checked={formHeadless} onCheckedChange={setFormHeadless} />
                      <Label htmlFor="headless">Headless Browser</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch id="block_images" checked={formBlockImages} onCheckedChange={setFormBlockImages} />
                      <Label htmlFor="block_images">Block Images</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch id="block_images_and_css" checked={formBlockImagesAndCss} onCheckedChange={setFormBlockImagesAndCss} />
                      <Label htmlFor="block_images_and_css">Block Images and CSS</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Switch id="wait_for_complete_page_load" checked={formWaitForCompletePageLoad} onCheckedChange={setFormWaitForCompletePageLoad} />
                      <Label htmlFor="wait_for_complete_page_load">Wait for Full Page Load</Label>
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="user-agent">User Agent</Label>
                      <Input id="user-agent" value={formUserAgent} onChange={(e) => setFormUserAgent(e.target.value)} placeholder="e.g. Mozilla/5.0..." />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="window-size">Window Size</Label>
                      <Input id="window-size" value={formWindowSize} onChange={(e) => setFormWindowSize(e.target.value)} placeholder="e.g. 1920x1080" />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="max-retry">Max Retries</Label>
                      <Input id="max-retry" type="number" value={formMaxRetry} onChange={(e) => setFormMaxRetry(Number(e.target.value))} />
                    </div>
                  </TabsContent>
                  <TabsContent value="parsing">
                    <div className="flex flex-col gap-4">
                      {formParseRules.map((rule, index) => (
                        <div key={rule.id} className="flex items-center gap-2">
                          <Input
                            placeholder="Key (e.g. title)"
                            value={rule.key}
                            onChange={(e) => {
                              const newRules = [...formParseRules]
                              newRules[index].key = e.target.value
                              setFormParseRules(newRules)
                            }}
                          />
                          <Input
                            placeholder="Value (e.g. h1)"
                            value={rule.value}
                            onChange={(e) => {
                              const newRules = [...formParseRules]
                              newRules[index].value = e.target.value
                              setFormParseRules(newRules)
                            }}
                          />
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => {
                              const newRules = formParseRules.filter((_, i) => i !== index)
                              setFormParseRules(newRules)
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setFormParseRules([...formParseRules, { id: crypto.randomUUID(), key: "", value: "" }])}
                      >
                        <PlusCircle className="mr-2 h-4 w-4" />
                        Add Rule
                      </Button>
                    </div>
                  </TabsContent>
                </Tabs>
              </form>
              <DialogFooter>
                <div className="flex gap-2">
                  <Button type="submit" form="spider-form" disabled={saving || !formName.trim() || !formProject}>
                    {saving ? "Saving…" : "Save"}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setFormCardOpen(false)}>Cancel</Button>
                </div>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-4">
              <div className="space-y-1">
                <CardTitle>Spiders ({data.count})</CardTitle>
                <CardDescription>Define entry points and run jobs for each project.</CardDescription>
              </div>
              <Button size="sm" onClick={openCreate} disabled={formCardOpen}>New Spider</Button>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-9 w-56" />
                  <div className="overflow-hidden rounded-md border">
                    <div className="grid grid-cols-6 gap-2 border-b p-3">
                      <Skeleton className="h-4 w-12" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-16 justify-self-end" />
                    </div>
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="grid grid-cols-6 items-center gap-2 p-3">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-36" />
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
                  <div className="mx-auto mb-2 h-12 w-12 rounded-full border flex items-center justify-center text-muted-foreground">🕷️</div>
                  <div className="text-lg font-medium">No spiders</div>
                  <div className="text-sm text-muted-foreground">Create spiders to crawl sites for a project.</div>
                  <div className="mt-4">
                    <Button onClick={openCreate}>New Spider</Button>
                  </div>
                </div>
              ) : (
                <DataTable columns={columns} data={data.results} filterKey="name" filterPlaceholder="Filter names..." />
              )}
            </CardContent>
          </Card>
          <Dialog open={urlsDialogOpen} onOpenChange={setUrlsDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Start URLs</DialogTitle>
              </DialogHeader>
              <div className="max-h-[60vh] overflow-auto space-y-2">
                {urlsDialogList.length === 0 ? (
                  <div className="text-muted-foreground">No start URLs.</div>
                ) : (
                  urlsDialogList.map((u, i) => (
                    <div key={`${u}-${i}`} className="text-sm break-all">
                      {u}
                    </div>
                  ))
                )}
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setUrlsDialogOpen(false)}>Close</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Delete spider?</AlertDialogTitle>
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


