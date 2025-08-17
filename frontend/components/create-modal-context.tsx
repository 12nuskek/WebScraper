"use client"

import type React from "react"
import { createContext, useContext, useState } from "react"

interface CreateModalContextType {
  openProjectForm: () => void
  openSpiderForm: () => void
  isCreateModalOpen: boolean
  setIsCreateModalOpen: (open: boolean) => void
  showProjectForm: boolean
  setShowProjectForm: (show: boolean) => void
  showSpiderForm: boolean
  setShowSpiderForm: (show: boolean) => void
}

const CreateModalContext = createContext<CreateModalContextType | undefined>(undefined)

export function CreateModalProvider({ children }: { children: React.ReactNode }) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [showProjectForm, setShowProjectForm] = useState(false)
  const [showSpiderForm, setShowSpiderForm] = useState(false)

  const openProjectForm = () => {
    setShowProjectForm(true)
    setShowSpiderForm(false)
    setIsCreateModalOpen(true)
  }

  const openSpiderForm = () => {
    setShowSpiderForm(true)
    setShowProjectForm(false)
    setIsCreateModalOpen(true)
  }

  return (
    <CreateModalContext.Provider
      value={{
        openProjectForm,
        openSpiderForm,
        isCreateModalOpen,
        setIsCreateModalOpen,
        showProjectForm,
        setShowProjectForm,
        showSpiderForm,
        setShowSpiderForm,
      }}
    >
      {children}
    </CreateModalContext.Provider>
  )
}

export function useCreateModal() {
  const context = useContext(CreateModalContext)
  if (context === undefined) {
    throw new Error("useCreateModal must be used within a CreateModalProvider")
  }
  return context
}
