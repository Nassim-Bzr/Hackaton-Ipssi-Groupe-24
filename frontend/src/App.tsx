import { Navigate, Route, Routes } from "react-router-dom"

import { Navbar } from "@/components/Navbar"
import { DocumentsPage } from "@/pages/DocumentsPage"
import { UploadPage } from "@/pages/UploadPage"

export function App() {
  return (
    <main className="max-w-7xl mx-auto p-6">
      <Navbar />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  )
}

export default App
